import os
import torch
import numpy as np
import pickle
import shutil
from ultralytics import YOLO

# Cargar el modelo YOLO pose
model = YOLO('/home/paula/Documentos/App/yolov8s-pose.pt')

# Rutas de las carpetas
VIDEO_DB_PATH = 'original_videos'  # Carpeta de videos originales
POSES_VIDEOS_PATH = '/home/paula/Documentos/App/posesvideosxver'  # Carpeta para videos procesados con poses superpuestas
METADATA_PATH = 'metadatos'  # Carpeta para guardar los metadatos
RUNS_PATH = 'runs/pose'  # Carpeta donde YOLO guarda los videos procesados por defecto

# Crear las carpetas si no existen
os.makedirs(POSES_VIDEOS_PATH, exist_ok=True)
os.makedirs(METADATA_PATH, exist_ok=True)

# Función para mover los archivos .avi y .pkl generados a la carpeta 'posesvideosxver' y 'metadatos'
def move_files():
    for root, dirs, files in os.walk(RUNS_PATH):
        for file in files:
            if file.endswith('.avi'):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(POSES_VIDEOS_PATH, file)
                shutil.move(src_path, dest_path)
                print(f"Archivo de video movido: {src_path} -> {dest_path}")
            elif file.endswith('.pkl'):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(METADATA_PATH, file)
                shutil.move(src_path, dest_path)
                print(f"Archivo de metadatos movido: {src_path} -> {dest_path}")

# Función para procesar los videos de la base de datos
def process_videos():
    video_files = [f for f in os.listdir(VIDEO_DB_PATH) if f.endswith('.mp4')]  # Ajusta al formato de video

    for video_file in video_files:
        VIDEO_PATH = os.path.join(VIDEO_DB_PATH, video_file)
        lista_de_diccionarios = []

        # Obtener resultados de YOLO pose (video se guarda temporalmente en 'runs/pose/')
        results = model.predict(source=VIDEO_PATH, conf=0.2, save=True, stream=True, verbose=False)

        # Extraer metadatos
        for element in results:
            boxes = element.boxes.xywh.cpu().numpy().astype(np.float16)
            if element.boxes.id is not None:
                track_ids = element.boxes.id.int().cpu().tolist()
                if (element.keypoints.conf is not None) and (element.keypoints.xyn is not None):
                    conf = np.expand_dims(element.keypoints.conf.cpu().numpy(), axis=2)
                    coord = element.keypoints.xy.cpu().numpy()
                    mask = coord < 0.01
                    conf[mask[..., 0]] = 0
                    keypoint_and_scores = np.concatenate((coord, conf), axis=2)
                    mi_diccionario2 = {
                        'llave_id': {
                            'boxes': boxes,
                            'track_ids': track_ids,
                            'keypoint_and_scores': keypoint_and_scores
                        }
                    }
            else:
                mi_diccionario2 = {
                    'llave_id': {
                        'boxes': [],
                        'track_ids': [],
                        'keypoint_and_scores': []
                    }
                }

            lista_de_diccionarios.append(mi_diccionario2)

        # Guardar metadatos en la carpeta 'metadatos'
        pkl_filename = f"{os.path.splitext(video_file)[0]}.pkl"
        with open(os.path.join(RUNS_PATH, pkl_filename), 'wb') as f:
            pickle.dump(lista_de_diccionarios, f)

    # Mover los archivos .avi y .pkl generados a las carpetas correspondientes
    move_files()

if __name__ == "__main__":
    process_videos()
