from flask import Flask, send_from_directory, request, jsonify, render_template_string
import os
from datetime import datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='.', template_folder='.')

@app.route('/')
def index():
    # Serve the index.html file located in the same folder.
    return send_from_directory('.', 'index.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    """
    Receives a multipart/form-data upload with the 'audio' file field,
    saves it to uploads/ and returns JSON with saved filename.
    """
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

if __name__ == '__main__':
    # Run development server. Visit http://127.0.0.1:5000
    app.run(debug=True)