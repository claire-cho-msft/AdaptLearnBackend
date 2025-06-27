import yaml
import json
from urllib.parse import urlparse

def _extract_filename_from_url(url):
    """Extract filename from URL and convert to .md format"""
    if url.startswith('http'):
        # External URLs - use the last part of the path
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if path_parts and path_parts[-1]:
            return f"{path_parts[-1]}.md"
        else:
            # Use domain name if no path
            return f"{parsed.netloc.replace('.', '_')}.md"
    elif url.endswith('.md'):
        # Already a markdown file
        return url
    elif url.endswith('.yml'):
        # YAML file, convert to .md
        return url.replace('.yml', '.md')
    else:
        # Internal URL path - extract last segment
        path_parts = url.strip('/').split('/')
        if path_parts and path_parts[-1]:
            return f"{path_parts[-1]}.md"
        else:
            return "content.md"

def get_left_sidebar_structure():
    # Load the YAML file with correct path
    import os
    yaml_path = os.path.join(os.path.dirname(__file__), '..', 'markdown', 'azure-developer-cli', 'index.yml')
    
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    # Extract landingContent
    landing_content = data.get('landingContent', [])

    # Process into simple format
    result = []
    for section in landing_content:
        section_data = {
            'title': section.get('title', ''),
            'links': []
        }
        
        # Use a set to track seen URLs and avoid duplicates
        seen_urls = set()
        
        # Collect all links from all linkLists in this section
        for link_list in section.get('linkLists', []):
            for link in link_list.get('links', []):
                original_url = link.get('url', '')
                filename = _extract_filename_from_url(original_url)
                new_url = f"/tutorial/{filename.replace('.md', '')}"
                
                # Only add if we haven't seen this URL before
                if new_url not in seen_urls:
                    seen_urls.add(new_url)
                    section_data['links'].append({
                        'text': link.get('text', ''),
                        'url': new_url
                    })
        
        result.append(section_data)
    return result

if __name__ == "__main__":
    # Only run when executed directly
    result = get_left_sidebar_structure()
    print(json.dumps(result, indent=2))