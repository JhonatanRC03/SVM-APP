import os
import random
import shutil
import time
import cv2
from moviepy.editor import VideoFileClip

# Rutas de las carpetas
POSES_VIDEOS_PATH = '/home/paula/Documentos/App/posesvideosxver'  # Carpeta con videos procesados
VIDEOS_XVER_PATH = 'videosxver'  # Carpeta para guardar clips de 30 segundos

# Crear la carpeta 'videosxver' si no existe
os.makedirs(VIDEOS_XVER_PATH, exist_ok=True)

def get_random_clip(source_path, dest_path, duration=3):
    # Cargar el video
    video_clip = VideoFileClip(source_path)
    video_duration = video_clip.duration
    
    if video_duration <= duration:
        print(f"El video {source_path} es demasiado corto para extraer un clip de {duration} segundos.")
        return
    
    # Seleccionar un tiempo aleatorio de inicio para el clip
    start_time = random.uniform(0, video_duration - duration)
    end_time = start_time + duration
    
    # Extraer el clip
    clip = video_clip.subclip(start_time, end_time)
    clip_filename = os.path.basename(source_path)
    clip_path = os.path.join(dest_path, clip_filename)
    
    # Guardar el clip en la carpeta de destino
    clip.write_videofile(clip_path, codec='libx264')
    print(f"Clip extraído y guardado: {clip_path}")

def process_videos():
    video_files = [f for f in os.listdir(POSES_VIDEOS_PATH) if f.endswith('.avi')]  # Ajusta al formato de video
    
    while True:
        if not video_files:
            print("No hay videos en la carpeta 'posesvideosxver'.")
            break
        
        # Seleccionar un video aleatorio
        video_file = random.choice(video_files)
        video_path = os.path.join(POSES_VIDEOS_PATH, video_file)
        
        # Obtener un clip de 30 segundos aleatorio
        get_random_clip(video_path, VIDEOS_XVER_PATH)
        
        # Esperar 60 segundos antes de procesar otro clip
        time.sleep(60)

if __name__ == "__main__":
    try:
        process_videos()
    except KeyboardInterrupt:
        print("Proceso detenido por el usuario.")
