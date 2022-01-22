# ============= imports =============

import json
import os.path
import discord
from discord.ext import commands, tasks
import asyncio

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
        title="To-do List", description="Assignments that haven't been turned in yet", color=0xF7DFA5)

    assignments = []
    if os.path.exists('savedAssignments.json'):
        with open('savedAssignments.json', 'r') as savedAssignments:
            assignments = json.load(savedAssignments)
    # Get Assignment List and Add Fields
    else:
        ctx.send('This seems to be the first time for the bot to request data from the Google Classroom API. Please wait for about 2 minutes and run this command again.')

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
            name=assignment["title"], value='Due: {}'.format(dueDatetime), inline=False)
    await ctx.send(embed=resultEmbed)


# ========= Run(start) the bot =========

# load secrets (json)
f = open('secrets.json')
secrets = json.load(f)

# run the bot
bot.run(secrets["token"])
