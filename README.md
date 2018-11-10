# chat_bot

A general chat bot application developed using AWS services - lambda, API Gateway, S3, Amazon Lex, SQS, DynamoDB, SNS
 
To access the application refer to the link-

https://dinnerchatassistant.auth.us-east-1.amazoncognito.com/login?response_type=token&client_id=5m3dsk8lurj87p57c8ohvpep91&redirect_uri=https://s3.amazonaws.com/chat-bot-web-app/index.html

The Chat bot is used as a dining suggestion application that suggest the best restaurants available as per user location to  book a table.

It finds all the necessary details via the chat bot agent and looks for the best restaurants in the city. The bot notifies of the best restaurant available through
a SMS to the user.