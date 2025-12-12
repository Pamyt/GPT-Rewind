"""
DeepSeek Chat Record Annual Summary Tool
This module provides Flask API endpoints for processing DeepSeek chat records
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import os
from pathlib import Path
import tempfile
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import API functions
try:
    from rewind.apis.base_api import (
        most_used_models,
        total_characters,
        most_used_language,
        session_count,
        refuse_counts
    )
    from rewind.apis.style_api import (
        emoji_counts,
        polite_extent
    )
    from rewind.apis.time_api import (
        chat_days,
        per_hour_distribution,
        time_limit,
    )
    logger.info("✓ All API modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠ Some API modules failed to load: {e}")

# Create Flask app
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'json'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the main page"""
    logger.info("GET / - Serving main page")
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    logger.info("POST /api/upload - File upload request")
    
    if 'file' not in request.files:
        logger.warning("No file in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("Empty filename")
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        logger.warning(f"Invalid file type: {file.filename}")
        return jsonify({'error': 'Only JSON files are supported'}), 400
    
    try:
        # Validate file size before saving
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes")
            return jsonify({'error': f'File too large (max {MAX_FILE_SIZE} bytes)'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.now().timestamp()}_{filename}")
        file.save(filepath)
        
        logger.info(f"File saved: {filepath} ({file_size} bytes)")
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filepath': filepath,
            'filename': filename
        }), 200
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze the uploaded chat record"""
    logger.info("POST /api/analyze - Analysis request")
    
    data = request.get_json()
    filepath = data.get('filepath')
    
    if not filepath or not os.path.exists(filepath):
        logger.warning(f"Invalid filepath: {filepath}")
        return jsonify({'error': 'Invalid file path'}), 400
    
    try:
        logger.info(f"Starting analysis for: {filepath}")
        
        # Process the data with error handling
        result = {
            'most_used_models': try_api(most_used_models, filepath, []),
            'total_characters': try_api(total_characters, filepath, []),
            'most_used_language': try_api(most_used_language, filepath, []),
            'refuse_counts': try_api(refuse_counts, filepath, 0),
            'emoji_counts': try_api(emoji_counts, filepath, []),
            'polite_extent': try_api(polite_extent, filepath, []),
            'chat_days': try_api(chat_days, filepath, []),
            'per_hour_distribution': try_api(per_hour_distribution, filepath, {}),
            'time_limit': try_api(time_limit, filepath, []),
            'session_count': try_api(session_count, filepath, {'session_count': 0})
        }
        
        logger.info("Analysis completed successfully")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    finally:
        # Clean up uploaded file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Cleaned up: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to cleanup: {e}")


def try_api(api_func, filepath, default_value):
    """Safely call API function with error handling"""
    try:
        return api_func(filepath)
    except Exception as e:
        logger.warning(f"API error in {api_func.__name__}: {str(e)}")
        return default_value


@app.route('/api/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('frontend/static', filename)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Starting DeepSeek Annual Summary Server")
    logger.info("="*60)
    logger.info(f"Server URL: http://localhost:5173")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info("Press Ctrl+C to stop the server")
    logger.info("="*60)
    
    try:
            app.run(debug=True, host='0.0.0.0', port=5173, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("\nServer stopped")

