import os
from static.py import yuyin
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
 
UPLOAD_VIDEO = './upload/video'
UPLOAD_AUDIO = './upload/audio'
UPLOAD_PIC = './upload/pic'
UPLOAD_PNG = './upload/png'
UPLOAD_SRT = './upload/srt'
UPLOAD_RECORD = './upload/record'
UPLOAD_SPLIT = './upload/split'
UPLOAD_OUTPUT = './upload/output'


app = Flask(__name__)

@app.route('/')
def index(name=None):
    return render_template('index.html', name=name)

@app.route('/api/upload/', methods=['POST'])
def upload_file():
    file = request.files['file']
    print(request.files)
    filename = secure_filename(file.filename)
    if filename.endswith('.mp4'):
        file.save(os.path.join(UPLOAD_VIDEO, filename))
    elif filename.endswith('.png') or filename.endswith('.jpg'):
        file.save(os.path.join(UPLOAD_PIC, filename))
    print('上传的文件为：', filename)
    data = {
        'filename': filename
    }
    return data

@app.route('/api/uploadVidDone/', methods=['POST'])
def upload_video_done():
    filename = request.values.get('filename')
    video_path = os.path.join(UPLOAD_VIDEO, filename)
    audio_path = os.path.join(UPLOAD_AUDIO, filename)
    record_path = os.path.join(UPLOAD_RECORD, filename)
    srt_path = os.path.join(UPLOAD_SRT, filename[:-4] + '.srt')
    split_path = UPLOAD_SPLIT
    yuyin.extract_audio(video_path, audio_path)
    yuyin.audio_split(audio_path, record_path, srt_path, split_path)
    print('操作', filename)
    data = {
        'data': 'data'
    }
    return data

@app.route('/api/uploadPicDone/', methods=['POST'])
def upload_pic_done():
    filename = request.values.get('filename')
    img_path = os.path.join(UPLOAD_PIC, filename)
    png_path = os.path.join(UPLOAD_PNG, filename[:-4] + '.png')
    yuyin.white_to_transparency(img_path, png_path)
    print('操作', filename)
    data = {
        'data': 'data'
    }
    return data

@app.route('/api/outputVideo/', methods=['POST'])
def output_video():
    video_name = request.values.get('video_name')
    png_name = request.values.get('png_name')
    video_path = os.path.join(UPLOAD_VIDEO, video_name)
    srt_path = os.path.join(UPLOAD_SRT, video_name[:-4] + '.srt')
    png_path = os.path.join(UPLOAD_PNG, png_name[:-4] + '.png')
    output_path = os.path.join(UPLOAD_OUTPUT, video_name)
    yuyin.add_subtitles(video_path, png_path, srt_path, output_path)
    print('操作', video_name)
    data = {
        'data': 'data'
    }
    return data

@app.route('/api/clearDone/', methods=['POST'])
def clear_done():
    folders = [UPLOAD_VIDEO, UPLOAD_AUDIO, UPLOAD_PIC, UPLOAD_PNG, UPLOAD_SRT, UPLOAD_RECORD, UPLOAD_SPLIT]
    for folder_path in folders:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    print('操作完成')
    data = {
        'data': 'data'
    }
    return data

if __name__ == '__main__':
    app.run(debug=True)