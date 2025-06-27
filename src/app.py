from flask import Flask, render_template, request, jsonify
import datetime
import datetime

app = Flask(__name__)

# Store slider states (in production, use a database)
slider_states = {}

@app.route("/")
def hello_world():
    return "Hello, World!"

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

@app.route("/get-slider-states")
def get_slider_states():
    """Get current slider states"""
    return jsonify(slider_states)

@app.route("/tutorial")
def tutorial():
    # Example data structure - you can modify this based on how you receive the data
    tutorial_data = {
        'title': 'Sample Tutorial - Getting Started Guide',
        'meta': '12/26/2024 • Applies to: Your Platform',
        'breadcrumbs': [
            {'name': 'Learn', 'url': '#'},
            {'name': 'Tutorials', 'url': '#'},
            {'name': 'Sample Tutorial - Getting Started Guide', 'url': None}
        ],
        'intro_paragraph': 'This is an introductory paragraph that explains what this tutorial covers. You can customize this content based on your specific needs.',
        'sections': [
            {
                'id': 'section-1',
                'title': 'Getting Started',
                'content': [
                    {'type': 'paragraph', 'text': 'This is the first section of your tutorial. You can include step-by-step instructions here.'},
                    {'type': 'list', 'elements': [
                        'First step in the process',
                        'Second step with more details',
                        'Third step to complete the setup'
                    ]},
                    {'type': 'paragraph', 'text': 'Additional explanatory text can go here to provide more context.'}
                ]
            },
            {
                'id': 'section-2', 
                'title': 'Advanced Configuration',
                'content': [
                    {'type': 'paragraph', 'text': 'This section covers more advanced topics and configurations.'},
                    {'type': 'note', 'text': 'This is an important note that users should pay attention to.'},
                    {'type': 'paragraph', 'text': 'More detailed instructions and explanations continue here.'}
                ]
            }
        ],
        'in_this_article': [
            {'title': 'Getting Started', 'anchor': '#section-1'},
            {'title': 'Advanced Configuration', 'anchor': '#section-2'}
        ]
    }
    
    return render_template('index.html', **tutorial_data)




if __name__ == "__main__":
    app.run()