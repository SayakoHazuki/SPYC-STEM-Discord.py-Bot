# ============= imports =============

from datetime import datetime
import logging
import json
import os.path
import re
from sqlite3 import Timestamp
from webbrowser import get
import discord
from discord.ext import commands, tasks

from classroom import authAndGetService, fetchAssignments, timestampFromDue
from timetable import getDayOfCycle, getLessonList

configFile = open('config.json')
config = json.load(configFile)


# For debugging only

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
        return await ctx.send('初次獲取資料需時約2分鐘, 請稍後重新使用指令')

    if assignments == 'No courses found':
        return await ctx.send('找不到課程')

    # Add the first 24 assignments to the embed as fields
    for assignment in assignments[:24]:
        dueDatetime = ''

        if 'dueDate' in assignment:
            dueDatetime = timestampFromDue(assignment)
        else:
            dueDatetime = '無截止日期'

        assignmentsEmbed.add_field(
            name=assignment["title"], value='截止時間: {}\n[開啟作業]({})'.format(dueDatetime, assignment["alternateLink"]), inline=False)

    return await ctx.send(embed=assignmentsEmbed)


@bot.command()
async def timetable(ctx, arg1='', arg2=''):
    if arg1 and not re.match(r'[A-H]', arg1):
        return await ctx.send('不存在 Day {}'.format(arg1))

    arg1 = arg1 or getDayOfCycle()
    arg2 = arg2 or config["class"]

    if not arg1:
        return await ctx.send('發生了預期外的錯誤')

    if arg1 == '/':
        return await ctx.send('本日為學校假期')

    param = {'day': arg1, 'class_': arg2,
             'date': datetime.now().strftime('%d %B, %Y')}
    lessons = getLessonList(param['class_'], param['day'])

    if lessons[0] == None:
        return await ctx.send('ValueError : {}'.format(lessons[1]))

    embedFields = []
    i = 0

    for lesson in lessons:
        embedFields.append({'name': '第 {} 節'.format(
            i+1), 'value': '{}\n'.format(lesson), 'inline': False})
        i += 1

    timetableEmbed = discord.Embed(
        title='{class_}班時間表'.format(**param),
        description='{date}\t\nDay {day}'.format(**param),
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
