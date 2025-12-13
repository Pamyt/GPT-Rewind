"""
DeepSeek Chat Record Annual Summary Tool.

This module provides Flask API endpoints for processing DeepSeek chat records,
handling file uploads, and generating analysis reports.
"""

import os
import logging
import tempfile
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import API functions
# pylint: disable=import-error
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
except ImportError as import_err:
    logger.warning("⚠ Some API modules failed to load: %s", import_err)

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
    """
    Check if the file extension is allowed.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def try_api(api_func, filepath, default_value):
    """
    Safely call an API function with error handling.

    Args:
        api_func (callable): The API function to call.
        filepath (str): The path to the file to process.
        default_value (any): The value to return in case of error.

    Returns:
        any: The result of the API call or the default value.
    """
    try:
        return api_func(filepath)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("API error in %s: %s", api_func.__name__, str(exc))
        return default_value


@app.route('/')
def index():
    """
    Serve the main page.

    Returns:
        str: Rendered HTML template.
    """
    logger.info("GET / - Serving main page")
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload requests.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    logger.info("POST /api/upload - File upload request")

    if 'file' not in request.files:
        logger.warning("No file in request")
        return jsonify({'error': 'No file provided'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        logger.warning("Empty filename")
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(uploaded_file.filename):
        logger.warning("Invalid file type: %s", uploaded_file.filename)
        return jsonify({'error': 'Only JSON files are supported'}), 400

    try:
        # Validate file size before saving
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)

        if file_size > MAX_FILE_SIZE:
            logger.warning("File too large: %d bytes", file_size)
            return jsonify({
                'error': f'File too large (max {MAX_FILE_SIZE} bytes)'
            }), 400

        # Save file temporarily
        filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.now().timestamp()
        filepath = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
        uploaded_file.save(filepath)

        logger.info("File saved: %s (%d bytes)", filepath, file_size)

        return jsonify({
            'message': 'File uploaded successfully',
            'filepath': filepath,
            'filename': filename
        }), 200

    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Upload error: %s", str(exc))
        return jsonify({'error': f'Upload failed: {str(exc)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze the uploaded chat record.

    Returns:
        tuple: JSON response and HTTP status code.
    """
    logger.info("POST /api/analyze - Analysis request")

    data = request.get_json()
    filepath = data.get('filepath')

    if not filepath or not os.path.exists(filepath):
        logger.warning("Invalid filepath: %s", filepath)
        return jsonify({'error': 'Invalid file path'}), 400

    try:
        logger.info("Starting analysis for: %s", filepath)

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

    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Analysis error: %s", str(exc))
        return jsonify({'error': f'Analysis failed: {str(exc)}'}), 500
    finally:
        # Clean up uploaded file
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info("Cleaned up: %s", filepath)
        except OSError as exc:
            logger.warning("Failed to cleanup: %s", exc)


@app.route('/api/static/<path:filename>')
def serve_static(filename):
    """
    Serve static files.

    Args:
        filename (str): The path of the file to serve.

    Returns:
        Response: The file response.
    """
    return send_from_directory('frontend/static', filename)


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        tuple: JSON status and HTTP status code.
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(err):  # pylint: disable=unused-argument
    """
    Handle 404 errors.

    Args:
        err: The error object.

    Returns:
        tuple: JSON error message and 404 status code.
    """
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(err):
    """
    Handle 500 errors.

    Args:
        err: The error object.

    Returns:
        tuple: JSON error message and 500 status code.
    """
    logger.error("Server error: %s", str(err))
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting DeepSeek Annual Summary Server")
    logger.info("=" * 60)
    logger.info("Server URL: http://localhost:5173")
    logger.info("Upload folder: %s", UPLOAD_FOLDER)
    logger.info("Press Ctrl+C to stop the server")
    logger.info("=" * 60)

    try:
        app.run(debug=True, host='0.0.0.0', port=5173, use_reloader=False)
    except KeyboardInterrupt:
        logger.info("\nServer stopped")
