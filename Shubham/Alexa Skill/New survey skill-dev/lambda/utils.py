import logging
import os
import boto3
from botocore.exceptions import ClientError
import requests
import json
import string
import nltk
import datetime
import pytz

stopwords_lst = ['i','me','my','myself','we','our','ours','ourselves','you',"you're","you've","you'll","you'd",'your','yours','yourself','yourselves','he','him','his','himself',
'she',"she's",'her','hers','herself','it',"it's",'its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that',"that'll",'these','those',
'am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while',
'of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under',
'again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same',
 'so','than','too','very','s','t','can','will','just','don',"don't",'should',"should've",'now','d','ll','m','o','re','ve','y','ain','aren',"aren't",'couldn',"couldn't",'didn',"didn't",
 'doesn',"doesn't",'hadn',"hadn't",'hasn',"hasn't",'haven',"haven't",'isn',"isn't",'ma','mightn',"mightn't",'mustn',"mustn't",'needn',"needn't",'shan',"shan't",'shouldn',"shouldn't",
 'wasn',"wasn't",'weren',"weren't",'won',"won't",'wouldn',"wouldn't"]

# Defining All useful Function in utils.py file

def create_presigned_url(object_name):
    """Generate a presigned URL to share an S3 object with a capped expiration of 60 seconds

    :param object_name: string
    :return: Presigned URL as string. If error, returns None.
    """
    s3_client = boto3.client('s3',
                             region_name=os.environ.get('S3_PERSISTENCE_REGION'),
                             config=boto3.session.Config(signature_version='s3v4',s3={'addressing_style': 'path'}))
    try:
        bucket_name = os.environ.get('S3_PERSISTENCE_BUCKET')
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=60*1)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

# S3 bucket Integration code
# s3_client = boto3.client('s3')

# # Get the pre-signed URL for your MP3 file
# presigned_url = s3_client.generate_presigned_url(
#     ClientMethod='get_object',
#     Params={'Bucket': 'your-bucket', 'Key': 'your-file.mp3'},
#     ExpiresIn=3600  # URL expires in an hour
# )

#Function for posting user responses in API
def posting_responses(my_objs):
    try :
        # url="https://api.openeyessurveys.com/public/api/questionResponse"  #Prod_API 
        url = "http://openeyessurveys-api.devbyopeneyes.com/public/api/questionResponse" #Dev_API
        headers = {'Content-Type':'application/json','Accept':'application/json','Authorization':'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
        
        yo = requests.post(url,headers=headers,data=json.dumps(my_objs))

        result =  "Data posted successfully."
    except :
        result =  "Data not posted successfully."
        
    return result

#Function to get boolean for checking MCQwithmultipleselection option present in user_reponse --> If any one option in response return True
def get_boolean(option_lst, user_response):
    # Remove punctuations from the sentence
    translator = str.maketrans("", "", string.punctuation)
    #If condition is to handle None User response when User skip question
    if user_response != None:
        user_response = user_response.translate(translator)
        for i in option_lst:
            if i in user_response:
                return False
        else:
            return True
    else :
        pass
    
#Function to get boolean for checking MCQwithmultipleselection option present in user_reponse  --> If all options in response return True
def is_check_multiple_mcq(option_lst,user_resp):
    # Lowercase both and removing punctuation from user response
    user_resp = user_resp.lower()
    option_lst = [i.lower() for i in option_lst]

    translator = str.maketrans("", "", string.punctuation)
    user_resp = user_resp.translate(translator)

    #Spliting user response and removing stopwords
    user_resp_lst = user_resp.split()
    user_resp_lst = [i for i in user_resp_lst if i not in stopwords_lst] 
    print(user_resp_lst)

    #Joining option list to check each user response present in list or not
    option_list_str = " ".join(option_lst)
    print(option_list_str)

    #Checking All user response present in option_list or not
    print([i in option_list_str for i in user_resp_lst])
    result = all([i in option_list_str for i in user_resp_lst])

    return result

# Function For Fetching invalid options from user response For MultipleMCQ
def get_wrong_options(option_lst,user_resp):
    # Lowercase both and removing punctuation from user response
    user_resp = user_resp.lower()
    option_lst = [i.lower() for i in option_lst]

    translator = str.maketrans("", "", string.punctuation)
    user_resp = user_resp.translate(translator)

    #Spliting user response and removing stopwords
    user_resp_lst = user_resp.split()
    user_resp_lst = [i for i in user_resp_lst if i not in stopwords_lst]

    #Joining option list to check each user response present in list or not
    option_list_str = " ".join(option_lst)

    #Checking All user response present in option_list or not
    result = [i in option_list_str for i in user_resp_lst]

    false_indices = [index for index,item in enumerate(result) if not item]
    invalid_options_lst =[user_resp_lst[i] for i in false_indices] 

    return invalid_options_lst

# Function for Timezone based thank you message return
def get_timezone_based_ty_msg(lang):
     # morning : 6am to 12 pm , afternoon : 12 pm to 6 pm , evening : 6 pm to 9 pm , night: 9 pm to 12 6 am 
    ct = datetime.datetime.utcnow()
    # Define the Indian time zone & US time zone
    # Here we are fetcing device selected langauge and accordingly we are converting UTC timezone into local timezone
    indian_timezone = pytz.timezone('Asia/Kolkata')
    us_timezone = pytz.timezone("US/Eastern")
    if lang == "en-IN":
        local_time = ct.astimezone(indian_timezone)
    elif lang == "en-US":
        local_time = ct.astimezone(us_timezone)
    elif lang == "hi-IN" :
        local_time = ct.astimezone(indian_timezone)
    else :
        pass
    lt_hr = local_time.hour
    if lt_hr in range(6,13):
        time_zone = "morning"
    elif lt_hr in range(13,17):
        time_zone = "afternoon"
    elif lt_hr in range(18,22):
        time_zone = "evening"
    elif lt_hr in range(22,25):
        time_zone = "night"
    else :
        time_zone = "day"
        
    return time_zone
