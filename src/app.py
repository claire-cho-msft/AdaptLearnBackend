from flask import Flask, render_template, request, jsonify
import datetime
import os
import re
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Load environment variables from .env file
load_dotenv()

# Import parser function
try:
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parser'))
    from parser import get_left_sidebar_structure
except ImportError:
    print("Warning: Could not import parser module")
    def get_left_sidebar_structure():
        return []

app = Flask(__name__)

# Initialize Hugging Face model for text generation (using a smaller, faster model)
print("🤖 Loading Hugging Face model for content adaptation...")
try:
    # Try different models in order of preference
    model_options = [
        "Qwen/Qwen3-0.6B",
        "distilgpt2",  # Fast and reliable
        "gpt2",        # Standard fallback  
        "microsoft/DialoGPT-small"  # Even smaller if needed
    ]
    
    text_generator = None
    for model_name in model_options:
        try:
            print(f"   Trying {model_name}...")
            text_generator = pipeline(
                "text-generation",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,  # Use GPU if available
                max_length=300,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256  # Standard pad token for GPT-2 based models
            )
            print(f"✅ Successfully loaded {model_name}")
            break
        except Exception as model_error:
            print(f"   ❌ Failed to load {model_name}: {model_error}")
            continue
    
    if text_generator:
        MODEL_AVAILABLE = True
    else:
        raise Exception("No suitable model could be loaded")
        
except Exception as e:
    print(f"⚠️  Warning: Could not load any Hugging Face model: {e}")
    print("   Content adaptation will be disabled.")
    print("   Try running: pip install torch transformers")
    text_generator = None
    MODEL_AVAILABLE = False

# Store slider states and adapted content cache
slider_states = {}
adapted_content_cache = {}

def markdown_to_html(markdown_content):
    """Convert markdown content to HTML"""
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
    html_content = md.convert(markdown_content)
    return html_content

