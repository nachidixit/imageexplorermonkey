
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from PIL import Image, ImageOps
import io
import os
import zipfile
import shutil

app = Flask(__name__)
CORS(app)

PROCESSED_FOLDER = 'processed_images'
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    operation = request.form.get('operation')

    try:
        image = Image.open(image_file.stream)
        processed_image = image

        if operation == 'resize':
            processed_image = image.resize((100, 100))
        elif operation == 'grayscale':
            processed_image = ImageOps.grayscale(image)
        elif operation == 'rotate':
            processed_image = image.rotate(90)

        filename = image_file.filename
        output_path = os.path.join(PROCESSED_FOLDER, filename)
        processed_image.save(output_path)

        return jsonify({'message': 'Image processed successfully', 'filename': filename}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_download_process', methods=['GET'])
def batch_download_process():
    zip_filename = 'processed_images.zip'
    zip_path = os.path.join(PROCESSED_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(PROCESSED_FOLDER):
            for file in files:
                if file != zip_filename:
                    zipf.write(os.path.join(root, file), arcname=file)

    return send_file(zip_path, as_attachment=True)

@app.route('/processed_images/<filename>', methods=['GET'])
def download_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
