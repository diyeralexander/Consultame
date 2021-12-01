from typing import Any, Text, Dict,Union, List ## Datatypes
import logging
import json
from credentials import host, host_remote, database, database_remote, tablename,tablename_remote,tablenamefeedback,tablenamefeedback_remote, user,user_remote,password,password_remote

from pymongo import MongoClient
from rasa_sdk import Action, Tracker  ##
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import (SlotSet, UserUtteranceReverted, ActionReverted, FollowupAction,EventType)

import re

USER_INTENT_OUT_OF_SCOPE = "out_of_scope"
#client_db = MongoClient(credentials.host,port=credentials.port)
#internal_db = client_db[credentials.database]
#internal_collection = internal_db[credentials.tablename]
#internal_collection_feedback = internal_db[credentials.tablenamefeedback]

client_db_remote = MongoClient(host_remote)
internal_db = client_db_remote[database_remote]
internal_collection = internal_db[tablename_remote]
internal_collection_feedback = internal_db[tablenamefeedback_remote]



logger = logging.getLogger(__name__)

class ActionSearch(Action):

    def name(self) -> Text:
        return "action_search"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #Calling the DB
        #calling an API
        # do anything
        #all caluculations are done
        camera = tracker.get_slot('camera')
        ram = tracker.get_slot('RAM')
        battery = tracker.get_slot('battery')

        dispatcher.utter_message(text='Here are your search results')
        dispatcher.utter_message(text='The features you entered: ' + str(camera) + ", " + str(ram) + ", " + str(battery))
        return []
########################

class ActionRecoverUserInfo(Action):

    def name(self) -> Text:
        return "action_recover_user_info"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #Calling the DB
        #calling an API
        # do anything
        #all caluculations are done
        name = tracker.get_slot('name')
        email = tracker.get_slot('email')

        dispatcher.utter_message(text='Gracias muy pronto responderemos a tus inquietudes')
        dispatcher.utter_message(text='Tus datos: ' + str(name) + ", " + str(email))
        return []
########################

class ActionShowLatestNews(Action):

    def name(self) -> Text:
        return "action_show_latest_news"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #Calling the DB
        #calling an API
        # do anything
        #all caluculations are done
        dispatcher.utter_message(text='Here the latest news for your category')
        return []

class ActionMyFallback(Action):

    def name(self) -> Text:
        return "action_my_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        
        # Fallback caused by TwoStageFallbackPolicy
        last_intent = tracker.latest_message["intent"]["name"]
        #last_intent2 = tracker.latest_message.get('intent')[1].get('name')
        #intent_ranking = tracker.events[-1].parse_data.get('intent', [])
        #print(last_intent2)
        #print(intent_ranking)
        if last_intent in ["nlu_fallback", USER_INTENT_OUT_OF_SCOPE]:
            return []

        # Fallback caused by Core
        else:
            dispatcher.utter_message(template="utter_default")
            return [UserUtteranceReverted()]
       
       
       
       #dispatcher.utter_message(template= "utter_fallback")

        # Revert user message which led to fallback.
        #return [UserUtteranceReverted()]

class ActionSendQuestion(Action):
    def name(self) -> Text:
        return "action_send_question"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> None:

        dispatcher.utter_message(response = "utter_fallback")

class YourResidence(Action):

    def name(self) -> Text:
        return "action_your_residence"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #Calling the DB
        #calling an API
        # do anything
        #all caluculations are done
        dispatcher.utter_message(template="utter_residence")

        return [UserUtteranceReverted(),FollowupAction(tracker.active_form.get('name'))]

class TodayWeather(Action):

    def name(self) -> Text:
        return "action_today_weather"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #Calling the DB
        #calling an API
        # do anything
        #all caluculations are done
        dispatcher.utter_message(template="utter_weather")

        return [UserUtteranceReverted(),FollowupAction(tracker.active_form.get('name'))]


class ActionSubmitUserRegisterForm(Action):
    def name(self) -> Text:
        return "action_submit_user_register_form"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        """Once we have all the information, attempt to add it to the
        Mongo database"""

        import datetime

        nombre = tracker.get_slot("name")
        email = tracker.get_slot("email")
        pregunta = tracker.get_slot("pregunta")
        fecha = datetime.datetime.now()
        clase = 'co.gov.minenergia.domain.PreguntaSinRespuesta'
        user_info = [nombre, email, pregunta, fecha]

        try:
            #gdrive = GDriveService()
            #gdrive.append_row(
            #    gdrive.SALES_SPREADSHEET_NAME, gdrive.SALES_WORKSHEET_NAME, sales_info
            #)
            name = tracker.get_slot('name')
            email = tracker.get_slot('email')
            pregunta = tracker.get_slot('pregunta')
            if(len(name)==0 or len(email)==0 or len(pregunta)==0):
                dispatcher.utter_message(response="utter_questionrequest_failed")
                return [SlotSet('name',None),SlotSet('email',None),SlotSet('pregunta', None)]
            newQuestion = {"email":email, "nombre":name,"pregunta":pregunta,"fecha":fecha,"_class":clase}
            internal_collection.insert_one(newQuestion)
            print("Gracias {}, estaremos respondiendo tu pregunta {} a tu correo {}".format(name,pregunta,email))
            dispatcher.utter_message(response="utter_confirm_questionrequest")
            return [SlotSet('name',None),SlotSet('pregunta', None),SlotSet("shown_privacy", False)]
        except Exception as e:
            logger.error(
                f"Failed to write data to mongo. Error: {e.message}",
                exc_info=True,
            )
            dispatcher.utter_message(response="utter_questionrequest_failed")
            return []


class ValidateUserRegisterForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_user_register_form"

    def validate_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate num_people value."""
        #name length must be >= 3 characters

        try:
            name_length = int(len(value))
        except:
            name_length = 20000
        #Query the DB and check the max value, that way it can be dynamic
        if name_length >= 3 and name_length !=20000 and name_length <=100:
            return {"name":value}
        else:
            dispatcher.utter_message(response="utter_wrong_name")

            return {"name":None}

    def validate_pregunta(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate num_people value."""
        #pregunta length must be >= 10 characters

        try:
            name_length = int(len(value))
        except:
            name_length = 20000
        #Query the DB and check the max value, that way it can be dynamic
        if name_length >= 10 and name_length !=20000:
            return {"pregunta":value}
        elif name_length >500:
            dispatcher.utter_message(response="utter_wrong_pregunta_max")
            return {"pregunta":None}
        else:
            dispatcher.utter_message(response="utter_wrong_pregunta")
            return {"pregunta":None}


    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate email value."""
        # must be a valid email

        try:
            valid_email = re.findall(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',value)[0]
            print("This is my email" +valid_email)
        except:
            valid_email = ''
        #Query the DB and check the max value, that way it can be dynamic
        if len(valid_email) > 0:
            return {"email":valid_email}
        else:
            dispatcher.utter_message(response="utter_wrong_email")

            return {"email":None}




class ActionSaveFeedback(Action):
    def name(self) -> Text:
        return "action_save_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        """Once we have all the information, attempt to add it to the
        Mongo database"""

        import datetime

        calificacion_string = tracker.get_slot("calificacion_value")
        try:
            calificacion = int(calificacion_string)
        except:
            calificacion = 0
        fecha = datetime.datetime.now()
        clase = 'co.gov.minenergia.domain.RespuestaEncuesta'
        penultimun = []
        #Test code
        for event in tracker.events:
            if event.get("event") == "bot":
               try:
                   penultimun.append(event.get("text"))
                   #print("event : ", event.get("text"))
               except:
                   pass
        #penultimun = penultimun[-1]
        encuesta=''
        usuario= tracker.get_slot('email')
        if(len(penultimun)>0):
            print('penultimo: \n')
            print(penultimun[-1])
            encuesta = penultimun[-1]
        calificacion_info = [calificacion, fecha, encuesta,usuario]

        try:
            if(calificacion==0):
                dispatcher.utter_message(response="utter_feedbackrequest_failed")
                return [SlotSet('name',None),SlotSet('email',None),SlotSet('pregunta', None),SlotSet('calificacion_value', None)]
            newCalificacion = {"encuesta":encuesta,"calificacion":calificacion, "fecha":fecha,"usuario":usuario,"_class":clase}
            internal_collection_feedback.insert_one(newCalificacion)
            print("Gracias por tu calificacion {} ".format(calificacion))
            dispatcher.utter_message(response="utter_confirm_feedbackrequest")
            return [SlotSet('name',None),SlotSet('email',None),SlotSet('pregunta', None), SlotSet('calificacion', None),SlotSet("shown_privacy", False)]
        except Exception as e:
            logger.error(
                f"Failed to write data to mongo. Error: {e.message}",
                exc_info=True,
            )
            dispatcher.utter_message(response="utter_feedbackrequest_failed")
            return []


class ActionSetFaqSlot(Action):
    """Returns the chitchat utterance dependent on the intent"""

    def name(self) -> Text:
        return "action_set_faq_slot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        full_intent = (
            tracker.latest_message.get("response_selector", {})
            .get("faq", {})
            .get("full_retrieval_intent")
        )
        if full_intent:
            topic = full_intent.split("/")[1]
        else:
            topic = None

        return [SlotSet("faq", topic)]

class ActionGreetUser(Action):
    """Greets the user with/without privacy policy"""

    def name(self) -> Text:
        return "action_greet_user"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[EventType]:
        intent = tracker.latest_message["intent"].get("name")
        shown_privacy = tracker.get_slot("shown_privacy")
        name_entity = next(tracker.get_latest_entity_values("name"), None)
        if intent == "greet" or (intent == "enter_data" and name_entity):
            if shown_privacy and name_entity and name_entity.lower() != "consultame":
                dispatcher.utter_message(response="utter_greet_name", name=name_entity)
                return []
            elif shown_privacy:
                dispatcher.utter_message(response="utter_greet_noname")
                return []
            else:
                dispatcher.utter_message(response="utter_greet")
                dispatcher.utter_message(response="utter_inform_privacypolicy")
                return [SlotSet("shown_privacy", True)]
        return []

class ActionRestartWithButton(Action):
    def name(self) -> Text:
        return "action_restart_with_button"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> None:

        dispatcher.utter_message(response="utter_restart_with_button")