def html_to_json_structure(html_content, title=""):
    """Convert HTML content to tutorial JSON structure"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    sections = []
    current_section = None
    section_counter = 1
    
    # Find all elements in the HTML
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'pre', 'blockquote', 'div']):
        
        # Only create new sections for H2 headers
        if element.name == 'h2':
            # Save previous section if it exists
            if current_section and current_section['content']:
                sections.append(current_section)
            
            # Create new section
            section_title = element.get_text().strip()
            current_section = {
                'id': f"section-{section_counter}",
                'title': section_title,
                'content': []
            }
            section_counter += 1
        
        # If we don't have a section yet, create a default one
        elif current_section is None:
            current_section = {
                'id': f"section-{section_counter}",
                'title': "Introduction",
                'content': []
            }
            section_counter += 1
        
        # Add content to current section (including other headers like H1, H3, H4, etc.)
        if element.name in ['h1', 'h3', 'h4', 'h5', 'h6']:
            # Include other headers as content within the current section
            current_section['content'].append({
                'type': 'paragraph',
                'text': str(element)
            })
        
        elif element.name == 'p':
            text = str(element)
            text_content = element.get_text().strip()
            
            # Skip paragraphs that are just Microsoft-style callouts 
            # (these should be handled by blockquote processing)
            if text_content.startswith('[!') and ']' in text_content:
                # This is likely a callout that will be processed elsewhere, skip it
                continue
            
            # Skip zone pivot markers
            if text_content.startswith('::: zone') or text_content.startswith('::: zone-end'):
                continue
                
            if text.strip():
                current_section['content'].append({
                    'type': 'paragraph',
                    'text': text
                })
        
        elif element.name in ['ul', 'ol']:
            items = []
            for li in element.find_all('li'):
                items.append(str(li).replace('<li>', '').replace('</li>', ''))
            if items:
                current_section['content'].append({
                    'type': 'list',
                    'elements': items
                })
        
        elif element.name == 'pre':
            current_section['content'].append({
                'type': 'paragraph',
                'text': str(element)
            })
        
        elif element.name == 'blockquote':
            # Process blockquote content to handle [!NOTE] format
            text = element.get_text().strip()
            
            # Skip empty blockquotes
            if not text:
                continue
            
            # Check if it's a Microsoft-style note block
            if text.startswith('[!NOTE]'):
                # Remove the [!NOTE] prefix and clean up the text
                note_text = text[7:].strip()  # Remove '[!NOTE]' and whitespace
                if note_text:  # Only add if there's actual content
                    current_section['content'].append({
                        'type': 'note',
                        'text': note_text
                    })
            elif text.startswith('[!'):
                # Handle other Microsoft-style callouts (WARNING, TIP, etc.)
                # Find the end of the callout type
                end_bracket = text.find(']')
                if end_bracket != -1:
                    callout_text = text[end_bracket + 1:].strip()
                    if callout_text:  # Only add if there's actual content
                        current_section['content'].append({
                            'type': 'note',
                            'text': callout_text
                        })
                else:
                    # Fallback to regular note if malformed but has content
                    if text:
                        current_section['content'].append({
                            'type': 'note',
                            'text': text
                        })
            else:
                # Regular blockquote - only add if has content
                if text:
                    current_section['content'].append({
                        'type': 'note',
                        'text': text
                    })
        
        elif element.name == 'div':
            # Handle zone pivot containers
            if element.get('class') and 'zone-pivot' in element.get('class'):
                pivot_lang = element.get('data-pivot', '')
                current_section['content'].append({
                    'type': 'zone-pivot',
                    'pivot': pivot_lang,
                    'html': str(element)
                })
            # Skip other divs for now
    
    # Add the last section
    if current_section and current_section['content']:
        sections.append(current_section)
    
    # If no sections were created, create a default one with all content
    if not sections:
        sections.append({
            'id': 'section-1',
            'title': 'Content',
            'content': [{
                'type': 'paragraph',
                'text': html_content
            }]
        })
    
    return sections

def load_markdown_file(filename, selected_language="nodejs"):
    """Load and process a markdown file into tutorial JSON structure"""
    filepath = Path(os.path.join(os.path.dirname(__file__), '..', 'markdown', 'azure-developer-cli', filename))
    
    if not filepath.exists():
        # Return a placeholder structure if file doesn't exist
        return {
            'title': filename.replace('.md', '').replace('-', ' ').title(),
            'meta': 'File not found',
            'breadcrumbs': [
                {'name': 'Learn', 'url': '/'},
                {'name': 'Azure Developer CLI', 'url': '/tutorial'},
                {'name': filename.replace('.md', '').replace('-', ' ').title(), 'url': None}
            ],
            'intro_paragraph': f'The file {filename} was not found.',
            'tip_content': 'This content is not yet available.',
            'sections': [{
                'id': 'section-1',
                'title': 'File Not Found',
                'content': [{
                    'type': 'paragraph',
                    'text': f'The requested file <code>{filename}</code> could not be found.'
                }]
            }],
            'in_this_article': [{'title': 'File Not Found', 'anchor': '#section-1'}]
        }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Strip YAML front matter
        markdown_content = strip_yaml_frontmatter(markdown_content)
        
        # Process zone pivots (use selected language)
        markdown_content = process_zone_pivots(markdown_content, selected_language)
        
        # Convert markdown to HTML
        html_content = markdown_to_html(markdown_content)
        
        # Convert HTML to JSON structure
        sections = html_to_json_structure(html_content)
        
        # Extract title from filename
        title = filename.replace('.md', '').replace('-', ' ').title()
        
        # Generate table of contents
        in_this_article = [{'title': section['title'], 'anchor': f"#{section['id']}"} for section in sections]
        
        return {
            'title': title,
            'meta': f'Azure Developer CLI Documentation',
            'breadcrumbs': [
                {'name': 'Learn', 'url': '/'},
                {'name': 'Azure Developer CLI', 'url': '/tutorial'},
                {'name': title, 'url': None}
            ],
            'intro_paragraph': None,
            'tip_content': None,
            'sections': sections,
            'in_this_article': in_this_article
        }
    
    except Exception as e:
        # Return error structure
        return {
            'title': f'Error loading {filename}',
            'meta': 'Error occurred',
            'breadcrumbs': [
                {'name': 'Learn', 'url': '/'},
                {'name': 'Azure Developer CLI', 'url': '/tutorial'},
                {'name': 'Error', 'url': None}
            ],
            'intro_paragraph': f'An error occurred while loading {filename}.',
            'tip_content': f'Error: {str(e)}',
            'sections': [{
                'id': 'section-1',
                'title': 'Error',
                'content': [{
                    'type': 'paragraph',
                    'text': f'Failed to load content: {str(e)}'
                }]
            }],
            'in_this_article': [{'title': 'Error', 'anchor': '#section-1'}]
        }

def strip_yaml_frontmatter(markdown_content):
    """Remove YAML front matter from markdown content"""
    # Check if content starts with ---
    if markdown_content.strip().startswith('---'):
        # Find the end of the front matter (second ---)
        lines = markdown_content.split('\n')
        end_index = -1
        
        # Start from line 1 (skip the first ---) and look for the closing ---
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_index = i
                break
        
        # If we found the closing ---, return content after it
        if end_index != -1:
            return '\n'.join(lines[end_index + 1:]).strip()
    
    # Return original content if no front matter found
    return markdown_content

def adapt_content_for_level(content, level, section_title=""):
    """Use local Hugging Face model to adapt content for different skill levels"""
    # Advanced level - return original content
    if level == 2:
        return content
    
    # Always use our manual adaptation functions regardless of AI model availability
    # This ensures the system works even if the AI model fails to load
    try:
        # Clean and prepare content for adaptation
        clean_content = content.strip()
        
        # Don't adapt very short content or content that looks like code/commands
        if len(clean_content) < 30 or clean_content.startswith('`') or clean_content.startswith('$'):
            return content
        
        # Create cache key
        cache_key = f"{hash(clean_content)}_{level}_{section_title}"
        
        # Check cache first
        if cache_key in adapted_content_cache:
            return adapted_content_cache[cache_key]
        
        if level == 0:  # Beginner
            adapted_content = create_beginner_adaptation(clean_content, section_title)
        elif level == 1:  # Intermediate  
            adapted_content = create_intermediate_adaptation(clean_content, section_title)
        else:
            adapted_content = content
        
        # Cache the result
        adapted_content_cache[cache_key] = adapted_content
        
        return adapted_content
        
    except Exception as e:
        print(f"Error adapting content: {e}")
        # Return original content if processing fails
        return content

def create_beginner_adaptation(content, section_title):
    """Create beginner-friendly adaptation of content"""
    
    # For beginners, provide concise but helpful context
    if 'install' in content.lower():
        adapted = f"""<div class="beginner-content">
