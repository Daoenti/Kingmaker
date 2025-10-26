import markdown
import re
from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader

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

# Setup Jinja2 environment
template_env = Environment(loader=FileSystemLoader('Resources/templates'))

# Create output directory
output_dir = Path('_site')
output_dir.mkdir(exist_ok=True)

# Base URL for GitHub Pages (repo name)
BASE_URL = '/Kingmaker'

# Copy logo to output directory
logo_src = Path('Resources/Images/kingmaker-logo.png')
if logo_src.exists():
    shutil.copy(logo_src, output_dir / 'kingmaker-logo.png')
    print("Logo copied to output directory")

# Copy all CSS files to output directory
css_dir = Path('Resources/Styles')
if css_dir.exists():
    for css_file in css_dir.glob('*.css'):
        shutil.copy(css_file, output_dir / css_file.name)
        print(f"CSS file copied: {css_file.name}")
else:
    print("Warning: Styles directory not found")

# Collect all markdown files
exclude_dirs = {'.git', '.github', '.obsidian', '.trash', '.makemd', '.space', '.venv', 'Tags'}
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

# Generate navigation HTML with collapsible sections
def generate_nav():
    nav_html = '<nav>\n'
    nav_html += f'<div class="logo"><a href="{BASE_URL}/" onclick="loadContent(\'{BASE_URL}/index.html\', \'Kingmaker Campaign\'); return false;"><img src="{BASE_URL}/kingmaker-logo.png" alt="Kingmaker Campaign"></a></div>\n'

    # Add theme switcher - dynamically build from available theme files
    nav_html += '<div class="theme-switcher">\n'
    nav_html += '<label for="theme-select">Theme:</label>\n'
    nav_html += '<select id="theme-select" onchange="changeTheme(this.value)">\n'

    # Find all theme CSS files
    css_dir = Path('Resources/Styles')
    if css_dir.exists():
        theme_files = sorted(css_dir.glob('theme-*.css'))
        for theme_file in theme_files:
            filename = theme_file.name
            # Create display name from filename
            # theme-gruvbox-dark.css -> Gruvbox Dark
            # theme-aon-dark.css -> Aon Dark
            # theme-cycle-dark.css -> Cycle Dark
            theme_name = filename.replace('theme-', '').replace('.css', '')

            # Convert hyphen-separated to Title Case
            display_name = ' '.join(word.capitalize() for word in theme_name.split('-'))

            nav_html += f'<option value="{filename}">{display_name}</option>\n'

    nav_html += '</select>\n'
    nav_html += '</div>\n'

    for folder in sorted(nav_structure.keys()):
        # Make the folder header clickable to collapse/expand
        folder_id = folder.replace(' ', '-').lower()
        nav_html += f'<div class="nav-section">\n'
        nav_html += f'<h2 class="collapsible" onclick="toggleSection(\'{folder_id}\')">'
        nav_html += f'<span class="toggle-icon">▼</span> {folder}</h2>\n'
        nav_html += f'<ul id="{folder_id}" class="nav-list">\n'

        # Add main files in this folder
        for file in sorted(nav_structure[folder]['files']):
            url = BASE_URL + '/' + str(file).replace('\\', '/').replace('.md', '.html')
            title = file.stem.replace('-', ' ').replace('_', ' ')
            nav_html += f'<li><a href="{url}" onclick="loadContent(\'{url}\', \'{title}\'); return false;">{title}</a></li>\n'

        # Add subfolders
        for subfolder in sorted(nav_structure[folder]['subfolders'].keys()):
            subfolder_id = f"{folder_id}-{subfolder.replace(' ', '-').lower()}"
            nav_html += f'<li class="subsection">\n'
            nav_html += f'<h3 class="collapsible" onclick="toggleSection(\'{subfolder_id}\')">'
            nav_html += f'<span class="toggle-icon">▼</span> {subfolder}</h3>\n'
            nav_html += f'<ul id="{subfolder_id}" class="nav-list timeline-list">\n'
            for file in sorted(nav_structure[folder]['subfolders'][subfolder]):
                url = BASE_URL + '/' + str(file).replace('\\', '/').replace('.md', '.html')
                title = file.stem.replace('_', ' ')

                # Remove number prefix from title (e.g., "00 - README" becomes "README")
                import re
                clean_title = re.sub(r'^\d+\s*-\s*', '', title)

                nav_html += f'<li><a href="{url}" onclick="loadContent(\'{url}\', \'{clean_title}\'); return false;">{clean_title}</a></li>\n'
            nav_html += '</ul>\n'
            nav_html += '</li>\n'

        nav_html += '</ul>\n'
        nav_html += '</div>\n'

    nav_html += '</nav>\n'
    return nav_html

nav_html = generate_nav()

# Function to fix internal links BEFORE markdown conversion
def fix_internal_links_pre(content, current_file):
    """Convert Obsidian-style [[links]] to markdown links before processing"""
    
    def replace_wikilink(match):
        link_text = match.group(1)
        # Remove any backslash escaping (Obsidian escapes pipes in tables)
        link_text = link_text.replace('\\|', '|')
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

    # Generate breadcrumbs
    breadcrumbs = []
    parts = list(md_file.parts)

    # Build breadcrumb trail
    for i, part in enumerate(parts[:-1]):  # Exclude the file itself
        # Create display name
        display_name = part.replace('-', ' ').replace('_', ' ')

        # Create URL if this is a folder with an index
        if i == 0:
            breadcrumbs.append({
                'name': display_name,
                'url': None  # Top level folder, no link
            })
        else:
            breadcrumbs.append({
                'name': display_name,
                'url': None  # Subfolder, no direct link
            })

    # Add current page (no link)
    clean_title = page_title
    # Remove number prefix from timeline entries
    clean_title = re.sub(r'^\d+\s*-\s*', '', clean_title)

    breadcrumbs.append({
        'name': clean_title,
        'url': None
    })

    # Save content-only version for AJAX loading
    content_file = output_dir / str(md_file).replace('.md', '-content.html')
    content_file.parent.mkdir(parents=True, exist_ok=True)
    content_file.write_text(html_content, encoding='utf-8')

    # Render page using Jinja2 template
    template = template_env.get_template('page.html')
    full_html = template.render(
        page_title=page_title,
        content=html_content,
        navigation=nav_html,
        base_url=BASE_URL,
        breadcrumbs=breadcrumbs
    )

    out_file.write_text(full_html, encoding='utf-8')

# Create index.html with home content
home_content = """<div class="home-content">
    <h1>⚔️ Kingmaker Campaign</h1>
    <p>Pathfinder Campaign Notes</p>
    <p>Use the navigation on the left to explore the campaign world.</p>
</div>"""

# Save home content separately for AJAX
(output_dir / 'index-content.html').write_text(home_content, encoding='utf-8')

# Render index page using Jinja2 template
index_template = template_env.get_template('index.html')
index_html = index_template.render(
    navigation=nav_html,
    base_url=BASE_URL
)

(output_dir / 'index.html').write_text(index_html, encoding='utf-8')

print(f"\nSite built successfully!")
print(f"   Generated {len(valid_files)} pages")
