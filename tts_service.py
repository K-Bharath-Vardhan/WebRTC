
import os
from datetime import datetime
from gtts import gTTS  # pip install gTTS
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def find_most_recent_text_file(folder: str):
    txt_files = []
    for fn in os.listdir(folder):
        if fn.lower().endswith('.txt'):
            full_path = os.path.join(folder, fn)
            try:
                mtime = os.path.getmtime(full_path)
                txt_files.append((mtime, full_path))
            except OSError:
                pass
    if not txt_files:
        return None
    txt_files.sort(key=lambda x: x[0], reverse=True)
    return txt_files[0][1]


def synthesize_text_to_speech(text: str, base_name: str = "output") -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    out_name = secure_filename(f"tts_{timestamp}_{base_name}.mp3")
    out_path = os.path.join(UPLOAD_FOLDER, out_name)

    # Generate and save the speech
    tts = gTTS(text=text, lang='en')  # Change 'en' to desired language code
    tts.save(out_path)

    return out_path


def synthesize_latest_text_file():
    txt_path = find_most_recent_text_file(UPLOAD_FOLDER)
    if not txt_path:
        raise FileNotFoundError("No .txt files found in uploads/")

    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text.strip():
        raise ValueError("The text file is empty.")

    MAX_CHARS = 20000
    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + "."

    base = os.path.splitext(os.path.basename(txt_path))[0]

    return synthesize_text_to_speech(text, base_name=base)