<h4>Quick Start Guide:</h4>
<p>{content}</p>

<div class="helpful-context">
<p><strong>What this does:</strong> Installs the Azure Developer CLI globally on your system, making it available from any terminal/command prompt.</p>

<p><strong>Next steps:</strong> After installation, you can verify it worked by running <code>azd version</code> in your terminal.</p>
</div>
</div>"""

    elif 'command' in content.lower() or 'run' in content.lower():
        adapted = f"""<div class="beginner-content">
<h4>Command Overview:</h4>
<p>{content}</p>

<div class="helpful-context">
<p><strong>What happens:</strong> This command packages your code, creates necessary cloud resources, and deploys your application to Azure.</p>

<p><strong>Typical runtime:</strong> First deployment takes 5-10 minutes. The command will show progress updates as it works.</p>
</div>
</div>"""

    elif 'deploy' in content.lower() or 'provision' in content.lower():
        adapted = f"""<div class="beginner-content">
<h4>Deployment Process:</h4>
<p>{content}</p>

<div class="helpful-context">
<p><strong>Two main steps:</strong></p>
<ul>
<li><strong>Provisioning:</strong> Creates cloud infrastructure (servers, databases, networks)</li>
<li><strong>Deployment:</strong> Uploads and runs your application on that infrastructure</li>
</ul>

<p><strong>Result:</strong> Your app becomes accessible via a public URL that Azure provides.</p>
</div>
</div>"""

    else:
        # Generic beginner adaptation - concise but helpful
        adapted = f"""<div class="beginner-content">
<p>{content}</p>

