const _svgtofont = require('svgtofont');
const svgtofont = _svgtofont.default || _svgtofont;
const path = require('path');
const fs = require('fs');
const os = require('os');

// Helper to clean Figma masks and nested groups from SVG
function cleanSvgContent(content) {
  // Remove <mask ...> ... </mask> blocks
  let cleaned = content.replace(/<mask[\s\S]*?<\/mask>/gi, '');
  // Remove mask="..." and clip-path="..." attributes
  cleaned = cleaned.replace(/\s+mask="[^"]*"/gi, '');
  cleaned = cleaned.replace(/\s+clip-path="[^"]*"/gi, '');
  return cleaned;
}

async function build() {
  const rootDir = path.resolve(__dirname, '..');
  const srcDir = path.join(rootDir, 'svg');
  const distDir = path.join(rootDir, 'dist');

  console.log('🚀 Starting MIS Gallery Font Generation...');

  // Create temporary directory with cleaned SVGs
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mis-svg-'));
  const svgFiles = fs.readdirSync(srcDir).filter(f => f.toLowerCase().endsWith('.svg'));

  if (svgFiles.length === 0) {
    console.error('❌ No SVG files found in ./svg directory!');
    process.exit(1);
  }

  console.log(`📁 Processing ${svgFiles.length} SVG icons...`);
  for (const file of svgFiles) {
    const rawContent = fs.readFileSync(path.join(srcDir, file), 'utf-8');
    const cleaned = cleanSvgContent(rawContent);
    fs.writeFileSync(path.join(tempDir, file), cleaned, 'utf-8');
  }

  // Run svgtofont engine
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
      meta: {
        description: 'Mertani Icon Studio (MIS Gallery) Official Web Font & Icon Collection',
        keywords: 'icons,font,svg,mertani,mis-gallery'
      },
      description: 'Gudang Ikon Resmi Mertani Icon Studio (MIS Gallery). Klik ikon untuk menyalin class CSS.',
      links: [
        {
          title: 'GitHub Repository',
          url: 'https://github.com/rizcode21/MIS-Gallery'
        }
      ]
    }
  });

  // Cleanup temp dir
  try {
    fs.rmSync(tempDir, { recursive: true, force: true });
  } catch (e) {}

  console.log('✅ MIS Gallery icon fonts generated successfully in dist/!');
}

build().catch((err) => {
  console.error('❌ Error building MIS Gallery font:', err);
  process.exit(1);
});
