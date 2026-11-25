const _svgtofont = require('svgtofont');
const svgtofont = _svgtofont.default || _svgtofont;
const path = require('path');
const fs = require('fs');
const os = require('os');

// Helper: Clean Figma masks, clipPath, and wrappers from monochrome SVGs
function cleanSvgContent(content) {
  let cleaned = content.replace(/<mask[\s\S]*?<\/mask>/gi, '');
  cleaned = cleaned.replace(/\s+mask="[^"]*"/gi, '');
  cleaned = cleaned.replace(/\s+clip-path="[^"]*"/gi, '');
  return cleaned;
}

// Helper: Scan SVGs for monochrome font generation (STRICTLY EXCLUDES 'color' folder)
function scanFontSvgDirectory(dir, baseDir = dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // EXCLUDE 'color' folder from font compilation
      if (entry.name.toLowerCase() === 'color') {
        continue;
      }
      results = results.concat(scanFontSvgDirectory(fullPath, baseDir));
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.svg')) {
      const relPath = path.relative(baseDir, fullPath).replace(/\\/g, '/');
      results.push({
        fullPath,
        relPath,
        fileName: entry.name
      });
    }
  }
  return results;
}

// Helper: Scan fullcolor SVGs from svg/color directory
function scanColorSvgDirectory(colorDir) {
  let results = [];
  if (!fs.existsSync(colorDir)) return results;
  const entries = fs.readdirSync(colorDir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(colorDir, entry.name);
    if (entry.isFile() && entry.name.toLowerCase().endsWith('.svg')) {
      results.push({
        fullPath,
        relPath: `color/${entry.name}`,
        fileName: entry.name
      });
    }
  }
  return results;
}

// Collection definitions (3-letter prefixes)
const COLLECTION_CONFIG = {
  cus: { name: 'Custom Mertani', collection: 'custom', color: '#10b981' },
  mat: { name: 'Material Symbol', collection: 'material-symbol', color: '#8b5cf6' },
  sfs: { name: 'SF Symbol', collection: 'sf-symbol', color: '#f59e0b' },
  bsi: { name: 'Bootstrap Icons', collection: 'bootstrap', color: '#6366f1' },
  bst: { name: 'Bootstrap Icons', collection: 'bootstrap', color: '#6366f1' },
  fth: { name: 'Feather', collection: 'feather', color: '#06b6d4' }
};

// Known states for color icons
const SUPPORTED_STATES = ['default', 'active', 'selected', 'warning', 'danger', 'disabled'];

// Parse monochrome font SVG filename (prefix-style-name.svg)
function parseFontIconInfo(relPath, fileName, manifestMap) {
  const baseNoExt = path.basename(fileName, '.svg').toLowerCase();
  const manifestItem = manifestMap ? manifestMap.get(relPath) : null;

  const match = baseNoExt.match(/^([a-z0-9]{3})-(regular|solid)-(.+)$/i);
  
  let prefix = 'cus';
  let style = relPath.startsWith('solid') ? 'solid' : 'regular';
  let iconName = baseNoExt;

  if (match) {
    prefix = match[1].toLowerCase();
    style = match[2].toLowerCase();
    iconName = match[3].toLowerCase();
  } else {
    if (relPath.includes('solid')) style = 'solid';
    else if (relPath.includes('regular')) style = 'regular';
  }

  const collConfig = COLLECTION_CONFIG[prefix] || {
    name: prefix.toUpperCase(),
    collection: prefix,
    color: '#64748b'
  };

  const glyphName = `${prefix}-${style}-${iconName}`;
  const className = `mis-${glyphName}`;

  // Generate developer-friendly aliases
  const aliases = new Set();
  aliases.add(`mis-${prefix}-${iconName}`);
  aliases.add(`mis-${style}-${iconName}`);
  aliases.add(`mis-${iconName}`);

  if (iconName.includes('-')) {
    aliases.add(`mis-${iconName.replace(/-/g, '_')}`);
    aliases.add(`mis-${prefix}-${iconName.replace(/-/g, '_')}`);
  }
  if (glyphName === 'cus-solid-dashboard') {
    aliases.add('mis-cus-regular-dashboard');
  }

  return {
    name: iconName,
    prefix,
    style,
    isFont: true,
    isColor: false,
    category: collConfig.name,
    categorySlug: collConfig.collection,
    badgeColor: collConfig.color,
    glyphName,
    className,
    aliases: Array.from(aliases),
    originalName: manifestItem ? manifestItem.name : iconName,
    project: manifestItem ? manifestItem.project : null
  };
}

