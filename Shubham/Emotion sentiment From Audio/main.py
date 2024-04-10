import streamlit as st
from audio_recorder_streamlit import audio_recorder
from audiorecorder import audiorecorder


import pandas as pd
import numpy as np
from pathlib import Path
import librosa
import soundfile as sf
import torch
import time
import io
import glob
from collections import Counter
from collections import defaultdict
from utils import *


# Streamlit UI code
st.title('Speech Emotion Recognition')
st.markdown("<br>", unsafe_allow_html=True)

st.subheader("Record or Drop your audio file : \n")
st.markdown("<br>", unsafe_allow_html=True)

# Audio File recording 
# audio_file = audio_recorder(pause_threshold=120.0, sample_rate=16000)
audio_file = audiorecorder("Click to record", "Click to stop recording")

# if audio_file:
#     audio_wave = st.audio(audio_file, format="audio/wav")
if len(audio_file) > 0:
    # To play audio in frontend:
    st.audio(audio_file.export().read()) 

    # To save audio to a file, use pydub export method:
    audio_file.export("audio.wav", format="wav")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: justify;'> OR </p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Browsing for audio file
uploaded_file = st.file_uploader("Browse for Audio File",type=["wav","mp3","m4a"])

# Check if audio is available
if audio_file or uploaded_file:
    st.write("Audio is available.")
    # Enable submit button
    if st.button("Submit",use_container_width = True):
        # Processing the audio data here
        with st.spinner("Processing audio..."):
          # Geting audio file from recoding or uploaded file
          if len(audio_file) > 0 :
            final_audio_file = r"D:\Emotion sentiment From Audio\audio.wav"
          elif uploaded_file != None :
            file_path = uploaded_file.name
            with open(os.path.join("D:\Emotion sentiment From Audio\Files_uploaded_user", file_path), "wb") as f:
                f.write(uploaded_file.getbuffer())  # Save the file to the specified folder
            final_audio_file = os.path.join("D:\Emotion sentiment From Audio\Files_uploaded_user", file_path)


          # Extracting Text Data From Audio File
          audio_text = get_text_from_whisper_model(final_audio_file,pipe) 

          # Extracting probablities from text using Roberta-Base-emotion model
          roberta_output = get_emotion_from_text_with_roberta(roberta_classifier,audio_text)

          # Getting desired output from roberta 
          emotions_dict,emotion_label = get_output_desired_format_for_roberta(roberta_output)

          # Extracting Keywords responsible for target Emotion with Gemini
          r1 = get_keywords_for_emotion(audio_text)

        st.success(audio_text)
        st.success(roberta_output)
        st.success(r1)


