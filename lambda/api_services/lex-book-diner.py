import json
import boto3

lex_client = boto3.client('lex-runtime')


def lambda_handler(event, context):
    for message in event["messages"]:
        text = message["unstructured"]["text"]
        text = text.lower()

    inputText = text
    print('Testing for input {}'.format(inputText))

    sessionAttributes = event["sessionAttributes"]

    response = lex_client.post_text(
        botName="BookDiner",
        botAlias="BookDiner",
        userId="John",
        sessionAttributes=sessionAttributes,
        inputText=inputText
    )

    print(response);

    return response
    # return construct_client_response(response)


def construct_client_response(response):
    message = response["message"]
    return {
        'statusCode': str(200),
        'message': message,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }