import subprocess
import sys
import os
import json
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import detect_silence
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ImageClip
from moviepy.video.tools.subtitles import SubtitlesClip
from PIL import Image, ImageEnhance
from datetime import timedelta
import auditok

# --------------------------- 图片转透明 ---------------------------
def white_to_transparency(img_file, png_file):
    # img_file = os.path.join(img_path, img_name)
    # png_file = os.path.join(png_path, file_name) + '.png'
    print(img_file)
    img = Image.open(img_file)
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] > 180 and item[1] > 180 and item[2] > 180:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    enhancer = ImageEnhance.Color(img).enhance(1)
    enhancer.save(png_file)
    
    #image_path = 'your_image.png'
    #image = Image.open(image_path)
    #trans_image = white_to_transparency(image)
    #trans_image.save('transparent_image.png')

def get_img_name():
    img_names = [f for f in os.listdir(img_path) if os.path.isfile(os.path.join(img_path, f))]
    return img_names

def img2png():
    img_names = get_img_name()
    for img_name in img_names:
        print(img_name)
        file_name = img_name[:-4]
        white_to_transparency(img_name, file_name) 

def add_img():
    video_clip = VideoFileClip("your_video.mp4")
    image_clip = (ImageClip("your_image.png")
        .set_duration(video_clip.duration)
        .resize(newsize=(video_clip.w, video_clip.h)))

# --------------------------- 字幕 ---------------------------
def s_to_time(seconds):
    seconds = float(seconds)
    td = timedelta(seconds=seconds)
    hrs, remainder = divmod(td.seconds, 3600)
    mins, secs = divmod(remainder, 60)
    millisecs = int((td.microseconds / 1000) % 1000)
    time_format = f"{hrs:02d}:{mins:02d}:{secs:02d},{millisecs:03d}"
    return time_format
    #print(time_format)

def extract_audio(video_path, audio_path):
    video = AudioSegment.from_file(video_path, format="mp4")
    video.export(audio_path, format="wav")

def v2t(audio_path):
    r = sr.Recognizer()
    audioFile = sr.AudioFile(audio_path)
    with audioFile as source:
        audioData = r.record(source)
    type(audioData)
    c = r.recognize_vosk(audioData, language='zh-cn')
    #print(c)
    content = json.loads(c)
    text = content['text']
    return text
    
def get_video_name():
    video_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    return video_names

def generate_srt(record_path, srt_path, start_time, end_time):
    with open(record_path, 'r') as f:
        data = f.read()
    print(data)
    lines = data.split(', ')
    with open(srt_path, "a", encoding='utf-8') as srt_file:
        for i, line in enumerate(lines):
            srt_file.write(f"{i+1}\n")
            srt_file.write(f"{start_time}--> {end_time}\n")
            srt_file.write(f"{line.strip()}\n\n")

def audio_split(audio_path, record_path, srt_path, split_path):
    audio_events = auditok.split(
        audio_path, 
        min_dur=0.5, 
        max_dur=1.8, 
        max_slience=0.3, 
        energy_threshold=55
    )
    with open(srt_path, "w", encoding='utf-8') as srt_file:
        for i, r in enumerate(audio_events):
            dur = r.duration
            r_start = r.start
            r_end = r.end
            if(dur < 1):
                r_start = r.start - 0.5 
                r_end = r.end + 0.5
            start = f'{r_start:.3f}'
            end = f'{r_end:.3f}'
            start_time = s_to_time(start)
            end_time = s_to_time(end)
            print(start_time, end_time)
            file_p = os.path.join(split_path, "event_{start:.3f}-{end:.3f}.wav")
            filename = r.save(file_p)
            c = v2t(filename)
            if(c):
                srt_file.write(f"{i+1}\n")
                srt_file.write(f"{start_time} --> {end_time}\n")
                srt_file.write(f"{c}\n")
                srt_file.write(f"\n")
    subprocess.run(['notepad.exe', srt_path])

def add_subtitles(video_path, png_path, srt_path, output_path):
    video_clip = VideoFileClip(video_path)
    image_clip = ImageClip(png_path)
    width, height = video_clip.w, video_clip.h
    video_size = (height, width)
    video = video_clip.resize(video_size)

    p_height = width * 0.7
    p_width = height * 0.7
    image_size = (p_height, p_width)
    image = image_clip.resize(image_size).set_opacity(0.9).set_duration(video_clip.duration)
    generator = lambda txt: TextClip(txt, font='SimHei', fontsize=80, color='white')
    subtitles = SubtitlesClip(srt_path, generator).set_pos(('center', width * 0.8))
    result = CompositeVideoClip([video, image, subtitles])
    result.write_videofile(output_path, fps=video.fps)

def main():
    # --------------------------- 字幕 ---------------------------
    video_names = get_video_name()
    for video_name in video_names:
        file_name = video_name[:-4] 
        video_path = os.path.join(file_path, 'mp4/' + file_name + '.mp4')
        audio_path = os.path.join(file_path, 'wav/' + file_name + '.wav')
        srt_path = os.path.join(file_path, 'srt/' + file_name + '.srt')
        record_path = os.path.join(file_path, 'record/' + file_name + '.txt')
        output_path = os.path.join(file_path, 'output/' + file_name + '.mp4')
        # print(file_name)

        # extract_audio(video_path, audio_path)
        # audio_split(audio_path, record_path, srt_path)
        add_subtitles(video_path, srt_path, output_path)

    # --------------------------- 图片转透明 ---------------------------
    # img2png()

# if __name__ == '__main__':
    # global file_path, folder_path, img_path, png_path, split_path
    # file_path = os.path.dirname(os.path.abspath(__file__))
    # folder_path = os.path.join(file_path, 'mp4/')
    # img_path = os.path.join(file_path, 'img/')
    # png_path = os.path.join(file_path, 'png/')
    # split_path = os.path.join(file_path, 'splitwav/')

    # main()
  