// Parse color SVG filename (prefix-color-name[-state].svg)
function parseColorIconInfo(fileName) {
  const baseNoExt = path.basename(fileName, '.svg').toLowerCase();
  
  // Format: prefix-color-name[-state].svg
  const match = baseNoExt.match(/^([a-z0-9]{3})-color-(.+)$/i);
  let prefix = 'cus';
  let rawName = baseNoExt;
  let state = null;

  if (match) {
    prefix = match[1].toLowerCase();
    rawName = match[2].toLowerCase();

    // Check if trailing segment is a known state
    for (const s of SUPPORTED_STATES) {
      if (rawName.endsWith(`-${s}`)) {
        state = s;
        rawName = rawName.slice(0, -(s.length + 1));
        break;
      }
    }
  }

  const collConfig = COLLECTION_CONFIG[prefix] || {
    name: prefix.toUpperCase(),
    collection: prefix,
    color: '#10b981'
  };

  return {
    name: rawName,
    state,
    prefix,
    style: 'color',
    isFont: false,
    isColor: true,
    category: collConfig.name,
    categorySlug: collConfig.collection,
    badgeColor: '#ec4899', // Pink badge for color
    fileName,
    distPath: `color/${fileName}`,
    className: `mis-color-${rawName}${state ? `-${state}` : ''}`
  };
}

