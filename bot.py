# ============= imports =============

from datetime import datetime
import logging
import json
import os.path
import re

import discord
from discord.ext import commands, tasks

from classroom import authAndGetService, fetchAssignments, timestampFromDue
from timetable import getDayOfCycle, getLessonList

configFile = open('config.json')
config = json.load(configFile)


# For debugging only ( can be excluded )

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

@tasks.loop(minutes=10)  # Repeat every 10 minutes
async def fetchAssignmentsTask(args):
    await fetchAssignments(args)  # fetch Assignments


@bot.event  # On bot ready
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    # Authorize Google Classroom API and get the API Service
    service = await authAndGetService()
    # Start fetching assignments every 10 minutes
    fetchAssignmentsTask.start(service)


# ========== Bot Commands ==========

@bot.command()  # Assignments command
async def assignments(ctx):
    assignmentsEmbed = discord.Embed(
        title="未繳交的作業", description="\t", color=0xF7DFA5)  # Creates the Message Embed

    assignments = []
    if os.path.exists('savedAssignments.json'):  # If savedAssignments.json exists
        with open('savedAssignments.json', 'r') as savedAssignments:
            # Read and load savedAssignments.json into assignments[]
            assignments = json.load(savedAssignments)

    # == Get Assignment List and Add Fields ==

    # If savedAssignments.json does not exist (Only when starting the bot for the first time)
    else:
        # Tells the user to wait for about 2 minutes
        return await ctx.send('初次獲取資料需時約2分鐘, 請稍後重新使用指令')

    # If no courses were found (usually impossible)
    if assignments == 'No courses found':
        # Tells the user that cannot find the courses
        return await ctx.send('找不到課程')

    # Add the first 24 assignments to the embed as fields
    #   P.S. 25 is the maximum limit of fields per Message Embed
    for assignment in assignments[:24]:
        dueDatetime = timestampFromDue(
            assignment) if 'dueDate' in assignment else '無截止日期'

        # Adds a field containing information of the assignment to the Message Embed
        assignmentsEmbed.add_field(
            name=assignment["title"], value='截止時間: {}\n[開啟作業]({})'.format(dueDatetime, assignment["alternateLink"]), inline=False)

    # Sends the message containing the Message Embed
    return await ctx.send(embed=assignmentsEmbed)


@bot.command()
async def timetable(ctx, arg1='', arg2=''):  # Timetable Command
    if arg1 and not re.match(r'[A-H]|today|tomorrow|tmr', arg1):
        # If the day received doesn't match the regex, warn the user
        return await ctx.send('不存在 Day {}'.format(arg1))

    arg1 = getDayOfCycle(True) if re.match(r'tomorrow|tmr', arg1) else arg1 or getDayOfCycle(False) 
    arg2 = arg2 or config["class"]

    if not arg1:  # Most likely won't happen
        return await ctx.send('發生了預期外的錯誤')

    if arg1 == '/':  # Tells the user if it's school holiday
        return await ctx.send('本日為學校假期')

    param = {'day': arg1, 'class_': arg2,
             'date': datetime.now().strftime('%d %B, %Y')}
    # Get the lesson list
    lessons = getLessonList(param['class_'], param['day'])

    if lessons[0] == None: # If lessons[0] is type Non, warn the user
        return await ctx.send('錯誤 : {}'.format(lessons[1]))

    embedFields = [] 
    i = 0

    for lesson in lessons:
        embedFields.append({'name': '第 {} 節'.format(
            i+1), 'value': '{}\n'.format(lesson), 'inline': False})
        i += 1

    timetableEmbed = discord.Embed(
        title='{class_}班時間表'.format(**param),
        description='{date} (Day {day})'.format(
            **param),
        color=0x03A4EC
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
