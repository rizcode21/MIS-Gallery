import re
import os
import shutil
import tempfile
import xml.etree.ElementTree as ET


def strip_ns(tag: str) -> str:
    """Strip XML namespace prefix from tag name."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def normalize_svg_path(d: str) -> str:
    """Expand SVG path shorthand commands like s/S and t/T to standard C/Q curves,

    ensuring maximum compatibility for the svg2font engine.
    """
    token_re = re.compile(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)')
    raw_tokens = token_re.findall(d)
    tokens = [m[0] if m[0] else float(m[1]) for m in raw_tokens]

    out_cmds = []
    i = 0
    cur_x, cur_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    last_cp2_x, last_cp2_y = 0.0, 0.0
    last_cmd = None

    while i < len(tokens):
        t = tokens[i]
        if isinstance(t, str):
            cmd = t
            i += 1
        else:
            cmd = last_cmd
            if cmd == 'M':
                cmd = 'L'
            elif cmd == 'm':
                cmd = 'l'

        if not cmd:
            break

        if cmd in ('M', 'm'):
            if i + 1 >= len(tokens):
                break
            x, y = tokens[i], tokens[i + 1]
            i += 2
            if cmd == 'm':
                cur_x += x
                cur_y += y
            else:
                cur_x = x
                cur_y = y
            start_x, start_y = cur_x, cur_y
            out_cmds.append(f'M {cur_x:.4f} {cur_y:.4f}')
            last_cmd = cmd
            last_cp2_x, last_cp2_y = cur_x, cur_y

        elif cmd in ('L', 'l'):
            if i + 1 >= len(tokens):
                break
            x, y = tokens[i], tokens[i + 1]
            i += 2
            if cmd == 'l':
                cur_x += x
                cur_y += y
            else:
                cur_x = x
                cur_y = y
            out_cmds.append(f'L {cur_x:.4f} {cur_y:.4f}')
            last_cmd = cmd
            last_cp2_x, last_cp2_y = cur_x, cur_y

        elif cmd in ('H', 'h'):
            if i >= len(tokens):
                break
            x = tokens[i]
            i += 1
            if cmd == 'h':
                cur_x += x
            else:
                cur_x = x
            out_cmds.append(f'L {cur_x:.4f} {cur_y:.4f}')
            last_cmd = cmd
            last_cp2_x, last_cp2_y = cur_x, cur_y

        elif cmd in ('V', 'v'):
            if i >= len(tokens):
                break
            y = tokens[i]
            i += 1
            if cmd == 'v':
                cur_y += y
            else:
                cur_y = y
            out_cmds.append(f'L {cur_x:.4f} {cur_y:.4f}')
            last_cmd = cmd
            last_cp2_x, last_cp2_y = cur_x, cur_y

        elif cmd in ('C', 'c'):
            if i + 5 >= len(tokens):
                break
            x1, y1, x2, y2, x, y = tokens[i:i + 6]
            i += 6
            if cmd == 'c':
                abs_x1, abs_y1 = cur_x + x1, cur_y + y1
                abs_x2, abs_y2 = cur_x + x2, cur_y + y2
                abs_x, abs_y = cur_x + x, cur_y + y
            else:
                abs_x1, abs_y1 = x1, y1
                abs_x2, abs_y2 = x2, y2
                abs_x, abs_y = x, y
            out_cmds.append(f'C {abs_x1:.4f} {abs_y1:.4f} {abs_x2:.4f} {abs_y2:.4f} {abs_x:.4f} {abs_y:.4f}')
            last_cp2_x, last_cp2_y = abs_x2, abs_y2
            cur_x, cur_y = abs_x, abs_y
            last_cmd = 'C'

        elif cmd in ('S', 's'):
            if i + 3 >= len(tokens):
                break
            x2, y2, x, y = tokens[i:i + 4]
            i += 4
            if last_cmd == 'C':
                rx = 2 * cur_x - last_cp2_x
                ry = 2 * cur_y - last_cp2_y
            else:
                rx = cur_x
                ry = cur_y

            if cmd == 's':
                abs_x2, abs_y2 = cur_x + x2, cur_y + y2
                abs_x, abs_y = cur_x + x, cur_y + y
            else:
                abs_x2, abs_y2 = x2, y2
                abs_x, abs_y = x, y

            out_cmds.append(f'C {rx:.4f} {ry:.4f} {abs_x2:.4f} {abs_y2:.4f} {abs_x:.4f} {abs_y:.4f}')
            last_cp2_x, last_cp2_y = abs_x2, abs_y2
            cur_x, cur_y = abs_x, abs_y
            last_cmd = 'C'

        elif cmd in ('Q', 'q'):
            if i + 3 >= len(tokens):
                break
            x1, y1, x, y = tokens[i:i + 4]
            i += 4
            if cmd == 'q':
                abs_x1, abs_y1 = cur_x + x1, cur_y + y1
                abs_x, abs_y = cur_x + x, cur_y + y
            else:
                abs_x1, abs_y1 = x1, y1
                abs_x, abs_y = x, y
            out_cmds.append(f'Q {abs_x1:.4f} {abs_y1:.4f} {abs_x:.4f} {abs_y:.4f}')
            last_cp2_x, last_cp2_y = abs_x1, abs_y1
            cur_x, cur_y = abs_x, abs_y
            last_cmd = 'Q'

        elif cmd in ('T', 't'):
            if i + 1 >= len(tokens):
                break
            x, y = tokens[i:i + 2]
            i += 2
            if last_cmd == 'Q':
                rx = 2 * cur_x - last_cp2_x
                ry = 2 * cur_y - last_cp2_y
            else:
                rx = cur_x
                ry = cur_y

            if cmd == 't':
                abs_x, abs_y = cur_x + x, cur_y + y
            else:
                abs_x, abs_y = x, y

            out_cmds.append(f'Q {rx:.4f} {ry:.4f} {abs_x:.4f} {abs_y:.4f}')
            last_cp2_x, last_cp2_y = rx, ry
            cur_x, cur_y = abs_x, abs_y
            last_cmd = 'Q'

        elif cmd in ('Z', 'z'):
            out_cmds.append('Z')
            cur_x, cur_y = start_x, start_y
            last_cmd = cmd
            last_cp2_x, last_cp2_y = cur_x, cur_y

        else:
            break

    return ' '.join(out_cmds) if out_cmds else d


def clean_and_flatten_svg_content(content: str) -> str:
    """Unwraps nested <g>, <mask ...>, <defs ...>, and <clipPath ...> tags

    typically produced by Figma / Illustrator, and flattens all visible paths directly into <svg>.
    """
    try:
        root = ET.fromstring(content)
    except Exception:
        return content

    viewBox = root.attrib.get('viewBox', '0 0 24 24')
    width = root.attrib.get('width', '24')
    height = root.attrib.get('height', '24')

    new_svg = ET.Element('svg', {
        'xmlns': 'http://www.w3.org/2000/svg',
        'viewBox': viewBox,
        'width': width,
        'height': height
    })

    found_elements = []

    def walk(node):
        tag = strip_ns(node.tag).lower()
        # Skip definition/mask containers
        if tag in ('mask', 'defs', 'clippath'):
            return

        if tag in ('path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline'):
            clean_attrib = {k: v for k, v in node.attrib.items() if not k.startswith('{')}
            clean_attrib.pop('mask', None)
            clean_attrib.pop('clip-path', None)

            if tag == 'path' and 'd' in clean_attrib:
                clean_attrib['d'] = normalize_svg_path(clean_attrib['d'])

            ET.SubElement(new_svg, tag, clean_attrib)
            found_elements.append(tag)

        for child in node:
            walk(child)

    for child in root:
        walk(child)

    if not found_elements:
        return content

    return ET.tostring(new_svg, encoding='utf-8').decode('utf-8')


def prepare_svg_directory(source_dir: str) -> tuple[str, bool]:
    """Inspects and copies SVGs to a temporary folder with flattened structure

    (unwrapping Figma/Illustrator masks/groups) and normalized path curves,
    preventing 'contains no path elements' and 'unsupported SVG path command' in the Go engine.
    Returns (effective_source_dir, is_temp).
    """
    svg_files = [f for f in os.listdir(source_dir) if f.lower().endswith('.svg')]
    if not svg_files:
        return source_dir, False

    # Create temporary directory with normalized and flattened SVGs
    temp_dir = tempfile.mkdtemp(prefix='svg2font_clean_')
    for fname in svg_files:
        src_path = os.path.join(source_dir, fname)
        dst_path = os.path.join(temp_dir, fname)
        try:
            with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            cleaned = clean_and_flatten_svg_content(content)
            with open(dst_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
        except Exception:
            shutil.copy2(src_path, dst_path)

    return temp_dir, True
