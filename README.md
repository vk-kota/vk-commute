# vk-commute
Python Dash App for TFL Tube status and Santander bike dock status.

## Deployment
The app can be deployed locally using Dash's built-in Flask server. If you want to do this, delete the line below from [app.py]():
  server = app.server()
  
To use Heroku, follow the steps below:
  $ heroku create APP-NAME # Choose a name for your app
  $ git push heroku master
  $ heroku ps:scale web=1


