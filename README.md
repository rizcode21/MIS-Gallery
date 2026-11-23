# 🎨 MIS Gallery (Mertani Icon Studio)

[![Build MIS Gallery Fonts](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml/badge.svg)](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml)
[![jsDelivr](https://data.jsdelivr.net/v1/package/gh/rizcode21/MIS-Gallery/badge)](https://www.jsdelivr.com/package/gh/rizcode21/MIS-Gallery)

Gudang Ikon & Web Font Terpusat Resmi **Mertani Icon Studio (MIS Gallery)** dengan arsitektur penamaan bergaya **Font Awesome** (`prefix-style-name.svg`).

Repositori ini secara otomatis mengonversi kumpulan file ikon SVG menjadi web font (TTF, WOFF, WOFF2, EOT, CSS) menggunakan **GitHub Actions** dan mendistribusikannya secara gratis melalui **jsDelivr CDN** dan **GitHub Pages**.

🌐 **Katalog Ikon Live:** [https://rizcode21.github.io/MIS-Gallery/](https://rizcode21.github.io/MIS-Gallery/)

---

## 📁 Struktur Folder Koleksi SVG

Struktur direktori di dalam `svg/` menggunakan sistem flat berbasis **style** visual:

```text
svg/
├── regular/            # Seluruh icon bergaya outline / stroke (hollow center)
│   ├── .gitkeep
│   ├── cus-regular-partnership.svg
│   ├── cus-regular-sales.svg
│   ├── cus-regular-settings.svg
│   ├── mat-regular-donut-small.svg
│   ├── mat-regular-local-shipping.svg
│   └── sfs-regular-magnifying-glass.svg
├── solid/              # Seluruh icon bergaya filled / blok penuh (siluet)
│   ├── .gitkeep
│   ├── cus-solid-dashboard.svg
│   ├── cus-solid-favorite.svg
│   └── cus-solid-notification.svg
└── icon-manifest.json  # Catatan mapping riwayat asal aset & proyek
```

---

## 🏷️ Standar Penamaan File (`prefix-style-name.svg`)

Format file wajib mengikuti aturan:
1. **Lowercase** & **kebab-case** (tanda hubung `-`, tanpa underscore atau spasi).
2. **Prefix (3 huruf):**
   - `cus` &rarr; Custom Mertani Studio (termasuk ikon Global & spesifik Proyek)
   - `mat` &rarr; Google Material Symbols
   - `sfs` &rarr; Apple SF Symbols
   - *(Standar masa depan: `bst` untuk Bootstrap, `fth` untuk Feather)*
3. **Style:**
   - `regular` &rarr; Outline / stroke
   - `solid` &rarr; Filled / blok penuh
4. **Name:** Nama ikon yang dinormalisasi (contoh: `magnifying-glass`, `donut-small`).

---

## 💻 Panduan untuk Developer (Cara Pakai di Website)

### 1. Pasang Link CSS
Developer cukup menyematkan 1 baris link CSS online berikut pada tag `<head>` HTML:

```html
<!-- Pasang CSS MIS Gallery via jsDelivr CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css">
```

### 2. Memanggil Ikon
Gunakan tag `<i>` dengan class `mis-<prefix>-<style>-<name>`:

```html
<!-- Regular (Outline) Icons -->
<i class="mis-cus-regular-partnership"></i>
<i class="mis-cus-regular-sales"></i>
<i class="mis-cus-regular-settings"></i>
<i class="mis-mat-regular-donut-small"></i>
<i class="mis-mat-regular-local-shipping"></i>
<i class="mis-sfs-regular-magnifying-glass"></i>

<!-- Solid (Filled) Icons -->
<i class="mis-cus-solid-dashboard"></i>
<i class="mis-cus-solid-favorite"></i>
<i class="mis-cus-solid-notification"></i>
```

> **Developer Aliases:** Tersedia juga alias singkat untuk kemudahan penulisan seperti `.mis-partnership`, `.mis-cus-dashboard`, dan `.mis-donut-small`.

### 3. Mengatur Warna & Ukuran via CSS:
Karena berbasis font vektor, Anda bisa mengubah warna, efek hover, dan ukurannya layaknya teks biasa:

```css
.mis-cus-regular-partnership {
  font-size: 32px;
  color: #10b981;
}

.mis-cus-solid-dashboard {
  font-size: 24px;
  color: #38bdf8;
}
```

---

## 🎨 Panduan untuk Desainer (Cara Menambah Ikon Baru)

1. **Export SVG dari Figma / Illustrator:**
   - Beri nama dengan format: `<prefix>-<style>-<nama-ikon>.svg`
   - Contoh: `cus-regular-user.svg` atau `cus-solid-user.svg`.
2. **Pilih Folder Tujuan:**
   - Jika icon berupa garis/outline &rarr; masukkan ke folder `svg/regular/`.
   - Jika icon berupa siluet blok penuh &rarr; masukkan ke folder `svg/solid/`.
3. **Unggah ke GitHub & Simpan:**
   - GitHub Actions otomatis meng-compile icon baru menjadi font web dan memperbarui link CSS dalam kurun waktu ~20 detik!

---

&copy; 2026 Mertani Icon Studio (MIS Gallery). All rights reserved.
