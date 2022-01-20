from __future__ import print_function

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os.path

import discord
from discord.ext import commands

import json

client = discord.Client()
bot = commands.Bot(command_prefix='!')

# on bot ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

# on test command
@bot.command()
async def test(ctx):
    await ctx.send('test')

# Google API Scopes
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.course-work.readonly',
          'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly']


def getAssignmentList():
    # Authorization (Google API)
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=59821)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Run if authorized:
    try:
        service = build('classroom', 'v1', credentials=creds)

        # Get courses list
        results = service.courses().list(
            pageSize=35, courseStates=['ACTIVE']).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return

        # Get assignment lists for all courses
        courseWorkList = []
        for course in courses:
            assignments = service.courses().courseWork().list(
                courseId=course['id'], orderBy='dueDate', pageSize=5).execute()
            courseWorkList.append(assignments)
            print('Retrieved assignment list for {}'.format(course['name']))

        # converts to list of assignments(dicts)
        assignmentList = []
        for courseWork in courseWorkList:
            if courseWork:
                for work in courseWork["courseWork"]:
                    assignmentList.append(work)

        # sort the list by due date/time
        sortedAssignments = sorted(lf,
                    key=lambda d: '{}{}{}{}{}'.format(d['dueDate']['year'],
                                                      f"{d['dueDate']['month']:02d}",
                                                      f"{d['dueDate']['day']:02d}",
                                                      f"{d['dueTime']['hours'] if 'hours' in d['dueTime'] else 23:02d}",
                                                      f"{d['dueTime']['minutes'] if 'minutes' in d['dueTime'] else 59:02d}") if 'dueDate' in d else '999999999999', reverse=False)

        # get submission states for all assignments in the list
        mySubmissions = []
        print('processing assignments:')
        for assignment in sortedAssignments:
            assignmentState = service.courses().courseWork().studentSubmissions().list(
                courseId=assignment['courseId'], courseWorkId=assignment['id'], userId='me').execute()
            mySubmissions.append(assignmentState)
            print(assignment["title"])

        # remove all submitted work from sortedAssignments[]
        for assignment in mySubmissions:
            if (assignment["studentSubmissions"][0]["state"] == 'RETURNED') or (assignment["studentSubmissions"][0]["state"]) == 'TURNED_IN':
                assignmentId = assignment["studentSubmissions"][0]["courseWorkId"]
                sortedAssignments = [d for d in l2 if d.get('id') != assignmentId]

        # converts result to string and save to l4.json
        resultsStrArr = []
        for i in sortedAssignments:
            resultsStrArr.append(json.dumps(i))

        with open('l4.json', 'w') as l4Json:
            l4Json.write('[{}]'.format(','.join(resultsStrArr)))

    # on HttpError
    except HttpError as error:
        print('An error occurred: %s' % error)

# load secrets (json)
f = open('secrets.json')
secrets = json.load(f)

# run the bot
client.run(secrets["token"])