// Generate modern, interactive web catalog supporting both Font and Fullcolor SVGs
function generateCatalogHtml(fontIcons, colorIcons) {
  const allIcons = [...fontIcons, ...colorIcons];
  const totalRegular = fontIcons.filter(i => i.style === 'regular').length;
  const totalSolid = fontIcons.filter(i => i.style === 'solid').length;
  const totalColor = colorIcons.length;

  return `<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MIS Gallery - Mertani Icon Studio</title>
  <link rel="stylesheet" href="mis-icons.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-hover: #334155;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --primary-hover: #0ea5e9;
      --regular: #10b981;
      --solid: #f59e0b;
      --color: #ec4899;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 2.5rem 1.5rem 4rem;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    header {
      text-align: center;
      margin-bottom: 2.5rem;
    }
    .badge-pill {
      display: inline-block;
      padding: 0.35rem 0.85rem;
      background: rgba(56, 189, 248, 0.15);
      color: var(--primary);
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
      border: 1px solid rgba(56, 189, 248, 0.25);
    }
    h1 {
      font-size: 2.25rem;
      font-weight: 700;
      letter-spacing: -0.025em;
      margin-bottom: 0.5rem;
    }
    header p {
      color: var(--text-muted);
      font-size: 1rem;
      max-width: 720px;
      margin: 0 auto 1.5rem;
      line-height: 1.6;
    }
    .cdn-box {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 0.85rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      max-width: 760px;
      margin: 0 auto;
      gap: 1rem;
    }
    .cdn-box code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #38bdf8;
      font-size: 0.85rem;
      overflow-x: auto;
      white-space: nowrap;
    }
    .btn-copy {
      background: #0284c7;
      color: #fff;
      border: none;
      padding: 0.45rem 0.9rem;
      border-radius: 0.5rem;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      flex-shrink: 0;
      transition: background 0.2s;
    }
    .btn-copy:hover { background: #0369a1; }
    
    /* Controls */
    .controls {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 2rem;
    }
    .search-wrapper {
      position: relative;
      max-width: 600px;
      margin: 0 auto;
      width: 100%;
    }
    .search-input {
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 0.85rem 1.25rem 0.85rem 2.75rem;
      font-size: 0.95rem;
      color: var(--text);
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .search-input:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }
    .search-icon {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }
    
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.5rem;
    }
    .tab-btn {
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.45rem 0.9rem;
      border-radius: 9999px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }
    .tab-btn:hover {
      background: var(--card-hover);
      color: var(--text);
    }
    .tab-btn.active {
      background: var(--primary);
      color: #0f172a;
      border-color: var(--primary);
      font-weight: 700;
    }
    .tab-btn .count {
      font-size: 0.72rem;
      opacity: 0.85;
      margin-left: 0.35rem;
    }

    /* Icon Grid */
    .icon-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
      gap: 1rem;
    }
    .icon-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1.5rem 1rem 1rem;
      text-align: center;
      position: relative;
      cursor: pointer;
      transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s, background 0.2s;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .icon-card:hover {
      transform: translateY(-3px);
      border-color: var(--primary);
      background: var(--card-hover);
      box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.3);
    }
    .badges-wrapper {
      position: absolute;
      top: 0.5rem;
      left: 0.5rem;
      right: 0.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .chip {
      font-size: 0.65rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 0.15rem 0.45rem;
      border-radius: 0.35rem;
      letter-spacing: 0.05em;
    }
    .chip-style {
      background: rgba(255,255,255,0.08);
      color: #94a3b8;
      border: 1px solid rgba(255,255,255,0.12);
    }
    .chip-style.regular { color: #34d399; background: rgba(52, 211, 153, 0.12); border-color: rgba(52, 211, 153, 0.25); }
    .chip-style.solid { color: #fbbf24; background: rgba(251, 191, 36, 0.12); border-color: rgba(251, 191, 36, 0.25); }
    .chip-style.color { color: #f472b6; background: rgba(244, 114, 182, 0.12); border-color: rgba(244, 114, 182, 0.25); }

    .icon-preview {
      font-size: 2.5rem;
      margin: 1rem 0 0.5rem;
      color: var(--text);
      transition: transform 0.2s, color 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      height: 48px;
    }
    .icon-preview img {
      max-height: 44px;
      max-width: 44px;
      object-fit: contain;
    }
    .icon-card:hover .icon-preview {
      color: var(--primary);
      transform: scale(1.1);
    }
    .icon-name {
      font-weight: 600;
      font-size: 0.88rem;
      margin-bottom: 0.25rem;
      color: var(--text);
      word-break: break-all;
    }
    .icon-class {
      font-family: monospace;
      font-size: 0.72rem;
      color: var(--text-muted);
      background: rgba(0,0,0,0.25);
      padding: 0.15rem 0.4rem;
      border-radius: 0.25rem;
      margin-bottom: 0.35rem;
    }
    .icon-sub {
      font-size: 0.68rem;
      color: #64748b;
    }

    /* Toast Notification */
    .toast {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #10b981;
      color: #fff;
      padding: 0.75rem 1.25rem;
      border-radius: 0.5rem;
      font-weight: 600;
      font-size: 0.9rem;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
      transform: translateY(150%);
      transition: transform 0.3s ease-out;
      z-index: 1000;
    }
    .toast.show {
      transform: translateY(0);
    }

    footer {
      text-align: center;
      margin-top: 4rem;
      padding-top: 2rem;
      border-top: 1px solid var(--border);
      color: var(--text-muted);
      font-size: 0.875rem;
    }
    footer a { color: var(--primary); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>

  <div class="container">
    <header>
      <div class="badge-pill">Mertani Icon Studio &bull; MIS Gallery</div>
      <h1>Icon Studio &amp; Web Font</h1>
      <p>Katalog resmi icon dengan pola penamaan <code>prefix-style-name[-state].svg</code>. Kategori monochrome (<strong>regular</strong> &amp; <strong>solid</strong>) terkompilasi sebagai web font, sedangkan <strong>color</strong> dipertahankan sebagai aset multi-color SVG utuh.</p>

      <div class="cdn-box">
        <code>&lt;link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css"&gt;</code>
        <button class="btn-copy" onclick="copyCdn()">Salin Link</button>
      </div>
    </header>

    <div class="controls">
      <div class="search-wrapper">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input type="text" id="searchInput" class="search-input" placeholder="Cari nama icon, prefix (bsi/cus/mat/sfs), atau style...">
      </div>

      <!-- Style Filters -->
      <div class="filter-row" id="styleTabs">
        <button class="tab-btn active" data-style="all">Semua Style <span class="count">${allIcons.length}</span></button>
        <button class="tab-btn" data-style="regular">Regular / Outline <span class="count">${totalRegular}</span></button>
        <button class="tab-btn" data-style="solid">Solid / Filled <span class="count">${totalSolid}</span></button>
        <button class="tab-btn" data-style="color">Color / Multi-color <span class="count">${totalColor}</span></button>
      </div>

      <!-- Collection Filters -->
      <div class="filter-row" id="collectionTabs">
        <button class="tab-btn active" data-collection="all">Semua Koleksi</button>
        <button class="tab-btn" data-collection="bsi">Bootstrap Icons (bsi)</button>
        <button class="tab-btn" data-collection="cus">Custom Mertani (cus)</button>
        <button class="tab-btn" data-collection="mat">Material Symbol (mat)</button>
        <button class="tab-btn" data-collection="sfs">SF Symbol (sfs)</button>
      </div>
    </div>

    <div class="icon-grid" id="iconGrid">
      ${fontIcons.map(item => `
        <div class="icon-card" data-style="${item.style}" data-collection="${item.prefix}" data-name="${item.name.toLowerCase()}" data-class="${item.className}" data-type="font" onclick="copyFontIcon('${item.className}')">
          <div class="badges-wrapper">
            <span class="chip" style="background: ${item.badgeColor}22; color: ${item.badgeColor}; border: 1px solid ${item.badgeColor}44;">
              ${item.prefix}
            </span>
            <span class="chip chip-style ${item.style}">
              ${item.style}
            </span>
          </div>
          <div class="icon-preview"><i class="${item.className}"></i></div>
          <div class="icon-name">${item.name}</div>
          <div class="icon-class">.${item.className}</div>
          <div class="icon-sub">Unicode: ${item.unicode || '-'}</div>
        </div>
      `).join('')}

      ${colorIcons.map(item => `
        <div class="icon-card" data-style="color" data-collection="${item.prefix}" data-name="${item.name.toLowerCase()}" data-class="${item.className}" data-type="color" onclick="copyColorIcon('${item.fileName}')">
          <div class="badges-wrapper">
            <span class="chip" style="background: ${item.badgeColor}22; color: ${item.badgeColor}; border: 1px solid ${item.badgeColor}44;">
              ${item.prefix}
            </span>
            <span class="chip chip-style color">
              COLOR
            </span>
          </div>
          <div class="icon-preview"><img src="${item.distPath}" alt="${item.name}" loading="lazy" /></div>
          <div class="icon-name">${item.name}${item.state ? ' (' + item.state + ')' : ''}</div>
          <div class="icon-class">${item.fileName}</div>
          <div class="icon-sub">Multi-color SVG Asset</div>
        </div>
      `).join('')}
    </div>

    <footer>
      <p>&copy; 2026 Mertani Icon Studio (MIS Gallery). Distributed via jsDelivr & GitHub Pages.</p>
      <p style="margin-top: 0.5rem;"><a href="https://github.com/rizcode21/MIS-Gallery" target="_blank">Lihat Repositori GitHub &rarr;</a></p>
    </footer>
  </div>

  <div id="toast" class="toast">Kode icon berhasil disalin!</div>

  <script>
    const searchInput = document.getElementById('searchInput');
    const styleTabs = document.querySelectorAll('#styleTabs .tab-btn');
    const collectionTabs = document.querySelectorAll('#collectionTabs .tab-btn');
    const cards = document.querySelectorAll('.icon-card');
    const toast = document.getElementById('toast');

    let activeStyle = 'all';
    let activeCollection = 'all';

    function filterIcons() {
      const q = searchInput.value.toLowerCase().trim();
      cards.forEach(card => {
        const style = card.dataset.style;
        const col = card.dataset.collection;
        const name = card.dataset.name;
        const cls = card.dataset.class;
        const matchesStyle = (activeStyle === 'all' || style === activeStyle);
        const matchesCollection = (activeCollection === 'all' || col === activeCollection);
        const matchesSearch = (!q || name.includes(q) || cls.includes(q) || col.includes(q) || style.includes(q));
        if (matchesStyle && matchesCollection && matchesSearch) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    styleTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        styleTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeStyle = tab.dataset.style;
        filterIcons();
      });
    });

    collectionTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        collectionTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeCollection = tab.dataset.collection;
        filterIcons();
      });
    });

    searchInput.addEventListener('input', filterIcons);

    function showToast(msg) {
      toast.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2200);
    }

    function copyFontIcon(className) {
      const snippet = '<i class="' + className + '"></i>';
      navigator.clipboard.writeText(snippet).then(() => {
        showToast('Tersalin: ' + snippet);
      }).catch(() => {
        showToast('Class tersalin: .' + className);
      });
    }

    function copyColorIcon(fileName) {
      const cdnUrl = 'https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/color/' + fileName;
      const snippet = '<img src="' + cdnUrl + '" alt="' + fileName + '" width="24" height="24" />';
      navigator.clipboard.writeText(snippet).then(() => {
        showToast('HTML Tag tersalin: <img src="..." />');
      }).catch(() => {
        showToast('URL tersalin: ' + cdnUrl);
      });
    }

    function copyCdn() {
      const cdn = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css">';
      navigator.clipboard.writeText(cdn).then(() => {
        showToast('Link CSS jsDelivr tersalin!');
      });
    }
  </script>
</body>
</html>`;
}

