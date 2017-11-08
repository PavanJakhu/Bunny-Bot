import discord
from discord.ext.commands import Bot
import time
import random
import json
import aiohttp
import logging
import re


class Util:
    prevAccessPet = 0
    prevAccessCarrot = 0
    prevAccess8Ball = 0
    prevAccessCS = 0
    prevCS = ""
    jsonData = None
    botCommandsChannel = None

bunnyBot = Bot(command_prefix="bunbun.")
client = aiohttp.ClientSession()
util = Util()


def findWholeWord(word):
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search


@bunnyBot.event
async def on_ready():
    print("Ready!")

    with open("data.json") as json_file:
        Util.jsonData = json.load(json_file)

    for server in bunnyBot.servers:
        Util.botCommandsChannel = discord.utils.get(server.channels, name="bot_commands", type=discord.ChannelType.text)


@bunnyBot.event
async def on_command_error(error, ctx):
    if ctx.message.content == "bunbun.8ball" and str(error) == "message is a required argument that is missing.":
        await bunnyBot.send_message(ctx.message.channel, "You didn't ask a question!")
    else:
        raise error


@bunnyBot.event
async def on_message(msg):
    #Clever Bot
    for mention in msg.mentions:
        if mention.name == bunnyBot.user.name:
            if time.time() - util.prevAccessCS > 40:
                util.prevCS = ""

            params = {
                "key": "CC3etFRu9AZtVw8ABtgEGiKvQ7w",
                "input": msg.content,
                "cs": util.prevCS
            }

            async with client.get("http://www.cleverbot.com/getreply", params=params) as r:
                if r.status == 200:
                    data = await r.json()

                    util.prevCS = data["cs"]
                    util.prevAccessCS = time.time()

                    await bunnyBot.send_message(msg.channel, data["output"])

    #Delete bad messages
    if msg.channel.name != "bot_commands":
        for x in Util.jsonData["bad words"]:
            if findWholeWord(x)(msg.content) != None:
                await bunnyBot.delete_message(msg)

                fmt = '{0.author} said a bad word: \"{0.content}\" in {0.channel.name}'
                fmt = fmt.format(msg)
                await bunnyBot.send_message(Util.botCommandsChannel, fmt)

                break

    await bunnyBot.process_commands(msg)


@bunnyBot.command(description="Let's you pet the adorable bunny bot!")
async def pet():
    if time.time() - util.prevAccessPet > 60:
        await bunnyBot.say(random.choice(Util.jsonData["pet sayings"]))
        util.prevAccessPet = time.time()


@bunnyBot.command(description="Let's you give a carrot to Bunny!")
async def carrot():
    if time.time() - util.prevAccessCarrot > 60:
        await bunnyBot.say(random.choice(Util.jsonData["carrot sayings"]))
        util.prevAccessCarrot = time.time()


@bunnyBot.command(name="8ball", description="Ask Bunny a question and she'll answer using her magic ball!")
async def _8ball(message : str):
        if time.time() - util.prevAccess8Ball > 60:
            if message.strip().endswith("?"):
                await bunnyBot.say(random.choice(Util.jsonData["8ball sayings"]))
                util.prevAccess8Ball = time.time()
            else:
                await bunnyBot.say("That's not a question! Try ending it with a \'?\'.")


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
bunnyBot.run("MjkzMTM0NTYyOTkxNTM4MTc2.DOQDWg.NToRN8LBxvmGWIb_iQa7qTPJNKk")
