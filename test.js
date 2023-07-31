var request = require('request');

request.post(
    'https://localhost:3000/start',
    { json: {  } },
    function (error, response, body) {
        if (!error && response.statusCode == 200) {
            console.log(body);
        }
    }
);


request.post(
  'https://localhost:3000/pause',
  { json: {  } },
  function (error, response, body) {
      if (!error && response.statusCode == 200) {
          console.log(body);
      }
  }
);