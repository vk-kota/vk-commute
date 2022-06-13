# vk-commute
Python Dash App for TFL Tube status and Santander bike dock status.

## Deployment

### Local deployment
The app can be deployed locally using Dash's built-in Flask server. If you want to do this, comment out line 192 in [app.py](https://github.com/vk-kota/vk-commute/blob/main/app.py). Follow the steps below:

1. Clone this repo locally and `cd` into the main folder.
2. Create a new Python virtual environment with the packages and versions mentioned in [requirements.txt](https://github.com/vk-kota/vk-commute/blob/main/app.py). `pip install` is recommended for `dash` because the default channel in `conda` may not have the correct version.
3. Run `app.py` using `python app.py`. This should start a server locally using the `Flask` server built into `dash`.
4. If step 3 above works, you can navigate to [127.0.0.1:8050](http://127.0.0.1:8050) and you should see the page being served.


### Remote deployment
  
To use Heroku, follow the steps below:

  + $ heroku create [app-name] 
  + $ git push heroku master
  + $ heroku ps:scale web=1


