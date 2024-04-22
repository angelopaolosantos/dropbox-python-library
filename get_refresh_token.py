import webbrowser
import base64
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
BASIC_AUTH = base64.b64encode(f'{APP_KEY}:{APP_SECRET}'.encode())

# ACCESS_CODE_GENERATED is initially empty. You need to run first with ACCESS_CODE_GENERATED = "" to get it. 
# Then paste it here or add to .env then run the second time to get the refresh token.
ACCESS_CODE_GENERATED = os.getenv('ACCESS_CODE_GENERATED')

if ACCESS_CODE_GENERATED != "":

    headers = {
        'Authorization': f"Basic {BASIC_AUTH}",
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = f'code={ACCESS_CODE_GENERATED}&grant_type=authorization_code'

    response = requests.post('https://api.dropboxapi.com/oauth2/token',
                            data=data,
                            auth=(APP_KEY, APP_SECRET))


    print(json.dumps(json.loads(response.text), indent=2))

else:
    url = f'https://www.dropbox.com/oauth2/authorize?client_id={APP_KEY}&' \
          f'response_type=code&token_access_type=offline'

    webbrowser.open(url)