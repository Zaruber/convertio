import os
import time
from datetime import datetime
from flask import Flask, render_template, request, send_file, url_for, jsonify
import ffmpeg
import humanize
from werkzeug.utils import secure_filename
from tqdm import tqdm

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max file size

# Поддерживаемые форматы
SUPPORTED_FORMATS = {
    'video': {
        'input': ['.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mp4'],
        'output': ['.mp4', '.mkv', '.avi', '.mov']
    },
    'audio': {
        'input': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
        'output': ['.mp3', '.wav', '.ogg', '.m4a']
    }
}

# Создаем папку для загрузок, если она не существует
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_file_info(file_path):
    """Получение информации о файле"""
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Определяем тип файла по расширению
    file_type = 'Неизвестный'
    for media_type, formats in SUPPORTED_FORMATS.items():
        if file_ext in formats['input']:
            file_type = f"{media_type.capitalize()}-файл ({file_ext})"
            break
    
    return {
        'size': humanize.naturalsize(file_size),
        'type': file_type
    }

def get_duration(file_path):
    """Получение длительности медиафайла"""
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe['streams'][0]['duration'])
        return duration
    except:
        return None

def convert_media(input_path, output_path, progress_callback=None):
    """Конвертация медиафайла с отслеживанием прогресса"""
    try:
        # Получаем информацию о длительности
        duration = get_duration(input_path)
        start_time = time.time()
        
        # Настраиваем параметры конвертации
        stream = ffmpeg.input(input_path)
        
        # Определяем тип выходного файла
        output_ext = os.path.splitext(output_path)[1].lower()
        
        # Настраиваем кодеки в зависимости от формата
        if output_ext == '.mp4':
            stream = ffmpeg.output(stream, output_path, acodec='aac', vcodec='h264')
        elif output_ext == '.mkv':
            stream = ffmpeg.output(stream, output_path, acodec='libvorbis', vcodec='libx264')
        elif output_ext in ['.mp3', '.m4a']:
            stream = ffmpeg.output(stream, output_path, acodec='libmp3lame')
        else:
            stream = ffmpeg.output(stream, output_path)
        
        # Запускаем конвертацию
        process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)
        
        # Отслеживаем прогресс
        while process.poll() is None:
            if duration:
                elapsed_time = time.time() - start_time
                progress = min(100, (elapsed_time / duration) * 100)
                if progress_callback:
                    progress_callback(progress)
            time.sleep(0.1)
        
        return True
    except ffmpeg.Error as e:
        print('Error:', e.stderr.decode() if e.stderr else str(e))
        return False

@app.route('/formats', methods=['GET'])
def get_formats():
    """API endpoint для получения поддерживаемых форматов"""
    return jsonify(SUPPORTED_FORMATS)

@app.route('/convert', methods=['POST'])
def convert():
    """API endpoint для конвертации файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400
    
    file = request.files['file']
    output_format = request.form.get('output_format')
    
    if not file or file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if not output_format:
        return jsonify({'error': 'Формат конвертации не указан'}), 400
    
    input_ext = os.path.splitext(file.filename)[1].lower()
    
    # Проверяем поддерживаемые форматы
    supported_input = False
    for formats in SUPPORTED_FORMATS.values():
        if input_ext in formats['input']:
            supported_input = True
            if output_format not in formats['output']:
                return jsonify({'error': f'Неподдерживаемый формат конвертации {output_format} для входного формата {input_ext}'}), 400
    
    if not supported_input:
        return jsonify({'error': f'Неподдерживаемый входной формат {input_ext}'}), 400
    
    try:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = os.path.splitext(filename)[0] + output_format
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        # Сохраняем входной файл
        file.save(input_path)
        
        # Получаем информацию о файле
        file_info = get_file_info(input_path)
        
        # Конвертируем файл
        if convert_media(input_path, output_path):
            # Получаем информацию о выходном файле
            output_info = get_file_info(output_path)
            
            # Удаляем входной файл
            os.remove(input_path)
            
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_filename
            )
        else:
            if os.path.exists(input_path):
                os.remove(input_path)
            return jsonify({'error': 'Ошибка конвертации'}), 500
            
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', formats=SUPPORTED_FORMATS)

if __name__ == '__main__':
    app.run(debug=True)
