from flask import Flask, request, render_template, jsonify
import speech_recognition as sr
import os
from pydub import AudioSegment
import logging

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    r = sr.Recognizer()
    text = ''
    try:
        if 'file' in request.files:  # Xử lý tệp âm thanh tải lên
            file = request.files['file']
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            logging.debug(f"Saving uploaded file: {file_path}")
            file.save(file_path)
            
            # Kiểm tra file có tồn tại và hợp lệ
            if not os.path.exists(file_path):
                raise Exception("Không thể lưu tệp âm thanh.")
            
            # Chuyển đổi định dạng sang WAV nếu không phải WAV
            logging.debug(f"Processing file: {file_path}")
            if not file.filename.lower().endswith('.wav'):
                audio = AudioSegment.from_file(file_path)
                file_path_wav = file_path.replace(os.path.splitext(file_path)[1], '.wav')
                logging.debug(f"Converting to WAV: {file_path_wav}")
                audio.export(file_path_wav, format='wav')
                file_path = file_path_wav
            
            with sr.AudioFile(file_path) as source:
                audio_data = r.record(source)
                logging.debug("Recognizing audio...")
                text = r.recognize_google(audio_data, language='vi-VN')
            
            # Xóa file tạm
            logging.debug(f"Removing temporary files: {file_path}")
            os.remove(file_path)
            if os.path.exists(file_path_wav):
                os.remove(file_path_wav)
        
        elif 'audio' in request.files:  # Xử lý ghi âm từ micro
            audio_blob = request.files['audio']
            file_path = os.path.join(UPLOAD_FOLDER, 'recording.webm')
            logging.debug(f"Saving recorded audio: {file_path}")
            audio_blob.save(file_path)
            
            # Kiểm tra file ghi âm
            if not os.path.exists(file_path):
                raise Exception("Không thể lưu file ghi âm.")
            
            # Chuyển webm sang wav
            audio = AudioSegment.from_file(file_path)
            file_path_wav = file_path.replace('.webm', '.wav')
            logging.debug(f"Converting to WAV: {file_path_wav}")
            audio.export(file_path_wav, format='wav')
            
            with sr.AudioFile(file_path_wav) as source:
                audio_data = r.record(source)
                logging.debug("Recognizing recorded audio...")
                text = r.recognize_google(audio_data, language='vi-VN')
            
            # Xóa file tạm
            logging.debug(f"Removing temporary files: {file_path}, {file_path_wav}")
            os.remove(file_path)
            os.remove(file_path_wav)
        
    except sr.UnknownValueError:
        logging.error("Speech recognition failed: Could not understand audio")
        text = 'Không thể nhận diện giọng nói. Vui lòng thử lại với âm thanh rõ ràng hơn.'
    except sr.RequestError as e:
        logging.error(f"Speech recognition service error: {e}")
        text = f'Lỗi kết nối dịch vụ Google Speech-to-Text: {e}'
    except Exception as e:
        logging.error(f"General error: {str(e)}")
        text = f'Lỗi: {str(e)}'
    
    return jsonify({'text': text})

if __name__ == '__main__':
    app.run(debug=True)