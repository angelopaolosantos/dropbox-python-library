################################################################
# DOWNLOAD ENTIRE FOLDER STRUCTURE FROM DROPBOX TO LOCAL DRIVE #
################################################################

# Instructions:
# (1) install dropbox API using pip
# > pip install dropbox

# (2) Create application to make requests to the Dropbox API
# - Go to: https://dropbox.com/developers/apps
# - Register your own App - e.g., call it "personal access to research data"
# - Copy secret *access token* after registering your app (click on get token)
#   Paste that access token to a file called *token_dropbox.txt*. 
#   Make sure you do not version this file on Git, as it would allow others
#   to obtain data from your Dropbox. For example, you can add that file name
#   to .gitignore.

import dropbox
from get_dropbox import get_files, get_folders
import os
from dotenv import load_dotenv

load_dotenv()

print('Authenticating with Dropbox...')

## Authenticate with Dropbox using an access token
## Read access token from file or .env

# access_token = open('token_dropbox.txt').read()
# or
# access_token = os.getenv('ACCESS_TOKEN')

# dbx = dropbox.Dropbox(access_token)

## Authenticate with Dropbox using an refresh token
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

dbx = dropbox.Dropbox(
            app_key = APP_KEY,
            app_secret = APP_SECRET,
            oauth2_refresh_token = REFRESH_TOKEN
        )

print('...authenticated with Dropbox owned by ' + dbx.users_get_current_account().name.display_name)

# (3) Obtain ID of folder that needs to be downloaded
#   folders = get_folders(), which generates a list with ID numbers for each folder
#   in your Dropbox (may take some time!!!)
#   Specifiy a path (if you know that path) for a directory "close" to your target
#   directory. Otherwise, this script will loop through the *entire* file structure
#   of your Dropbox, which will take a lot of time.

## examples:
# folders=get_folders(dbx, 'myfolder/mysubfolder/')
# folders=get_folders(dbx, '')

# Let's take a look at these folder IDs
# print(folders)

# Select target folder and copy desired folder ID below, empty "" for root folder
# folder_id = 'id:LaTKfbmvyLwAAAAAAAEbdA'
folder_id = ""

# Set target download directory on your local computer; ends with (e.g., raw_data/, 'D:/dropbox/')
download_dir = os.getenv('DOWNLOAD_DIR')

##################
# DOWNLOAD FILES #
##################

# obtain list of files of target dir
print('Obtaining list of files in target directory...')
get_files(dbx, folder_id, download_dir)