<div class="helpful-context">
<p><strong>Context:</strong> This relates to cloud development - building applications that run on remote servers instead of just your local machine.</p>
</div>
</div>"""
    
    return adapted

def create_intermediate_adaptation(content, section_title):
    """Create intermediate-level adaptation of content"""
    
    # For intermediate users, focus on practical implementation details
    if 'install' in content.lower():
        adapted = f"""<div class="intermediate-content">
<p>{content}</p>

<div class="implementation-details">
<p><strong>Implementation notes:</strong> Adds Azure Developer CLI to your system PATH for global access. Consider version management if working with multiple CLI versions across projects.</p>

<p><strong>Integration:</strong> Works with popular IDEs and CI/CD pipelines. Configure with your Azure subscription and set up authentication for automated workflows.</p>
</div>
</div>"""

    elif 'workflow' in content.lower() or 'process' in content.lower() or 'command' in content.lower() or 'run' in content.lower():
        adapted = f"""<div class="intermediate-content">
<p>{content}</p>

<div class="workflow-context">
<p><strong>Workflow integration:</strong> Fits into standard dev → test → deploy cycles. Can be incorporated into GitHub Actions, Azure DevOps, or other CI/CD pipelines.</p>

<p><strong>Performance:</strong> Initial deployments: 5-10 minutes. Subsequent updates are faster due to incremental changes.</p>
</div>
</div>"""

    elif 'deploy' in content.lower() or 'provision' in content.lower():
        adapted = f"""<div class="intermediate-content">
<p>{content}</p>

<div class="architecture-context">
<p><strong>Technical process:</strong> Provisioning creates Azure resources via Infrastructure as Code templates (Bicep/ARM). Build phase compiles your app. Deployment phase pushes to provisioned infrastructure.</p>

<p><strong>Architecture considerations:</strong> Plan resource groups, VNet configuration, auto-scaling policies, and security (Key Vault for secrets, proper authentication/authorization).</p>
</div>
</div>"""

    else:
        # Generic intermediate adaptation - practical and focused
        adapted = f"""<div class="intermediate-content">
<p>{content}</p>

