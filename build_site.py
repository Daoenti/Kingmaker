import os
import markdown
import re
from pathlib import Path

# Markdown extensions for better rendering
md = markdown.Markdown(extensions=[
    'extra',
    'codehilite',
    'toc',
    'tables',
    'fenced_code',
    'attr_list',
    'def_list',
    'wikilinks',
])

# Create output directory
output_dir = Path('_site')
output_dir.mkdir(exist_ok=True)

# Base URL for GitHub Pages (repo name)
BASE_URL = '/Kingmaker'

# CSS for the site
css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    min-height: 100vh;
}

nav {
    width: 300px;
    background: #2c3e50;
    color: white;
    padding: 20px;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
}

nav h1 {
    font-size: 24px;
    margin-bottom: 20px;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

nav h2 {
    font-size: 16px;
    margin-top: 20px;
    margin-bottom: 10px;
    color: #3498db;
    text-transform: uppercase;
    letter-spacing: 1px;
}

nav h3 {
    font-size: 14px;
    margin-top: 10px;
    margin-bottom: 5px;
    margin-left: 10px;
    color: #95a5a6;
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
    color: #ecf0f1;
    text-decoration: none;
    display: block;
    padding: 5px 10px;
    border-radius: 4px;
    transition: background 0.2s;
}

nav a:hover {
    background: #34495e;
    color: #3498db;
}

main {
    flex: 1;
    padding: 40px;
    background: white;
}

main h1 {
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

main h2 {
    color: #2c3e50;
    margin-top: 30px;
    margin-bottom: 15px;
}

main h3 {
    color: #34495e;
    margin-top: 20px;
    margin-bottom: 10px;
}

main p {
    margin-bottom: 15px;
}

main ul, main ol {
    margin-left: 30px;
    margin-bottom: 15px;
}

main li {
    margin-bottom: 5px;
}

main code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
}

main pre {
    background: #f4f4f4;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    margin-bottom: 15px;
}

main pre code {
    background: none;
    padding: 0;
}

main blockquote {
    border-left: 4px solid #3498db;
    padding-left: 20px;
    margin: 20px 0;
    color: #555;
    font-style: italic;
}

main table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

main th, main td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

main th {
    background: #3498db;
    color: white;
}

main tr:nth-child(even) {
    background: #f9f9f9;
}

.home-content {
    text-align: center;
    padding: 60px 20px;
}

.home-content h1 {
    font-size: 48px;
    margin-bottom: 20px;
    border: none;
}

.home-content p {
    font-size: 20px;
    color: #666;
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

# Build a map of file names to paths for internal links
file_map = {}
for f in md_files:
    # Store both with and without .md extension
    file_map[f.stem] = f
    file_map[f.name] = f

# Build navigation structure
nav_structure = {}
for f in md_files:
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
    nav_html += '<h1>🎲 Kingmaker Campaign</h1>\n'
    
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

# Function to fix internal links
def fix_internal_links(html_content, current_file):
    """Convert Obsidian-style [[links]] and markdown links to proper HTML links"""
    
    # Fix [[WikiLinks]]
    def replace_wikilink(match):
        link_text = match.group(1)
        # Check if it has a pipe for custom text [[link|text]]
        if '|' in link_text:
            target, display = link_text.split('|', 1)
        else:
            target = display = link_text
        
        # Try to find the target file
        target_clean = target.strip()
        if target_clean in file_map:
            target_path = file_map[target_clean]
            url = BASE_URL + '/' + str(target_path).replace('\\', '/').replace('.md', '.html')
            return f'<a href="{url}">{display}</a>'
        else:
            # Link not found, just return the text
            return display
    
    html_content = re.sub(r'\[\[([^\]]+)\]\]', replace_wikilink, html_content)
    
    # Fix relative markdown links like [text](File.md)
    def replace_mdlink(match):
        display = match.group(1)
        target = match.group(2)
        
        # Only process .md links
        if target.endswith('.md'):
            target_name = Path(target).stem
            if target_name in file_map:
                target_path = file_map[target_name]
                url = BASE_URL + '/' + str(target_path).replace('\\', '/').replace('.md', '.html')
                return f'<a href="{url}">{display}</a>'
        
        # Return original if not found or not .md
        return match.group(0)
    
    html_content = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', replace_mdlink, html_content)
    
    return html_content

# Convert each markdown file to HTML
for md_file in md_files:
    print(f"Converting: {md_file}")
    
    content = md_file.read_text(encoding='utf-8')
    html_content = md.convert(content)
    md.reset()
    
    # Fix internal links
    html_content = fix_internal_links(html_content, md_file)
    
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
print(f"   Generated {len(md_files)} pages")
