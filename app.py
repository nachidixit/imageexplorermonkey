from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
CORS(app)

@app.route('/process_image', methods=['POST'])
def process_image():
    operation = request.form.get('operation')
    image_file = request.files.get('image')
    watermark_text = request.form.get('watermark_text')
    width = request.form.get('width')
    height = request.form.get('height')
    new_format = request.form.get('format')
    
    if not image_file:
        return jsonify({'error': 'No image uploaded'}), 400
    
    img = Image.open(image_file.stream)
    output = io.BytesIO()

    if operation == 'Compress Image':
        img.save(output, format="JPEG", optimize=True, quality=40)
    
    elif operation == 'Resize Image':
        img = img.resize((int(width), int(height)))
        img.save(output, format=img.format)
    
    elif operation == 'Convert Format':
        img.save(output, format=new_format.upper())
    
    elif operation == 'Add Watermark':
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 10), watermark_text, font=font, fill=(255, 255, 255))
        img.save(output, format=img.format)
    
    elif operation == 'Auto Rename File':
        # Just return success, handle renaming on client if needed
        img.save(output, format=img.format)

    output.seek(0)
    return send_file(output, mimetype='image/jpeg', as_attachment=True, download_name='processed_image.jpg')

if __name__ == '__main__':
    app.run(debug=True)
