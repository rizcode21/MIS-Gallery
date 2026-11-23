# 🎨 Panduan Penggunaan SVG to Font Studio (Portable Edition)

Selamat datang di **SVG to Font Studio**! Aplikasi ini dirancang khusus agar siapa pun—baik desainer, web developer, maupun pengguna awam—dapat mengonversi kumpulan file ikon SVG menjadi web font (TTF, WOFF, WOFF2, EOT, CSS) dengan sangat mudah tanpa perlu menginstal aplikasi tambahan apa pun dan tanpa perlu membuka terminal (*command prompt*).

Aplikasi ini bersifat **PORTABLE**: Anda cukup menyalin file `SVG2Font_Studio.exe` ke komputer mana pun (Windows) dan langsung melakukan klik ganda (*double-click*) untuk menjalankannya.

---

## 🚀 Cara Cepat Menggunakan (Hanya 3 Langkah!)

1. **Buka Aplikasi:**
   - Klik ganda file `SVG2Font_Studio.exe`.
2. **Pilih Folder SVG:**
   - Klik tombol **`Pilih Folder...`** di samping kolom *Folder Sumber SVG*, lalu pilih folder tempat Anda menyimpan file-file `.svg`.
   - Kolom *Folder Tujuan Output* akan otomatis terisi dengan folder `dist` di samping folder SVG Anda (bisa Anda ubah sesuai keinginan).
3. **Mulai Konversi:**
   - Klik tombol besar berwarna biru: **`🚀 MULAI KONVERSI KE FONT`**.
   - Tunggu beberapa detik hingga muncul pesan sukses!
   - Klik **`📂 Buka Folder Hasil`** untuk melihat file font yang dibuat, atau klik **`🌐 Buka Preview HTML`** untuk melihat katalog ikon di browser.

---

## 🌟 Opsi Paling Fleksibel: Converter HTML Mandiri (`converter.html`)

