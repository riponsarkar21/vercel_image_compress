import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/compressed_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

progress = 0  # To track the progress

def compress_image(file, prefix, suffix, max_size_kb):
    global progress
    img = Image.open(file)
    filename, ext = os.path.splitext(file.filename)
    new_filename = f"{prefix}{filename}{suffix}{ext}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    
    quality = 95  # Start with high quality and adjust
    img.save(output_path, quality=quality)
    
    while os.path.getsize(output_path) > max_size_kb * 1024:
        quality -= 5
        img.save(output_path, quality=quality)
        if quality <= 5:  # Avoid too low quality
            break

    return new_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    global progress
    files = request.files.getlist('files')
    prefix = request.form.get('prefix', "")
    suffix = request.form.get('suffix', "")
    max_size_kb = int(request.form.get('max_size'))

    progress = 0
    total_files = len(files)

    compressed_files = []
    for file in files:
        filename = compress_image(file, prefix, suffix, max_size_kb)
        compressed_files.append(filename)
        progress += 1 / total_files * 100

    return jsonify({"files": compressed_files, "message": "Compression completed!"})

@app.route('/progress')
def get_progress():
    global progress
    return jsonify(progress=int(progress))

if __name__ == '__main__':
    app.run(debug=True, port=5002)
