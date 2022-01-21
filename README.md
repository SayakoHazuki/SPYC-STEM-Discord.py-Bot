**INCOMPLETED**

##### Current progress:
- [x] function to retrieve to-do assignments
- [ ] bot command to send the assignment list
- [ ] bot command to get the timetable
- [ ] ...

the `getAssignmentList()` function in bot.py will retrieve all unsubmitted assignments from Google Classroom and saves to l4.json

**It may take around 1 minute to retrieve the list of unsubmitted assignments** (currently trying to reduce the time)

#### Set-up
- requires: Google API OAuth2 Token (stored as `./credentials.json`)
- discord bot (token stored in `./secrets.json`)

```js
// secrets.json
{"token":"yourTokenHere"}
```

##### To get google api credentials:
Google Cloud Platform
https://console.cloud.google.com/

1. Create a new project for 'web application'
2. In the Libraries tab (under API & Services) search for 'Google Classroom API' and enable it
3. In the Credentials tab (just below the Libraries tab), press 'Create Credentials' and choose OAuth client ID
4. Set application type to 'web application', under the 'Authorized redirect URIs field add uri 'https://localhost:59821/
5. Press Create and wait for a pop-up menu which says 'OAuth client created'. In the menu press 'DOWNLOAD JSON'
6. Move the downloaded file to your working directory and rename it as `credentials.json`
7. run `py .\bot.py` in command prompt/terminal
8. A browser window will pop up, sign in and authorize using the school account (pyc19xxx@school.pyc.edu.hk)
