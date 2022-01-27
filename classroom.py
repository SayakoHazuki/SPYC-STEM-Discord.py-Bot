import json
from googleapiclient.errors import HttpError

import time
from datetime import datetime, timedelta, timezone

import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Move Function to thread so that it wont block other scripts

import functools
import typing
import asyncio


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper

# ===== Google API Authorization =====


# Google API Scopes
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
          'https://www.googleapis.com/auth/classroom.course-work.readonly',
          'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly']


async def authAndGetService():
    creds = None
    service = None
    # If token.json exists, read the token
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

    service = build('classroom', 'v1', credentials=creds)
    print('[Google Classroom API] Authorized')
    return service


@to_thread
def fetchAssignments(service):
    try:
        print('Getting assignments from Google Classroom API...')
        # Get active courses list
        results = service.courses().list(
            pageSize=35, courseStates=['ACTIVE']).execute()

        # Get Courses List from the request response
        courses = results.get('courses', [])

        # Print 'No courses found' of no active courses were found
        if not courses:
            return 'No courses found'

        # ===== Get assignment lists for all courses =====
        courseWorkList = []

        # Get assignment list from every course in the course list
        for course in courses:
            results = service.courses().courseWork().list(
                courseId=course['id'], orderBy='dueDate', pageSize=5).execute()

            assignments = results.get('courseWork')

            # Add the assignments retreived into courseWorkList[]
            if assignments:
                courseWorkList.append(assignments[0])
        # Now assignmentList[] contains all assignments from all courses
        # We have to sort the list by due date/time using the following code
        sortedAssignments = sortByDue(courseWorkList)

        # In order to only keep the assignments that haven't been turned in yet
        # We need to get the states for each assignment
        mySubmissions = []
        for assignment in sortedAssignments:
            assignmentState = service.courses().courseWork().studentSubmissions().list(
                courseId=assignment['courseId'], courseWorkId=assignment['id'], userId='me').execute()
            mySubmissions.append(assignmentState)

        # Now mySubmissions[] contains studentSubmissions for all the assignments
        #   (For studentSubmissions refer to the docs at https://developers.google.com/classroom/reference/rest/v1/courses.courseWork.studentSubmissions?hl=en#StudentSubmission)

        # remove all the submitted work from sortedAssignments[]
        for assignment in mySubmissions:
            if (assignment["studentSubmissions"][0]["state"] == 'RETURNED') or (assignment["studentSubmissions"][0]["state"]) == 'TURNED_IN':
                assignmentId = assignment["studentSubmissions"][0]["courseWorkId"]
                sortedAssignments = [
                    d for d in sortedAssignments if d.get('id') != assignmentId]

        # converts result to string and save to savedAssignments.json
        resultsStrArr = []
        for i in sortedAssignments:
            resultsStrArr.append(json.dumps(i))

        with open('savedAssignments.json', 'w') as l4Json:
            l4Json.write('[\n\t{}\n]'.format(',\n\t'.join(resultsStrArr)))

        print(
            'Finished getting assignments, assignment list saved to savedAssignments.json')
        return sortedAssignments

    # on HttpError
    except HttpError as error:
        print('An error occurred: {}'.format(error))


def sortByDue(list):
    return sorted(list,
                  key=lambda d: '{}{}{}{}{}'.format(d['dueDate']['year'],
                                                    f"{d['dueDate']['month']:02d}",
                                                    f"{d['dueDate']['day']:02d}",
                                                    f"{d['dueTime']['hours'] if 'hours' in d['dueTime'] else 23:02d}",
                                                    f"{d['dueTime']['minutes'] if 'minutes' in d['dueTime'] else 59:02d}") if 'dueDate' in d else '999999999999', reverse=False)


def timestampFromDue(assignment):
    due = {
        "y": assignment["dueDate"]["year"],
        "m": assignment["dueDate"]["month"],
        "d": assignment["dueDate"]["day"],
        "h": assignment["dueTime"]["hours"] if 'dueTime' in assignment and 'hours' in assignment["dueTime"] else 23,
        "min": assignment["dueTime"]["minutes"] if 'dueTime' in assignment and 'minutes' in assignment["dueTime"] else 59,
    }
    dueDatetime = '<t:{}:f>'.format(int(time.mktime(datetime(
        due["y"], due["m"], due["d"], due["h"], due["min"], 0, 0).timetuple()))+28800)
    return dueDatetime
