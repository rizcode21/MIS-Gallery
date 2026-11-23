# 🎨 MIS Gallery (Mertani Icon Studio)

[![Build MIS Gallery Fonts](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml/badge.svg)](https://github.com/rizcode21/MIS-Gallery/actions/workflows/build-font.yml)
[![jsDelivr](https://data.jsdelivr.com/v1/package/gh/rizcode21/MIS-Gallery/badge)](https://www.jsdelivr.com/package/gh/rizcode21/MIS-Gallery)

Gudang Ikon & Web Font Terpusat Resmi **Mertani Icon Studio (MIS Gallery)**. 

Repositori ini secara otomatis mengonversi kumpulan file ikon SVG menjadi web font (TTF, WOFF, WOFF2, EOT, CSS) menggunakan **GitHub Actions** dan mendistribusikannya secara gratis melalui **jsDelivr CDN** dan **GitHub Pages**.

🌐 **Katalog Ikon Live:** [https://rizcode21.github.io/MIS-Gallery/](https://rizcode21.github.io/MIS-Gallery/)

---

## 💻 Panduan untuk Developer (Cara Pakai di Website)

Developer cukup memasang 1 baris link CSS online berikut pada tag `<head>` di file HTML atau template web Anda:

```html
<!-- Pasang CSS MIS Gallery via jsDelivr CDN -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css">
```

### Memanggil Ikon:
Gunakan tag `<i>` dengan prefix class `mis-<nama-file>`:

```html
<i class="mis-Partnership"></i>
<i class="mis-Sales"></i>
<i class="mis-donut_small"></i>
<i class="mis-local_shipping"></i>
<i class="mis-settings"></i>
```

### Mengatur Warna & Ukuran via CSS:
Karena berbasis font vektor, Anda bisa mengubah warna dan ukurannya layaknya teks biasa:

```css
.mis-Partnership {
  font-size: 32px;
  color: #ff6900;
}
.mis-Sales {
  font-size: 24px;
  color: #10b981;
}
```

---

## 🎨 Panduan untuk Desainer (Cara Menambah Ikon Baru)

*Desainer tidak perlu menginstal aplikasi apa pun atau menjalankan perintah terminal!*

1. **Export SVG dari Figma / Illustrator:**
   - Beri nama file yang jelas dan rapi (contoh: `checkout.svg`, `user-profile.svg`).
2. **Buka Folder SVG di GitHub:**
   - Kunjungi folder [svg/](https://github.com/rizcode21/MIS-Gallery/tree/main/svg) di browser Anda.
3. **Unggah File:**
   - Klik tombol **`Add file`** ➜ **`Upload files`**.
   - Tarik & lepas (*drag and drop*) file `.svg` baru Anda ke browser.
4. **Simpan:**
   - Klik tombol hijau **`Commit changes`**.
5. **Selesai! 🚀**
   - Robot otomatis (*GitHub Actions*) akan langsung mengonversi dan memperbarui font serta link CSS dalam ~20 detik. Seluruh website proyek yang memanggil link CSS otomatis mendapatkan ikon baru tersebut.

---

## 🛠️ File Converter Mandiri (Offline)

Bagi tim yang ingin melakukan konversi cepat tanpa internet di laptop masing-masing (macOS & Windows), tersedia file mandiri:
- **`converter.html`**: Cukup klik 2x file ini untuk membuka web converter offline di browser Anda.

---

&copy; 2026 Mertani Icon Studio (MIS Gallery). All rights reserved.