Selain file `.exe`, Anda kini memiliki file **[converter.html](file:///d:/RIZ/Pribadi/Code/VibeCoding/Projects/SVG_to_Font/converter.html)**.

### Mengapa Ini Sangat Praktis untuk macOS / Laptop Mana Pun?
1. **100% In-Browser (Client-Side):** Semua proses konversi font berjalan langsung di dalam memori browser menggunakan JavaScript modern (`opentype.js` + `JSZip`).
2. **Tidak Butuh Server & Tidak Butuh Buka .EXE:** Anda cukup meng-copy folder ini ke laptop **macOS (MacBook/iMac)**, lalu:
   - Klik 2x file `converter.html`.
   - Browser **Safari / Google Chrome** akan langsung terbuka.
   - Tarik & lepas file SVG dari Finder Mac Anda.
   - Klik **"🚀 KONVERSI & UNDUH ZIP"**.
   - Selesai! File font `.ttf`, `.css`, dan `preview.html` langsung terunduh.
3. **100% Offline:** File pustaka pendukung sudah tersimpan di folder `lib/`, sehingga tetap berjalan lancar meski laptop sedang tidak terhubung ke internet.

---

## 🌐 Fitur Spesial: Mode Web (Akses untuk macOS, Linux, dan Mobile)

Jika di tim Anda ada rekan kerja yang menggunakan **macOS (MacBook/iMac)**:
1. Jalankan `SVG2Font_Studio.exe` di komputer Windows Anda.
2. Pada bagian **"🌐 Mode Web Server"**, klik tombol **`▶️ Nyalakan Server Web`**.
3. Status akan berubah menjadi hijau dan memunculkan alamat jaringan, contoh:
   - `http://192.168.1.50:8080`
4. Klik tombol **`Salin Link Mac`** dan bagikan link tersebut ke rekan Anda yang memakai Mac.
5. Rekan Anda cukup membuka link tersebut di browser **Safari atau Google Chrome** di Mac mereka:
   - Tampilan Web Studio akan terbuka dengan antarmuka Drag & Drop.
   - Mereka bisa menarik file SVG dari Finder Mac mereka.
   - Klik **"🚀 KONVERSI & UNDUH ZIP"**.
   - Browser Mac akan langsung mengunduh file `.zip` berisi font lengkap (TTF, WOFF, WOFF2, CSS, dan HTML preview).
   - **Tanpa perlu menginstal aplikasi apa pun di Mac!**

---

## 🛠️ Catatan Fitur & Fungsi Lengkap

Semua kemampuan teknis dari engine backend telah terintegrasi secara visual:

### 1. Penanganan Elemen SVG Lanjutan (`-convert-shapes`)
- **Fitur:** *Konversi Bentuk Otomatis*.
- **Fungsi:** Secara standar, font font generator hanya bisa membaca elemen `<path>`. Namun dengan fitur ini diaktifkan (default: aktif), elemen bentuk dasar seperti:
  - Kotak (`<rect>`)
  - Lingkaran (`<circle>`)
  - Elips (`<ellipse>`)
  - Garis (`<line>`)
  - Poligon (`<polygon>`)
  - Polyline (`<polyline>`)
  akan otomatis dikonversi menjadi garis lengkung/path sehingga ikon tetap terbentuk utuh dan tidak hilang.

### 2. Pengaturan Nama Font & Prefix CSS
- **Nama Font (`-font-name`):** Nama keluarga font yang akan dihasilkan (misal: `my-icons`, `custom-font`).
- **Prefix Class CSS (`-prefix`):** Awalan nama class pada file stylesheet CSS. Contoh: jika prefix diisi `icon-` dan Anda memiliki file `home.svg`, maka di HTML Anda cukup memanggil `<i class="icon-home"></i>`.
- **Start Unicode (`-start-unicode`):** Titik awal kode karakter Unicode (default: `59905` atau `\ea01` pada area *Private Use Area* Unicode agar tidak bentrok dengan karakter teks biasa).

### 3. Pembersihan Folder Output Otomatis (`-empty`)
- Secara otomatis mengosongkan folder output sebelum proses konversi dimulai agar file lama tidak menumpuk atau bentrok dengan file baru.

### 4. Pilihan Format Font Output (`-exclude`)
Anda dapat memilih format apa saja yang ingin dibuat dengan mencentang kotak:
- **TTF (TrueType):** Format standar untuk instalasi lokal di Windows/Mac dan browser desktop.
- **WOFF (Web Open Font Format):** Standar web font untuk hampir semua browser modern.
- **WOFF2 (Compressed):** Versi kompresi terbaik dengan ukuran file paling kecil, sangat cepat untuk loading website.
- **EOT (Embedded OpenType):** Khusus untuk kompatibilitas browser lama (seperti Internet Explorer).
- **SVG Font:** Format font berbasis XML SVG.

### 5. File Pendukung & Metadata
- **CSS Stylesheet:** Menghasilkan file `.css` yang sudah menyertakan deklarasi `@font-face` dan class siap pakai.
- **JSON Metadata (`info.json`):** Berisi daftar mapping lengkap nama ikon, nama class, kode unicode karakter, dan entitas HTML.
- **SVG Symbol Sprite (`symbol.svg`):** Kumpulan ikon dalam bentuk sprite `<symbol>` untuk penggunaan SVG inline.

### 6. Fitur Ekstra: Preview HTML Interaktif
Aplikasi ini secara otomatis membuat halaman **`preview.html`** di folder hasil konversi. Pada halaman ini Anda dapat:
- Melihat wujud visual seluruh ikon font yang baru saja dibuat.
- Menguji ukuran ikon dengan slider (*16px* sampai *72px*).
- Mengetik nama ikon pada kotak pencarian untuk mencari ikon tertentu secara instan.
- **Klik 1x pada kartu ikon:** Otomatis menyalin tag HTML (contoh: `<i class="icon-home"></i>`) langsung ke clipboard komputer Anda.

---

## ❓ Troubleshooting / Tanya Jawab

1. **Apakah komputer lain perlu menginstal Python atau Go?**
   - **TIDAK.** Aplikasi ini sudah dipaketkan menjadi file executable mandiri (*standalone portable .exe*). Semua mesin dan dependensi sudah terbungkus rapi di dalamnya.

2. **Bagaimana jika ikon saya tidak muncul atau terpotong?**
   - Pastikan opsi *Konversi Bentuk Otomatis* selalu tercentang.
   - Pastikan file SVG Anda tidak berisi gambar bitmap (seperti PNG/JPG yang hanya di-*embed* ke dalam SVG).

3. **Cara menggunakan font di website:**
   1. Salin folder hasil konversi ke folder project website Anda.
   2. Panggil file CSS di bagian `<head>` HTML:
      ```html
      <link rel="stylesheet" href="dist/my-icons.css">
      ```
   3. Gunakan ikon di mana saja pada halaman web:
      ```html
      <i class="icon-namafile"></i>
      ```
