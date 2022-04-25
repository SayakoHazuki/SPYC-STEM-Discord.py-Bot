# ============= imports =============

from datetime import datetime
import json
import re

import discord
from discord.ext import commands, tasks

from SpycAPI import SpycAPI as spyc

# ============ Bot Config ============

activity = discord.Activity(
    type=discord.ActivityType.listening, name="$timetable today <class>")
intents = discord.Intents().all()  # Specify the bot intents
bot = commands.Bot(command_prefix='$',
                   intents=intents, activity=activity)  # Create the bot bot
service = None  # Will be used to store Google Classroom API Service


# =========== Bot Events ===========


@bot.event  # On bot ready
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


@bot.command()
async def timetable(ctx, *args):  # Timetable Command
    """
    Get timetable command
    arg1: 
    """
    class_args = re.findall(r'[1-6][A-Ea-e]', ''.join(args))
    date_args = re.findall(r'[0-3]?[0-9]/[0-3]?[0-9]', ''.join(args))

    if len(class_args) == 0:
        return await ctx.reply('請在指令中輸入班別')

    if len(class_args) > 1:
        return await ctx.reply(
            f'請每次輸入一個班別\n(共輸入了{len(class_args)}個班別: {" ".join(class_args)}'
        )

    if len(date_args) == 0:
        date_args.append(datetime.now().strftime('%d/%m'))

    if len(date_args) > 1:
        return ctx.reply(
            f'請每次輸入一個日期\n(共輸入了{len(date_args)}組日期: {" ".join(date_args)}'
        )

    _datetime = datetime(datetime.now().year,
                         int(date_args[0].split('/')[1]),
                         int(date_args[0].split('/')[0]))

    lessons = spyc.getDateLessons(class_args[0], _datetime)
    return await ctx.reply('\n'.join(list(map(lambda p: p.formattedString, lessons))))


# ========= Run(start) the bot =========

# load secrets (json)
f = open('secrets.json')
secrets = json.load(f)

# run the bot
bot.run(secrets["token"])
