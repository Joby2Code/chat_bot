import json

wordmap = {};


def _createWordMap():
    wordmap["hello"] = ["Hello,Greetings, Nice to meet you!, How are you?"]
    wordmap["help"] = ["How may I help you?, What products are you interested in ?"]
    wordmap["thank"] = ["You are welcome"]


def lambda_handler(event, context):
    _createWordMap();
    print(event["messages"]);
    for message in event["messages"]:
        text = message["unstructured"]["text"]

    response = wordmap[text]

    return {
        "response": response
    }
