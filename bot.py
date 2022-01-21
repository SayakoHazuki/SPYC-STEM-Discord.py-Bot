# imports

from __future__ import print_function
import json
import os.path
import discord
from discord.ext import commands

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

client = discord.Client()
bot = commands.Bot(command_prefix='!')


@client.event
# on bot ready
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@bot.command()
# on test command
async def test(ctx):
    await ctx.send('test')

# Google API Scopes
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.course-work.readonly',
          'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly']


def getAssignmentList():
    # ======== Authorization (Google API) ========
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        # Refresh Token if token is expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # Generate OAuth2 Client token if token is not present
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=59821)

        # Save new token to token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # ======== Run if authorized: ========
    try:
        # Build the Classroom Service
        service = build('classroom', 'v1', credentials=creds)

        # Get active courses list
        results = service.courses().list(
            pageSize=35, courseStates=['ACTIVE']).execute()

        # Get Courses List from the request response
        courses = results.get('courses', [])

        # Print 'No courses found' of no active courses were found
        if not courses:
            print('No courses found.')
            return

        # ===== Get assignment lists for all courses =====
        courseWorkList = []

        # Get assignment list from every course in the course list
        for course in courses:
            assignments = service.courses().courseWork().list(
                courseId=course['id'], orderBy='dueDate', pageSize=5).execute()

            # Add the assignments retreived into courseWorkList[]
            courseWorkList.append(assignments)
            print('Retrieved assignment list for {}'.format(course['name']))

        # In courseWorkList[], assignments for each course is saved courseWork{}
        # Which means:
        #   courseWorkList = [ { "courseWork" : [ assignment{}, assignment{}, ...] } ]
        # Therefore we need to convert it into a list of assignments : [ assignment{}, assignment{}, ...]
        assignmentList = []
        for courseWork in courseWorkList:
            if courseWork:
                for work in courseWork["courseWork"]:
                    assignmentList.append(work)

        # Now assignmentList[] contains all assignments from all courses
        # We have to sort the list by due date/time using the following code
        sortedAssignments = sorted(assignmentList,
                                   key=lambda d: '{}{}{}{}{}'.format(d['dueDate']['year'],
                                                                     f"{d['dueDate']['month']:02d}",
                                                                     f"{d['dueDate']['day']:02d}",
                                                                     f"{d['dueTime']['hours'] if 'hours' in d['dueTime'] else 23:02d}",
                                                                     f"{d['dueTime']['minutes'] if 'minutes' in d['dueTime'] else 59:02d}") if 'dueDate' in d else '999999999999', reverse=False)

        # In order to only keep the assignments that haven't been turned in yet
        # We need to get the states for each assignment
        mySubmissions = []
        print('processing assignments:')
        for assignment in sortedAssignments:
            assignmentState = service.courses().courseWork().studentSubmissions().list(
                courseId=assignment['courseId'], courseWorkId=assignment['id'], userId='me').execute()
            mySubmissions.append(assignmentState)
            print(assignment["title"])

        # Now mySubmissions[] contains studentSubmissions for all the assignments
        #   (For studentSubmissions refer to the docs at https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions?hl=en#StudentSubmission)

        # remove all the submitted work from sortedAssignments[] 
        for assignment in mySubmissions:
            if (assignment["studentSubmissions"][0]["state"] == 'RETURNED') or (assignment["studentSubmissions"][0]["state"]) == 'TURNED_IN':
                assignmentId = assignment["studentSubmissions"][0]["courseWorkId"]
                sortedAssignments = [
                    d for d in sortedAssignments if d.get('id') != assignmentId]

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
# client.run(secrets["token"])

getAssignmentList()
