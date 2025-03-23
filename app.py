from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image, ImageOps, ImageDraw, ImageFont
import io
import os
import zipfile

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "ImageExplorerMonkey Backend is Running!"

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    operation = request.form.get('operation')
    watermark_text = request.form.get('watermark_text', '')

    try:
        img = Image.open(image_file.stream)

        if operation == 'resize':
            img = img.resize((500, 500))
        elif operation == 'grayscale':
            img = ImageOps.grayscale(img)
        elif operation == 'rotate':
            img = img.rotate(90)
        elif operation == 'watermark' and watermark_text:
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            draw.text((10, 10), watermark_text, fill='red', font=font)

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        return send_file(img_bytes, download_name=f'processed_{os.path.splitext(image_file.filename)[0]}.png', as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/batch_download_process', methods=['POST'])
def batch_download_process():
    files = request.files.getlist('images')
    operation = request.form.get('operation')
    watermark_text = request.form.get('watermark_text', '')

    if not files:
        return jsonify({'error': 'No images provided for batch processing.'}), 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image_file in files:
            img = Image.open(image_file.stream)

            if operation == 'resize':
                img = img.resize((500, 500))
            elif operation == 'grayscale':
                img = ImageOps.grayscale(img)
            elif operation == 'rotate':
                img = img.rotate(90)
            elif operation == 'watermark' and watermark_text:
                draw = ImageDraw.Draw(img)
                font = ImageFont.load_default()
                draw.text((10, 10), watermark_text, fill='red', font=font)

            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            zip_file.writestr(f'processed_{os.path.splitext(image_file.filename)[0]}.png', img_bytes.read())

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='processed_images_batch.zip')

if __name__ == '__main__':
    app.run(debug=True, port=5000)