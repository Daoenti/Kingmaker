import os
import markdown
import re
from pathlib import Path
import shutil

# Markdown extensions for better rendering
md = markdown.Markdown(extensions=[
    'extra',
    'codehilite',
    'toc',
    'tables',
    'fenced_code',
    'attr_list',
    'def_list',
])

# Create output directory
output_dir = Path('_site')
output_dir.mkdir(exist_ok=True)

# Base URL for GitHub Pages (repo name)
BASE_URL = '/Kingmaker'

# Copy logo to output directory
logo_src = Path('kingmaker-logo.png')
if logo_src.exists():
    shutil.copy(logo_src, output_dir / 'kingmaker-logo.png')
    print("Logo copied to output directory")

# CSS for the site - DARK MODE
css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #e4e4e4;
    background: #1a1a1a;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    min-height: 100vh;
}

nav {
    width: 300px;
    background: #0d1117;
    color: #c9d1d9;
    padding: 20px;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #30363d;
}

nav .logo {
    width: 100%;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #30363d;
}

nav .logo img {
    width: 100%;
    height: auto;
    display: block;
}

nav h1 {
    font-size: 24px;
    margin-bottom: 20px;
    border-bottom: 2px solid #58a6ff;
    padding-bottom: 10px;
    color: #58a6ff;
}

nav h2 {
    font-size: 16px;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #58a6ff;
    text-transform: uppercase;
    letter-spacing: 1px;
}

nav h3 {
    font-size: 14px;
    margin-top: 10px;
    margin-bottom: 5px;
    margin-left: 10px;
    color: #8b949e;
    font-weight: normal;
}

nav ul {
    list-style: none;
}

nav li {
    margin: 5px 0;
}

nav .subsection {
    margin-left: 15px;
}

nav a {
    color: #c9d1d9;
    text-decoration: none;
    display: block;
    padding: 5px 10px;
    border-radius: 4px;
    transition: background 0.2s;
}

nav a:hover {
    background: #21262d;
    color: #58a6ff;
}

main {
    flex: 1;
    padding: 40px;
    background: #0d1117;
}

main h1 {
    color: #c9d1d9;
    border-bottom: 3px solid #58a6ff;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

main h2 {
    color: #c9d1d9;
    margin-top: 30px;
    margin-bottom: 15px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 8px;
}

main h3 {
    color: #c9d1d9;
    margin-top: 20px;
    margin-bottom: 10px;
}

main h4, main h5, main h6 {
    color: #c9d1d9;
    margin-top: 15px;
    margin-bottom: 8px;
}

main p {
    margin-bottom: 15px;
    color: #c9d1d9;
}

main ul, main ol {
    margin-left: 30px;
    margin-bottom: 15px;
}

main li {
    margin-bottom: 5px;
    color: #c9d1d9;
}

main a {
    color: #58a6ff;
    text-decoration: none;
}

main a:hover {
    text-decoration: underline;
}

main code {
    background: #161b22;
    color: #f0883e;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    border: 1px solid #30363d;
}

main pre {
    background: #161b22;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 15px;
    border: 1px solid #30363d;
}

main pre code {
    background: none;
    padding: 0;
    border: none;
    color: #c9d1d9;
}

main blockquote {
    border-left: 4px solid #58a6ff;
    padding-left: 20px;
    margin: 20px 0;
    color: #8b949e;
    font-style: italic;
}

main table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

main th, main td {
    border: 1px solid #30363d;
    padding: 10px;
    text-align: left;
}

main th {
    background: #161b22;
    color: #58a6ff;
    font-weight: 600;
}

main td {
    color: #c9d1d9;
}

main tr:nth-child(even) {
    background: #161b22;
}

main tr:hover {
    background: #21262d;
}

main hr {
    border: none;
    border-top: 1px solid #30363d;
    margin: 20px 0;
}

main strong {
    color: #c9d1d9;
    font-weight: 600;
}

main em {
    color: #c9d1d9;
}

.home-content {
    text-align: center;
    padding: 60px 20px;
}

.home-content h1 {
    font-size: 48px;
    margin-bottom: 20px;
    border: none;
    color: #58a6ff;
}

.home-content p {
    font-size: 20px;
    color: #8b949e;
}

/* Scrollbar styling for dark mode */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #0d1117;
}

