export const environment = {
  production: false,
  apiServerUrl: 'https://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'fsnd-cfikido3.us', // the auth0 domain prefix
    audience: 'coffeeshop', // the audience set for the auth0 app
    clientId: 'xigFGiZrGW5vn0GG8AMsinZsDJHW2Tf6', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:8100/login-results', // the base url of the running ionic application. 
  }
};
