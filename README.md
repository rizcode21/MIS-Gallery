# 🎨 MIS Gallery (Mertani Icon Studio)

[![Build MIS Gallery Fonts](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml/badge.svg)](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml)
[![jsDelivr](https://data.jsdelivr.net/v1/package/gh/rizcode21/MIS-Gallery/badge)](https://www.jsdelivr.com/package/gh/rizcode21/MIS-Gallery)

Gudang Ikon & Web Font Terpusat Resmi **Mertani Icon Studio (MIS Gallery)**. 

Repositori ini secara otomatis mengonversi kumpulan file ikon SVG dari berbagai kategori menjadi web font (TTF, WOFF, WOFF2, EOT, CSS) menggunakan **GitHub Actions** dan mendistribusikannya secara gratis melalui **jsDelivr CDN** dan **GitHub Pages**.

🌐 **Katalog Ikon Live:** [https://rizcode21.github.io/MIS-Gallery/](https://rizcode21.github.io/MIS-Gallery/)

---

## 📁 Struktur Folder Koleksi SVG

Seluruh icon SVG dipisahkan secara rapi ke dalam subfolder kategori di dalam direktori `svg/`:

```text
svg/
├── Custom/
│   ├── Global/             # Ikon custom umum untuk semua proyek & branding
│   ├── Project A/          # Ikon custom eksklusif untuk Project A
│   ├── Project B/          # Ikon custom eksklusif untuk Project B
│   └── Project C/          # Ikon custom eksklusif untuk Project C
├── Material_Symbol/        # Koleksi ikon dari Google Material Symbols
└── SF_Symbol/              # Koleksi ikon dari Apple SF Symbols
```

> **Catatan:** Jika ada proyek baru di kemudian hari, cukup buat folder baru di dalam `svg/Custom/<Nama Proyek>/` dan sistem otomatis mendeteksi dan memberi prefix yang sesuai.

---

## 💻 Panduan untuk Developer (Cara Pakai di Website)

### 1. Pasang Link CSS
Developer cukup menyematkan 1 baris link CSS online berikut pada tag `<head>` HTML:

```html
<!-- Pasang CSS MIS Gallery via jsDelivr CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css">
```

### 2. Memanggil Ikon Berdasarkan Kategori
Ikon dapat dipanggil menggunakan tag `<i>` dengan prefix class sesuai kategorinya:

| Kategori | Folder Asal | Contoh Class Utama | Contoh Alias Alternatif |
| :--- | :--- | :--- | :--- |
| **Custom Global** | `svg/Custom/Global/` | `<i class="mis-global-partnership"></i>` | `<i class="mis-partnership"></i>` |
| **Custom Project A** | `svg/Custom/Project A/` | `<i class="mis-proja-dashboard"></i>` | `<i class="mis-project-a-dashboard"></i>` |
| **Custom Project B** | `svg/Custom/Project B/` | `<i class="mis-projb-favorite"></i>` | `<i class="mis-project-b-favorite"></i>` |
| **Custom Project C** | `svg/Custom/Project C/` | `<i class="mis-projc-notification"></i>` | `<i class="mis-project-c-notification"></i>` |
| **Material Symbol** | `svg/Material_Symbol/` | `<i class="mis-mat-donut_small"></i>` | `<i class="mis-ms-donut_small"></i>` |
| **SF Symbol** | `svg/SF_Symbol/` | `<i class="mis-sf-magnifyingglass"></i>` | - |

### 3. Mengatur Warna & Ukuran via CSS:
Karena berbasis font vektor, Anda bisa mengubah warna, efek hover, dan ukurannya layaknya font teks biasa:

```css
/* Ikon Global */
.mis-global-partnership {
  font-size: 32px;
  color: #10b981;
}

/* Ikon Project A */
.mis-proja-dashboard {
  font-size: 24px;
  color: #3b82f6;
}

/* Ikon Material Symbol */
.mis-mat-donut_small {
  font-size: 20px;
  color: #8b5cf6;
}
```

---

## 🎨 Panduan untuk Desainer (Cara Menambah Ikon Baru)

*Desainer tidak perlu menginstal aplikasi terminal atau menjalankan kode apa pun!*

1. **Export SVG dari Figma / Illustrator:**
   - Pastikan path SVG berbentuk shape / outline vector yang rapi.
   - Beri nama file yang jelas (contoh: `invoice.svg`, `profile.svg`).
2. **Pilih Folder Tujuan di GitHub:**
   - Kunjungi folder [svg/](https://github.com/rizcode21/MIS-Gallery/tree/main/svg) di browser Anda:
     - Masukkan ke `svg/Custom/Global/` jika icon dipakai secara umum.
     - Masukkan ke `svg/Custom/Project X/` jika icon khusus untuk proyek tertentu.
     - Masukkan ke `svg/Material_Symbol/` atau `svg/SF_Symbol/` jika mengambil dari pustaka open source tersebut.
3. **Unggah File:**
   - Klik tombol **`Add file`** ➜ **`Upload files`**.
   - Tarik & lepas (*drag and drop*) file `.svg` baru Anda ke browser.
4. **Simpan:**
   - Klik tombol hijau **`Commit changes`**.
5. **Selesai! 🚀**
   - GitHub Actions otomatis meng-compile icon baru menjadi font web dan memperbarui link CSS dalam kurun waktu ~20 detik. Seluruh website proyek yang memanggil link CSS otomatis bisa langsung menggunakan icon baru tersebut!

---

## 🛠️ File Converter Mandiri (Offline)

Bagi tim yang ingin melakukan konversi cepat tanpa internet di laptop masing-masing (macOS & Windows), tersedia file mandiri:
- **`converter.html`**: Cukup klik 2x file ini untuk membuka web converter offline di browser Anda.

---

&copy; 2026 Mertani Icon Studio (MIS Gallery). All rights reserved.
