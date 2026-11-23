import os
import sys
import json
import socket
import shutil
import zipfile
import tempfile
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import svg_optimizer


def get_local_ip():
    """Retrieve local IP on current network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


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
    """Generate modern interactive preview HTML."""
    css_file = f"{font_name}.css"
    glyphs_html = []

    for name, data in info_data.items():
        cls_name = data.get("className", f"{prefix}-{name}")
        encoded_code = data.get("encodedCode", "")
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
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h1>🎨 {font_name} Font Preview</h1>
            <p>Total Ikon: <span id="count">{len(info_data)}</span> | Prefix CSS: <code>.{prefix}*</code></p>
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
            setTimeout(() => {{ t.classList.remove('show'); }}, 2000);
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
</html>"""
    preview_path = os.path.join(output_dir, "preview.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return preview_path


# HTML Page for the Web App Mode
WEB_APP_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SVG to Font Studio (Web Edition) - macOS & Windows</title>
    <style>
        :root {
            --bg: #090d16;
            --surface: #111827;
            --card: #1f2937;
            --card-hover: #374151;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
            --text: #f9fafb;
            --text-muted: #9ca3af;
            --border: #374151;
            --success: #10b981;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            padding: 40px 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .container {
            max-width: 900px;
            width: 100%;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 32px;
            font-weight: 800;
            color: var(--accent);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }
        .badge {
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 999px;
            margin-top: 8px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        .header p {
            font-size: 15px;
            color: var(--text-muted);
            margin-top: 10px;
        }
        .dropzone {
            background: var(--surface);
            border: 2px dashed var(--border);
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }
        .dropzone:hover, .dropzone.dragover {
            border-color: var(--accent);
            background: rgba(56, 189, 248, 0.04);
            transform: scale(1.005);
        }
        .dropzone-icon {
            font-size: 48px;
            margin-bottom: 12px;
        }
        .dropzone h3 {
            font-size: 18px;
            margin-bottom: 6px;
        }
        .dropzone p {
            font-size: 14px;
            color: var(--text-muted);
        }
        #fileInput {
            display: none;
        }
        .preview-area {
            margin-top: 25px;
            display: none;
        }
        .preview-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
            gap: 12px;
            max-height: 280px;
            overflow-y: auto;
            padding: 10px;
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        .svg-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 8px;
            text-align: center;
            position: relative;
        }
        .svg-card .svg-view {
            width: 36px;
            height: 36px;
            margin: 0 auto 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .svg-card .svg-view svg {
            width: 100%;
            height: 100%;
            fill: var(--text);
        }
        .svg-card .svg-title {
            font-size: 11px;
            color: var(--text);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .btn-remove {
            position: absolute;
            top: 4px;
            right: 4px;
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: none;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 11px;
            cursor: pointer;
            line-height: 18px;
        }
        .btn-remove:hover {
            background: #ef4444;
            color: #fff;
        }
        .config-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            margin-top: 25px;
        }
        .config-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }
        .field label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text);
        }
        .field input {
            width: 100%;
            padding: 10px 14px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 14px;
            outline: none;
        }
        .field input:focus {
            border-color: var(--accent);
        }
        .options-list {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
            padding-top: 10px;
            border-top: 1px solid var(--border);
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            cursor: pointer;
            user-select: none;
        }
        .checkbox-label input {
            accent-color: var(--accent);
            cursor: pointer;
        }
        .btn-convert {
            width: 100%;
            background: linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%);
            color: #fff;
            border: none;
            padding: 15px;
            font-size: 16px;
            font-weight: 700;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .btn-convert:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(14, 165, 233, 0.45);
        }
        .btn-convert:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .status-box {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            display: none;
            font-size: 14px;
        }
        .status-box.success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
            display: block;
        }
        .status-box.error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #f87171;
            display: block;
        }
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid #ffffff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 0.8s linear infinite;
            display: none;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        footer {
            margin-top: 40px;
            text-align: center;
            font-size: 13px;
            color: var(--text-muted);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 SVG to Font Studio <span class="badge">Web Edition</span></h1>
            <p>Konversi kumpulan ikon SVG menjadi file Font (TTF, WOFF, WOFF2, CSS, Demo HTML) langsung dari browser.</p>
        </div>

        <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
            <div class="dropzone-icon">📁</div>
            <h3>Tarik & Lepas File SVG ke Sini</h3>
            <p>atau klik untuk memilih beberapa file SVG dari komputer Anda</p>
            <input type="file" id="fileInput" multiple accept=".svg">
        </div>

        <div class="preview-area" id="previewArea">
            <div class="preview-header">
                <strong id="countLabel">0 Ikon Dipilih</strong>
                <button onclick="clearFiles()" style="background:none; border:none; color:#ef4444; cursor:pointer; font-size:13px;">Hapus Semua</button>
            </div>
            <div class="grid" id="svgGrid"></div>
        </div>

        <div class="config-card">
            <div class="config-grid">
                <div class="field">
                    <label>Nama Font:</label>
                    <input type="text" id="fontName" value="my-icons">
                </div>
                <div class="field">
                    <label>Prefix Class CSS:</label>
                    <input type="text" id="prefix" value="icon">
                </div>
                <div class="field">
                    <label>Start Unicode:</label>
                    <input type="text" id="startUnicode" value="59905">
                </div>
            </div>

            <div class="options-list">
                <label class="checkbox-label">
                    <input type="checkbox" id="convertShapes" checked>
                    <span>Konversi Bentuk Otomatis (Figma & Shapes)</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="fmtTTF" checked>
                    <span>TTF</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="fmtWOFF" checked>
                    <span>WOFF</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="fmtWOFF2" checked>
                    <span>WOFF2</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="fmtEOT" checked>
                    <span>EOT</span>
                </label>
            </div>

            <button class="btn-convert" id="btnConvert" onclick="convertAndDownload()" disabled>
                <div class="spinner" id="spinner"></div>
                <span id="btnText">🚀 KONVERSI & UNDUH ZIP (FONT + CSS)</span>
            </button>

            <div class="status-box" id="statusBox"></div>
        </div>

        <footer>
            SVG to Font Studio &bull; Siap digunakan untuk macOS, Windows, Linux, dan Mobile.
        </footer>
    </div>

    <script>
        let uploadedFiles = []; // { name, content }

        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const previewArea = document.getElementById('previewArea');
        const svgGrid = document.getElementById('svgGrid');
        const countLabel = document.getElementById('countLabel');
        const btnConvert = document.getElementById('btnConvert');
        const statusBox = document.getElementById('statusBox');
        const spinner = document.getElementById('spinner');
        const btnText = document.getElementById('btnText');

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        async function handleFiles(files) {
            statusBox.style.display = 'none';
            for (const file of files) {
                if (file.name.toLowerCase().endsWith('.svg')) {
                    const text = await file.text();
                    uploadedFiles.push({ name: file.name, content: text });
                }
            }
            renderPreview();
        }

        function renderPreview() {
            svgGrid.innerHTML = '';
            if (uploadedFiles.length === 0) {
                previewArea.style.display = 'none';
                btnConvert.disabled = true;
                return;
            }

            previewArea.style.display = 'block';
            countLabel.innerText = `${uploadedFiles.length} Ikon Dipilih`;
            btnConvert.disabled = false;

            uploadedFiles.forEach((f, idx) => {
                const card = document.createElement('div');
                card.className = 'svg-card';
                card.innerHTML = `
                    <button class="btn-remove" onclick="removeFile(${idx})">&times;</button>
                    <div class="svg-view">${f.content}</div>
                    <div class="svg-title" title="${f.name}">${f.name}</div>
                `;
                svgGrid.appendChild(card);
            });
        }

        function removeFile(idx) {
            uploadedFiles.splice(idx, 1);
            renderPreview();
        }

        function clearFiles() {
            uploadedFiles = [];
            fileInput.value = '';
            renderPreview();
        }

        async function convertAndDownload() {
            if (uploadedFiles.length === 0) return;

            btnConvert.disabled = true;
            spinner.style.display = 'block';
            btnText.innerText = 'Mengonversi Font...';
            statusBox.style.display = 'none';

            const payload = {
                fontName: document.getElementById('fontName').value.trim() || 'my-icons',
                prefix: document.getElementById('prefix').value.trim() || 'icon',
                startUnicode: document.getElementById('startUnicode').value.trim() || '59905',
                convertShapes: document.getElementById('convertShapes').checked,
                formats: {
                    ttf: document.getElementById('fmtTTF').checked,
                    woff: document.getElementById('fmtWOFF').checked,
                    woff2: document.getElementById('fmtWOFF2').checked,
                    eot: document.getElementById('fmtEOT').checked
                },
                files: uploadedFiles
            };

            try {
                const res = await fetch('/api/convert', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const err = await res.text();
                    throw new Error(err || 'Gagal mengonversi SVG ke font.');
                }

                // Download the ZIP file
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${payload.fontName}-bundle.zip`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

                statusBox.className = 'status-box success';
                statusBox.innerHTML = `🎉 <strong>Berhasil!</strong> File <code>${payload.fontName}-bundle.zip</code> telah berhasil diunduh. Ekstrak ZIP tersebut dan buka <code>preview.html</code> untuk melihat katalog ikon.`;
            } catch (err) {
                statusBox.className = 'status-box error';
                statusBox.innerText = `Terjadi Kesalahan: ${err.message}`;
            } finally {
                btnConvert.disabled = false;
                spinner.style.display = 'none';
                btnText.innerText = '🚀 KONVERSI & UNDUH ZIP (FONT + CSS)';
            }
        }
    </script>
</body>
</html>
"""


class WebAppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(WEB_APP_HTML.encode("utf-8"))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/convert":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            try:
                data = json.loads(body)
                font_name = data.get("fontName", "my-icons")
                prefix = data.get("prefix", "icon").rstrip("-")
                start_unicode = str(data.get("startUnicode", "59905"))
                convert_shapes = data.get("convertShapes", True)
                formats = data.get("formats", {})
                files = data.get("files", [])

                if not files:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"Tidak ada file SVG yang dikirim.")
                    return

                # Create temp processing directories
                raw_svg_dir = tempfile.mkdtemp(prefix="svg_web_raw_")
                output_dir = tempfile.mkdtemp(prefix="svg_web_out_")

                # Save SVGs
                for item in files:
                    fname = item.get("name", "icon.svg")
                    content = item.get("content", "")
                    with open(os.path.join(raw_svg_dir, fname), "w", encoding="utf-8") as f:
                        f.write(content)

                # Optimize and flatten SVGs
                clean_src, is_temp = svg_optimizer.prepare_svg_directory(raw_svg_dir)

                # Build excludes
                excludes = ["svg", "symbol.svg"]
                if not formats.get("ttf", True):
                    excludes.append("ttf")
                if not formats.get("woff", True):
                    excludes.append("woff")
                if not formats.get("woff2", True):
                    excludes.append("woff2")
                if not formats.get("eot", True):
                    excludes.append("eot")

                engine = get_engine_path()
                cmd = [
                    engine,
                    "-sources", clean_src,
                    "-output", output_dir,
                    "-font-name", font_name,
                    "-prefix", prefix,
                    "-start-unicode", start_unicode,
                    "-info",
                    "-empty",
                    "-exclude", ",".join(excludes)
                ]
                if convert_shapes:
                    cmd.append("-convert-shapes")

                # Run engine
                proc = subprocess.run(cmd, capture_output=True, text=True)
                if proc.returncode != 0:
                    err = proc.stderr.strip() or proc.stdout.strip() or "Engine error"
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(err.encode("utf-8"))
                    return

                # Generate interactive preview HTML
                info_path = os.path.join(output_dir, "info.json")
                if os.path.isfile(info_path):
                    try:
                        with open(info_path, "r", encoding="utf-8") as f:
                            info_data = json.load(f)
                        generate_interactive_preview_html(output_dir, font_name, prefix, info_data)
                    except Exception:
                        pass

                # Package all generated files into a ZIP
                zip_path = os.path.join(tempfile.gettempdir(), f"{font_name}-bundle.zip")
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, out_files in os.walk(output_dir):
                        for f in out_files:
                            file_full_path = os.path.join(root, f)
                            arcname = os.path.relpath(file_full_path, output_dir)
                            zipf.write(file_full_path, arcname)

                # Send ZIP response
                with open(zip_path, "rb") as f:
                    zip_bytes = f.read()

                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{font_name}-bundle.zip"')
                self.send_header("Content-Length", str(len(zip_bytes)))
                self.end_headers()
                self.wfile.write(zip_bytes)

                # Cleanup temp
                try:
                    shutil.rmtree(raw_svg_dir, ignore_errors=True)
                    shutil.rmtree(output_dir, ignore_errors=True)
                    if is_temp:
                        shutil.rmtree(clean_src, ignore_errors=True)
                    if os.path.isfile(zip_path):
                        os.remove(zip_path)
                except Exception:
                    pass

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy standard logs in console
        pass


class WebServerManager:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return True, self.port

        # Try designated port, or next available port
        for p in range(self.port, self.port + 20):
            try:
                self.server = HTTPServer(("0.0.0.0", p), WebAppHandler)
                self.port = p
                self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
                self.is_running = True
                return True, self.port
            except OSError:
                continue
        return False, self.port

    def stop(self):
        if self.is_running and self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.is_running = False


# For standalone running: python web_server.py
if __name__ == "__main__":
    manager = WebServerManager(8080)
    success, port = manager.start()
    if success:
        ip = get_local_ip()
        print(f"=====================================================")
        print(f"  🎨 SVG to Font Studio - Web Server Berjalan! ")
        print(f"=====================================================")
        print(f"  Akses dari komputer ini : http://localhost:{port}")
        print(f"  Akses dari macOS / HP   : http://{ip}:{port}")
        print(f"=====================================================")
        print(f"  Tekan Ctrl+C untuk menghentikan server.")
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
            print("\nServer dihentikan.")
    else:
        print("Gagal menjalankan web server.")
