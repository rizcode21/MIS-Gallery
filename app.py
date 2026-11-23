import os
import sys
import json
import shutil
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk
import svg_optimizer
import web_server

# Enable high DPI awareness on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_engine_path():
    """Locate the bundled or external svg2font core executable."""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    candidates = [
        os.path.join(base_dir, "bin", "svg2font_core.exe"),
        os.path.join(base_dir, "svg2font_core.exe"),
        os.path.join(base_dir, "bin", "svg2font.exe"),
        os.path.join(base_dir, "svg2font.exe"),
        r"D:\RIZ\Kantor\svg2font.exe",
    ]

    for p in candidates:
        if os.path.isfile(p):
            return p
    return "svg2font.exe"


def generate_interactive_preview_html(output_dir, font_name, prefix, info_data):
    """Generate a modern, responsive HTML preview with search and click-to-copy."""
    css_file = f"{font_name}.css"
    glyphs_html = []

    for name, data in info_data.items():
        cls_name = data.get("className", f"{prefix}{name}")
        encoded_code = data.get("encodedCode", "")
        # Remove leading backslash for display if present
        clean_code = encoded_code.replace("\\", "")
        glyphs_html.append(f"""
        <div class="icon-card" data-name="{name}" onclick="copyCode('{cls_name}', '{encoded_code}')">
            <div class="icon-glyph"><i class="{cls_name}"></i></div>
            <div class="icon-name" title="{name}">{name}</div>
            <div class="icon-code">{clean_code}</div>
        </div>
        """)

    all_glyphs = "\n".join(glyphs_html)

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview Font: {font_name}</title>
    <link rel="stylesheet" href="{css_file}">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --card-hover: #334155;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.2);
            --border-color: #334155;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            padding: 30px 20px;
            min-height: 100vh;
        }}
        .header {{
            max-width: 1200px;
            margin: 0 auto 30px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }}
        .header-title h1 {{
            font-size: 26px;
            font-weight: 700;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .header-title p {{
            font-size: 14px;
            color: var(--text-sub);
            margin-top: 4px;
        }}
        .controls {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .search-box {{
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background: var(--card-bg);
            color: var(--text-main);
            font-size: 14px;
            outline: none;
            width: 250px;
            transition: border-color 0.2s;
        }}
        .search-box:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 2px var(--accent-glow);
        }}
        .size-slider {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: var(--text-sub);
        }}
        .size-slider input {{
            cursor: pointer;
            accent-color: var(--accent);
        }}
        .grid {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 16px;
        }}
        .icon-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px 12px 14px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .icon-card:hover {{
            background: var(--card-hover);
            transform: translateY(-2px);
            border-color: var(--accent);
            box-shadow: 0 4px 12px var(--accent-glow);
        }}
        .icon-glyph {{
            font-size: 36px;
            color: var(--text-main);
            margin-bottom: 12px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: font-size 0.2s;
        }}
        .icon-name {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-main);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 100%;
        }}
        .icon-code {{
            font-size: 11px;
            font-family: monospace;
            color: var(--text-sub);
            margin-top: 4px;
        }}
        #toast {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #0284c7;
            color: #ffffff;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
            z-index: 1000;
        }}
        #toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}
        .stats {{
            font-size: 13px;
            color: var(--text-sub);
            margin-top: 6px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h1>🎨 {font_name} Font Preview</h1>
            <p>Total Ikon: <span id="count">{len(info_data)}</span> | Prefix CSS: <code>.{prefix}*</code></p>
            <div class="stats">Klik kartu ikon untuk menyalin class CSS ke clipboard</div>
        </div>
        <div class="controls">
            <input type="text" id="search" class="search-box" placeholder="Cari nama ikon..." oninput="filterIcons()">
            <div class="size-slider">
                <span>Ukuran:</span>
                <input type="range" id="size" min="16" max="72" value="36" oninput="changeSize(this.value)">
                <span id="size-val">36px</span>
            </div>
        </div>
    </div>

    <div class="grid" id="grid">
        {all_glyphs}
    </div>

    <div id="toast">Tersalin ke clipboard!</div>

    <script>
        function copyCode(className, code) {{
            const tag = `<i class="${{className}}"></i>`;
            navigator.clipboard.writeText(tag).then(() => {{
                showToast(`Tersalin: ${{tag}}`);
            }}).catch(() => {{
                showToast(`Class: .${{className}}`);
            }});
        }}

        function showToast(msg) {{
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.classList.add('show');
            setTimeout(() => {{
                t.classList.remove('show');
            }}, 2200);
        }}

        function filterIcons() {{
            const query = document.getElementById('search').value.toLowerCase();
            const cards = document.querySelectorAll('.icon-card');
            let visible = 0;
            cards.forEach(card => {{
                const name = card.getAttribute('data-name').toLowerCase();
                if (name.includes(query)) {{
                    card.style.display = 'flex';
                    visible++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});
            document.getElementById('count').innerText = visible;
        }}

        function changeSize(val) {{
            document.getElementById('size-val').innerText = val + 'px';
            const glyphs = document.querySelectorAll('.icon-glyph');
            glyphs.forEach(g => {{
                g.style.fontSize = val + 'px';
                g.style.height = (parseInt(val) + 12) + 'px';
            }});
        }}
    </script>
</body>
</html>
"""
    preview_path = os.path.join(output_dir, "preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return preview_path


class SVGToFontApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SVG to Font Studio - GUI Converter")
        self.geometry("820x760")
        self.minsize(750, 680)

        # Apply Modern Theme
        try:
            sv_ttk.set_theme("dark")
        except Exception:
            pass

        # Variables
        self.source_dir = tk.StringVar(value="")
        self.output_dir = tk.StringVar(value="")
        self.font_name = tk.StringVar(value="my-icons")
        self.prefix = tk.StringVar(value="icon")
        self.start_unicode = tk.StringVar(value="59905")

        # Feature Flags (All features from README)
        self.var_convert_shapes = tk.BooleanVar(value=True)    # -convert-shapes
        self.var_empty_output = tk.BooleanVar(value=True)      # -empty
        self.var_generate_info = tk.BooleanVar(value=True)     # -info
        self.var_generate_css = tk.BooleanVar(value=True)      # uncheck -> -no-css
        self.var_generate_symbols = tk.BooleanVar(value=True)  # uncheck -> -no-symbols
        self.var_generate_preview = tk.BooleanVar(value=True)  # interactive HTML demo

        # Format Toggles
        self.fmt_ttf = tk.BooleanVar(value=True)
        self.fmt_woff = tk.BooleanVar(value=True)
        self.fmt_woff2 = tk.BooleanVar(value=True)
        self.fmt_eot = tk.BooleanVar(value=True)
        self.fmt_svg = tk.BooleanVar(value=False)

        self.svg_count = 0
        self.last_preview_path = None
        self.last_output_dir = None

        # Web Server Manager for macOS access
        self.web_manager = web_server.WebServerManager(8080)
        self.web_server_active = False
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._build_ui()
        self._check_engine()

    def _build_ui(self):
        # Main Canvas with Scrollbar for flexibility
        main_frame = ttk.Frame(self, padding="20 15 20 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Banner
        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 15))

        title_lbl = ttk.Label(
            header,
            text="SVG to Font Studio",
            font=("Segoe UI", 18, "bold"),
            foreground="#38bdf8"
        )
        title_lbl.pack(anchor=tk.W)

        sub_lbl = ttk.Label(
            header,
            text="Ubah kumpulan ikon SVG menjadi file font (TTF, WOFF, WOFF2, EOT), CSS, dan HTML preview dengan mudah.",
            font=("Segoe UI", 9)
        )
        sub_lbl.pack(anchor=tk.W, pady=(2, 0))

        # --- Card 1: Direktori Input & Output ---
        dir_card = ttk.LabelFrame(main_frame, text=" 📁 Lokasi File ", padding="12 10")
        dir_card.pack(fill=tk.X, pady=(0, 12))

        # Source
        ttk.Label(dir_card, text="Folder Sumber SVG:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        src_entry = ttk.Entry(dir_card, textvariable=self.source_dir)
        src_entry.grid(row=0, column=1, sticky=tk.EW, padx=8, pady=4)
        src_btn = ttk.Button(dir_card, text="Pilih Folder...", command=self._browse_source)
        src_btn.grid(row=0, column=2, padx=2, pady=4)

        self.lbl_svg_info = ttk.Label(dir_card, text="Belum ada folder yang dipilih", foreground="#94a3b8", font=("Segoe UI", 8))
        self.lbl_svg_info.grid(row=1, column=1, sticky=tk.W, padx=8, pady=(0, 6))

        # Output
        ttk.Label(dir_card, text="Folder Tujuan Output:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=4)
        out_entry = ttk.Entry(dir_card, textvariable=self.output_dir)
        out_entry.grid(row=2, column=1, sticky=tk.EW, padx=8, pady=4)
        out_btn = ttk.Button(dir_card, text="Pilih Folder...", command=self._browse_output)
        out_btn.grid(row=2, column=2, padx=2, pady=4)

        dir_card.columnconfigure(1, weight=1)

        # --- Card 2: Pengaturan Font & Identitas ---
        settings_card = ttk.LabelFrame(main_frame, text=" ⚙️ Pengaturan Font & Tampilan ", padding="12 10")
        settings_card.pack(fill=tk.X, pady=(0, 12))

        # Row 0: Nama Font & Prefix CSS
        ttk.Label(settings_card, text="Nama Font:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5), pady=4)
        font_entry = ttk.Entry(settings_card, textvariable=self.font_name, width=18)
        font_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=4)

        ttk.Label(settings_card, text="Prefix Class CSS:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5), pady=4)
        prefix_entry = ttk.Entry(settings_card, textvariable=self.prefix, width=15)
        prefix_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 20), pady=4)

        ttk.Label(settings_card, text="Start Unicode:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5), pady=4)
        unicode_entry = ttk.Entry(settings_card, textvariable=self.start_unicode, width=10)
        unicode_entry.grid(row=0, column=5, sticky=tk.W, pady=4)

        # Row 1: Fitur Unggulan (Convert Shapes & Empty Output)
        ttk.Separator(settings_card, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=6, sticky=tk.EW, pady=8)

        feat_frame = ttk.Frame(settings_card)
        feat_frame.grid(row=2, column=0, columnspan=6, sticky=tk.W)

        c1 = ttk.Checkbutton(
            feat_frame,
            text="Konversi Bentuk Otomatis (rect, circle, line, polygon) [-convert-shapes]",
            variable=self.var_convert_shapes
        )
        c1.pack(anchor=tk.W, pady=2)

        c2 = ttk.Checkbutton(
            feat_frame,
            text="Bersihkan folder tujuan terlebih dahulu [-empty]",
            variable=self.var_empty_output
        )
        c2.pack(anchor=tk.W, pady=2)

        c3 = ttk.Checkbutton(
            feat_frame,
            text="Buat file CSS (@font-face & class ikon) [-css]",
            variable=self.var_generate_css
        )
        c3.pack(anchor=tk.W, pady=2)

        c4 = ttk.Checkbutton(
            feat_frame,
            text="Buat file info.json (Metadata Unicode) [-info]",
            variable=self.var_generate_info
        )
        c4.pack(anchor=tk.W, pady=2)

        c5 = ttk.Checkbutton(
            feat_frame,
            text="Buat Halaman Preview Interaktif (HTML Demo)",
            variable=self.var_generate_preview
        )
        c5.pack(anchor=tk.W, pady=2)

        # --- Card 3: Pilihan Format Output Font ---
        fmt_card = ttk.LabelFrame(main_frame, text=" 📦 Format Font yang Dihasilkan ", padding="12 10")
        fmt_card.pack(fill=tk.X, pady=(0, 12))

        fmt_box = ttk.Frame(fmt_card)
        fmt_box.pack(fill=tk.X)

        ttk.Checkbutton(fmt_box, text="TTF (TrueType)", variable=self.fmt_ttf).pack(side=tk.LEFT, padx=12)
        ttk.Checkbutton(fmt_box, text="WOFF (Modern Web)", variable=self.fmt_woff).pack(side=tk.LEFT, padx=12)
        ttk.Checkbutton(fmt_box, text="WOFF2 (Compressed)", variable=self.fmt_woff2).pack(side=tk.LEFT, padx=12)
        ttk.Checkbutton(fmt_box, text="EOT (Legacy)", variable=self.fmt_eot).pack(side=tk.LEFT, padx=12)
        ttk.Checkbutton(fmt_box, text="SVG Font", variable=self.fmt_svg).pack(side=tk.LEFT, padx=12)

        # --- Card Web Server (Untuk Akses macOS / Jaringan Lokal) ---
        web_card = ttk.LabelFrame(main_frame, text=" 🌐 Mode Web Server (Untuk Akses dari macOS / Browser) ", padding="10 8")
        web_card.pack(fill=tk.X, pady=(0, 12))

        web_top = ttk.Frame(web_card)
        web_top.pack(fill=tk.X)

        self.btn_toggle_web = ttk.Button(
            web_top,
            text="▶️ Nyalakan Server Web",
            command=self._toggle_web_server
        )
        self.btn_toggle_web.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_web_status = ttk.Label(
            web_top,
            text="Server web nonaktif. Nyalakan untuk mengizinkan pengguna Mac mengakses via Safari/Chrome.",
            foreground="#94a3b8",
            font=("Segoe UI", 9)
        )
        self.lbl_web_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_web_open = ttk.Button(
            web_top,
            text="Buka di Browser",
            command=self._open_web_browser,
            state=tk.DISABLED
        )
        self.btn_web_open.pack(side=tk.RIGHT, padx=4)

        self.btn_web_copy = ttk.Button(
            web_top,
            text="Salin Link Mac",
            command=self._copy_mac_link,
            state=tk.DISABLED
        )
        self.btn_web_copy.pack(side=tk.RIGHT, padx=4)

        # --- Card 4: Status & Log ---
        log_card = ttk.LabelFrame(main_frame, text=" 📝 Status & Catatan Proses ", padding="8 6")
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.txt_log = tk.Text(log_card, height=6, bg="#1e293b", fg="#e2e8f0", insertbackground="#ffffff", font=("Consolas", 9), relief=tk.FLAT)
        self.txt_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_card, orient=tk.VERTICAL, command=self.txt_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log.config(yscrollcommand=scrollbar.set)

        self.progress_bar = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # --- Action Buttons ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        self.btn_convert = ttk.Button(
            btn_frame,
            text="🚀 MULAI KONVERSI KE FONT",
            style="Accent.TButton",
            command=self._start_conversion_thread
        )
        self.btn_convert.pack(side=tk.LEFT, padx=(0, 10), ipady=4)

        self.btn_open_folder = ttk.Button(
            btn_frame,
            text="📂 Buka Folder Hasil",
            command=self._open_output_folder,
            state=tk.DISABLED
        )
        self.btn_open_folder.pack(side=tk.LEFT, padx=(0, 10), ipady=4)

        self.btn_open_preview = ttk.Button(
            btn_frame,
            text="🌐 Buka Preview HTML",
            command=self._open_preview_html,
            state=tk.DISABLED
        )
        self.btn_open_preview.pack(side=tk.LEFT, ipady=4)

        self._log("Aplikasi SVG to Font Studio siap digunakan.")

    def _log(self, message):
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)

    def _check_engine(self):
        engine = get_engine_path()
        if os.path.isfile(engine):
            self._log(f"Engine backend terdeteksi: {os.path.basename(engine)}")
        else:
            self._log("Peringatan: File engine backend tidak ditemukan secara otomatis.")

    def _browse_source(self):
        path = filedialog.askdirectory(title="Pilih Folder Berisi File SVG")
        if path:
            self.source_dir.set(os.path.normpath(path))
            # Auto set output dir if empty
            if not self.output_dir.get().strip():
                default_out = os.path.join(path, "dist")
                self.output_dir.set(os.path.normpath(default_out))
            self._scan_svgs(path)

    def _browse_output(self):
        path = filedialog.askdirectory(title="Pilih Folder Tujuan Penyimpanan")
        if path:
            self.output_dir.set(os.path.normpath(path))

    def _scan_svgs(self, path):
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(".svg")]
            self.svg_count = len(files)
            if self.svg_count > 0:
                self.lbl_svg_info.config(
                    text=f"✅ Ditemukan {self.svg_count} file ikon SVG di folder ini.",
                    foreground="#38bdf8"
                )
                self._log(f"Memindai folder: {self.svg_count} file SVG terdeteksi.")
            else:
                self.lbl_svg_info.config(
                    text="⚠️ Tidak ada file berformat .svg di folder ini.",
                    foreground="#f59e0b"
                )
                self._log("Peringatan: Tidak ditemukan file .svg di folder yang dipilih.")
        except Exception as e:
            self.lbl_svg_info.config(text=f"Gagal membaca folder: {e}", foreground="#ef4444")

    def _start_conversion_thread(self):
        src = self.source_dir.get().strip()
        out = self.output_dir.get().strip()

        if not src or not os.path.isdir(src):
            messagebox.showwarning("Peringatan", "Silakan pilih folder sumber SVG yang valid terlebih dahulu!")
            return

        if not out:
            messagebox.showwarning("Peringatan", "Silakan tentukan folder tujuan output!")
            return

        if self.svg_count == 0:
            # Re-check
            files = [f for f in os.listdir(src) if f.lower().endswith(".svg")]
            if not files:
                messagebox.showwarning("Peringatan", "Folder sumber tidak memiliki file berformat .svg!")
                return
            self.svg_count = len(files)

        # Disable buttons & start progress
        self.btn_convert.config(state=tk.DISABLED)
        self.btn_open_folder.config(state=tk.DISABLED)
        self.btn_open_preview.config(state=tk.DISABLED)
        self.progress_bar.start(10)

        t = threading.Thread(target=self._run_conversion, daemon=True)
        t.start()

    def _run_conversion(self):
        src = self.source_dir.get().strip()
        out = self.output_dir.get().strip()
        font_name = self.font_name.get().strip() or "my-icons"
        prefix = self.prefix.get().strip() or "icon"
        clean_prefix = prefix.rstrip("-") if prefix.endswith("-") else prefix
        start_unicode = self.start_unicode.get().strip() or "59905"

        engine = get_engine_path()
        if not os.path.isfile(engine):
            self._ui_callback(lambda: self._on_failure(f"Engine backend tidak ditemukan di: {engine}"))
            return

        # Prepare and optimize SVGs if smooth curves need expansion or Figma masks need flattening
        self._ui_callback(lambda: self._log("Memeriksa struktur & kurva path SVG..."))
        effective_src, is_temp = svg_optimizer.prepare_svg_directory(src)
        if is_temp:
            self._ui_callback(lambda: self._log("Mengoptimalkan & merapikan path SVG untuk engine..."))

        # Build exclude list
        excludes = []
        if not self.fmt_svg.get():
            excludes.append("svg")
        if not self.fmt_ttf.get():
            excludes.append("ttf")
        if not self.fmt_woff.get():
            excludes.append("woff")
        if not self.fmt_woff2.get():
            excludes.append("woff2")
        if not self.fmt_eot.get():
            excludes.append("eot")
        if not self.var_generate_symbols.get():
            excludes.append("symbol.svg")

        cmd = [
            engine,
            "-sources", effective_src,
            "-output", out,
            "-font-name", font_name,
            "-prefix", clean_prefix,
            "-start-unicode", str(start_unicode)
        ]

        if self.var_convert_shapes.get():
            cmd.append("-convert-shapes")

        if self.var_empty_output.get():
            cmd.append("-empty")

        if self.var_generate_info.get() or self.var_generate_preview.get():
            cmd.append("-info")

        if not self.var_generate_css.get():
            cmd.append("-no-css")

        if not self.var_generate_symbols.get():
            cmd.append("-no-symbols")

        if excludes:
            cmd.extend(["-exclude", ",".join(excludes)])

        self._ui_callback(lambda: self._log(f"Menjalankan konversi untuk {self.svg_count} file SVG..."))

        try:
            # Ensure output dir exists
            os.makedirs(out, exist_ok=True)

            # Hide console window on Windows
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo
            )
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                err_msg = stderr.strip() or stdout.strip() or f"Proses keluar dengan kode {proc.returncode}"
                self._ui_callback(lambda: self._on_failure(err_msg))
                return

            if stdout.strip():
                self._ui_callback(lambda: self._log(f"Output: {stdout.strip()}"))

            # Generate preview HTML if enabled
            preview_created = False
            info_file = os.path.join(out, "info.json")
            if self.var_generate_preview.get() and os.path.isfile(info_file):
                try:
                    with open(info_file, "r", encoding="utf-8") as f:
                        info_data = json.load(f)
                    preview_path = generate_interactive_preview_html(out, font_name, clean_prefix, info_data)
                    self.last_preview_path = preview_path
                    preview_created = True
                    self._ui_callback(lambda: self._log(f"✅ Preview HTML dibuat: {os.path.basename(preview_path)}"))
                except Exception as e:
                    self._ui_callback(lambda: self._log(f"Peringatan: Gagal membuat preview HTML: {e}"))

            self.last_output_dir = out
            self._ui_callback(lambda: self._on_success(preview_created))

        except Exception as e:
            self._ui_callback(lambda: self._on_failure(str(e)))
        finally:
            if is_temp and os.path.isdir(effective_src):
                try:
                    shutil.rmtree(effective_src, ignore_errors=True)
                except Exception:
                    pass

    def _ui_callback(self, fn):
        self.after(0, fn)

    def _on_success(self, has_preview):
        self.progress_bar.stop()
        self.btn_convert.config(state=tk.NORMAL)
        self.btn_open_folder.config(state=tk.NORMAL)
        if has_preview:
            self.btn_open_preview.config(state=tk.NORMAL)

        self._log("🎉 Selesai! Semua font berhasil dibuat dengan sempurna.")
        messagebox.showinfo(
            "Berhasil!",
            f"Konversi font '{self.font_name.get()}' berhasil!\n"
            f"File telah disimpan di:\n{self.last_output_dir}"
        )

    def _on_failure(self, error_message):
        self.progress_bar.stop()
        self.btn_convert.config(state=tk.NORMAL)
        self._log(f"❌ Error: {error_message}")
        messagebox.showerror("Terjadi Kesalahan", f"Gagal mengonversi SVG:\n\n{error_message}")

    def _open_output_folder(self):
        if self.last_output_dir and os.path.isdir(self.last_output_dir):
            if os.name == "nt":
                os.startfile(self.last_output_dir)
            else:
                webbrowser.open(self.last_output_dir)

    def _open_preview_html(self):
        if self.last_preview_path and os.path.isfile(self.last_preview_path):
            webbrowser.open(f"file:///{os.path.abspath(self.last_preview_path).replace(os.sep, '/')}")
        elif self.last_output_dir:
            fallback = os.path.join(self.last_output_dir, "preview.html")
            if os.path.isfile(fallback):
                webbrowser.open(f"file:///{os.path.abspath(fallback).replace(os.sep, '/')}")

    def _toggle_web_server(self):
        if not self.web_server_active:
            ok, port = self.web_manager.start()
            if ok:
                self.web_server_active = True
                ip = web_server.get_local_ip()
                self.mac_url = f"http://{ip}:{port}"
                self.local_url = f"http://localhost:{port}"
                self.btn_toggle_web.config(text="⏹️ Hentikan Server")
                self.lbl_web_status.config(
                    text=f"🟢 Server Aktif! Akses dari Mac/HP: {self.mac_url}",
                    foreground="#34d399"
                )
                self.btn_web_open.config(state=tk.NORMAL)
                self.btn_web_copy.config(state=tk.NORMAL)
                self._log(f"🌐 Server Web AKTIF pada: {self.mac_url} (Lokal: {self.local_url})")
            else:
                messagebox.showerror("Error", "Gagal menjalankan web server lokal.")
        else:
            self.web_manager.stop()
            self.web_server_active = False
            self.btn_toggle_web.config(text="▶️ Nyalakan Server Web")
            self.lbl_web_status.config(
                text="Server web nonaktif. Nyalakan untuk mengizinkan pengguna Mac mengakses via Safari/Chrome.",
                foreground="#94a3b8"
            )
            self.btn_web_open.config(state=tk.DISABLED)
            self.btn_web_copy.config(state=tk.DISABLED)
            self._log("🌐 Server Web telah dihentikan.")

    def _open_web_browser(self):
        if hasattr(self, "local_url"):
            webbrowser.open(self.local_url)

    def _copy_mac_link(self):
        if hasattr(self, "mac_url"):
            self.clipboard_clear()
            self.clipboard_append(self.mac_url)
            messagebox.showinfo(
                "Link Berhasil Disalin!",
                f"Link telah disalin ke clipboard:\n{self.mac_url}\n\n"
                f"Buka link ini di browser Safari atau Chrome di macOS yang terhubung ke Wi-Fi yang sama!"
            )

    def _on_window_close(self):
        if self.web_server_active:
            self.web_manager.stop()
        self.destroy()


if __name__ == "__main__":
    app = SVGToFontApp()
    app.mainloop()
