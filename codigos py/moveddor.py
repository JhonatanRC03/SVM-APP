import os
import shutil
import random
import json
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Rutas de carpetas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOSXVER_DIR = os.path.join(BASE_DIR, 'videosxver')
REGISTROS_DIR = os.path.join(BASE_DIR, 'registros')
REGISTROS_VIDEOS_DIR = os.path.join(REGISTROS_DIR, 'videos')
REGISTROS_METADATOS_DIR = os.path.join(REGISTROS_DIR, 'metadatos')

# Crear carpetas si no existen
os.makedirs(VIDEOSXVER_DIR, exist_ok=True)
os.makedirs(REGISTROS_VIDEOS_DIR, exist_ok=True)
os.makedirs(REGISTROS_METADATOS_DIR, exist_ok=True)

# Guardar un video en la carpeta videosxver
def save_video_to_videosxver(file_name, video_data):
    random_number = random.randint(100000, 999999)
    new_file_name = f'videoxver_{random_number}_{file_name}'
    file_path = os.path.join(VIDEOSXVER_DIR, new_file_name)
    with open(file_path, 'wb') as f:
        f.write(video_data)
    return new_file_name

# Mover un video de videosxver a registros
def move_video_to_registros(file_name, metadata):
    random_number = random.randint(100000, 999999)
    new_file_name = f'registro_{random_number}_{file_name}'
    source = os.path.join(VIDEOSXVER_DIR, file_name)
    destination_video = os.path.join(REGISTROS_VIDEOS_DIR, new_file_name)
    
    # Mover archivo
    shutil.move(source, destination_video)
    
    # Guardar metadatos
    metadata_path = os.path.join(REGISTROS_METADATOS_DIR, f'{new_file_name}.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

    return new_file_name

@app.route('/upload', methods=['POST'])
def upload_video():
    file = request.files['file']
    file_name = file.filename
    video_data = file.read()
    
    new_file_name = save_video_to_videosxver(file_name, video_data)
    return jsonify({'status': 'success', 'file_name': new_file_name})

@app.route('/validate', methods=['POST'])
def validate_video():
    data = request.json
    file_name = data['file_name']
    metadata = data['metadata']
    
    new_file_name = move_video_to_registros(file_name, metadata)
    return jsonify({'status': 'success', 'new_file_name': new_file_name})

@app.route('/videosxver', methods=['GET'])
def get_videosxver():
    videos = os.listdir(VIDEOSXVER_DIR)
    return jsonify(videos)

@app.route('/registros', methods=['GET'])
def get_registros():
    registros_videos = os.listdir(REGISTROS_VIDEOS_DIR)
    return jsonify(registros_videos)

# Para descargar videos
@app.route('/download/<folder>/<file_name>', methods=['GET'])
def download_video(folder, file_name):
    if folder == 'videosxver':
        directory = VIDEOSXVER_DIR
    elif folder == 'registros':
        directory = REGISTROS_VIDEOS_DIR
    else:
        return jsonify({'error': 'Invalid folder'}), 400

    return send_from_directory(directory, file_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
