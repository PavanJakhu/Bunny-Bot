import time
import random
import discord
import json
from discord.ext.commands import Bot


class Util:
    prevAccessPet = 0
    prevAccessCarrot = 0
    jsonData = None
    botCommandsChannel = None

bunnyBot = Bot(command_prefix="bunbun.")
util = Util()


@bunnyBot.event
async def on_ready():
    print("Ready!")

    with open("data.json") as json_file:
        Util.jsonData = json.load(json_file)

    for server in bunnyBot.servers:
        Util.botCommandsChannel = discord.utils.get(server.channels, name="bot_commands", type=discord.ChannelType.text)


@bunnyBot.event
async def on_message(msg):
    if msg.channel.name != "bot_commands":
        for x in Util.jsonData["bad words"]:
            if x in msg.content.casefold():
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


bunnyBot.run("MjkzMTM0NTYyOTkxNTM4MTc2.C7zX_A.MTzQzRnqWm3Qaz7XRK9ZAV44qw4")
