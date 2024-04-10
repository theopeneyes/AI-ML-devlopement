# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import random
import datetime
import pytz
import string
import re
from ask_sdk_model import (Intent, IntentConfirmationStatus, Slot, SlotConfirmationStatus, Response, DialogState, ui)
from ask_sdk_model.directive import Directive
from ask_sdk_model.dialog import DelegateDirective
from ask_sdk_model.dialog import ElicitSlotDirective,ConfirmSlotDirective
from ask_sdk_model.intent import Intent
from urllib3._collections import HTTPHeaderDict
import urllib.request
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from threading import Thread
from ask_sdk_core.utils import is_intent_name, get_slot_value, get_dialog_state
from ask_sdk_model.request_envelope import RequestEnvelope
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler,AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.response_helper import (get_plain_text_content, get_rich_text_content)
from ask_sdk_model.interfaces.display import (ImageInstance, Image, RenderTemplateDirective, ListTemplate1,BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1)
from ask_sdk_model.intent_confirmation_status import IntentConfirmationStatus
from ask_sdk_core.response_helper import ResponseFactory
from ask_sdk_model import Response
from ask_sdk_core.serialize import DefaultSerializer
import ask_sdk_model.dialog as dialog
from utils import posting_responses,get_boolean,is_check_multiple_mcq,get_wrong_options
# import sys
# print(sys.version)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        try:
            # This try block execute when user invoke home_intent
            attr = handler_input.attributes_manager.session_attributes
            if attr["home_intent"]:
                speak_output = "Ok. Let’s begin. Tell me your six-digit Survey code."
                repropmt = "Sorry. I have difficulties listening to your response. Could you please tell me six-digit survey code again."
                return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(repropmt)
                    .response
                )

        except KeyError :
            attr = handler_input.attributes_manager.session_attributes
            global device_id
            device_id = handler_input.request_envelope.context.system.device.device_id
            # print("Device ID is :",device_id)
            speak_output = "Welcome to OpenEyes Surveys. Tell me your six-digit Survey code to begin."
            repropmt = "I could not hear you. Could you please tell me your six-digit Survey Code?"
            attr["home_intent"] = False
            # print(handler_input.attributes_manager.session_attributes.get("session_state"))
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(repropmt)
                .response
            )

class SurveyIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SurveyIntent")(handler_input) and not handler_input.attributes_manager.session_attributes.get("session_state")
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # print(handler_input.attributes_manager.session_attributes.get("session_state"))
        attr = handler_input.attributes_manager.session_attributes
        attr["counter"] = 0
        # attr["options"] = 0
        # attr["rating"] = 0
        attr["mcq_options"] = []
        attr["other_flag"] = False
        attr["option_dict_abcd"] = {}
        
        global question_types_lst
        question_types_lst = []
        id=get_slot_value(handler_input=handler_input, slot_name="survey")
        id_len = len(id)
        # print(id,id_len)
        if id_len == 6 :
            surveyid = requests.get("https://api.openeyessurveys.com/public/api/getSurveyId/{}".format(id)) #+ str(idd))
            # surveyid = requests.get("http://openeyessurveys-api.devbyopeneyes.com/public/api/getSurveyId/{}".format(id)) #+ str(idd))
            respss= surveyid.json()
            codes= (respss["code"])
            # print(codes)
            if str(codes) == "200":
                data_id = (respss["data"]["id"])
                r=requests.get("https://api.openeyessurveys.com/public/api/getSurveyDetails/{}".format(data_id)) #+ str(data_id) )
                # r=requests.get("http://openeyessurveys-api.devbyopeneyes.com/public/api/getSurveyDetails/{}".format(data_id)) #+ str(data_id) )
                resp= r.json()
                global datas
                datas=(resp["data"]["surveyDetails"])
                global main_survey_id
                main_survey_id=(datas["id"])
                global main_platform_id
                main_platform_id=(datas["platform_id"])
                global survey_name
                survey_name = (datas["survey_name"])
                global survey_owner_ty_msg
                survey_owner_ty_msg = resp["data"]["surveyDetails"]["thank_you_message"]
                urls="https://api.openeyessurveys.com/public/api/startSurvey"
                # urls="http://openeyessurveys-api.devbyopeneyes.com/public/api/startSurvey"    
                headers = {'Content-Type':'application/json','Accept':'application/json','Authorization':'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
                myobj = {
                    "survey_id":main_survey_id,
                    "device_id" : device_id,
                    "platform_id": main_platform_id
                        }           
                y = requests.post(url=urls,headers=headers,data=json.dumps(myobj))
                # print(myobj)
                #Fetching all required data from API
                global resps
                resps=y.json()
                #messages=(resps["message"])
                survey_status_code = str(resps["code"])
                if survey_status_code == "200" :
                        
                    global datass
                    datass=(resps["data"]["Questions"])
                    #Extracting length of survey in variable len_survey
                    global len_survey
                    len_survey = len(datass)
                    # print("Length of survey is :",len_survey)
                    ids=(datass[attr["counter"]]["question_id"])
                    survey_id=(datass[attr["counter"]]["survey_id"])
                    platform_id=(datass[attr["counter"]]["platform_id"])
                    question_option_id=(datass[attr["counter"]]["question_option_id"])
                    ques=(datass[attr["counter"]]["question"])
                    global question_text
                    question_text = (ques["question_text"])
                    attr["question_text"]=(ques["question_text"])
                    question_type_id=(ques["question_type_id"])
                    handler_input.attributes_manager.session_attributes = attr
                    global description
                    description = (datas["description"])
                    # speak_output =  "Found it. If you need assistance, say “Help” at any time. Let's begin the survey, okay?" #Direct questions will start
                    attr["session_state"]= True
                    
                    return QuestionIntentHandler().handle(handler_input)
                    
                elif survey_status_code == "404" :
                    speak_output = "This survey is not available right now. Please provide valid survey code to start survey."
                    
                    return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
                    )
                else :
                    speak_output = "Please provide valid survey code."

            elif str(codes) == "404":
                #We are clearing data which got in previous session so if user provide wrong survey code and trigger question intent he did not get questions
                try:
                    resps.clear()
                except :
                    pass
                speak_output = "Sorry. I could not find a survey. Please verify and tell me six-digit survey code again. "
                
                return (
                    handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
                    )

        elif id_len != 6:
            #We are clearing data which got in previous session so if user provide wrong survey code and trigger question intent he did not get questions
            try:
                resps.clear()
            except:
                pass
            speak_output ="Sorry, I am unable to find your six-digit survey code. Say 'Stop' to end the skill, and try again later. "
            
            return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
                )

class QuestionIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("QuestionIntent")(handler_input) 
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        global intent_lst
        intent_lst = attr["intent_history"]
        user_response = get_slot_value(handler_input=handler_input, slot_name="answer")
        # This try block if there is no user response None then we cant lower it so we handle that exception
        try :
            user_response = user_response.lower()
        except :
            pass
        # This try block is just for Support_intent,report_question_intent & report_survey_intent trigger or not because at first time intent list have only 1 item so it will give error for 2nd item while fetching
        try :
            if intent_lst[-2] == "SupportTypeIntent":
                support_type_intent = True
                report_question_intent,report_survey_intent = False,False
            elif intent_lst[-2] == "ReportQuestionIntent":
                report_question_intent = True
                support_type_intent,report_survey_intent = False,False
            elif intent_lst[-2] == "ReportSurveyIntent":
                report_survey_intent =True
                support_type_intent,report_question_intent = False,False
            else :
                support_type_intent,report_question_intent,report_survey_intent = False,False,False
        except IndexError :
            support_type_intent,report_question_intent,report_survey_intent = False,False,False
        # condition for Converting User responses for MCQ question as option a/b/c/d into option text
        if user_response != None and (attr.get("question_type") == "b166063b-0740-11ec-af38-1908de41ac9c" or attr.get("question_type") =="b1662e42-0740-11ec-af38-1908de41ac9c") :
            mcq_response_text = ""
            for i in attr["option_dict_abcd"].keys():
                if i in user_response:
                    mcq_response_text += attr["option_dict_abcd"][i]
            
            if mcq_response_text != "":
                user_response = mcq_response_text
            else :
                user_response = user_response
        ###### END OF CODE #####
        
        if intent_lst[-1] != "AMAZON.ResumeIntent" and support_type_intent :
            support_response = user_response
            speak_output = "Thank you. I have submitted your request. Hang tight. Someone will get back to you as soon as possible. To continue survey just say 'resume'."
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        #If user report survey at any question in survey this block will execute and propmpt thank you message(Test this condition properly)
        elif report_survey_intent and intent_lst[-1] != "HelpExitIntent" and intent_lst[-1] != "AMAZON.ResumeIntent": #intent_lst[-2] == "ReportSurveyIntent"
            speak_output = "Got it. Your feedback is extremely valuable to us. Thank you for your participation.Have a wonderful day!"
            # attr["report_survey_response"] = user_response
            return(
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .set_should_end_session(True)
                    .response
            )
        # IF user in help intent and user_response was other than help related options
        elif attr.get("help_intent"):
            speak_output = "Sorry? I don't understand. How may I help you? <break time='0.15s'/> Please provide valid options related to help. To get out of help just say 'exit help'."
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        # Condition for handling responses other than number for Rating & GroupRating
        elif attr.get("question_type") == '77b55f4a-639e-4708-9412-5b46f7e3972b' and attr["intent_history"][-1] != "RatingTypeIntent" and attr["intent_history"][-1] != "AMAZON.NextIntent" and attr["intent_history"][-1] != "AMAZON.ResumeIntent":
            
            speak_output = "Please provide valid rating number in between 1 to 5."
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        elif attr.get("question_type") == 'ec856a6e-a071-4496-829e-ce407ad3d3fa' and attr["intent_history"][-1] != "RatingTypeIntent" and attr["intent_history"][-1] != "AMAZON.NextIntent" and attr["intent_history"][-1] != "AMAZON.ResumeIntent":
            
            speak_output = "Please provide valid rating number in between 1 to 5. "
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        # Condition for Handling unwanted response for MCQ type question
        elif attr.get("question_type") == "b166063b-0740-11ec-af38-1908de41ac9c" and user_response != None and user_response not in attr.get("mcq_options") and not attr["other_flag"] and attr["intent_history"][-1] != "AMAZON.NextIntent" and attr["intent_history"][-1] != "AMAZON.ResumeIntent":
            
            speak_output = "Please provide valid option from given list of option."
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        # In MCQ with Other if user_response is "other"
        elif attr.get("question_type") == "b166063b-0740-11ec-af38-1908de41ac9c" and "other" in attr.get("mcq_options") and user_response == "other":
            attr["other_flag"] = True
            speak_output = "Please describe any other option of your choice."
            
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        # Condition for Handling unwanted response for MCQwithmultipleselection 
        elif attr.get("question_type") == "b1662e42-0740-11ec-af38-1908de41ac9c" and user_response != None and not is_check_multiple_mcq(attr["mcq_options"],user_response) and attr["intent_history"][-1] != "AMAZON.NextIntent" and attr["intent_history"][-1] != "AMAZON.ResumeIntent":
            invalid_options_from_user = get_wrong_options(attr["mcq_options"],user_response)
            if len(invalid_options_from_user) > 0 and len(invalid_options_from_user) <= 3:
                invalid_options_str = " ".join(invalid_options_from_user)
                speak_output = f"You selected wrong options :{invalid_options_str}. Please select only valid options from given list."
            else :
                speak_output = "Please select only valid options from given list of options."
            return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
            )
        else :
            intent_name = ask_utils.get_intent_name(handler_input)
            reprompt = "Please answer the question otherwise skill will end."
            try:  
                Descriptive = 'b16631e5-0740-11ec-af38-1908de41ac9c'
                Dropdownwithsingleselection = 'b1662a30-0740-11ec-af38-1908de41ac9c'
                global MCQ
                MCQ = 'b166063b-0740-11ec-af38-1908de41ac9c'
                global MCQwithmultipleselection
                MCQwithmultipleselection = 'b1662e42-0740-11ec-af38-1908de41ac9c'
                global ShortAnswer
                ShortAnswer = 'b1662dde-0740-11ec-af38-1908de41ac9c'
                global Rating
                Rating = '77b55f4a-639e-4708-9412-5b46f7e3972b'
                global GroupRating
                GroupRating = 'ec856a6e-a071-4496-829e-ce407ad3d3fa'
                #messages=(resps["message"])
                datass=(resps["data"]["Questions"]) # All Question data list
                response_posting_index = 2 #Just assign var for fetching Question data while posting answer in Else block after execution of try bolck
                response_posting_index_last_q = 1 #Just assign var for fetching Question data while posting answer in except block for last question
                #Logic for Condition Branching(Disqualification based on answer)
                #with this if condition we are checking condition is applied on question or not 
                if attr["counter"] > 0 and attr.get("question_type") == MCQ and user_response != None and datass[attr["counter"]-1]["question"]["options"][0]["has_question"] == 1:
                    option_with_logic = {}
                    option_lst_for_action_type = []
                    action_type_lst = []
                    ques=(datass[attr["counter"]-1]["question"])
                    option_data = ques["options"]
                    len_options_cl = len(option_data)
                    for i in range(len_options_cl):
                        option_lst_for_action_type.append(option_data[i]["option_text"].lower())
                        action_type_lst.append(option_data[i]["options_logic"][0]["action_type"].lower())
                    option_with_logic = dict(zip(option_lst_for_action_type,action_type_lst))
                    # IF MCQ question given with other option then fetching its action type and placing in dict option_with_logic
                    try:
                        other_logic = ques["other_logic"][0]
                        other_action_type = other_logic["action_type"].lower()
                        option_with_logic["other"] = other_action_type
                    except IndexError:
                        option_with_logic["other"] = None
                    for x in option_with_logic.keys():
                        if x == user_response:
                            action_type = option_with_logic[x]
                            break
                        else :
                            action_type = option_with_logic["other"]
                    # print("Option dictionary : ",option_with_logic,action_type)
                    if action_type == "hide":
                        attr["counter"] += 1
                        response_posting_index = 3
                        response_posting_index_last_q = 2
                    else :
                        pass
                else :
                    pass
                ques=(datass[attr["counter"]]["question"]) # Fetching question data with help of counter
                # global questions
                # questions=(datass[attr["options"]-1]["question"])
                attr["question_text"]=(ques["question_text"])
                global ratingss
                ratingss=(ques["rating"])
                global question_type_id
                question_type_id=(ques["question_type_id"])
                is_other=(ques["is_other"])
                # global is_others
                # is_others=(questions["is_other"])
                # if str(is_others) == "1":
                #     global flag
                #     flag = 1
                options_keys=[]
                response=[]
                dictionary={}
                global mcq_options
                mcq_options=[]
                global rating_groups
                rating_groups = []
                global mcqsthatnotdisplay
                mcqsthatnotdisplay=[]
                global ratingsss
                ratingsss=[]
                global ratingsthatnotdisply
                ratingsthatnotdisply =[]
                optionss= len(ques["options"])
                #For mandatory question 
                global is_mandatory
                is_mandatory = ques["is_required"]
                global QuestionLimits
                QuestionLimits=(resps["data"]["QuestionLimits"])
                # global optionsthatnotdisplay
                # optionsthatnotdisplay= len(questions["options"])
                #appending type of question in "question type" key in session attribute
                # attr["question_type"].append(question_type_id)
                attr["question_type"] = question_type_id
                try:
                    question_types_lst.append(attr["question_type"])
                except:
                    pass
                if str(question_type_id) == MCQwithmultipleselection:
                    dictionary.clear()
                    mcq_options.clear()
                    for i in range(optionss):
                        options=(ques["options"])
                        option_texts=((options[i]["option_text"]))
                        mcq_options.append(option_texts.lower().strip())
                        optionss=len(options)
                    attr["mcq_options"] = mcq_options
                    # Code to speak output options as option-A/B/C/D-option_text
                    # abc_str = "abcdefghijklmnopqrstuvwxyz"
                    # option_dict_abcd = { "option " + abc_str[mcq_options.index(i)] : i for i in mcq_options}
                    # attr["option_dict_abcd"] = option_dict_abcd
                    
                    # options_speak_output =  ""
                    # for key,value in option_dict_abcd.items():
                    #     options_speak_output += key +" : "+ value +"\n" + "<break time='0.15s'/>"
                        
                    # speak_output= "Choose your best answer's for the question" + "<break time='0.15s'/> Question " + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + options_speak_output
                    # Normal Speak_output without option-a/b/c/d
                    speak_output= "Choose multiple answers for the question" + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options)
                    # if str(is_other) == "0":
                    #     speak_output= "Choose your best answer for the question" + "<break time='0.15s'/> Question " + str(attr["counter"]+1)+ "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options) 
                    # else:
                    #     speak_output= "Choose your best answer for the question" + "<break time='0.15s'/> Question " + str(attr["counter"]+1) + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options) +" Other"
                    attr["counter"] += 1
                elif str(question_type_id) == Descriptive:
                    handler_input.attributes_manager.session_attributes = attr
                    speak_output= "Answer the question in detail" + "<break time='0.15s'/>" +  "<break time='0.15s'/>" +  " " + attr["question_text"] + " You can take your time to think about answer. Start your answer with 'Alexa Answer is' :  <audio src= 'https://aaudiobucket.s3.eu-west-1.amazonaws.com/Trimmed_calm_music.mp3'/>"
                    attr["counter"] += 1
                elif str(question_type_id) == ShortAnswer:
                    handler_input.attributes_manager.session_attributes = attr
                    speak_output=  "Answer the question in brief" + "<break time='0.15s'/>" +  "<break time='0.15s'/>" +  " " + attr["question_text"]
                    attr["counter"] += 1
                elif str(question_type_id) == MCQ:
                    dictionary.clear()
                    mcq_options.clear()
                    for i in range(optionss):
                        options=(ques["options"])
                        option_texts=((options[i]["option_text"]))
                        mcq_options.append(option_texts.lower().strip())
                        optionss=len(options)
                    
                    # if str(is_other) == "0":
                    #     attr["mcq_options"] = mcq_options
                    # else :
                    #     mcq_options.append("other")
                    #     attr["mcq_options"] = mcq_options
                    # Code to speak output options as option-A/B/C/D-option_text
                    # abc_str = "abcdefghijklmnopqrstuvwxyz"
                    # option_dict_abcd = { "option " + abc_str[mcq_options.index(i)] : i for i in mcq_options}
                    # attr["option_dict_abcd"] = option_dict_abcd
                    
                    # options_speak_output =  ""
                    # for key,value in option_dict_abcd.items():
                    #     options_speak_output += key +" : "+ value +"\n" + "<break time='0.15s'/>"
                            
                    # speak_output= "Choose your one best answer for the question" + "<break time='0.15s'/> Question " + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + options_speak_output 
                    # Remove this below code if need optin-a/b/c/d in speak_output
                    if str(is_other) == "0":
                        attr["mcq_options"] = mcq_options
                        speak_output= "Choose your one best answer for the question" + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options) 
                    else: 
                        mcq_options.append("other")
                        attr["mcq_options"] = mcq_options
                        speak_output= "Choose your one best answer for the question" + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options) #+ " Other" 
                        
                    attr["counter"] += 1
                elif str(question_type_id) == Dropdownwithsingleselection:
                    dictionary.clear()
                    mcq_options.clear()
                    for i in range(optionss):
                        options=(ques["options"])
                        option_texts=((options[i]["option_text"]))
                        mcq_options.append(option_texts.lower())
                        optionss=len(options)
                    if str(is_other)=="0":
                        speak_output = "Choose your one best answer for the question" + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options) 
                    else:
                        speak_output = "Choose your one best answer for the question" + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] + " " + str(mcq_options) + " Other"  
                    attr["counter"] += 1
                elif str(question_type_id) == Rating:
                    handler_input.attributes_manager.session_attributes = attr
                    rating_range = ques["rating"]
                    # speak_output= "Question " + str(attr["counter"]+1) +  " " + attr["question_text"] +  "Rate out of {}.".format(rating_range)
                    speak_output= "Out of {},rate the question".format(rating_range) + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] 
                    attr["counter"] += 1
                elif str(question_type_id) == GroupRating:
                    attr["rating_groups_counter"] = 0
                    rating_groups.clear()
                    rating_range = ques["rating_range"]
                    global response_dict
                    response_dict = {"response_text":[],"question_option_id":[],"_id":[]}
                    for i in range(optionss):
                        options=(ques["options"])
                        option_texts=((options[i]["option_text"]))
                        rating_groups.append(option_texts)
                    group_rating_ques_text = attr["question_text"]
                    
                    # speak_output =  "Question " + str(attr["counter"]+1) +  " " + attr["question_text"] +  " Rate out of {}.".format(rating_range) + "<break time='0.5s'/>" + rating_groups[0]
                    speak_output = "Out of {}, rate the few questions".format(rating_range) + "<break time='0.15s'/>" + "<break time='0.15s'/>" +  " " + attr["question_text"] + "<break time='0.25s'/>" + rating_groups[0]
                    attr["counter"] += 1
                else:
                    dictionary.clear()
                    mcq_options.clear()
                    for i in range(optionss):
                        options=(ques["options"])
                        option_texts=((options[i]["option_text"]))
                        mcq_options.append(option_texts)
                    speak_output = "Question " +  " " + attr["question_text"]  + str(mcq_options)
                    attr["counter"] += 1 
            except IndexError:
                # morning : 6am to 12 pm , afternoon : 12 pm to 6 pm , evening : 6 pm to 9 pm , night: 9 pm to 12 6 am 
                lang = handler_input.request_envelope.request.locale
                ct = datetime.datetime.utcnow()
                # Define the Indian time zone & US time zone
                # Here we are fetcing device selected langauge and accordingly we are converting UTC timezone into local timezone
                indian_timezone = pytz.timezone('Asia/Kolkata')
                us_timezone = pytz.timezone("US/Eastern")
                if lang == "en-IN":
                    local_time = ct.astimezone(indian_timezone)
                elif lang == "en-US":
                    local_time = ct.astimezone(us_timezone)
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
                global survey_owner_ty_msg
                if survey_owner_ty_msg == None :
                    speak_output = "Thank you for completing the survey. You have a wonderful {}!".format(time_zone)
                else :
                    survey_owner_ty_msg = re.sub("<[^>]*>","",survey_owner_ty_msg)
                    speak_output = survey_owner_ty_msg
                # Code for posting Answer of last question 
                if user_response != None and report_question_intent != True:
                    # Fetching required Data for posting in API
                    ids=(datass[attr["counter"]-response_posting_index_last_q]["question_id"])
                    _id=(datass[attr["counter"]-response_posting_index_last_q]["id"])
                    survey_id=(datass[attr["counter"]-response_posting_index_last_q]["survey_id"])
                    platform_id=(datass[attr["counter"]-response_posting_index_last_q]["platform_id"])
                    
                    ques=(datass[attr["counter"]-response_posting_index_last_q]["question"])
                    question_type_ids=(ques["question_type_id"])
                    is_other = str(ques["is_other"])
                    question_textss=(ques["question_text"])
                    options_1 = ques["options"]
                    len_options = len(options_1)
                    if len_options != 0 and question_type_ids == "b166063b-0740-11ec-af38-1908de41ac9c" :
                        #Logic for MCQ type question posting answer with options ID
                        options_text_lst = []
                        option_id_lst = []
                        for i in range(len_options):
                            option_id_lst.append(options_1[i]["id"])
                            options_text_lst.append(options_1[i]["option_text"].lower())
                        option_dict = dict(zip(options_text_lst,option_id_lst))
                        for i in option_dict.keys():
                            if i == user_response.lower():
                                response_option_id = option_dict[i]
                                break
                            else :
                                response_option_id = "IsOther"
                        response_text = user_response
                    elif len_options != 0 and question_type_ids == "b1662e42-0740-11ec-af38-1908de41ac9c" :
                        #Logic for MCQwithmultipleselection posting answer with options ID
                        # Remove punctuations from the sentence
                        translator = str.maketrans("", "", string.punctuation)
                        clean_user_response = user_response.translate(translator)
                        options_text_lst = []
                        option_id_lst = []
                        for i in range(len_options):
                            option_id_lst.append(options_1[i]["id"])
                            options_text_lst.append(options_1[i]["option_text"].lower())
                        option_dict = dict(zip(options_text_lst,option_id_lst))
                        user_response_options = []
                        for i in options_text_lst:
                            if i in clean_user_response:
                                user_response_options.append(i)
                            else :
                                pass
                        response_text,response_option_id = "",""
                        for i in option_dict.keys():
                            if i in user_response_options:
                                response_text += i + ","
                                response_option_id +=  option_dict[i] + ","
                            else:
                                pass
                        response_text = response_text[:-1]
                        response_option_id = response_option_id[:-1]
                    else :
                        response_option_id = ""
                        response_text = user_response
                    if intent_lst[-2] == "ReportQuestionIntent":
                        response_text = "Reported question: " + user_response
                    else :
                        pass
                    # This code is just formating email response text -> Not permanant solution
                    if "email" in question_textss and intent_lst[-2] != "ReportQuestionIntent":
                        response_text = response_text.lower()
                        response_text = response_text.replace("at the rate","@")
                        response_text = response_text.replace(" at ","@").replace("dot",".")
                        response_text = response_text.replace(" ","")
                    else :
                        pass
                    print(question_textss,response_text,response_option_id)
                    myobjs ={"_id":_id,
                    "survey_id": survey_id, 
                    "platform_id": platform_id, 
                    "question_id": ids, 
                    "question_type_id": question_type_ids,
                    "response_text": response_text,
                    "question_option_id": response_option_id,
                    "device_id": device_id }
                    r = posting_responses(myobjs)
                else :
                    pass

                #This if condition if user report last question of survey
                if  report_question_intent and intent_lst[-1] != "HelpExitIntent": #intent_lst[-2] == "ReportQuestionIntent"
                    speak_output1 = "Thank you! I have marked the question for review." 
                    speak_output = speak_output1 + speak_output
                    # attr["report_question_response"] = user_response
                    # Code for Posting report question comment to API for last question
                    # Fetching Required Data For API psoting
                    ids=(datass[attr["counter"]-response_posting_index_last_q]["question_id"])
                    _id=(datass[attr["counter"]-response_posting_index_last_q]["id"])
                    survey_id=(datass[attr["counter"]-response_posting_index_last_q]["survey_id"])
                    platform_id=(datass[attr["counter"]-response_posting_index_last_q]["platform_id"])
                    
                    ques=(datass[attr["counter"]-response_posting_index_last_q]["question"])
                    question_type_ids=(ques["question_type_id"])
                    is_other = str(ques["is_other"])
                    question_textss=(ques["question_text"])
                    options_1 = ques["options"]
                    flag_comment = user_response
                    
                    myobjs ={"_id":_id,
                    "survey_id": survey_id, 
                    "platform_id": platform_id, 
                    "question_id": ids, 
                    "question_type_id": question_type_ids,
                    "response_text": flag_comment,
                    "question_option_id": "",
                    "device_id": device_id }
                    
                    # url = "http://openeyessurveys-api.devbyopeneyes.com/public/api/questionFlagReport"
                    # headers = {'Content-Type':'application/json','Accept':'application/json','Authorization':'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
                    # yf = requests.post(url,headers=headers,data=json.dumps(myobjs))
                    
                # Calling last API after End of survey with all answers given...
                url="https://api.openeyessurveys.com/public/api/voiceSurveySubmit" 
                # url="http://openeyessurveys-api.devbyopeneyes.com/public/api/voiceSurveySubmit"    
                headers = {'Content-Type':'application/json','Accept':'application/json','Authorization':'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
                myobjs ={"survey_id": main_survey_id,
                "device_id" : device_id,
                "platform_id": main_platform_id}
                yo = requests.post(url,headers=headers,data=json.dumps(myobjs))
                    
                return(
                    handler_input.response_builder
                        .speak(speak_output)
                        .ask(reprompt)
                        .set_should_end_session(True)
                        .response
                )
            else :
                # Posting of answer on API
                if user_response != None and report_question_intent != True:
                    if attr["counter"] > 1:
                        ids=(datass[attr["counter"]-response_posting_index]["question_id"])
                        _id=(datass[attr["counter"]-response_posting_index]["id"])
                        survey_id=(datass[attr["counter"]-response_posting_index]["survey_id"])
                        platform_id=(datass[attr["counter"]-response_posting_index]["platform_id"])
                        
                        ques=(datass[attr["counter"]-response_posting_index]["question"])
                        question_textss=(ques["question_text"])
                        is_other = str(ques["is_other"])
                        question_type_ids=(ques["question_type_id"])
                        options_1 = ques["options"]
                        len_options = len(options_1)
                        if len_options != 0 and question_type_ids == "b166063b-0740-11ec-af38-1908de41ac9c" :
                            #Logic for MCQ type question posting answer with options ID
                            options_text_lst = []
                            option_id_lst = []
                            for i in range(len_options):
                                option_id_lst.append(options_1[i]["id"])
                                options_text_lst.append(options_1[i]["option_text"].lower())
                            option_dict = dict(zip(options_text_lst,option_id_lst))
                            for i in option_dict.keys():
                                if i == user_response.lower():
                                    response_option_id = option_dict[i]
                                    break
                                else :
                                    response_option_id = "IsOther"
                            response_text = user_response
                        elif len_options != 0 and question_type_ids == "b1662e42-0740-11ec-af38-1908de41ac9c" :
                            #Logic for MCQwithmultipleselection posting answer with options ID
                            # Remove punctuations from the sentence
                            translator = str.maketrans("", "", string.punctuation)
                            clean_user_response = user_response.translate(translator)
                            options_text_lst = []
                            option_id_lst = []
                            for i in range(len_options):
                                option_id_lst.append(options_1[i]["id"])
                                options_text_lst.append(options_1[i]["option_text"].lower())
                            option_dict = dict(zip(options_text_lst,option_id_lst))
                            user_response_options = []
                            for i in options_text_lst:
                                if i in clean_user_response:
                                    user_response_options.append(i)
                                else :
                                    pass
                            response_text,response_option_id = "",""
                            for i in option_dict.keys():
                                if i in user_response_options:
                                    response_text += i + ","
                                    response_option_id +=  option_dict[i] + ","
                                else:
                                    pass
                            response_text = response_text[:-1]
                            response_option_id = response_option_id[:-1]
                        else :
                            response_option_id = ""
                            response_text = user_response
                        if intent_lst[-2] == "ReportQuestionIntent":
                            response_text = "Reported question: " + user_response
                        else :
                            pass
                        # This code is just formating email response text -> Not permanant solution
                        if "email" in question_textss and intent_lst[-2] != "ReportQuestionIntent":
                            response_text = response_text.lower()
                            response_text = response_text.replace("at the rate","@")
                            response_text = response_text.replace(" at ","@").replace("dot",".")
                            response_text = response_text.replace(" ","")
                        else :
                            pass
                        print(question_textss,response_text,response_option_id)
                        myobjs ={"_id":_id,
                        "survey_id": survey_id, 
                        "platform_id": platform_id, 
                        "question_id": ids, 
                        "question_type_id": question_type_ids,
                        "question_option_id": response_option_id,
                        "response_text": response_text,
                        "device_id": device_id }
                        print(myobjs)
                        r = posting_responses(myobjs)
                    else :
                        pass
                else :
                    pass
            if  report_question_intent and intent_lst[-1] != "HelpExitIntent" and intent_lst[-1] != "AMAZON.ResumeIntent": #intent_lst[-2] == "ReportQuestionIntent"
                speak_output1 = "Thank you! I have marked the question for review. Let’s move to the to next question: " 
                speak_output1 += speak_output
                # attr["report_question_response"] = user_response
                # Posting report Question comment to API
                #This if condition if user report last question of survey
                # Code for Posting report question comment to API for last question
                # Fetching Required Data For API psoting
                ids=(datass[attr["counter"]-response_posting_index_last_q]["question_id"])
                _id=(datass[attr["counter"]-response_posting_index_last_q]["id"])
                survey_id=(datass[attr["counter"]-response_posting_index_last_q]["survey_id"])
                platform_id=(datass[attr["counter"]-response_posting_index_last_q]["platform_id"])
                    
                ques=(datass[attr["counter"]-response_posting_index_last_q]["question"])
                question_type_ids=(ques["question_type_id"])
                is_other = str(ques["is_other"])
                question_textss=(ques["question_text"])
                options_1 = ques["options"]
                flag_comment = user_response
                    
                myobjs ={"_id":_id,
                    "survey_id": survey_id, 
                    "platform_id": platform_id, 
                    "question_id": ids, 
                    "question_type_id": question_type_ids,
                    "response_text": flag_comment,
                    "question_option_id": "",
                    "device_id": device_id }
                    
                # url = "http://openeyessurveys-api.devbyopeneyes.com/public/api/questionFlagReport"
                # headers = {'Content-Type':'application/json','Accept':'application/json','Authorization':'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
                # yf = requests.post(url,headers=headers,data=json.dumps(myobjs))

                return(
                    handler_input.response_builder
                        .speak(speak_output1)
                        .ask(reprompt)
                        .response
                )
            else :
                reprompt = "Please answer the question otherwise skill will end."
                return(
                    handler_input.response_builder
                            .speak(speak_output)
                            .ask(reprompt)
                            .set_should_end_session(False)
                            .response
                    )


class RatingTypeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("RatingTypeIntent")(handler_input)
    
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        global rating_var
        rating_var = get_slot_value(handler_input=handler_input, slot_name="rating")
        if attr["question_type"] == Rating :
            attr["answer_{}".format(attr["counter"])] = rating_var
            ids=(datass[attr["counter"]-1]["question_id"])
            _id=(datass[attr["counter"]-1]["id"])
            survey_id=(datass[attr["counter"]-1]["survey_id"])
            platform_id=(datass[attr["counter"]-1]["platform_id"])
                
            ques=(datass[attr["counter"]-1]["question"])
            question_type_ids=(ques["question_type_id"])
            
            question_textss=(ques["question_text"])
            response_text = rating_var
            question_textss=(ques["question_text"])
            print(question_textss,rating_var)
            myobjs ={"_id":_id,
            "survey_id": survey_id, 
            "platform_id": platform_id, 
            "question_id": ids, 
            "question_type_id": question_type_ids,
            "response_text": response_text,
            "device_id": device_id }
            r = posting_responses(myobjs)

            return QuestionIntentHandler().handle(handler_input)

        elif attr["question_type"] == GroupRating:
            #Group_rating question logic

            response_dict["response_text"].append(rating_var)
            ids=(datass[attr["counter"]-1]["question_id"])
            _id=(datass[attr["counter"]-1]["id"])
            response_dict["_id"].append(_id)
            survey_id=(datass[attr["counter"]-1]["survey_id"])
            platform_id=(datass[attr["counter"]-1]["platform_id"])
            ques=(datass[attr["counter"]-1]["question"])
            question_type_ids=(ques["question_type_id"])
            question_textss=(ques["question_text"])
            options = ques["options"]
            
            try:
                option_id = options[attr["rating_groups_counter"]]["id"]
                response_dict["question_option_id"].append(option_id)
                attr["rating_groups_counter"] += 1
                group_option_text = rating_groups[attr["rating_groups_counter"]]
                speak_output = "Rate: " + group_option_text
                
                return(
                handler_input.response_builder
                        .speak(speak_output)
                        .ask(speak_output)
                        .response
                )
            except IndexError:
                option_id = options[attr["rating_groups_counter"]-1]["id"]
                response_dict["question_option_id"].append(option_id)
                updated_response_dict = {"response_text":"","question_option_id":"","_id":""}
                # This code is to convert grouptype response into datbase acceptable format
                for i,v in enumerate(response_dict["response_text"]):
                    if i == 0:
                        updated_response_dict["response_text"] += str(v)
                    else:
                        updated_response_dict["response_text"] += "," + str(v)

                for i,v in enumerate(response_dict["question_option_id"]):
                    if i == 0:
                        updated_response_dict["question_option_id"] += str(v)
                    else:
                        updated_response_dict["question_option_id"] += "," + str(v)

                response_dict["_id"] = list(set(response_dict["_id"]))
                for i in response_dict["_id"]:
                    updated_response_dict["_id"] += i
                print(question_textss,updated_response_dict)
                response_text = updated_response_dict
                myobjs ={"_id":_id,
                "survey_id": survey_id, 
                "platform_id": platform_id, 
                "question_id": ids, 
                "question_type_id": question_type_ids,
                "question_option_id":response_text["question_option_id"],
                "response_text": response_text["response_text"],
                "device_id": device_id }
                r = posting_responses(myobjs)
                
                return QuestionIntentHandler().handle(handler_input)
        else :
            speak_output = "Please provide valid response for given question."
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
        
class DescriptiveTypeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("DescriptiveTypeIntent")(handler_input)
    
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        global rating_var
        descriptive_var = get_slot_value(handler_input=handler_input, slot_name="Descriptive_answer")
        if attr["question_type"] == "b16631e5-0740-11ec-af38-1908de41ac9c" :
            attr["answer_{}".format(attr["counter"])] = descriptive_var
            ids=(datass[attr["counter"]-1]["question_id"])
            _id=(datass[attr["counter"]-1]["id"])
            survey_id=(datass[attr["counter"]-1]["survey_id"])
            platform_id=(datass[attr["counter"]-1]["platform_id"])
                
            ques=(datass[attr["counter"]-1]["question"])
            question_type_ids=(ques["question_type_id"])
            
            question_textss=(ques["question_text"])
            response_text = descriptive_var
            question_textss=(ques["question_text"])
            print(question_textss,descriptive_var)
            myobjs ={"_id":_id,
            "survey_id": survey_id, 
            "platform_id": platform_id, 
            "question_id": ids, 
            "question_type_id": question_type_ids,
            "response_text": response_text,
            "device_id": device_id }
            r = posting_responses(myobjs)

            return QuestionIntentHandler().handle(handler_input)
        else :
            speak_output = "Please provide valid response for given question to continue survey."
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
    

class SupportIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SupportIntent")(handler_input)
    
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        speak_output = "Ahh. We are always here to support you. send your querry to info@theOpenEyes.com and will get back to you as soon as possible. To continue survey just say 'resume'."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# class SupportTypeIntentHandler(AbstractRequestHandler):
#     def can_handle(self, handler_input):
#         return ask_utils.is_intent_name("SupportTypeIntent")(handler_input)
    
#     def handle(self, handler_input):
#         attr = handler_input.attributes_manager.session_attributes
#         slot_var1 = get_slot_value(handler_input=handler_input, slot_name="support_options") #Variable type string

#         # if slot_var1 == "technical":
#         #     speak_output = "Our tech support team is available 24/7. Please call  +91 9898989898 TECH-SUPPORT for assistance."
#         # elif slot_var1 == "general":
#         #     speak_output = "For general questions or comments, please send an email to info@ourcompany.com."
#         # else :
#         #     speak_output = "I'm sorry, I didn't understand your request. Please try again."
#         support_type_values = ["technical","general","technical support","general support"]
#         if slot_var1 in support_type_values:
#             speak_output = "Got it. Please say your issue in detail. Upon your completion, I will send it to our technical department, and someone will get back to you via email. Just say “I am ready” when you are ready."
#         elif slot_var1 == "I am ready":
#             speak_output = "Go ahead. I am listening."
#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 .ask(speak_output)
#                 .response
#         )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        attr = handler_input.attributes_manager.session_attributes
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"
        
        # return QuestionIntentHandler().handle(handler_input)
        return  (
            handler_input.response_builder
                .speak(speak_output)
                .ask(reprompt)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["help_intent"] = True
        speak_output = "Hello, how can I help? <break time='0.15s'/> You can say any of the following options : 'report question', 'report survey', 'home', 'resume', 'repeat'."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HelpExitIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelpExitIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["help_intent"] = False
        #Making attr["question_type"] empty because we are returning question intent which will impact and does give question text
        attr["question_type"] = ""
        
        # After exit from survey Survey will resume where user left 
        if attr.get("session_state") == None :
            speak_output = "Please provide first valid six-digit survey code to start survey."
        else :
            attr["counter"] -= 1
            speak_output = "I hope the Help feature was able to provide you with the assistance you needed. Let me resume the survey where we left off : "
            speak_output_QuestionIntent = QuestionIntentHandler().handle(handler_input).output_speech.ssml.replace("<speak>","").replace("</speak>","")
            speak_output = speak_output + speak_output_QuestionIntent
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class RepeatIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        if attr.get("help_intent"):
            speak_output = "Just say, 'Alexa repeat' after exit from help and I will repeat the last thing I said. To get out of help just say 'exit help'."
        else :
            speak_output = attr["repeat_speech_output"]

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class HomeIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):  
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HomeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        if attr.get("help_intent"):
            speak_output = "Just say, 'Alexa home' after exit from Help and I will take you to the beginning of the skill where you could say the survey code and start another survey. To get out of help just say 'exit help'."
            
            return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
        else :
            attr["home_intent"] = True
            attr["session_state"]= False

            return LaunchRequestHandler().handle(handler_input)

class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.ResumeIntent")(handler_input) #AMAZON.ResumeIntent

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        if attr.get("help_intent"):
            speak_output = "Just say, 'Alexa resume' or 'Alexa continue' after exit from help and I will continue survey where you have left off. To get out of help just say 'exit help'."
        elif attr.get("session_state") == None :
            speak_output = "Please provide first valid six-digit survey code to start survey."
        else :
            attr["counter"] -= 1
            speak_output = "Let me resume the survey where we left off : "
            speak_output_QuestionIntent = QuestionIntentHandler().handle(handler_input).output_speech.ssml.replace("<speak>","").replace("</speak>","")
            speak_output = speak_output + speak_output_QuestionIntent
        
        # if resume_slot == "continue" or "resume" and attr.get("help_intent"):
        #     speak_output = "Just say, 'Alexa resume' or 'Alexa continue' after exit from help and I will continue survey where you have left off. To get out of help just say 'exit help'."
        # elif resume_slot == "cancel reporting" :
        #     attr["counter"] -= 1
        #     speak_output = "Let me resume the survey where we left off : "
        #     speak_output_QuestionIntent = QuestionIntentHandler().handle(handler_input).output_speech.ssml.replace("<speak>","").replace("</speak>","")
        #     speak_output = speak_output + speak_output_QuestionIntent
            
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class StopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        lang = handler_input.request_envelope.request.locale
        ct = datetime.datetime.utcnow()
        # Define the Indian time zone & US time zone
        # Here we are fetcing device selected langauge and accordingly we are converting UTC timezone into local timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')
        us_timezone = pytz.timezone("US/Eastern")
        if lang == "en-IN":
            local_time = ct.astimezone(indian_timezone)
        elif lang == "en-US":
            local_time = ct.astimezone(us_timezone)
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
        speak_output = "Ok. Let’s close this. Thank you for using OpenEyes Survey, please rate our skill in your Alexa app. Have a wonderful {}!".format(time_zone)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )


class CancelIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        if attr.get("help_intent"):
            speak_output = "To get out of help just say 'exit help'."
        elif attr.get("session_state") == None :
            speak_output = "Please provide first valid six-digit survey code to start survey."
        elif attr["intent_history"][-2] == "ReportQuestionIntent" or attr["intent_history"][-2] == "ReportSurveyIntent":
            attr["counter"] -= 1
            speak_output = "Let me resume the survey where we left off : "
            speak_output_QuestionIntent = QuestionIntentHandler().handle(handler_input).output_speech.ssml.replace("<speak>","").replace("</speak>","")
            speak_output = speak_output + speak_output_QuestionIntent
        else :
            speak_output = "Please provide valid response for seamless flow of survey."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ReportQuestionIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReportQuestionIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["question_type"] = ""
        if attr.get("help_intent") :
            speak_output = "Just say, 'report question' after exit from Help and I will mark the last question for review. To get out of help just say 'exit help'."
        elif attr.get("session_state") == None :
            speak_output = "Please provide first valid six-digit survey code to start survey."
        else :
            speak_output = "Sure. To report a question for review, I would like to know your reason. Could you please share that briefly? Alternatively, you can say 'cancel report' and I will take you right back where you were."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ReportSurveyIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReportSurveyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["question_type"] = ""
        if attr.get("help_intent") :
            speak_output = "Just say, 'report survey' after exit from Help and I will mark the survey for review with your valuable feedback. To get out of help just say 'exit help'."
        elif attr.get("session_state") == None :
            speak_output = "Please provide first valid six-digit survey code to start survey."
        else :
            speak_output = "Sure. To report this survey for review, I would like to know your reason. Could you please share that briefly? Alternatively, you can say 'cancel report' and I will take you right back where you were."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class SkipIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NextIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        # print("We are in skip Intent :",is_mandatory,type(is_mandatory))
        if attr.get("session_state") == None :
            speak_output = "Please provide first valid six-digit survey code to start survey."
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
        elif is_mandatory == 1:
            speak_output = "Your response is mandatory for given question."
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
        else :
            if len_survey == attr["counter"] :
                speak_output = "You skipped last question of survey, " + QuestionIntentHandler().handle(handler_input).output_speech.ssml.replace("<speak>","").replace("</speak>","")
                
                return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .set_should_end_session(True)
                    .response
            )
            else :
                speak_output = "Moving to next question :" + QuestionIntentHandler().handle(handler_input).output_speech.ssml.replace("<speak>","").replace("</speak>","")
                
                return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        attr = handler_input.attributes_manager.session_attributes
        speak_output = "You just triggered " + intent_name + "."
        
        if speak_output == "You just triggered SurveyIntent.":
            if attr.get("help_intent"):
                speak_output = "Sorry? I don't understand. How may I help you? <break time='0.15s'/> Please provide valid options related to help. To get out of help just say 'exit help'."
                
                return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response)
                
            elif attr["question_type"] == Rating or attr["question_type"] == GroupRating :
                speak_output = "Please provide valid rating range in between 1 to 5."
                
                return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response)

            elif attr.get("question_type") == "b166063b-0740-11ec-af38-1908de41ac9c" :
                
                speak_output = "Please provide valid option from given list of option."
                
                return (
                handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response)

            else :
                return QuestionIntentHandler().handle(handler_input)
        else:
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .ask("add a reprompt if you want to keep the session open for the user to respond")
                    .response
            )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Please provide valid response. Please start skill again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# This interceptor fetches the speech_output and reprompt messages from the response and pass them as session attributes to be used by the repeat intent handler later on.
class RepeatInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        attr = handler_input.attributes_manager.session_attributes
        try:
            attr["repeat_speech_output"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        except:
            pass
        # try:
        #     attr["repeat_reprompt"] = response.reprompt.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        # except:
        #     attr["repeat_reprompt"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")

# This interceptor fetches last intent triggered and append in intent_history list
class IntentHistoryInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        try:
            
            # Get the intent history from the session attributes
            intent_history = attr.get('intent_history', [])
            
            # Get the current intent from the request envelope
            current_intent = handler_input.request_envelope.request.intent
            
            # Add the current intent to the intent history
            intent_history.append(current_intent.name)
            
            # Update the session attributes with the new intent history
            attr['intent_history'] = intent_history
        except AttributeError:
            pass

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SurveyIntentHandler())
sb.add_request_handler(QuestionIntentHandler())
sb.add_request_handler(RatingTypeIntentHandler()) #DescriptiveTypeIntentHandler
sb.add_request_handler(DescriptiveTypeIntentHandler())
sb.add_request_handler(SupportIntentHandler())
# sb.add_request_handler(SupportTypeIntentHandler()) 
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(HelpExitIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(HomeIntentHandler())
sb.add_request_handler(ResumeIntentHandler()) 
sb.add_request_handler(CancelIntentHandler())
sb.add_request_handler(ReportQuestionIntentHandler())
sb.add_request_handler(ReportSurveyIntentHandler())
sb.add_request_handler(StopIntentHandler())
sb.add_request_handler(SkipIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_response_interceptor(RepeatInterceptor())
sb.add_global_request_interceptor(IntentHistoryInterceptor())

lambda_handler = sb.lambda_handler()