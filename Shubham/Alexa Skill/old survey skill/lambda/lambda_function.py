# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
from urllib3._collections import HTTPHeaderDict
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from threading import Thread
from ask_sdk_core.utils import is_intent_name, get_slot_value
from ask_sdk_model import Response, DialogState, Intent
from ask_sdk_core.utils import is_intent_name, get_dialog_state, get_slot_value
from ask_sdk_model.dialog import ElicitSlotDirective
from ask_sdk_model.request_envelope import RequestEnvelope 
from ask_sdk_model.response_envelope import ResponseEnvelope
from ask_sdk_model import (Intent , IntentConfirmationStatus, Slot, SlotConfirmationStatus)
import random
from ask_sdk_runtime.skill_builder import AbstractSkillBuilder
from ask_sdk_runtime.view_resolvers import AbstractTemplateLoader
from ask_sdk_core.serialize import DefaultSerializer
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler,AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.response_helper import (get_plain_text_content, get_rich_text_content)
import urllib.request
from ask_sdk_model.interfaces.display import (ImageInstance, Image, RenderTemplateDirective, ListTemplate1,BackButtonBehavior, ListItem, BodyTemplate2, BodyTemplate1)
from ask_sdk_model import ui, Response
from ask_sdk_model.dialog import DelegateDirective
from ask_sdk_model.intent_confirmation_status import IntentConfirmationStatus
from ask_sdk_model.directive import Directive
from ask_sdk_core.response_helper import ResponseFactory
import ask_sdk_model.dialog as dialog

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("")(handler_input)
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global intent
        intent=0
        global resume
        resume=0
        attr = handler_input.attributes_manager.session_attributes
        speak_output = "Welcome to OpenEyes' Surveys, the world's largest database of surveys by voice. Please tell me your Survey I D ?"
        handler_input.attributes_manager.session_attributes = attr
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask("Please tell me your Survey I D to begin.")
            .response
        )

class SurveyIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("SurveyIntent")(handler_input)
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        survey=get_slot_value( 
            handler_input=handler_input, slot_name="survey")
        attr["counter"]= 0
        URL="http://openeyessurveys-api.devbyopeneyes.com/public/api/survey"
        headers = {'Authorization': 'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
        r = requests.get(url=URL,headers=headers)
        data= r.json()
        data_=len(data)
        count=(data["count"])
        survey_id=[]
        global mcq_options
        mcq_options=[]
        input_=str(survey)
        for i in range(count):
            _idnum=((data["data"][i]['survey_id']))
            survey_id.append(_idnum)
            survey__id = len(survey_id)
        flag=0
        for j in range(survey__id):
            if str(survey) == str(survey_id[j]):
                flag=1
                counter=j
                break
        if(flag == 1):
            global intent
            intent=4
            global resume
            resume=4
            id_num=((data["data"][counter]['_id']))
            global short_description
            short_description=((data["data"][counter]["introduction_text"]))
            api= "http://openeyessurveys-api.devbyopeneyes.com/public/api/questions/" + str(id_num)
            headers = {'Authorization': 'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
            rs = requests.get(url=api)
            #rs = requests.get(url=api,headers=headers)
            #rs = requests.get(url = URL, headers = headers)
            #global datas
            datas= rs.json()
            #global ques 
            ques=((datas["data"][attr["counter"]]["question_text"]))
            #ques_type=((datas["data"][attr["counter"]]["question_type"]))
            #question_type = (ques_type["display_text"])
            #options=len((datas["data"][attr["counter"]]["options"]))

            speech_output= ques + "Let's begin openeyes Survey, okay?"
            #handler_input.attributes_manager.session_attributes = attr
        #else:
            #speech_output="I cannot find Survey I D . Let's try one more time. Please tell me your Survey I D"
        
        return (
            handler_input.response_builder
            .speak(speech_output)
            .ask("Please tell me your Survey I D")
            .response
            )

'''
class QuestionIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("QuestionIntent")(handler_input) 
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        answer=get_slot_value( 
            handler_input=handler_input, slot_name="answer")
        try:
            global dictionary
            dictionary={}
            global intent
            intent=5
            global resume
            resume=5
            global ques 
            #question_id=((datas["data"][attr["counter"]-1]["_id"]))
            ques=((datas["data"][attr["counter"]]["question_text"]))
            ques_type=((datas["data"][attr["counter"]]["question_type"]))
            #question_type_id=((datas["data"][attr["counter"]]["question_type_id"]))
            options=len((datas["data"][attr["counter"]]["options"]))
            question_type = (ques_type["display_text"])
            options_keys=[]
            response=[]
            if str(question_type) == "MCQ with multiple selection":
                dictionary.clear()
                mcq_options.clear()
                for i in range(options):
                    options=((datas["data"][attr["counter"]]["options"]))
                    mcq = (options[i]["option_text"])
                    mcq_options.append(mcq)
                options=len((datas["data"][attr["counter"]]["options"]))
                for i in range(options):
                    options=((datas["data"][attr["counter"]]["options"]))
                    option_key = (options[i]["option_key"])
                    options_keys.append(option_key)
                dictionary = dict(zip(options_keys, mcq_options))       
                speech_output = ques +str(dictionary)
                attr["counter"] += 1
                handler_input.attributes_manager.session_attributes = attr
            elif str(question_type) == "Short Answer":
                dictionary.clear()
                mcq_options.clear()
                attr["counter"] += 1
                handler_input.attributes_manager.session_attributes = attr
                speech_output=ques
            elif str(question_type) == "Descriptive":
                dictionary.clear()
                mcq_options.clear()
                attr["counter"] += 1
                handler_input.attributes_manager.session_attributes = attr
                speech_output=ques
            elif str(question_type) == "MCQ":
                dictionary.clear()
                mcq_options.clear()
                for i in range(options):
                    options=((datas["data"][attr["counter"]]["options"]))
                    mcq = (options[i]["option_text"])
                    mcq_options.append(mcq)
                options=len((datas["data"][attr["counter"]]["options"]))
                for i in range(options):
                    options=((datas["data"][attr["counter"]]["options"]))
                    option_key = (options[i]["option_key"])
                    options_keys.append(option_key)
                dictionary = dict(zip(options_keys, mcq_options))       
                speech_output = ques +str(dictionary)
                attr["counter"] += 1
                handler_input.attributes_manager.session_attributes = attr
            elif str(question_type) == "Dropdown with single selection":
                dictionary.clear()
                mcq_options.clear()
                for i in range(options):
                    options=((datas["data"][attr["counter"]]["options"]))
                    mcq = (options[i]["option_text"])
                    mcq_options.append(mcq)
                options=len((datas["data"][attr["counter"]]["options"]))
                for i in range(options):
                    options=((datas["data"][attr["counter"]]["options"]))
                    option_key = (options[i]["option_key"])
                    options_keys.append(option_key)
                dictionary = dict(zip(options_keys, mcq_options))       
                speech_output = ques +str(dictionary)
                attr["counter"] += 1
                handler_input.attributes_manager.session_attributes = attr
            else:
                dictionary.clear()
                mcq_options.clear()
                speech_output = ques
                attr["counter"] += 1
                handler_input.attributes_manager.session_attributes = attr
            
            if str(answer) in str(options_keys):
                option_keys=len(options_keys)
                for i in range(option_keys):
                    if str(answer) == str(options_keys[i]):
                        options=((datas["data"][i]["options"]))
                        mcqs = (options[i]["option_details"])
                        question_option_id = (options[i]["_id"])
                        url="http://openeyessurveys-api.devbyopeneyes.com/public/api/question-response"    
                        headers = {'Authorization': 'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
                        myobj = {
                                "response":[{
                                            	"question_id":question_id,
                                            	"platform_id":"602a2eae27e5ac1f5c8e8983",
                                            	"question_option_id":question_option_id,
                                            	"question_type_id":question_type_id,
                                            	"response_text":mcqs,
                                            	"ip_address":"null"
                                            	}]
                                }
                        y = requests.post(url,headers=headers,data=json.dumps(myobj))
                        resp=y.json()
            else:
                if str(answer) in str(mcq_options):
                    option_keys=len(options_keys)
                    for i in range(option_keys):
                        if str(answer) == str(mcq_options[i]):
                            options=((datas["data"][i]["options"]))
                            mcqs = (options[i]["option_details"])
                            question_option_id = (options[i]["_id"])
                            url="http://openeyessurveys-api.devbyopeneyes.com/public/api/question-response"    
                            headers = {'Authorization': 'mNIPg8r7wMnOhnQByiX1KpwjHwz3CzCnr7O9hQY0uZ1AXcwGcFVnxApaFKIY6Rs0keYaaVyoH1gaTqTBgQX2b1YRLVIlFdQfDCHLcWzRdxO7pCJlcV0aqaeYEJSABoXS'}
                            myobj = {
                                    "response":[{
                                                	"question_id":question_id,
                                                	"platform_id":"602a2eae27e5ac1f5c8e8983",
                                                	"question_option_id":question_option_id,
                                                	"question_type_id":question_type_id,
                                                	"response_text":answer,
                                                	"ip_address":"null"
                                                	}]
                                    }
                            y = requests.post(url,headers=headers,data=json.dumps(myobj))
                            resp=y.json()
            
        except IndexError:
            speech_output="Thank You for taking our survey, if you would like to take another survey please say the SurveyID or say exit or stop to end the survey."
        return (
            handler_input.response_builder
            .add_directive(directive = dialog.ElicitSlotDirective(
                        slot_to_elicit = 'answer'
                        )
                    )
            .speak(speech_output)
            .ask(speech_output)
            .response
            )
            
class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)
    
    def handle(self, handler_input):
        #language_prompts = handler_input.attributes_manager.request_attributes
        attr = handler_input.attributes_manager.session_attributes
        if intent==0:
            speech_output="I said...Welcome to OpenEyes' Surveys, the world's largest database of surveys by voice Please tell me your Survey I D ?"
        #elif intent==1:
            #speech_output = attr["repeat_speech_output"]
        elif intent==2:
            speech_output= "I said..." + ques + str(dictionary)
        elif intent==3:
            speech_output="I said...Welcome to OpenEyes' Surveys, the world's largest database of surveys by voice Please tell me your Survey I D ?"
        elif intent==5:
            speech_output= "I said...Thank you for using OpenEyes Survey, please rate our skill in the your Alexa app. Goodbye"
        else:
            speech_output="Just say, “Alexa repeat” for me to repeat the last thing I said. If you want to continue then say “Resume”"
        
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(speech_output)
                .response
            )

class HomeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HomeIntent")(handler_input)
    
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        if intent==4:
            speak_output="Just say, “Alexa home” for me to end the skill. If you want to continue then say “Resume”"
        else:
            attr["counter"]= 0
            speak_output = "Welcome to OpenEyes' Surveys, the world's largest database of surveys by voice Please tell me your Survey I D ?" 
            
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
            )
    
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global intent
        intent=4
        help_=get_slot_value( 
            handler_input=handler_input, slot_name="help")
        if help_ == "options":
            speak_output="Help Options Include: Repeat, Home, Stop Or you can resume what you were doing."
        elif help_ == "repeat":
            speak_output="Just say, “Alexa repeat” for me to repeat the last thing I said"
        elif help_ == "stop":    
            speak_output="Just say, “Alexa Stop” for me to end the skill."
        elif help_ == "resume":
            speak_output = "If you need further assistance you can contact us through your Alexa app."
        elif help_ == "home":
            speak_output = "Just say, “Alexa home” for me to return to the start of the skill”"
        else:
            speak_output="Sorry? I don't understand. Hoe may I help you?"
        return (
            handler_input.response_builder
            .add_directive(directive = dialog.ElicitSlotDirective(
                        slot_to_elicit = 'help'
                        )
                    )
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class StopIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        if intent==4:
            speak_output="Just say, “Alexa Stop” for me to end the skill. If you want to continue then say “Resume”"
        else:
            speak_output = "Thank you for using OpenEyes Survey, please rate our skill in the your Alexa app. Goodbye"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                #.ask(speak_output)
                .response
        )
class PauseIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        speak_output =  "okay"
        
        return (
            handler_input.response_builder
            .speak(speak_output)
            .ask(speak_output)
            .response
        )

class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for Resume Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        if resume==0:
            speech_output="Welcome back...Welcome to OpenEyes' Surveys, the world's largest database of surveys by voice Please tell me your Survey I D ?"
        elif resume==1:
            speech_output = "Welcome back..." + short_description + "Let's begin openeyes Survey, okay?"
        elif resume==2:
            speech_output= "Welcome back..." + ques + str(dictionary)
        elif resume==3:
            speech_output="Welcome back...Welcome to OpenEyes' Surveys, the world's largest database of surveys by voice Please tell me your Survey I D ?"
        elif resume==5:
            speech_output= "Welcome back...Thank you for using OpenEyes Survey, please rate our skill in the your Alexa app. Goodbye"
        else:
            speech_output="If you need further assistance you can contact us through your Alexa app."
        
        return (
            handler_input.response_builder
                .speak(speech_output)
                .ask(speech_output)
                .response
        )


class RepeatInterceptor(AbstractResponseInterceptor):

    def process(self, handler_input, response):
        attr = handler_input.attributes_manager.session_attributes
        attr["repeat_speech_output"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        try:
            attr["repeat_reprompt"] = response.reprompt.output_speech.ssml.replace("<speak>","").replace("</speak>","")
        except:
            attr["repeat_reprompt"] = response.output_speech.ssml.replace("<speak>","").replace("</speak>","")
'''
class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
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
        speak_output = "You just triggered " + intent_name + "."

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

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(SurveyIntentHandler())
#sb.add_request_handler(QuestionIntentHandler())
#sb.add_request_handler(RepeatIntentHandler())
#sb.add_request_handler(HomeIntentHandler())
#sb.add_request_handler(HelpIntentHandler())
#sb.add_request_handler(StopIntentHandler())
#sb.add_request_handler(PauseIntentHandler())
#sb.add_request_handler(ResumeIntentHandler())
#sb.add_global_response_interceptor(RepeatInterceptor())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()