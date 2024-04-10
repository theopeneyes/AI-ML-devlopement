import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from collections import defaultdict
import numpy as np
import os
import os
import getpass

from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_google_genai import ChatGoogleGenerativeAI


if "GOOGLE_API_KEY" not in os.environ:
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("AIzaSyCmHaAnPDxw-zzb3Lm3DUr6L4syot5LD1s")

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

#Loading distil-whisperdistil-small.en model from local
# whisper_model_path = r"D:\Emotion sentiment From Audio\distil-whisperdistil-small.en"


# whisper_model = AutoModelForSpeechSeq2Seq.from_pretrained(whisper_model_path, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True)
# whisper_model.to(device)

# whisper_processor = AutoProcessor.from_pretrained(whisper_model_path)

# pipe = pipeline(
#     "automatic-speech-recognition",
#     model=whisper_model,
#     tokenizer=whisper_processor.tokenizer,
#     feature_extractor=whisper_processor.feature_extractor,
#     max_new_tokens=512,
#     torch_dtype=torch_dtype,
#     device=device,
# )

#Loading distil-whisperdistil-medium.en model from local

torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_path = r"D:\Emotion sentiment From Audio\distil-whisperdistil-medium.en"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_path, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)

processor = AutoProcessor.from_pretrained(model_path)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=512,
    chunk_length_s=15,
    batch_size=64,
    torch_dtype=torch_dtype,
    device=device,
)

def get_text_from_whisper_model(audio_file,pipe):

    sample = audio_file
    result = pipe(sample)
    return result["text"]

# sample = r"D:\Emotion sentiment From Audio\Movie dialouge Audio Files\Sad_dialouge_from_dear_john.mp3"
# t1 = get_text_from_whisper_model(sample,pipe)
# print(t1)

# Model For Emotion Extraction From Text
Roberta_model_path = r"D:\Emotion sentiment From Audio\distilRoberta_base_emotion"
from transformers import pipeline
roberta_classifier = pipeline("text-classification", model=Roberta_model_path, return_all_scores=True)

def get_emotion_from_text_with_roberta(classifier,audio_text):
    roberta_output = classifier(audio_text)
    
    return roberta_output

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

def get_keywords_for_emotion(audio_text):
  # creating the output parser
  response_schemas = [
    ResponseSchema(name="Emotion Class", description="Emotion/Tone for the given text",type='string'),
    ResponseSchema(name="Confidense Score", description="Probability value of the predicted Emotion/Tone",type='float'),
    ResponseSchema(name="Keywords for target emotion", description="List of key-words as unigram or bigram  responsible for predicted emotion/tone from given text",type='list')
    ]
  output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
  format_instructions = output_parser.get_format_instructions()
  
  # Prompt for inference with Gemini Model
  input_prompt = """
    Generate single emotion for text delimated in triple bracket below, strictly a single emotion out of [Neutral,Sad,Happy,Angry] with probability score as confidense
    and also give list keywords as unigram or bigram from given text responsible for predicted emotion.

    text : ```{text}```

    Always return output sticktly only in format: {format_instructions}
    """
  
  prompt = PromptTemplate(
    template=input_prompt,
    input_variables=["text"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )
  
  model = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.9)
  
  # Creating chain 
  chain = prompt | model | output_parser

  result = chain.invoke({"text":audio_text})

  return result