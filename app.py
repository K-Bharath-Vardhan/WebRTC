from flask import Flask, send_from_directory, request, jsonify, render_template_string, abort, send_file
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from tts_service import synthesize_latest_text_file, UPLOAD_FOLDER  # 👈 import your service

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='.', template_folder='.')

@app.route('/')
def index():
    # Serve the index.html file located in the same folder.
    return send_from_directory('.', 'index.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio part"}), 400

    f = request.files['audio']
    if f.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # sanitize filename and add timestamp
    filename = secure_filename(f.filename)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    saved_name = f"{timestamp}_{filename}"
    saved_path = os.path.join(UPLOAD_FOLDER, saved_name)
    f.save(saved_path)

    return jsonify({"filename": saved_name}), 200

@app.route('/synthesize-latest', methods=['GET'])
def synthesize_latest():
    try:
        # Call your TTS helper (from tts_service import synthesize_latest_text_file)
        out_path = synthesize_latest_text_file()  # returns absolute or relative path to mp3
        # Ensure file exists
        if not os.path.isfile(out_path):
            app.logger.error("TTS output file not found: %s", out_path)
            return jsonify({"error": "TTS output not found"}), 500

        # Use send_file to stream the MP3 with proper mime type
        return send_file(out_path, mimetype='audio/mpeg', as_attachment=False)
    except FileNotFoundError as e:
        app.logger.error("TTS error: %s", e)
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        app.logger.error("TTS error: %s", e)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Log full exception for debugging (check Render logs)
        app.logger.exception("TTS generation failed")
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

@app.route('/save-transcript', methods=['POST'])
def save_transcript():
    if not request.is_json:
        return jsonify({"error": "Expected JSON"}), 400

    data = request.get_json()
    text = data.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Empty transcript"}), 400

    # filename optional; sanitize and default to "transcript"
    user_filename = data.get("filename", "transcript")
    safe_base = secure_filename(user_filename) or "transcript"
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    save_name = f"{timestamp}_{safe_base}.txt"
    save_path = os.path.join(UPLOAD_FOLDER, save_name)

    try:
        # Write UTF-8 text
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    return jsonify({"filename": save_name, "url": f"/uploads/{save_name}"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