async function build() {
  const rootDir = path.resolve(__dirname, '..');
  const srcDir = path.join(rootDir, 'svg');
  const distDir = path.join(rootDir, 'dist');
  const colorDir = path.join(srcDir, 'color');
  const distColorDir = path.join(distDir, 'color');
  const manifestPath = path.join(srcDir, 'icon-manifest.json');

  console.log('🚀 Starting MIS Gallery Font & Asset Build (Font Awesome Architecture)...');

  // Load manifest if available
  let manifestMap = new Map();
  if (fs.existsSync(manifestPath)) {
    try {
      const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
      if (Array.isArray(manifest.icons)) {
        for (const item of manifest.icons) {
          manifestMap.set(item.newPath.replace(/^svg\//, ''), item);
        }
      }
    } catch (e) {
      console.warn('⚠️ Could not parse icon-manifest.json:', e.message);
    }
  }

  // 1. Process Color SVGs (STRICTLY EXCLUDED from font compilation & currentColor replacement)
  if (!fs.existsSync(distColorDir)) {
    fs.mkdirSync(distColorDir, { recursive: true });
  }

  const colorSvgFiles = scanColorSvgDirectory(colorDir);
  const processedColorIcons = [];

  console.log(`🎨 Found ${colorSvgFiles.length} color SVG icons in svg/color/ (EXCLUDED from font compilation):`);
  for (const item of colorSvgFiles) {
    const meta = parseColorIconInfo(item.fileName);
    // Copy as-is to dist/color/ preserving 100% of fullcolor attributes and gradients intact
    const rawContent = fs.readFileSync(item.fullPath, 'utf-8');
    fs.writeFileSync(path.join(distColorDir, item.fileName), rawContent, 'utf-8');
    processedColorIcons.push(meta);
    console.log(`   [COLOR] ${item.fileName} -> copied to dist/color/${item.fileName} (intact fullcolor SVG)`);
  }

  // 2. Scan Monochrome SVGs (Only regular and solid subfolders)
  const fontSvgFiles = scanFontSvgDirectory(srcDir);

  if (fontSvgFiles.length === 0) {
    console.error('❌ No monochrome SVG files found for icon font in svg/regular or svg/solid!');
    process.exit(1);
  }

  console.log(`\n📁 Found ${fontSvgFiles.length} monochrome SVG icons for icon font:`);

  // Create temporary directory for flattened font SVGs
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mis-svg-'));
  const processedFontIcons = [];

  for (const item of fontSvgFiles) {
    const meta = parseFontIconInfo(item.relPath, item.fileName, manifestMap);
    console.log(`   [${meta.prefix.toUpperCase()}/${meta.style.toUpperCase()}] ${item.fileName} -> glyph: ${meta.glyphName}`);

    // Read and clean SVG content
    const rawContent = fs.readFileSync(item.fullPath, 'utf-8');
    const cleaned = cleanSvgContent(rawContent);

    // Staged filename with glyph name
    const stagedFileName = `${meta.glyphName}.svg`;
    fs.writeFileSync(path.join(tempDir, stagedFileName), cleaned, 'utf-8');

    processedFontIcons.push({
      ...meta,
      stagedFileName,
      sourceRelPath: `svg/${item.relPath}`
    });
  }

  // Run svgtofont engine on monochrome icons only
  console.log('\n⚙️  Running svgtofont compiler for monochrome web font...');
  await svgtofont({
    src: tempDir,
    dist: distDir,
    fontName: 'mis-icons',
    classNamePrefix: 'mis',
    css: true,
    emptyDist: false,
    startUnicode: 0xea01,
    svgicons2svgfont: {
      fontHeight: 1000,
      normalize: true
    },
    website: {
      title: 'MIS Gallery - Mertani Icon Studio',
      logo: '',
      version: '2.1.0',
      description: 'Gudang Ikon Resmi Mertani Icon Studio (MIS Gallery).',
      links: [
        {
          title: 'GitHub Repository',
          url: 'https://github.com/rizcode21/MIS-Gallery'
        }
      ]
    }
  });

  // Extract unicodes from generated CSS
  const cssPath = path.join(distDir, 'mis-icons.css');
  let cssContent = fs.readFileSync(cssPath, 'utf-8');

  for (const icon of processedFontIcons) {
    const re = new RegExp(`\\.mis-${icon.glyphName}::before\\s*\\{\\s*content:\\s*"([^"]+)";`, 'i');
    const match = cssContent.match(re);
    icon.unicode = match ? match[1] : '';
  }

  // Append developer convenience aliases to mis-icons.css
  let aliasesCss = '\n/* --- Developer Aliases & Backwards Compatibility --- */\n';
  let aliasCount = 0;
  for (const icon of processedFontIcons) {
    if (icon.aliases && icon.aliases.length > 0 && icon.unicode) {
      for (const alias of icon.aliases) {
        aliasesCss += `.${alias}::before { content: "${icon.unicode}"; }\n`;
        aliasCount++;
      }
    }
  }
  if (aliasCount > 0) {
    fs.appendFileSync(cssPath, aliasesCss, 'utf-8');
    console.log(`🔗 Appended ${aliasCount} CSS class aliases to mis-icons.css`);
  }

  // Combine metadata: both font icons and color assets
  const combinedMetadata = {
    fontIcons: processedFontIcons,
    colorIcons: processedColorIcons,
    totalCount: processedFontIcons.length + processedColorIcons.length
  };

  const metaJson = JSON.stringify(combinedMetadata, null, 2);
  fs.writeFileSync(path.join(distDir, 'icons.json'), metaJson, 'utf-8');
  fs.writeFileSync(path.join(distDir, 'info.json'), metaJson, 'utf-8');
  console.log(`📋 Written icons.json & info.json metadata (${processedFontIcons.length} font icons, ${processedColorIcons.length} color SVGs)`);

  // Generate web catalog supporting both Font and Color SVGs
  const customHtml = generateCatalogHtml(processedFontIcons, processedColorIcons);
  fs.writeFileSync(path.join(distDir, 'index.html'), customHtml, 'utf-8');
  console.log('✨ Generated modern web catalog in dist/index.html (with full Color SVG support)');

  // Cleanup temp dir
  try {
    fs.rmSync(tempDir, { recursive: true, force: true });
  } catch (e) {}

  console.log('✅ MIS Gallery build complete!\n');
}

build().catch((err) => {
  console.error('❌ Error building MIS Gallery font:', err);
  process.exit(1);
});
