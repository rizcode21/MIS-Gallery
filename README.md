# 🎨 MIS Gallery (Mertani Icon Studio)

[![Build MIS Gallery Fonts](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml/badge.svg)](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml)
[![jsDelivr](https://data.jsdelivr.net/v1/package/gh/rizcode21/MIS-Gallery/badge)](https://www.jsdelivr.com/package/gh/rizcode21/MIS-Gallery)

Gudang Ikon & Web Font Terpusat Resmi **Mertani Icon Studio (MIS Gallery)** dengan arsitektur penamaan bergaya **Font Awesome** (`prefix-style-name[-state].svg`).

Sistem ini mendukung dua jalur aset terpadu:
1. **Monochrome Icons (`regular` & `solid`):** Dikonversi otomatis menjadi web font (TTF, WOFF, WOFF2, EOT, CSS) untuk pewarnaan dinamis via CSS (`color: #...`).
2. **Multi-color / Fullcolor Icons (`color`):** Dikecualikan dari font dan dipertahankan 100% sebagai file SVG berwarna asli dengan dukungan variasi *state*.

🌐 **Katalog Ikon Live:** [https://rizcode21.github.io/MIS-Gallery/](https://rizcode21.github.io/MIS-Gallery/)

---

## 📁 Struktur Folder Koleksi SVG

```text
svg/
├── regular/            # Ikon monochrome outline / stroke (dikonversi ke web font)
│   ├── .gitkeep
│   ├── cus-regular-partnership.svg
│   ├── cus-regular-sales.svg
│   ├── cus-regular-settings.svg
│   ├── mat-regular-donut-small.svg
│   ├── mat-regular-local-shipping.svg
│   └── sfs-regular-magnifying-glass.svg
├── solid/              # Ikon monochrome filled / siluet penuh (dikonversi ke web font)
│   ├── .gitkeep
│   ├── cus-solid-dashboard.svg
│   ├── cus-solid-favorite.svg
│   └── cus-solid-notification.svg
├── color/              # Ikon multi-color / fullcolor (dipertahankan sebagai SVG utuh)
│   └── .gitkeep
└── icon-manifest.json  # Catatan mapping riwayat asal aset & proyek
```

---

## 🏷️ Standar Penamaan File

### 1. Ikon Font Monochrome (`prefix-style-name.svg`)
- Format: `<prefix>-<regular|solid>-<name>.svg`
- Contoh: `cus-regular-settings.svg`, `cus-solid-dashboard.svg`.

### 2. Ikon Berwarna / Multi-color (`prefix-color-name[-state].svg`)
- Format: `<prefix>-color-<name>[-<state>].svg`
- Bagian `style` wajib bertuliskan `color`.
- State yang didukung: `default`, `active`, `selected`, `warning`, `danger`, `disabled`.
- Contoh:
  - `cus-color-dam.svg`
  - `cus-color-dam-default.svg`
  - `cus-color-dam-active.svg`
  - `cus-color-sensor-warning.svg`

---

## 💻 Panduan untuk Developer (Cara Pakai di Website)

### A. Memanggil Ikon Font Monochrome (via CDN CSS)
Pasang link CSS di tag `<head>`:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css">
```

Panggil menggunakan tag `<i>`:
```html
<!-- Regular (Outline) -->
<i class="mis-cus-regular-partnership"></i>
<i class="mis-mat-regular-donut-small"></i>

<!-- Solid (Filled) -->
<i class="mis-cus-solid-dashboard"></i>
<i class="mis-cus-solid-favorite"></i>
```

Ubah ukuran & warna via CSS:
```css
.mis-cus-regular-partnership {
  font-size: 24px;
  color: #10b981;
}
```

### B. Memanggil Ikon Berwarna / Fullcolor (via Direct SVG CDN)
Gunakan tag `<img>` atau inline `<svg>` langsung ke CDN:
```html
<img src="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/color/cus-color-dam-active.svg" alt="Dam Active" width="32" height="32" />
```

---

## 🎨 Panduan untuk Desainer (Cara Menambah Ikon Baru)

1. **Tentukan Kategori Visual:**
   - **Garis / Outline tunggal** &rarr; Beri nama `prefix-regular-name.svg` dan masukkan ke `svg/regular/`.
   - **Siluet / Blok hitam tunggal** &rarr; Beri nama `prefix-solid-name.svg` dan masukkan ke `svg/solid/`.
   - **Berwarna / Lebih dari 1 warna / Duotone** &rarr; Beri nama `prefix-color-name[-state].svg` dan masukkan ke `svg/color/`.
2. **Unggah ke GitHub:**
   - Robot otomatis (*GitHub Actions*) akan langsung meng-compile font dan mendistribusikan SVG berwarna dalam kurun waktu ~30 detik!

---

&copy; 2026 Mertani Icon Studio (MIS Gallery). All rights reserved.
