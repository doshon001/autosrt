简单的python程序
为视频添加字幕和图片，效率并不算高，语音识别也不是很准确…… v_v

新建虚拟环境
python -m venv venv
启动虚拟环境
.\venv\Scripts\activate
启动flask
flask run --reload

https://jaist.dl.sourceforge.net/project/cmusphinx/Acoustic%20and%20Language%20Models/Mandarin/cmusphinx-zh-cn-5.2.tar.gz?viasf=1
下载放cmusphinx-zh-cn-5.2.tar.gz 解压后的每个文件放入.\venv\Lib\site-packages\speech_recognition\pocketsphinx-data\zh-CN 

https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
下载解压后，重命名为model放入程序所在目录的主目录