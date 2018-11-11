const AWS = require('aws-sdk')
AWS.config.update({ region: 'us-east-1' })
const sqs = new AWS.SQS({ apiVersion: '2012-11-05' })
const ddb = new AWS.DynamoDB({ apiVersion: '2012-10-08' });
const yelp = require('yelp-fusion')
const sns = new AWS.SNS({ apiVersion: '2010-03-31' });

const QUEUE_URL = process.env.QUEUE_URL
const YELP_KEY = process.env.YELP_KEY
const DB_NAME = process.env.DB_NAME

const yelpClient = yelp.client(YELP_KEY)

exports.handler = async(event) => {
  const getParams = {
    AttributeNames: [
      "SentTimestamp"
    ],
    MaxNumberOfMessages: 10,
    MessageAttributeNames: [
      "All"
    ],
    QueueUrl: QUEUE_URL,
    VisibilityTimeout: 20,
    WaitTimeSeconds: 0,
  };
  try {
    const messages = await getSqsMessages(getParams)
    await Promise.all(messages.map(message => handleMessage(message)))
  }
  catch (err) {
    console.log(err)
  }

};

const handleMessage = (message) => {
  return new Promise((resolve, reject) => {
    const diningLocation = message.MessageAttributes['Location'].StringValue
    const diningCuisine = message.MessageAttributes['Cuisine'].StringValue
    const phoneNumber = message.MessageAttributes['Contact'].StringValue
    const peopleCnt = message.MessageAttributes['NumberOfPeople'].StringValue
    const diningDate = message.MessageAttributes['DiningDate'].StringValue
    const diningTime = message.MessageAttributes['DiningTime'].StringValue

    yelpClient.search({
      location: diningLocation,
      categories: diningCuisine,
    }).then(res => {
      let smsMessage
      if (res.jsonBody.businesses) {
        const restaurant = res.jsonBody.businesses[0]
        const restaurantName = restaurant.name
        const restaurantAddress = `${restaurant.location.address1} ${restaurant.location.city}`
        smsMessage = composeMessage(
          restaurantName, restaurantAddress, peopleCnt, diningDate, diningTime)
      }
      else {
        smsMessage = 'No result found'
      }
      return putIntoDB(smsMessage, message.MessageAttributes, phoneNumber)
    }).then((res) => {
      return sendSms(res.msg, res.phoneNumber)
    }).then(() => {
      const deleteParams = {
        QueueUrl: QUEUE_URL,
        ReceiptHandle: message.ReceiptHandle
      }
      return deleteSqsMessages(deleteParams)
    }).then(() => {
      resolve()
    })
  })

}

const getSqsMessages = (params) => {
  return new Promise((resolve, reject) => {
    sqs.receiveMessage(params, function(err, data) {
      if (err) {
        reject(err)
      }
      else if (data.Messages) {
        resolve(data.Messages)
      }
    });
  })
}

const deleteSqsMessages = (params) => {
  return new Promise((resolve, reject) => {
    sqs.deleteMessage(params, function(err, data) {
      if (err) {
        reject(err)
      }
      else {
        resolve()
      }
    })
  })
}

const composeMessage = (name, address, people, date, time) => {
  return `Yo, try ${name} at ${address} for ${people} people on ${date} at ${time}`
}

const putIntoDB = (smsMessage, userQuery, contactId) => {
  return new Promise((resolve, reject) => {
    const params = {
      TableName: DB_NAME,
      Item: {
        'ContactId': { S: contactId },
        'SmsMessage': { S: smsMessage },
        'UserQuery': {
          M: {
            'Locatoin': { S: userQuery['Location'].StringValue },
            'Date': { S: userQuery['DiningDate'].StringValue },
            'Time': { S: userQuery['DiningTime'].StringValue },
            'Cuisine': { S: userQuery['Cuisine'].StringValue },
            'NumberOfPeople': { S: userQuery['NumberOfPeople'].StringValue },
          }
        },
      }
    }
    ddb.putItem(params, function(err) {
      if (err) {
        reject(err)
      }
      else {
        resolve({ msg: smsMessage, phoneNumber: contactId })
      }
    })
  })
}

const sendSms = (msg, phoneNumber) => {
  const params = {
    Message: msg,
    PhoneNumber: `+1${phoneNumber}`,
  }
  return sns.publish(params).promise()
}
