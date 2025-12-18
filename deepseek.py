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
from rewind.utils.providers import ProviderType

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
        filename (str): The name of the file to check.

    Returns:
        bool: True if extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def try_api(api_func, filepath, default_value, provider_type='deepseek'):
    """
    Safely call an API function with error handling and provider type injection.

    Args:
        api_func: The API function to call.
        filepath: Path to the JSON file.
        default_value: Return value on failure.
        provider_type: The AI provider (deepseek, qwen, etc.).

    Returns:
        The result of api_func or default_value on error.
    """
    try:
        # 尝试调用带有 provider_type 参数的函数
        return api_func(filepath, ProviderType(provider_type))
    except TypeError:
        try:
            return api_func(filepath)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning(
                "API error in %s (fallback): %s",
                api_func.__name__, str(exc)
            )
            return default_value
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("API error in %s: %s", api_func.__name__, str(exc))
        return default_value


@app.route('/')
def index():
    """
    Serve the main page.

    Returns:
        Rendered HTML template for the index page.
    """
    logger.info("GET / - Serving main page")
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload requests.
    Expects 'file' and 'provider_type' in FormData.

    Returns:
        JSON response with file path or error message.
    """
    logger.info("POST /api/upload - File upload request")

    if 'file' not in request.files:
        logger.warning("No file in request")
        return jsonify({'error': 'No file provided'}), 400

    uploaded_file = request.files['file']
    # 从 FormData 获取 provider_type，默认为 deepseek
    provider_type = request.form.get('provider_type', 'deepseek')

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
        # 构造文件名格式：时间戳___厂商类型___原始文件名
        # 这样可以在 /api/analyze 阶段从文件名中还原出厂商类型，而无需修改前端 analyzeData 逻辑
        filename = secure_filename(uploaded_file.filename)
        safe_provider = secure_filename(provider_type)
        timestamp = datetime.now().timestamp()

        # 使用三个下划线作为分隔符，降低文件名冲突概率
        saved_filename = f"{timestamp}___{safe_provider}___{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, saved_filename)

        uploaded_file.save(filepath)

        logger.info(
            "File saved: %s (%d bytes) [Provider: %s]",
            filepath, file_size, safe_provider
        )

        return jsonify({
            'message': 'File uploaded successfully',
            'filepath': filepath,
            'filename': filename,
            'provider_type': safe_provider
        }), 200

    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error("Upload error: %s", str(exc))
        return jsonify({'error': f'Upload failed: {str(exc)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze the uploaded chat record.
    Extracts provider_type from the filepath to determine analysis logic.

    Returns:
        JSON response containing analysis metrics.
    """
    logger.info("POST /api/analyze - Analysis request")

    data = request.get_json()
    filepath = data.get('filepath')

    if not filepath or not os.path.exists(filepath):
        logger.warning("Invalid filepath: %s", filepath)
        return jsonify({'error': 'Invalid file path'}), 400

    # 从文件名中解析 provider_type
    try:
        basename = os.path.basename(filepath)
        # 分割文件名：timestamp___provider___filename
        parts = basename.split('___')
        if len(parts) >= 3:
            provider_type = parts[1]
        else:
            provider_type = 'deepseek'  # 默认回退
    except Exception:  # pylint: disable=broad-exception-caught
        provider_type = 'deepseek'

    logger.info(
        "Starting analysis for: %s using provider: %s",
        filepath, provider_type
    )

    try:
        # Process the data with error handling
        # Pass provider_type to all try_api calls
        # 格式化字典以避免行过长
        result = {
            'most_used_models': try_api(
                most_used_models, filepath, [], provider_type
            ),
            'total_characters': try_api(
                total_characters, filepath, [], provider_type
            ),
            'most_used_language': try_api(
                most_used_language, filepath, [], provider_type
            ),
            'refuse_counts': try_api(
                refuse_counts, filepath, 0, provider_type
            ),
            'emoji_counts': try_api(
                emoji_counts, filepath, [], provider_type
            ),
            'polite_extent': try_api(
                polite_extent, filepath, [], provider_type
            ),
            'chat_days': try_api(
                chat_days, filepath, [], provider_type
            ),
            'per_hour_distribution': try_api(
                per_hour_distribution, filepath, {}, provider_type
            ),
            'time_limit': try_api(
                time_limit, filepath, [], provider_type
            ),
            'session_count': try_api(
                session_count, filepath, {'session_count': 0}, provider_type
            )
        }

        logger.info("Analysis completed successfully")
        return jsonify(result), 200

    except Exception as exc:  # pylint: disable=broad-exception-caught
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
    Serve static files from the frontend directory.

    Args:
        filename (str): Name of the file to serve.

    Returns:
        Response: File content.
    """
    return send_from_directory('frontend/static', filename)


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON status and timestamp.
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(_err):
    """
    Handle 404 errors.

    Args:
        _err: The error object (unused).

    Returns:
        JSON error message and 404 status.
    """
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(err):
    """
    Handle 500 errors.

    Args:
        err: The error object.

    Returns:
        JSON error message and 500 status.
    """
    logger.error("Server error: %s", str(err))
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Suppress Flask startup messages by disabling logging temporarily
    cli = logging.getLogger('werkzeug')
    cli.setLevel(logging.ERROR)

    print(
        "\033[1m\033[35m  Excellent!\033[0m Now you can access the page on "
        "\033[1m\033[34mhttp://127.0.0.1:5173\033[0m"
    )
    print("\033[32m  Enjoy! Press \033[1mCTRL+C\033[0m\033[32m to quit\033[0m")
    print()

    try:
        app.run(debug=False, host='0.0.0.0', port=5173, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\033[33m👋 Server stopped. Goodbye!\033[0m")
