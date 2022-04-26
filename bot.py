# ============= imports =============

from datetime import datetime
import json
import re

import discord
from discord.ext import commands
import termtables as tt

from SpycAPI import HolidayException, SpycAPI as spyc

# ============ Bot Config ============

activity = discord.Activity(
    type=discord.ActivityType.listening, name="$timetable today <class>")
intents = discord.Intents().all()  # Specify the bot intents
bot = commands.Bot(command_prefix='$', help_command=None,
                   intents=intents, activity=activity)  # Create the bot bot


# =========== Bot Events ===========


@bot.event  # On bot ready
async def on_ready():
    print('Logged in as {0.user}'.format(bot))


@bot.command()
async def help(ctx):
    help_description = (
        ':wave: Hello! 我係一個用 Python 寫嘅 Discord bot! \n'
        '如果想試下整一個屬於自己嘅 Discord Bot, \n'
        '可以參考[呢一份筆記](https://ite-ite.gitbook.io/discord-personal-assistant/ '
        '"SPYC Stem Elite Course: Discord Personal Assistant") \n'
        '亦歡迎參考[我呢個bot嘅程式碼](https://github.com/Kai9073/SPYC-STEM-Discord.py-Bot/tree/v2 '
        '"Kai9073/SPYC-STEM-Discord.py at v2") \n'
    )

    command_list = [
        {
            "syntax": "$timetable `Class` `Optional: Date(DD/MM)`",
            "desc": "查看時間表"
        },
        {
            "syntax": "$apis",
            "desc": "查看學校的 API 列表"
        },
        {
            "syntax": "$env",
            "desc": "查看透過使用 M5Stack 所記錄，校園內的溫度、濕度、氣壓等資訊"
        },
        {
            "syntax": "$help",
            "desc": "(此指令) 查看指令列表等"
        }
    ]
    commands_field_desc = ''

    for cmd in command_list:
        commands_field_desc += '**{syntax}**\n> {desc}\n\n'.format(**cmd)

    help_embed = discord.Embed(description=help_description,colour=0xd88317)
    help_embed.set_author(
        name="小英同學",
        icon_url=("https://cdn.discordapp.com/avatars/933610860012793877/"
                  "e7fe11793f2491a66bfdf79ba4e21fdc.png")
    )
    help_embed.add_field(name="指令列表", value=commands_field_desc)
    return await ctx.reply(embed=help_embed)


@bot.command()
async def timetable(ctx, *args):  # Timetable Command
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

    _class = class_args[0]
    _datetime = datetime(datetime.now().year,
                         int(date_args[0].split('/')[1]),
                         int(date_args[0].split('/')[0]))
    timestamp = f'<t:{int(_datetime.timestamp())}:D>'

    loadingMessage = await ctx.reply("正在獲取時間表資訊...")

    try:
        lessons = spyc.getDateLessons(_class, _datetime)
        lessonsString = '\n'.join(
            list(map(
                lambda line: f'{line} ',
                tt.to_string(
                        data=list(
                            map(lambda period: [period.subject, period.venue], lessons)),
                        header=["Subject", "Venue"],
                        padding=(0, 3),
                        alignment="cc"
                ).splitlines()
            ))
        )

        cycleDayString = f'Day {spyc.getCycleDay(_datetime)}'

        timetable_embed = discord.Embed(
            title="Timetable",
            description=f'**S.{_class.upper()} | {timestamp} | {cycleDayString}**'
            + f'```\n{lessonsString}\n```',
            colour=0x008847
        )
        timetable_embed.set_footer(
            text="API: iot.spyc.hk", icon_url="https://app.gitbook.com/public/emojis/2692.png?v=6.0.0")

        await loadingMessage.delete()
        return await ctx.reply(embed=timetable_embed)

    except HolidayException:
        timetable_embed = discord.Embed(
            title="Timetable",
            description=f'**S.{_class.upper()} | {timestamp} | Holiday**\n'
            + f'```\n{_datetime.strftime("%x")} is a school holiday.\n```',
            colour=0x008847
        )
        await loadingMessage.delete()
        return await ctx.reply(embed=timetable_embed)


@bot.command()
async def apis(ctx, *args):
    apis_list_desc = (
        '**IoT Devices**\n'
        '`GET` https://iot.spyc.hk/report\n'
        '> Returns general weather report fetched from HKO as string.\n'
        '`GET` https://iot.spyc.hk/forecast\n'
        '> Returns general weather forecast fetched from HKO as string.\n'
        '`GET` https://iot.spyc.hk/spycenv\n'
        '> Returns ENV data from all IoT weather stations on campus.\n'
        '`POST` https://iot.spyc.hk/postdata\n'
        '> Posts ENV data to database.\n'
        '**Timetables**\n'
        '`GET` https://iot.spyc.hk/timetable\n'
        '> Returns all timetable objects.\n'
        '`GET` https://iot.spyc.hk/timetable?cl=class\n'
        '> Returns the timetable object as specified.\n'
        '`GET` https://iot.spyc.hk/cyclecal\n'
        '> Returns dates to day-of-cycle mapping.\n'
        '**For Testing Post Requests**\n'
        '`POST` https://iot.spyc.hk/fordebug\n'
        '> Posts any data you want for testing and debugging.\n'
    )

    apis_list_embed = discord.Embed(
        title="SPYC-STEM APIs", colour=0x346ddb,
        description=apis_list_desc,
        url="https://stem.spyc.hk/spyc-api/iot.spyc.hk"
    )
    apis_list_embed.set_footer(
        text="API BaseURL: iot.spyc.hk",
        icon_url="https://app.gitbook.com/public/emojis/2692.png?v=6.0.0"
    )

    return await ctx.reply(embed=apis_list_embed)


@bot.command()
async def env(ctx, *args):
    envdata = spyc.getEnvDataStrings()

    dataStrings = []
    for data in envdata:
        dataString = (
            f'{data.lastUpdate} '
            f':round_pushpin:{data.location}\n'
            f'{data.temperature:.1f}°C (HI {data.heatIndex:.1f}°C) '
            f'{data.relativeHumidity:.1f}% {data.airPressure}hPa\n'
        )
        dataStrings.append(dataString)

    envembed = discord.Embed(title="Campus Environment Data",
                             description='\n'.join(dataStrings),
                             colour=0x346ddb)
    return await ctx.reply(embed=envembed)


@bot.command()
async def weather(ctx, *args):
    pass

# ========= Run(start) the bot =========

# load secrets (json)
f = open('secrets.json')
secrets = json.load(f)

# run the bot
bot.run(secrets["token"])
