const _svgtofont = require('svgtofont');
const svgtofont = _svgtofont.default || _svgtofont;
const path = require('path');
const fs = require('fs');
const os = require('os');

// Helper: Clean Figma masks, clipPath, and wrappers from SVG
function cleanSvgContent(content) {
  let cleaned = content.replace(/<mask[\s\S]*?<\/mask>/gi, '');
  cleaned = cleaned.replace(/\s+mask="[^"]*"/gi, '');
  cleaned = cleaned.replace(/\s+clip-path="[^"]*"/gi, '');
  return cleaned;
}

// Helper: Recursively discover all SVG files
function scanSvgDirectory(dir, baseDir = dir) {
  let results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results = results.concat(scanSvgDirectory(fullPath, baseDir));
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

// Categorize SVG based on folder path and determine prefix & aliases
function getCategoryInfo(relPath) {
  const parts = relPath.split('/');
  const rawBaseName = path.basename(relPath, path.extname(relPath));
  const baseName = rawBaseName.toLowerCase().replace(/[^a-z0-9_-]/g, '_');

  // Schema matching
  // 1. Custom / Global
  if (relPath.startsWith('Custom/Global/')) {
    return {
      name: baseName,
      category: 'Custom: Global',
      categorySlug: 'custom-global',
      badgeColor: '#10b981', // Emerald green
      prefix: 'global-',
      glyphName: `global-${baseName}`,
      aliases: [`mis-${baseName}`],
      originalName: rawBaseName
    };
  }

  // 2. Custom / Project A, B, C, etc.
  const projectMatch = relPath.match(/^Custom\/([^/]+)\//i);
  if (projectMatch) {
    const projectName = projectMatch[1]; // e.g. "Project A"
    const projSlug = projectName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '');
    const shortProj = projSlug.replace('project-', 'proj'); // e.g. "proja"
    return {
      name: baseName,
      category: `Custom: ${projectName}`,
      categorySlug: `custom-${projSlug}`,
      badgeColor: '#3b82f6', // Blue
      prefix: `${shortProj}-`,
      glyphName: `${shortProj}-${baseName}`,
      aliases: [`mis-${projSlug}-${baseName}`],
      originalName: rawBaseName
    };
  }

  // 3. Material_Symbol
  if (relPath.startsWith('Material_Symbol/')) {
    return {
      name: baseName,
      category: 'Material Symbol',
      categorySlug: 'material-symbol',
      badgeColor: '#8b5cf6', // Violet
      prefix: 'mat-',
      glyphName: `mat-${baseName}`,
      aliases: [`mis-ms-${baseName}`, `mis-${baseName}`],
      originalName: rawBaseName
    };
  }

  // 4. SF_Symbol
  if (relPath.startsWith('SF_Symbol/')) {
    return {
      name: baseName,
      category: 'SF Symbol',
      categorySlug: 'sf-symbol',
      badgeColor: '#f59e0b', // Amber
      prefix: 'sf-',
      glyphName: `sf-${baseName}`,
      aliases: [],
      originalName: rawBaseName
    };
  }

  // Default / Other subfolder
  const folderName = parts.length > 1 ? parts[0] : 'General';
  const folderSlug = folderName.toLowerCase().replace(/[^a-z0-9_-]/g, '-');
  return {
    name: baseName,
    category: folderName,
    categorySlug: folderSlug,
    badgeColor: '#6b7280', // Gray
    prefix: `${folderSlug}-`,
    glyphName: `${folderSlug}-${baseName}`,
    aliases: [`mis-${baseName}`],
    originalName: rawBaseName
  };
}

// Generate modern, interactive web catalog
function generateCatalogHtml(iconsMeta) {
  // Collect unique categories
  const categoriesMap = new Map();
  for (const item of iconsMeta) {
    if (!categoriesMap.has(item.categorySlug)) {
      categoriesMap.set(item.categorySlug, {
        name: item.category,
        slug: item.categorySlug,
        count: 0,
        color: item.badgeColor
      });
    }
    categoriesMap.get(item.categorySlug).count++;
  }
  const categories = Array.from(categoriesMap.values());

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
      max-width: 650px;
      margin: 0 auto 1.5rem;
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
    
    /* Controls: Search & Category Tabs */
    .controls {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
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
    
    .category-tabs {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.5rem;
    }
    .tab-btn {
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-size: 0.85rem;
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
      font-size: 0.75rem;
      opacity: 0.8;
      margin-left: 0.35rem;
    }

    /* Icon Grid */
    .icon-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
    .cat-chip {
      position: absolute;
      top: 0.5rem;
      left: 0.5rem;
      font-size: 0.65rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 0.15rem 0.45rem;
      border-radius: 0.35rem;
      letter-spacing: 0.05em;
    }
    .icon-preview {
      font-size: 2.5rem;
      margin: 0.75rem 0;
      color: var(--text);
      transition: transform 0.2s, color 0.2s;
    }
    .icon-card:hover .icon-preview {
      color: var(--primary);
      transform: scale(1.1);
    }
    .icon-name {
      font-weight: 600;
      font-size: 0.9rem;
      margin-bottom: 0.25rem;
      color: var(--text);
      word-break: break-all;
    }
    .icon-class {
      font-family: monospace;
      font-size: 0.75rem;
      color: var(--text-muted);
      background: rgba(0,0,0,0.25);
      padding: 0.15rem 0.4rem;
      border-radius: 0.25rem;
      margin-bottom: 0.35rem;
    }
    .icon-unicode {
      font-size: 0.7rem;
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
      <h1>Central Icon Web Font</h1>
      <p>Koleksi icon resmi yang terbagi ke dalam kategori Global, Project-specific, dan Koleksi Eksternal. Klik kartu icon untuk menyalin kode HTML.</p>

      <div class="cdn-box">
        <code>&lt;link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rizcode21/MIS-Gallery@main/dist/mis-icons.css"&gt;</code>
        <button class="btn-copy" onclick="copyCdn()">Salin Link</button>
      </div>
    </header>

    <div class="controls">
      <div class="search-wrapper">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        <input type="text" id="searchInput" class="search-input" placeholder="Cari nama icon, kategori, atau class...">
      </div>

      <div class="category-tabs" id="categoryTabs">
        <button class="tab-btn active" data-category="all">Semua <span class="count">${iconsMeta.length}</span></button>
        ${categories.map(c => `<button class="tab-btn" data-category="${c.slug}">${c.name} <span class="count">${c.count}</span></button>`).join('')}
      </div>
    </div>

    <div class="icon-grid" id="iconGrid">
      ${iconsMeta.map(item => `
        <div class="icon-card" data-category="${item.categorySlug}" data-name="${item.name.toLowerCase()}" data-class="${item.className}" data-unicode="${item.unicode}" onclick="copyIcon('${item.className}')">
          <span class="cat-chip" style="background: ${item.badgeColor}22; color: ${item.badgeColor}; border: 1px solid ${item.badgeColor}44;">
            ${item.category.replace('Custom: ', '')}
          </span>
          <i class="${item.className} icon-preview"></i>
          <div class="icon-name">${item.originalName}</div>
          <div class="icon-class">.${item.className}</div>
          <div class="icon-unicode">Unicode: ${item.unicode}</div>
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
    const tabs = document.querySelectorAll('.tab-btn');
    const cards = document.querySelectorAll('.icon-card');
    const toast = document.getElementById('toast');

    let activeCategory = 'all';

    function filterIcons() {
      const q = searchInput.value.toLowerCase().trim();
      cards.forEach(card => {
        const cat = card.dataset.category;
        const name = card.dataset.name;
        const cls = card.dataset.class;
        const matchesCategory = (activeCategory === 'all' || cat === activeCategory);
        const matchesSearch = (!q || name.includes(q) || cls.includes(q) || cat.includes(q));
        if (matchesCategory && matchesSearch) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    }

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeCategory = tab.dataset.category;
        filterIcons();
      });
    });

    searchInput.addEventListener('input', filterIcons);

    function showToast(msg) {
      toast.innerText = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2200);
    }

    function copyIcon(className) {
      const snippet = '<i class="' + className + '"></i>';
      navigator.clipboard.writeText(snippet).then(() => {
        showToast('Tersalin: ' + snippet);
      }).catch(() => {
        showToast('Class tersalin: .' + className);
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

  console.log('🚀 Starting MIS Gallery Font Generation with Category Support...');

  // Recursively scan SVG directory
  const svgFiles = scanSvgDirectory(srcDir);

  if (svgFiles.length === 0) {
    console.error('❌ No SVG files found in ./svg directory or its subfolders!');
    process.exit(1);
  }

  console.log(`📁 Found ${svgFiles.length} SVG icons across subfolders:`);

  // Create temporary directory for flattened and prefixed SVGs
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mis-svg-'));
  const processedIcons = [];

  for (const item of svgFiles) {
    const meta = getCategoryInfo(item.relPath);
    console.log(`   [${meta.category}] ${item.fileName} -> glyph: ${meta.glyphName}`);

    // Read and clean SVG content
    const rawContent = fs.readFileSync(item.fullPath, 'utf-8');
    const cleaned = cleanSvgContent(rawContent);

    // Staged filename with prefix
    const stagedFileName = `${meta.glyphName}.svg`;
    fs.writeFileSync(path.join(tempDir, stagedFileName), cleaned, 'utf-8');

    processedIcons.push({
      ...meta,
      stagedFileName,
      className: `mis-${meta.glyphName}`,
      sourceRelPath: `svg/${item.relPath}`
    });
  }

  // Run svgtofont engine
  console.log('\n⚙️  Running svgtofont compiler...');
  await svgtofont({
    src: tempDir,
    dist: distDir,
    fontName: 'mis-icons',
    classNamePrefix: 'mis',
    css: true,
    emptyDist: true,
    startUnicode: 0xea01,
    svgicons2svgfont: {
      fontHeight: 1000,
      normalize: true
    },
    website: {
      title: 'MIS Gallery - Mertani Icon Studio',
      logo: '',
      version: '1.0.0',
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

  // Match class to unicode: .mis-xxx::before { content: "\ea01"; }
  for (const icon of processedIcons) {
    const re = new RegExp(`\\.mis-${icon.glyphName}::before\\s*\\{\\s*content:\\s*"([^"]+)";`, 'i');
    const match = cssContent.match(re);
    icon.unicode = match ? match[1] : '';
  }

  // Append developer convenience aliases to mis-icons.css
  let aliasesCss = '\n/* --- Developer Aliases --- */\n';
  let aliasCount = 0;
  for (const icon of processedIcons) {
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

  // Write structured metadata json (dist/icons.json and dist/info.json)
  const metaJson = JSON.stringify(processedIcons, null, 2);
  fs.writeFileSync(path.join(distDir, 'icons.json'), metaJson, 'utf-8');
  fs.writeFileSync(path.join(distDir, 'info.json'), metaJson, 'utf-8');
  console.log(`📋 Written icons.json & info.json metadata (${processedIcons.length} icons)`);

  // Overwrite dist/index.html with modern interactive categorized showcase
  const customHtml = generateCatalogHtml(processedIcons);
  fs.writeFileSync(path.join(distDir, 'index.html'), customHtml, 'utf-8');
  console.log('✨ Generated modern categorized web catalog in dist/index.html');

  // Cleanup temp dir
  try {
    fs.rmSync(tempDir, { recursive: true, force: true });
  } catch (e) {}

  console.log('✅ MIS Gallery icon fonts & catalog built successfully in dist/!\n');
}

build().catch((err) => {
  console.error('❌ Error building MIS Gallery font:', err);
  process.exit(1);
});
