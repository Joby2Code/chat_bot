
//var apigClient = apigClientFactory.newClient({});

/*var apigClient = apigClientFactory.newClient({
  accessKey: 'AKIAZT452VYZRYJWKQRC',
  secretKey: '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',
});*/

var API_KEY = 'oXljzw5a4X2KK3iWFWjkX1ASYmUrBx1kaDil0oCw';

/*var apigClient = apigClientFactory.newClient({
  apiKey: API_KEY
});*/



var params = {
  // This is where any modeled request parameters should be added.
  // The key is the parameter name, as it is defined in the API in API Gateway.
  param0: '',
  param1: ''
};




var additionalParams = {
  // If there are any unmodeled query parameters or headers that must be
  //   sent with the request, add them here.
  headers: {
    'Access-Control-Allow-Origin':'*'
  }
};


function postRequest(body) {
  var apigClient = apigClientFactory.newClient({});
  apigClient.chatbotPost(params, body, additionalParams)
    .then(function(result){
      text = parseServerResponse(result);
      insertChat("you", text);
    }).catch( function(result){
      console.log(result)
    });

}

function parseServerResponse(response){

  msg_list = response.data.message;

  if (msg_list === undefined) {
    text = "Sorry I dont have an answer right now!"
    return text;
  } 
  text = msg_list
  return text;
  
}


function generateRandomInteger(min, max) {
  return Math.floor(min + Math.random()*(max + 1 - min))
}
 
 