# Explanation of the code

This file contains a line-by-line explanation of bot.py.

## Module imports (Line 1-16)
```py
import json
import os.path
```
Here we import two modules: [json](https://docs.python.org/3/library/json.html) and [os.path](https://docs.python.org/3/library/os.path.html). 

[json](https://docs.python.org/3/library/json.html) is a built-in package for Python. It is a JSON encoder and decoder for Python. You may find more information about JSON(JavaScript Object Notation) [here](https://json.org/)

[os.path](https://docs.python.org/3/library/os.path.html) is a module for python the impements useful functions on pathnames.

```py
import discord
from discord.ext import commands
```
In the first line, we import the [discord.py](https://discordpy.readthedocs.io/en/stable) module. This helps us interact with the [Discord API](https://discord.com/developers/docs/intro), allowing us to easily read/send messages and get/send information from/to Discord easily.

In the second line, we import the module [commands](https://discordpy.readthedocs.io/en/stable/ext/commands/index.html) from [discord.py](https://discordpy.readthedocs.io/en/stable)'s extensions. This is a bot commands framework for discord.py, it allows us to easily create commands for our Discord bot.

```py
import time
from datetime import datetime, timezone
```
Here we import another two modules: [time](https://docs.python.org/3/library/time.html) and [datetime](https://docs.python.org/3/library/datetime.html)

[time](https://docs.python.org/3/library/time.html) is a module that provides time-related functions, for example time conversions.

[datetime](https://docs.python.org/3/library/datetime.html) is a module that allow us to create date/time/datetime variables easily.

These two modules are used in the bot to get the assignment due date and time from Google Classroom.

```py
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
```
Here we import 5 modules. All of the above are modules for us to get information from the Google API / Google Classroom API so that the bot get the assignment list from Google Classroom.

For more information regarding the above modules, see [Google Classroom API - Python Quickstart](https://developers.google.com/classroom/quickstart/python)

## Bot Config (Line 17-25)
In this part of code, we configure the bot settings.
```py
intents = discord.Intents().all()
```
According to [this announcement in October 2021](https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message-Content-Privileged-Intent-for-Verified-Bots), bots need to state their intents (e.g. whether the bot needs to read user information, whether the bot needs to send messages etc.) 

By stating the bot requires all intents, the bot get most of the permissions that it will need. You may read more about Intents [here](https://discord.com/developers/docs/topics/gateway#gateway-intents)
```py
bot = commands.Bot(command_prefix='$', intents=intents)
```
the above code creates the bot client for our bot. A bot client allows us to use our bot. Without the client, we cannot control the bot and the bot won't do anything.

```py
creds = None
service = None
```
These two variables, `creds` and `service`, is used to store our Google API Credentials and the resource for interaction with the Google Classroom API respectively.