<div class="technical-context">
<p><strong>Development context:</strong> Aligns with modern DevOps and Infrastructure as Code principles. Abstracts complexity while maintaining control over underlying infrastructure.</p>
</div>
</div>"""
    
    return adapted

@app.route("/slider-update", methods=['POST'])
def slider_update():
    """Handle slider state updates from frontend"""
    data = request.get_json()
    slider_id = data.get('slider_id')
    position = data.get('position')
    section_id = data.get('section_id')
    
    # Store the slider state
    slider_states[slider_id] = {
        'position': position,
        'section_id': section_id,
        'timestamp': str(datetime.datetime.now())
    }
    
    print(f"Slider {slider_id} moved to position {position} (section: {section_id})")
    
    # You can add logic here based on the slider position
    response_data = {'status': 'success', 'message': f'Slider {slider_id} updated to position {position}'}
    
    # Example: Different responses based on slider position
    if position == 0:
        response_data['level'] = 'beginner'
    elif position == 1:
        response_data['level'] = 'intermediate'
    else:
        response_data['level'] = 'advanced'
    
    return jsonify(response_data)

@app.route("/adapt-content", methods=['POST'])
def adapt_content():
    """Adapt section content based on difficulty level"""
    data = request.get_json()
    section_id = data.get('section_id')
    level = data.get('level', 2)  # Default to advanced
    filename = data.get('filename', 'overview.md')
    
    try:
        # Load the original content
        selected_language = request.args.get('lang', 'nodejs')
        tutorial_data = load_markdown_file(filename, selected_language)
        
        # Find the section to adapt
        target_section = None
        for section in tutorial_data['sections']:
            if section['id'] == section_id:
                target_section = section
                break
        
        if not target_section:
            return jsonify({'error': 'Section not found'}), 404
        
        # Adapt content items individually, preserving structure
        adapted_content = []
        
        for content_item in target_section['content']:
            if content_item['type'] == 'paragraph':
                # Extract and adapt only the text content, preserving HTML structure
                soup = BeautifulSoup(content_item['text'], 'html.parser')
                
                # Check if this is a code block or technical element that shouldn't be adapted
                if soup.find('code') or soup.find('pre') or content_item['text'].startswith('<pre>'):
                    # Keep code blocks unchanged
                    adapted_content.append(content_item)
                else:
                    # Extract plain text for adaptation
                    plain_text = soup.get_text().strip()
                    if plain_text and len(plain_text) > 20:  # Only adapt substantial text
                        # Adapt the plain text - this returns HTML already
                        adapted_html = adapt_content_for_level(plain_text, level, target_section['title'])
                        
                        # The adapted content is already in HTML format, so we use it directly
                        adapted_content.append({
                            'type': 'paragraph',
                            'text': adapted_html
                        })
                    else:
                        # Keep short text unchanged
                        adapted_content.append(content_item)
                        
            elif content_item['type'] == 'note':
                # Adapt note content - this returns HTML already
                if len(content_item['text']) > 20:
                    adapted_note_html = adapt_content_for_level(content_item['text'], level, target_section['title'])
                    adapted_content.append({
                        'type': 'paragraph',  # Change from 'note' to 'paragraph' since adapted content is HTML
                        'text': adapted_note_html
                    })
                else:
                    adapted_content.append(content_item)
                    
            else:
                # Keep lists, code blocks, videos, etc. unchanged
                adapted_content.append(content_item)
        
        return jsonify({
            'status': 'success',
            'section_id': section_id,
            'level': level,
            'adapted_content': adapted_content
        })
        
    except Exception as e:
        print(f"Error adapting content: {e}")
        return jsonify({'error': str(e)}), 500

@app.route("/clear-cache", methods=['POST'])
def clear_cache():
    """Clear the adapted content cache"""
    global adapted_content_cache
    cache_size = len(adapted_content_cache)
    adapted_content_cache.clear()
    
    return jsonify({
        'status': 'success',
        'message': f'Cleared {cache_size} cached items',
        'cache_size': cache_size
    })

@app.route("/cache-status")
def cache_status():
    """Get current cache status"""
    return jsonify({
        'cache_size': len(adapted_content_cache),
        'cached_items': list(adapted_content_cache.keys())[:10]  # Show first 10 keys
    })

@app.route("/get-slider-states")
def get_slider_states():
    """Get current slider states"""
    return jsonify(slider_states)

@app.route("/tutorial")
@app.route("/tutorial/<filename>")
def tutorial(filename=None):
    """
    Display tutorial content from markdown files
    If no filename provided, show overview/index page
    """
    # Default to overview if no filename provided
    if filename is None:
        filename = "overview.md"
    elif not filename.endswith('.md'):
        filename = f"{filename}.md"
    
    # Get language preference from query parameter, default to nodejs
    selected_language = request.args.get('lang', 'nodejs')
    
    # Load the main content
    tutorial_data = load_markdown_file(filename, selected_language)
    
    # Get sidebar structure from parser
    try:
        sidebar_structure = get_left_sidebar_structure()
    except Exception as e:
        print(f"Error loading sidebar structure: {e}")
        sidebar_structure = []
    
    # Add sidebar structure to template data
    tutorial_data['sidebar_structure'] = sidebar_structure
    tutorial_data['current_page'] = filename
    tutorial_data['selected_language'] = selected_language
    
    return render_template('index.html', **tutorial_data)

def process_zone_pivots(markdown_content, selected_language="nodejs"):
    """Process zone pivots to show only the first zone pivot in each section"""
    lines = markdown_content.split('\n')
    processed_lines = []
    in_zone = False
    zone_count = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check for zone pivot start
        if line_stripped.startswith('::: zone pivot='):
            zone_count += 1
            if zone_count == 1:
                # Keep the first zone pivot
                in_zone = True
                continue  # Skip the zone marker itself
            else:
                # Skip subsequent zone pivots
                in_zone = False
                continue
            
        # Check for zone end
        elif line_stripped == '::: zone-end':
            if zone_count == 1 and in_zone:
                in_zone = False
            continue
            
        # Include lines only if we're in the first zone or not in any zone
        if in_zone or zone_count == 0:
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

if __name__ == "__main__":
    app.run(debug=True)