import streamlit as st
from audiorecorder import audiorecorder
import pandas as pd
import numpy as np
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor
import os
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

# Loading model from local 
wav2vec2_model_path = Path(r"D:\Emotion sentiment From Audio\wav2vec2-base-superb-er")
wav2vec2_model = Wav2Vec2ForSequenceClassification.from_pretrained(wav2vec2_model_path)
wav2vec2_feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(wav2vec2_model_path)

labels = wav2vec2_model.config.id2label
# {0: 'neu', 1: 'hap', 2: 'ang', 3: 'sad'}

# Function For extracting probabilities from wav2vec2 model
def get_prob_from_wav2vec2_model(audio_path,feature_extractor,model):
  speech, _ = librosa.load(audio_path, sr=16000, mono=True)
  # compute attention masks and normalize the waveform if needed
  inputs = feature_extractor(speech, sampling_rate=16000, padding=True, return_tensors="pt")

  logits = model(**inputs).logits
  # Below Lines return emotion label predicted by wav2vec2 model
  predicted_ids = torch.argmax(logits, dim=-1)
  labels = [model.config.id2label[_id] for _id in predicted_ids.tolist()]
  
  # We are going to return probability values for each label class
  probabilities = torch.nn.functional.softmax(logits, dim=-1)
  r1 = probabilities.detach().numpy().reshape(-1) # Returning Wav2vec2 prob

  return r1

# test_file = Path(r"D:\Emotion sentiment From Audio\Ses05M_impro03_M012_Happy.wav")
# emotion_label = get_emotion_from_wav2vec2_model(test_file,feature_extractor,model)
# print(emotion_label)

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
          
          # Chunking Audio File into chunks and passing chunks to further process
          y, sr = librosa.load(final_audio_file)

          chunk_duration = 30  # Adjust duration as needed (in seconds)
          
          num_chunks = int(np.ceil(len(y) / (sr * chunk_duration)))

          chunks = np.array_split(y, num_chunks)

          trimmed_chunks = []
          for chunk in chunks:
            trimmed_chunk, _ = librosa.effects.trim(chunk, top_db=30)  # Adjust threshold as needed
            trimmed_chunks.append(trimmed_chunk)
          
          # Saving All chunks 
          for i, chunk in enumerate(trimmed_chunks):
            filename = f"chunk_{i}.wav"
            # Write out audio as 24bit PCM WAV
            sf.write(filename, chunk, sr)
          
          # Code For passing each chunk to model 
          # Actual model processing (replace with your model's API) --> Here we will get Probabilities from wav2vec2 model 
          chunks_directory = Path("D:\Emotion sentiment From Audio")
          wav_files = glob.glob(f"{chunks_directory}/*.wav")
#           wav2vec2_prob = get_prob_from_wav2vec2_model(final_audio_file,wav2vec2_feature_extractor,wav2vec2_model)
#           print(wav2vec2_prob)

#           try:
#             # Extracting text from Audio File
#             audio_text = get_text_from_whisper_model(audio_file,pipe) #audio_file
#           except: 
#             audio_text = get_text_from_whisper_model(final_audio_file,pipe) 

#           # Extracting probablities from text using Roberta-Base-emotion model
#           roberta_output = get_emotion_from_text_with_roberta(roberta_classifier,audio_text)
         
#           for i in roberta_output[0]:
#             if i["label"] == "anger": 
#                 i["label"] = "ang"
#             elif i["label"] == "disgust":
#                 i["label"] = "sad"
#             elif i["label"] == "fear": 
#                 i["label"] = "sad"
#             elif i["label"] == "joy":
#                 i["label"] = "hap"
#             elif i["label"] == "neutral":
#                 i["label"] = "neu"  
#             elif i["label"] == "sadness":
#                 i["label"] = "sad"
#             elif i["label"] == "surprise":
#                 i["label"] = "hap"

#           # Use a defaultdict to accumulate scores for each label
#           label_scores = defaultdict(float)

#           for item in roberta_output[0]:
#             label_scores[item['label']] += item['score']

#           # Create a new list with the updated scores
#           updated_roberta_output = [{'label': label, 'score': score} for label, score in label_scores.items()]

#           # Defined the desired order of labels
#           desired_order = ['neu', 'hap', 'ang', 'sad']

#           # Rearrange the list using a custom key function
#           arranged_updated_roberta_output = sorted(updated_roberta_output, key=lambda item: desired_order.index(item['label']))
          
#           roberta_prob = []
#           for i in arranged_updated_roberta_output:
#             roberta_prob.append(i["score"])
          
#           print(roberta_prob)
#           # Adding two prob list from wav2vec2 (Tone Based emotion) & Roberta Model (Text/Langauge based emotion)
#           list_sum = np.add(wav2vec2_prob, roberta_prob)

#           # Normalize the sum
#           result = list_sum / np.sum(list_sum)
#           result = np.array(result)
#           print(result)
#           emotion = labels[np.argmax(result)]
        
#           if emotion == "hap":
#               final_emotion = "Happy 😄"
#           elif emotion == "sad":
#               final_emotion = "Sad 😔"
#           elif emotion == "ang":
#               final_emotion = "Angry 😠"
#           elif emotion == "neu":
#               final_emotion = "Neutral 😑"

#         # Clear progress bar and display output
#         st.success("Model processing complete!")

#         # Display Model Final Emotion & Speech-Text
#         st.write(f"Speech-Text :{audio_text}")
#         st.markdown("<br>", unsafe_allow_html=True)
#         st.markdown(f"<h4 style='text-align: center;'> Emotion for given Audio is {final_emotion} </h4>", unsafe_allow_html=True)
# else:
#     st.write("Please record or upload an audio file.")
          chunks_text = []
          chunks_extracted_emotions = []

          # Extracting Emotions From Entire Text
          audio_text = get_text_from_whisper_model(final_audio_file,pipe) 
          chunks_text.append(audio_text)

          # Extracting probablities from text using Roberta-Base-emotion model
          roberta_output_full_audio = get_emotion_from_text_with_roberta(roberta_classifier,audio_text)
          
          # Getting desired output from roberta 
          fa_emotion_dict,fa_emotion_label = get_output_desired_format_for_roberta(roberta_output_full_audio)

          for file in wav_files:
            # wav2vec2_prob = get_prob_from_wav2vec2_model(file,wav2vec2_feature_extractor,wav2vec2_model)
            # print("Wav2vec2 Probability : ",wav2vec2_prob)
            
            # Extracting text From Audio
            audio_text = get_text_from_whisper_model(file,pipe) 
            chunks_text.append(audio_text)

            # Extracting probablities from text using Roberta-Base-emotion model
            chunk_roberta_output = get_emotion_from_text_with_roberta(roberta_classifier,audio_text)

            chunk_emotion_dict,chunk_emotion_label = get_output_desired_format_for_roberta(chunk_roberta_output)

            chunks_extracted_emotions.append(chunk_emotion_label)

            # Display Model Final Emotion & Speech-Text
            cnt = 1
            st.markdown("<br>", unsafe_allow_html=True)
            st.write(f"Speech-Text chunk {cnt} :{audio_text}")
            st.write(f"Emotions :",chunk_emotion_dict)

            cnt += 1
            
            counts = Counter(chunks_extracted_emotions)
            most_frequent_item, count = counts.most_common(1)[0]
            
            print(most_frequent_item)
          
          st.markdown("<br>", unsafe_allow_html=True)
          st.markdown(f"<h4 style='text-align: center;'> Emotion for given Audio is {fa_emotion_dict} and {fa_emotion_label} </h4>", unsafe_allow_html=True)            
