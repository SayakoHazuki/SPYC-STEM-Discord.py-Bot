# Google Classroom Discord Bot

## Commands:
### $timetable [Day] [Class]
- Get timetable  
##### Parameters:
- Day: [Optional] Day of cycle (e.g. A)  
    - default: Day of cycle of today
- Class: [Optional] Your class (e.g. 1A)  
    - default: class in `config.json`

The bot will reply with the timetable list.

### $assignments
- Get assignment list

## Set-up
- requires: Google API OAuth2 Token (stored as `./credentials.json`)
- discord bot (token stored in `./secrets.json`)

```js
// secrets.json
{"token":"yourTokenHere"}
```

### Python dependencies
**Python 3** (recommended: latest stable version)  
google-api-python-client  
google-auth-httplib2  
google-auth-oauthlib
discord.py


### To get google api credentials:
1. Visit [Google Cloud Platform](https://console.cloud.google.com/) and sign in using **your personal account (not your school account)**
    - Only education accounts aged 18 or above / perseonal accounts aged 13 or above can access to this service
2. Create a new project for 'web application'
3. In the Libraries tab (under API & Services) search for 'Google Classroom API' and enable it
4. In the Credentials tab (just below the Libraries tab), press 'Create Credentials' and choose OAuth client ID
5. Set application type to 'web application', under the 'Authorized redirect URIs field add uri 'https:/6localhost:59821/
6. Press Create and wait for a pop-up menu which says 'OAuth client created'. In the menu press 'DOWNLOAD JSON'
7. Move the downloaded file to your working directory and rename it as `credentials.json`
8. run `py .\bot.py` in command prompt/terminal
9. A browser window will pop up, sign in and authorize using the school account (pyc19xxx@school.pyc.edu.hk)

### Creating a bot 
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create an application
3. In the bot tab, create a bot
4. In the URL Generator under OAuth2 Category in the sidebar, generate an URL and copy it
    - with scopes "Bot", "Messages.read" and "applications.commands"
    - with bot permission "Administrator"
5. In the bot tab, under Intents section, enable:
    - PRESENCE INTENT
    - SERVER MEMBERS INTENT
    - MESSAGE CONTENT INTENT
6. Go to the link obtained in step 4, complete the authorization to add the bot
