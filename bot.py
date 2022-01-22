# ============= imports =============

import json
import os.path
import discord
from discord.ext import commands, tasks

from classroom import authAndGetService, fetchAssignments, timestampFromDue

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
    # Create Discord Message Embed
    resultEmbed = discord.Embed(
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
        resultEmbed.add_field(
            name=assignment["title"], value='截止時間: {}\n[開啟作業]({})'.format(dueDatetime, assignment["alternateLink"]), inline=False)
    await ctx.send(embed=resultEmbed)


# ========= Run(start) the bot =========

# load secrets (json)
f = open('secrets.json')
secrets = json.load(f)

# run the bot
bot.run(secrets["token"])
