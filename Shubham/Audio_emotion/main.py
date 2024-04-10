import streamlit as st
from audiorecorder import audiorecorder
import altair as alt

import pandas as pd
import numpy as np
from utils import *
import os


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
            final_audio_file = r"D:\Audio_emotion\audio.wav"
          elif uploaded_file != None :
            file_path = uploaded_file.name
            with open(os.path.join(r"D:\Audio_emotion\files_uploaded_by_user", file_path), "wb") as f:
              f.write(uploaded_file.getbuffer())  # Save the file to the specified folder
            final_audio_file = os.path.join(r"D:\Audio_emotion\files_uploaded_by_user", file_path)


          # Extracting Text Data From Audio File
          audio_text = get_text_from_whisper_model(final_audio_file) 

          # Extracting probablities from text using Roberta-Base-emotion model
          roberta_output = get_emotion_from_text_with_roberta(audio_text)

          # Getting desired output from roberta 
          emotions_dict,emotion_label = get_output_desired_format_for_roberta(roberta_output)

          # Extracting Keywords responsible for target Emotion with Gemini
          try :
            r1 = get_keywords_for_emotion(audio_text,emotion_label)
            keywords_lst = r1["Keywords for target emotion"]
            key_words = ""
            for i,word in enumerate(keywords_lst):
              if i==0:
                key_words = key_words +word
              else :
                key_words = key_words + ", " + word
          except :
             key_words = "Harmless words related to angry emotion not generated due to saftey reason."

        # Display all analysis on streamlit UI     
        col1, col2  = st.columns(2)

        with col1:
          st.success("Speech-Text : ")
          st.markdown("<br>", unsafe_allow_html=True)
          st.write(audio_text)

        with col2:
            st.success("Probability Distrubution for Emotion : ")
            df = pd.DataFrame.from_dict(emotions_dict, orient='index', columns=['Probability'])
            df = df.reset_index().rename(columns={"index":"Emotion"})
            df["Probability"] = df["Probability"].str.rstrip('%')
            df["Probability"] = df["Probability"].astype(float)
            c = (
              alt.Chart(df).mark_bar().encode(x = 'Emotion', y = 'Probability', color = 'Emotion')
            )
            st.altair_chart(c, use_container_width=True)

        st.success("Key-words responsible for target Emotion : ")
        st.write(key_words)

        


