import pyaudio
import wave
import whisper
import streamlit as st
from googletrans import Translator
 
Format = pyaudio.paInt16
Channels = 1
Rate = 44100
FramesPerBuffer = 1024
 
FILE_Path = r"D:\GitHub\sitp-bronze96\code\Record1.wav"
 
def getAudio(filePath,sec):
    """ 从麦克风录制音频并保存到指定文件路径 """
    p = pyaudio.PyAudio()
    stream = p.open(format=Format, channels=Channels, rate=Rate, input=True, frames_per_buffer=FramesPerBuffer)
    wf=wave.open(FILE_Path,"wb")
    wf.setnchannels(Channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(Rate)
    print("Recording...")
    for w in range(int(Rate*sec/FramesPerBuffer)):
        data = stream.read(FramesPerBuffer)
        wf.writeframes(data)
    print("Done Recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()
 
 
def AudioToText(audioPath):
    """ 将音频文件转换为文本并进行翻译 """
    model = whisper.load_model("turbo")
 
    audio = whisper.load_audio(audioPath)
    audio = whisper.pad_or_trim(audio)
 
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
 
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
 
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    print(result.text)
 
    translator = Translator()
    translatedText = translator.translate(result.text, src='zh-CN', dest='en')
    print(f"Translated text: {translatedText.text}")
    return result.text,translatedText.text
 
def AudioWeb():
    """ 用户界面：录音并识别音频内容 """
    recordTime = st.number_input(label='请输入录音时间(1-20秒)',
    min_value=1,
    max_value=20,
    value=5,
    step=1
    )
    if st.button("录音",key='recordAudioButton'):
        recordingStatus = st.empty()
        recognitionStatus = st.empty()
        print("开始录音")
        recordingStatus.write("开始录音")
        getAudio(FILE_Path,recordTime)
        recognitionStatus.write("录音结束,开始识别")
        audioText,translatedText = AudioToText(FILE_Path)
        recordingStatus.empty()
        recognitionStatus.empty()
        st.write("识别结果为:")
        st.text(audioText)
       
        print("识别结束")
        return translatedText
#AudioToText(FILE_Path)