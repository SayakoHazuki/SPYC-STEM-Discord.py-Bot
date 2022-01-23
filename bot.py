# ============= imports =============

import json
import os.path
from sqlite3 import Timestamp
from webbrowser import get
import discord
from discord.ext import commands, tasks

from classroom import authAndGetService, fetchAssignments, timestampFromDue
from timetable import getLessonList

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# ============ Bot Config ============

intents = discord.Intents().all()  # Specify the bot intents
bot = commands.Bot(command_prefix='$',
                   intents=intents)  # Create the bot client
service = None  # Will be used to store Google Classroom API Service


# =========== Bot Events ===========

@tasks.loop(minutes=10)
async def fetchAssignmentsTask(args):
    await fetchAssignments(args)


@bot.event  # On bot ready
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    service = await authAndGetService()
    fetchAssignmentsTask.start(service)


# ========== Bot Commands ==========

@bot.command()  # Assignments command
async def assignments(ctx):
    assignmentsEmbed = discord.Embed(
        title="未繳交的作業", description="\t", color=0xF7DFA5)

    assignments = []
    if os.path.exists('savedAssignments.json'):
        with open('savedAssignments.json', 'r') as savedAssignments:
            assignments = json.load(savedAssignments)
    # Get Assignment List and Add Fields
    else:
        ctx.send('初次獲取資料需時約2分鐘, 請稍後重新使用指令')

    if assignments == 'No courses found':
        return ctx.send('No courses found')

    # Add the first 24 assignments to the embed as fields
    for assignment in assignments[:24]:
        dueDatetime = ''
        if 'dueDate' in assignment:
            dueDatetime = timestampFromDue(assignment)
        else:
            dueDatetime = 'No Due Date'
        assignmentsEmbed.add_field(
            name=assignment["title"], value='截止時間: {}\n[開啟作業]({})'.format(dueDatetime, assignment["alternateLink"]), inline=False)
    await ctx.send(embed=assignmentsEmbed)


@bot.command()
async def timetable(ctx, arg1 = 'None', arg2 = 'None'):
    if (arg1 == 'None' and arg2 == 'None') :
        return await ctx.send('請輸入班別以及Day')
    
    param = {'class_': arg1, 'day': arg2}
    lessons = getLessonList(param['class_'], param['day'])

    if lessons[0] == None:
        return ctx.send('ValueError : {}'.format(lessons[1]))

    print(lessons)
    embedFields = []
    i = 0

    for lesson in lessons:
        embedFields.append({'name': '第 {} 節'.format(
            i+1), 'value': '{}\n'.format(lesson), 'inline': False})
        i += 1

    timetableEmbed = discord.Embed(
        title='{class_}班 Day {day} 時間表'.format(**param)
    )

    for field in embedFields:
        timetableEmbed.add_field(**field)

    await ctx.send(embed=timetableEmbed)

# ========= Run(start) the bot =========

# load secrets (json)
f = open('secrets.json')
secrets = json.load(f)

# run the bot
bot.run(secrets["token"])
