import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from collections import defaultdict
import numpy as np
import os
from dotenv import load_dotenv

import google.generativeai as genai

from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Getting Gemini API Key From Environment
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

# Function For ASR Model
def get_text_from_whisper_model(audio_file): 
  #Loading distil-whisperdistil-medium.en model from local

  torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

  model_path = r"D:\Audio_emotion\distil-whisperdistil-medium.en"

  model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_path, torch_dtype=torch_dtype, use_safetensors=True
    )

  processor = AutoProcessor.from_pretrained(model_path)

  pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=15,
    batch_size=64,
    torch_dtype=torch_dtype,
    device=device,
    )

  sample = audio_file
  result = pipe(sample)

  return result["text"]

# sample = r"D:\Audio_emotion\Test_audio_files\Tom cruise angry dialouge.mp3"
# t1 = get_text_from_whisper_model(sample)
# print(t1)

# Model For Emotion Extraction From Text
def get_emotion_from_text_with_roberta(audio_text):
    
  Roberta_model_path = r"D:\Audio_emotion\distilRoberta_base_emotion"
  roberta_classifier = pipeline("text-classification", model=Roberta_model_path, return_all_scores=True)
  roberta_output = roberta_classifier(audio_text)
    
  return roberta_output

# Getting Desired Probability Output
def get_output_desired_format_for_roberta(lst):
    '''
    Take List as Input parameter and Return Two variable one dict with key as emotion label and value as its ptobability,
    second one is final emotion label whose probability is higher.
    '''
    for i in lst[0]:
        if i["label"] == "anger": 
          i["label"] = "ang"
        elif i["label"] == "disgust":
          i["label"] = "sad"
        elif i["label"] == "fear": 
          i["label"] = "sad"
        elif i["label"] == "joy":
          i["label"] = "hap"
        elif i["label"] == "neutral":
          i["label"] = "neu"  
        elif i["label"] == "sadness":
          i["label"] = "sad"
        elif i["label"] == "surprise":
          i["label"] = "hap"

    # Use a defaultdict to accumulate scores for each label
    label_scores = defaultdict(float)

    for item in lst[0]:
        label_scores[item['label']] += item['score']

        # Create a new list with the updated scores
        updated_roberta_output = [{'label': label, 'score': score} for label, score in label_scores.items()]

        # Defined the desired order of labels
        desired_order = ['neu', 'hap', 'ang', 'sad']

        # Rearrange the list using a custom key function
        arranged_updated_roberta_output = sorted(updated_roberta_output, key=lambda item: desired_order.index(item['label']))
        
        roberta_prob = []
        for i in arranged_updated_roberta_output:
            roberta_prob.append(i["score"])
        
        prob_percent = [str(round(i*100,2))+"%" for i in roberta_prob]
        final_result = dict(zip(desired_order,prob_percent))
        final_emotion_label = desired_order[np.argmax(roberta_prob)]
        
        if final_emotion_label == "hap":
            final_emotion_label = "Happy 😄"
        elif final_emotion_label == "sad":
            final_emotion_label = "Sad 😔"
        elif final_emotion_label == "ang":
            final_emotion_label = "Angry 😠"
        elif final_emotion_label == "neu":
            final_emotion_label = "Neutral 😑"

    return final_result,final_emotion_label
          
# Using gemini API to Extract Keywords for target Emotion 
def get_keywords_for_emotion(audio_text,emotion):
  # creating the output parser
  response_schemas = [
    ResponseSchema(name="Keywords for target emotion", description="List of key-words as unigram or bigram  responsible for given emotion/tone from given text",type='list')
    ]
  output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
  format_instructions = output_parser.get_format_instructions()
  
  # Prompt for inference with Gemini Model
  input_prompt = """
    From below given text delimated in triple bracket, give me keywords as list of unigram/bigram which is responsible for {emotion} emotion/tone from given text.

    text : ```{text}```

    Always return output sticktly only in format: {format_instructions}
    """
  
  prompt = PromptTemplate(
    template=input_prompt,
    input_variables=["text","emotion"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )
  
  model = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.8,top_k=5)
  
  # Creating chain 
  chain = prompt | model | output_parser

  try:
    result = chain.invoke({"emotion":emotion,"text":audio_text})
  except :
    result = "Harmless words related to target emotion not generated for saftey reason."

  return result