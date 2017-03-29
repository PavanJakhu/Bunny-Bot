import time
import random
import discord
import threading
import asyncio
import urllib.request
import json
from discord.ext.commands import Bot


class Util:
    prevAccessPet = 0
    prevAccessCarrot = 0
    jsonData = None
    botCommandsChannel = None
    streamChannel = None
    livePicarto = {}

bunnyBot = Bot(command_prefix="fox.")
util = Util()


def check_picarto_notifications():
    threading.Timer(1, check_picarto_notifications).start()
    for streamer in Util.jsonData["picarto streamers"]:
        response = urllib.request.urlopen("https://api.picarto.tv/v1/channel/name/" + streamer)
        data = json.load(response)
        if data["online"] and data["name"] not in Util.livePicarto:
            desc = "**{0}**\nViewers: {1}\nTotal views: {2}\nFollowers: {3}\nCategory: {4}\nCommissions: {5}".\
                format(data["title"], data["viewers"], data["viewers_total"], data["followers"], data["category"],
                       data["commissions"]
                       )
            em = discord.Embed(
                title=data["name"] + " has started streaming!",
                description=desc,
                url="https://picarto.tv/" + data["name"],
            )
            imageURL = "https://picarto.tv/user_data/usrimg/{0}/dsdefault.jpg".format(data["name"].lower())
            em.set_thumbnail(url=imageURL)
            coro = bunnyBot.send_message(Util.streamChannel, embed=em)
            fut = asyncio.run_coroutine_threadsafe(coro, bunnyBot.loop)
            try:
                result = fut.result(15)
            except asyncio.TimeoutError:
                print('The coroutine took too long, cancelling the task...')
                fut.cancel()
            except Exception as exc:
                print('The coroutine raised an exception: {!r}'.format(exc))
            else:
                Util.livePicarto[data["name"]] = result
        elif not data["online"] and data["name"] in Util.livePicarto:
            coro = bunnyBot.delete_message(Util.livePicarto[data["name"]])
            fut = asyncio.run_coroutine_threadsafe(coro, bunnyBot.loop)
            try:
                result = fut.result(15)
            except asyncio.TimeoutError:
                print('The coroutine took too long, cancelling the task...')
                fut.cancel()
            except Exception as exc:
                print('The coroutine raised an exception: {!r}'.format(exc))
            else:
                del Util.livePicarto[data["name"]]


@bunnyBot.event
async def on_ready():
    print("Ready!")

    with open("data.json") as json_file:
        Util.jsonData = json.load(json_file)

    print("Length of Picarto IDs: " + str(len(Util.jsonData["picarto streamers"])))

    for server in bunnyBot.servers:
        Util.botCommandsChannel = discord.utils.get(server.channels, name="bot_commands", type=discord.ChannelType.text)
        Util.streamChannel = discord.utils.get(server.channels, name="stream_announcements",
                                               type=discord.ChannelType.text)

    threading.Timer(1, check_picarto_notifications).start()

@bunnyBot.event
async def on_message(msg):
    for x in Util.jsonData["bad words"]:
        if x in msg.content.casefold():
            await bunnyBot.delete_message(msg)

            fmt = '{0.author} said a bad word: \"{0.content}\" at {0.timestamp} in {0.channel.name}'
            fmt = fmt.format(msg)
            print(fmt)
            fmt = fmt.casefold()
            for badWord in Util.jsonData["bad words"]:
                fmt = fmt.replace(badWord, "BAD WORD")
            await bunnyBot.send_message(
                discord.utils.get(msg.server.channels, name="bot_commands", type=discord.ChannelType.text),
                fmt)

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


@bunnyBot.command(description="Register your Picarto for notications.")
async def registerPicarto(name : str):
    if name not in Util.jsonData["picarto streamers"]:
        Util.jsonData["picarto streamers"].append(name)
        with open("data.json", 'w') as outfile:
            json.dump(Util.jsonData, outfile)

        await bunnyBot.say("Added your Picarto!")
    else:
        await bunnyBot.say("You are already registered.")

bunnyBot.run("Mjk0MjM1NzE1MDU3ODc2OTk1.C7SM4Q.9uGEFeWJieeOBQqNiNk8szndLYc")
