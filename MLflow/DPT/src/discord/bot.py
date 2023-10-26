#!/usr/bin/env python3

from ..chat.converse import Client
from dotenv import load_dotenv
from .. import const
import discord
import json
import os


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.members = True

bot = Client()
client = discord.Client(intents=intents)


# HORRIBLE SOLUTION -- TODO FIXIT
ended = []


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user or \
       (type(message.channel) == discord.threads.Thread and client.user not in message.mentions) or \
       'Team' in message.author.roles or \
       message.channel.id in ended: return
    if 'stop' in message.content.lower():
        ended.append(message.channel.id)
        await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        return

    await message.add_reaction('\N{THINKING FACE}')
    try:
        if set(message.content.lower().split()).intersection(const.ENTERPRISE_KEYWORDS):
            avi = discord.utils.get(client.users, name="Avi Lozowick", discriminator="3096")
            dean = discord.utils.get(client.users, name="Dean", discriminator="4371")
            result = f"{avi.mention} and {dean.mention} can help you with this question. They'll reach out to you shortly here or on a DM!"
        elif message.attachments:
            result = "I'm sorry, I can't read images just yet! Can you describe your task in words?"
        else: result = bot.result(message.content)

        if type(message.channel) != discord.threads.Thread:
            thread = await message.create_thread(name=f'Debugging with {message.author.name}', auto_archive_duration=1440)
            result = "Hello, I'm a bot here to help you debug! To get me to post follow-ups further down the thread, please @ me, or quote-reply to one of my messages. If you'd like me to stop talking at any time, please say 'stop'.\n\n" + result + "\n\n Was I helpful? Please vote \N{THUMBS UP SIGN} / \N{THUMBS DOWN SIGN}"
        else: thread = message.channel
    except:
        result = "I ran into an error; not sure what went wrong. Please try again!"
        thread = message.channel

    await thread.send(result)
    await message.remove_reaction('\N{THINKING FACE}', client.user)

client.run(TOKEN)
