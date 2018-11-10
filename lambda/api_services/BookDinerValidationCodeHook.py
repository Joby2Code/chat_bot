import json
import datetime
import time
import os
import dateutil.parser
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --Helper Functions to build response

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response



# --Helper Functions
def try_ex(func):
    try:
        return func()
    except KeyError:
        return None


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_text(text):
    if not text or not text.isalpha():
        return False
    else:
        return True
        
def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland']
    return city.lower() in valid_cities


def isvalid_date(date):
    print('inside date validation...')
    try:
        datetime.strptime(date, '%m/%d/%Y')
        return True
    except ValueError:
        return False
        
def isvalid_cuisine(cuisine):
    cuisine_types = ['asian', 'thai', 'american', 'mexican', 'chinese', 'indian']
    return cuisine.lower() in cuisine_types
    

# --def validateGreetings

def validateGreetings(slots):
    '''
    validation of the greeting intents
    '''
    name = try_ex(lambda: slots['Name'])
    if name:
        if not isvalid_text(name):
            logger.debug('name {} input is invalid'.format(name))
            return build_validation_result(
                False,
                'Name',
                'Name {} has invalid characters, Please try again!'.format(name)
                )
        else:
            logger.debug('Name {} is valid'.format(name))
            return {'isValid': True}
    
    else:
        logger.debug('name {} input is invalid'.format(name))
        return build_validation_result(
                False,
                'Name',
                'Greetings, May I know your first name please.?'
                )

def validateThankYouIntent(slots):
    pass


def validateDinningSuggestionsIntent(slots):
    '''
    To check for the slots in DiningSuggestionsIntent
    '''
    location = try_ex(lambda: slots['Location'])
    date = try_ex(lambda: slots['Date'])
    cuisine = try_ex(lambda: slots['Cuisine'])
    time = try_ex(lambda: slots['Time'])
    number = try_ex(lambda: slots['Number'])
    
    print('Location in validateDinningSuggestionsIntent',location)
    
    if not location:
        return build_validation_result(
            False,
            'Location',
            'Where would you like to dine?'
        )
    
    if not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support the city {}, Please try with a different city'.format(location)
        )
    
    print ('Validating Date', date)
    
    if date:
        if not isvalid_date(date):
            return build_validation_result(
                False,
                'Date',
                '{} date is invalid, Please enter the date in mm/dd/yyyy format.'.format(date)
                )
        
    if not date:
        return build_validation_result(
            False,
            'Date',
            'When would you like to book the table? Enter the date in mm/dd/yyyy format.'
        )
    
    
    
    if not cuisine:
        return build_validation_result(
            False,
            'Cuisine',
            'What cuisine do you prefer?'
        )
    
    if not isvalid_cuisine(cuisine):
        return build_validation_result(
            False,
            'Cuisine',
            'We currently do not support the suisine {}, Please try a different option'.format(location)
        )
    #Apply validations for number, time change the slot type to address    
    return {'isValid': True}
 
    
# ---Intents---

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug(
        'dispatch userID: {},intentName:{} '.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    logger.debug('Session Attribute {}'.format(session_attributes))
    print(intent_request)
    # Dispatch to intents
    if intent_request['invocationSource'] == 'DialogCodeHook':

        if (intent_name == 'GreetingsIntent'):
            logger.debug('Validating slots for GreetingsIntent....')
            validation_result = validateGreetings(intent_request['currentIntent']['slots'])

        elif (intent_name == 'ThankYouIntent'):
            validation_result = validateThankYouIntent(intent_request['currentIntent']['slots'])

        elif (intent_name == 'DiningSuggestionsIntent'):
            logger.debug('Validating slots for DiningSuggestionsIntent....')
            validation_result = validateDinningSuggestionsIntent(intent_request['currentIntent']['slots'])
            

        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        else:
            return delegate(
                session_attributes,
                intent_request['currentIntent']['slots']
                )
    else:
        pass
    
# Main Halder for validations
def lambda_handler(event, context):
    """
    Route incoming request based on intent

    """
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    print(event)
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)

    