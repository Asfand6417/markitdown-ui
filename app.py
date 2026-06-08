import os
from flask import Flask, render_template, request, send_file, jsonify
from markitdown import MarkItDown
from pathlib import Path
import io

# Get the absolute path to the app directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

# Create necessary folders
os.makedirs(TEMPLATE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize MarkItDown
md = MarkItDown()

@app.route('/')
def index():
    template_path = os.path.join(TEMPLATE_DIR, 'index.html')
    print(f"Looking for template at: {template_path}")
    print(f"Template exists: {os.path.exists(template_path)}")
    print(f"Template readable: {os.access(template_path, os.R_OK)}")
    
    if not os.path.exists(template_path):
        return f"Template not found at {template_path}", 500
    
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}\n\nTemplate path: {template_path}", 500

@app.route('/test')
def test():
    return jsonify({
        'status': 'Flask is working!',
        'template_dir': TEMPLATE_DIR,
        'template_exists': os.path.exists(os.path.join(TEMPLATE_DIR, 'index.html'))
    })

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file temporarily
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        try:
            # Convert using markitdown
            result = md.convert(filepath)
            
            # Get the markdown text content
            markdown_content = result.text_content
            
            # Generate markdown filename
            base_name = Path(file.filename).stem
            md_filename = f"{base_name}.md"
            
            # Return as downloadable file
            md_content = io.BytesIO(markdown_content.encode('utf-8'))
            
            return send_file(
                md_content,
                mimetype='text/markdown',
                as_attachment=True,
                download_name=md_filename
            )
        
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"Template folder: {TEMPLATE_DIR}")
    print(f"Upload folder: {UPLOAD_DIR}")
    print(f"Template file exists: {os.path.exists(os.path.join(TEMPLATE_DIR, 'index.html'))}")
    app.run(debug=True, host='localhost', port=5000)