::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #484f58;
}

@media (max-width: 768px) {
    .container {
        flex-direction: column;
    }
    
    nav {
        width: 100%;
        height: auto;
        position: relative;
    }
}
"""

# Write CSS file
(output_dir / 'style.css').write_text(css)

# Collect all markdown files
exclude_dirs = {'.git', '.github', '.obsidian', '.trash', '.makemd', '.space', 'Tags'}
md_files = []

for f in Path('.').rglob('*.md'):
    if not any(excluded in f.parts for excluded in exclude_dirs):
        md_files.append(f)

print(f"Found {len(md_files)} markdown files")

# Function to remove YAML frontmatter
def remove_frontmatter(content):
    """Remove YAML frontmatter from markdown content"""
    # Check if content starts with ---
    if content.startswith('---'):
        # Find the end of frontmatter (second ---)
        parts = content.split('---', 2)
        if len(parts) >= 3:
            # Return everything after the frontmatter
            return parts[2].lstrip()
    return content

# Pre-process files to check if they have content after frontmatter removal
valid_files = []
for f in md_files:
    content = f.read_text(encoding='utf-8')
    content_no_frontmatter = remove_frontmatter(content)
    
    # Check if there's actual content (not just whitespace)
    if content_no_frontmatter.strip():
        valid_files.append(f)
    else:
        print(f"  Skipping {f} (empty after frontmatter removal)")

print(f"Valid files with content: {len(valid_files)}")

# Build a map of file names to paths for internal links (only valid files)
file_map = {}
for f in valid_files:
    # Store by stem (filename without extension)
    file_map[f.stem] = f
    # Also store full path variants
    file_map[str(f).replace('\\', '/')] = f
    # Store with .md extension
    file_map[f.name] = f
    
print(f"File map has {len(file_map)} entries")

# Build navigation structure (only valid files)
nav_structure = {}
for f in valid_files:
    path_parts = list(f.parts)
    
    if len(path_parts) > 1:
        # Use first part as main folder
        folder = path_parts[0]
        if folder not in nav_structure:
            nav_structure[folder] = {'files': [], 'subfolders': {}}
        
        # Check if there's a subfolder
        if len(path_parts) > 2:
            subfolder = path_parts[1]
            if subfolder not in nav_structure[folder]['subfolders']:
                nav_structure[folder]['subfolders'][subfolder] = []
            nav_structure[folder]['subfolders'][subfolder].append(f)
        else:
            nav_structure[folder]['files'].append(f)
    else:
        if 'Root' not in nav_structure:
            nav_structure['Root'] = {'files': [], 'subfolders': {}}
        nav_structure['Root']['files'].append(f)

# Generate navigation HTML
def generate_nav():
    nav_html = '<nav>\n'
    nav_html += f'<div class="logo"><a href="{BASE_URL}/"><img src="{BASE_URL}/kingmaker-logo.png" alt="Kingmaker Campaign"></a></div>\n'
    
    for folder in sorted(nav_structure.keys()):
        nav_html += f'<h2>{folder}</h2>\n'
        nav_html += '<ul>\n'
        
        # Add main files in this folder
        for file in sorted(nav_structure[folder]['files']):
            url = BASE_URL + '/' + str(file).replace('\\', '/').replace('.md', '.html')
            title = file.stem.replace('-', ' ').replace('_', ' ')
            nav_html += f'<li><a href="{url}">{title}</a></li>\n'
        
        # Add subfolders
        for subfolder in sorted(nav_structure[folder]['subfolders'].keys()):
            nav_html += f'<li class="subsection">\n'
            nav_html += f'<h3>{subfolder}</h3>\n'
            nav_html += '<ul>\n'
            for file in sorted(nav_structure[folder]['subfolders'][subfolder]):
                url = BASE_URL + '/' + str(file).replace('\\', '/').replace('.md', '.html')
                title = file.stem.replace('-', ' ').replace('_', ' ')
                nav_html += f'<li><a href="{url}">{title}</a></li>\n'
            nav_html += '</ul>\n'
            nav_html += '</li>\n'
        
        nav_html += '</ul>\n'
    
    nav_html += '</nav>\n'
    return nav_html

nav_html = generate_nav()

# Function to fix internal links BEFORE markdown conversion
def fix_internal_links_pre(content, current_file):
    """Convert Obsidian-style [[links]] to markdown links before processing"""
    
    def replace_wikilink(match):
        link_text = match.group(1)
        # Check if it has a pipe for custom text [[link|text]]
        if '|' in link_text:
            target, display = link_text.split('|', 1)
        else:
            target = display = link_text
        
        # Try to find the target file
        target_clean = target.strip()
        
        # Try exact match first
        if target_clean in file_map:
            target_path = file_map[target_clean]
            url = BASE_URL + '/' + str(target_path).replace('\\', '/').replace('.md', '.html')
            return f'[{display}]({url})'
        
        # Try with .md extension
        if target_clean + '.md' in file_map:
            target_path = file_map[target_clean + '.md']
            url = BASE_URL + '/' + str(target_path).replace('\\', '/').replace('.md', '.html')
            return f'[{display}]({url})'
        
        # Try case-insensitive match
        for key, path in file_map.items():
            if key.lower() == target_clean.lower():
                url = BASE_URL + '/' + str(path).replace('\\', '/').replace('.md', '.html')
                return f'[{display}]({url})'
        
        print(f"  Warning: Could not find link target '{target_clean}'")
        # Link not found, just return the text
        return display
    
    content = re.sub(r'\[\[([^\]]+)\]\]', replace_wikilink, content)
    return content

# Function to fix markdown links to .md files
def fix_md_links(content):
    """Fix relative markdown links to .md files"""
    
    def replace_mdlink(match):
        full_match = match.group(0)
        display = match.group(1)
        target = match.group(2)
        
        # Only process .md links (not URLs)
        if target.endswith('.md') and not target.startswith('http'):
            # Extract filename
            target_name = Path(target).stem
            
            # Try to find it
            if target_name in file_map:
                target_path = file_map[target_name]
                url = BASE_URL + '/' + str(target_path).replace('\\', '/').replace('.md', '.html')
                return f'[{display}]({url})'
            
            # Try with full relative path
            if target in file_map:
                target_path = file_map[target]
                url = BASE_URL + '/' + str(target_path).replace('\\', '/').replace('.md', '.html')
                return f'[{display}]({url})'
        
        # Return original if not found or not .md
        return full_match
    
    content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', replace_mdlink, content)
    return content

# Convert each markdown file to HTML (only valid files)
for md_file in valid_files:
    print(f"Converting: {md_file}")
    
    content = md_file.read_text(encoding='utf-8')
    
    # Remove frontmatter
    content = remove_frontmatter(content)
    
    # Fix internal links BEFORE markdown conversion
    content = fix_internal_links_pre(content, md_file)
    content = fix_md_links(content)
    
    # Now convert to HTML
    html_content = md.convert(content)
    md.reset()
    
    out_file = output_dir / str(md_file).replace('.md', '.html')
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    page_title = md_file.stem.replace('-', ' ').replace('_', ' ')
    
    # Use absolute path to CSS for all pages
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - Kingmaker Campaign</title>
    <link rel="stylesheet" href="{BASE_URL}/style.css">
</head>
<body>
    <div class="container">
        {nav_html}
        <main>
            {html_content}
        </main>
    </div>
</body>
</html>"""
    
    out_file.write_text(full_html, encoding='utf-8')

# Create index.html
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kingmaker Campaign</title>
    <link rel="stylesheet" href="{BASE_URL}/style.css">
</head>
<body>
    <div class="container">
        {nav_html}
        <main>
            <div class="home-content">
                <h1>⚔️ Kingmaker Campaign</h1>
                <p>Pathfinder Campaign Notes</p>
                <p>Use the navigation on the left to explore the campaign world.</p>
            </div>
        </main>
    </div>
</body>
</html>"""

(output_dir / 'index.html').write_text(index_html, encoding='utf-8')

print(f"\n✅ Site built successfully!")
print(f"   Generated {len(valid_files)} pages")
