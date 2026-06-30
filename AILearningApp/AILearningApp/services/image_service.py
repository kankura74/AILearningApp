import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def save_icon(file):

    if file.filename == "":
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return None

    new_filename = f"{uuid.uuid4()}.{ext}"

    upload_dir = os.path.join(current_app.root_path, "static", "uploads")

    os.makedirs(upload_dir, exist_ok=True)

    path = os.path.join(upload_dir, new_filename)

    file.save(path)

    print("UPLOAD PATH:", upload_dir)
    print("FILE PATH:", path)

    return new_filename