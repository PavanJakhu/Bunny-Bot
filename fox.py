import time
import random
import discord
import asyncio
import aiohttp
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
    liveTwitch = {}

bunnyBot = Bot(command_prefix="fox.")
client = aiohttp.ClientSession()
util = Util()


async def check_picarto():
    await bunnyBot.wait_until_ready()
    while not bunnyBot.is_closed:
        try:
            if Util.jsonData and Util.jsonData["picarto streamers"]:
                async with client.get("https://api.picarto.tv/v1/online?adult=true&gaming=true") as r:
                    if r.status == 200:
                        data = await r.json()
                        for registeredUser in Util.jsonData["picarto streamers"]:
                            currentlyLive = False
                            for i, streamer in enumerate(data):
                                if registeredUser == streamer["name"].lower():
                                    currentlyLive = True
                                    if registeredUser not in Util.livePicarto:
                                        desc = "Viewers: {0}\nCategory: {1}". \
                                            format(str(streamer["viewers"]), streamer["category"])
                                        em = discord.Embed(
                                            title=streamer["name"] + " has started streaming!",
                                            description=desc,
                                            url="https://picarto.tv/" + streamer["name"]
                                        )
                                        em.set_thumbnail(url="https://picarto.tv/user_data/usrimg/{0}/dsdefault.jpg".format(
                                            streamer["name"].lower()))
                                        result = await bunnyBot.send_message(Util.streamChannel, embed=em)
                                        Util.livePicarto[streamer["name"].lower()] = result

                                        break
                            if registeredUser in Util.livePicarto and not currentlyLive:
                                await bunnyBot.delete_message(Util.livePicarto[registeredUser.lower()])
                                del Util.livePicarto[registeredUser.lower()]
                                break
        except aiohttp.errors.ClientOSError:
            print("Client OS error.")
        except TimeoutError:
            print("Client timed out.")
        except ConnectionResetError:
            print("Connection reset")
        await asyncio.sleep(2)


async def update_picarto():
    await bunnyBot.wait_until_ready()
    while not bunnyBot.is_closed:
        if Util.livePicarto:
            async with client.get("https://api.picarto.tv/v1/online?adult=true&gaming=true") as r:
                if r.status == 200:
                    print("Hello 1")
                    data = await r.json()
                    for liveStreamer, message in Util.livePicarto.items():
                        print("Hello 2")
                        for streamer in data:
                            print("Hello 3")
                            if liveStreamer == streamer["name"]:
                                print("Hello 4")
                                desc = "Viewers: {0}\nCategory: {1}". \
                                    format(str(streamer["viewers"]), streamer["category"])
                                em = discord.Embed(
                                    title=streamer["name"] + " has started streaming!",
                                    description=desc,
                                    url="https://picarto.tv/" + streamer["name"]
                                )
                                print(streamer["viewers"])
                                em.set_thumbnail(url="https://picarto.tv/user_data/usrimg/{0}/dsdefault.jpg".format(
                                    streamer["name"].lower()))
                                await bunnyBot.edit_message(message, new_content=None, embed=em)
                                break
        await asyncio.sleep(900)


async def check_twitch():
    await bunnyBot.wait_until_ready()
    while not bunnyBot.is_closed:
        if Util.jsonData and Util.jsonData["twitch streamers"]:
            for streamer in Util.jsonData["twitch streamers"]:
                async with client.get("https://api.twitch.tv/kraken/users?client_id=hpo4gemorvc1ooc0qb03utlot4spzw?login=" + streamer.lower()) as r1:
                    if r1.status == 200:
                        data = await r1.json()
                        if not data["users"]:
                            id = data["users"][0]["_id"]
                            async with client.get("https://api.twitch.tv/kraken/streams/" + id) as r2:
                                if r2.status == 200:
                                    data = r2.json()
                                    if data["stream"] is not None:
                                        desc = "**{0}**\nViewers: {1}\nTotal views: {2}\nFollowers: {3}\nGame: {4}"\
                                            .format(
                                            data["stream"]["channel"]["status"],
                                            data["stream"]["viewers"],
                                            data["stream"]["channel"]["views"],
                                            data["stream"]["channel"]["followers"],
                                            data["stream"]["channel"]["game"]
                                        )
                                        em = discord.Embed(
                                            title=streamer + " has started streaming!",
                                            description=desc,
                                            url=data["stream"]["channel"]["url"],
                                        )
                                        em.set_thumbnail(url=data["stream"]["channel"]["logo"])
                                        result = await bunnyBot.send_message(Util.streamChannel, embed=em)
                                        Util.liveTwitch[streamer.lower()] = result
                                    elif streamer.lower() in Util.liveTwitch:
                                        await bunnyBot.delete_message(Util.liveTwitch[streamer.lower()])
                                        del Util.liveTwitch[streamer.lower()]
        await asyncio.sleep(1)


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


@bunnyBot.command(description="Register your Picarto for notications.")
async def registerPicarto(name : str):
    try:
        urllib.request.urlopen("https://api.picarto.tv/v1/channel/name/" + name.lower())
    except urllib.error.HTTPError:
        await bunnyBot.say("This account does not exist.")
    else:
        if name not in Util.jsonData["picarto streamers"]:
            Util.jsonData["picarto streamers"].append(name.lower())
            with open("data.json", 'w') as outfile:
                json.dump(Util.jsonData, outfile)

            await bunnyBot.say("Added your Picarto!")
        else:
            await bunnyBot.say("You are already registered.")


@bunnyBot.command(description="Unregister your Picarto for notications.")
async def unregisterPicarto(name : str):
    try:
        urllib.request.urlopen("https://api.picarto.tv/v1/channel/name/" + name)
    except urllib.error.HTTPError:
        await bunnyBot.say("This account does not exist.")
    else:
        if name in Util.jsonData["picarto streamers"]:
            if name.lower() in Util.livePicarto:
                await bunnyBot.delete_message(Util.livePicarto[name.lower()])
                del Util.livePicarto[name.lower()]
            del Util.jsonData["picarto streamers"][Util.jsonData["picarto streamers"].index(name.lower())]
            with open("data.json", 'w') as outfile:
                json.dump(Util.jsonData, outfile)

            await bunnyBot.say("Removed from notifications.")
        else:
            await bunnyBot.say("You are not in the database.")


#@bunnyBot.command(description="Register your Twitch for notications.")
async def registerTwitch(name : str):
    async with client.get("https://api.twitch.tv/kraken/users?login=" + name.lower() + "?client_id=hpo4gemorvc1ooc0qb03utlot4spzw") as r1:
        print(await r1.text())
        if r1.status == 200:
            data = await r1.json()
            if not data["users"]:
                if name not in Util.jsonData["twitch streamers"]:
                    Util.jsonData["twitch streamers"].append(name.lower())
                    with open("data.json", 'w') as outfile:
                        json.dump(Util.jsonData, outfile)

                    await bunnyBot.say("Added your Twitch!")
                else:
                    await bunnyBot.say("You are already registered.")
            else:
                await bunnyBot.say("This account does not exist.")


#@bunnyBot.command(description="Unregister your Twitch for notications.")
async def unregisterTwitch(name : str):
    async with client.get("https://api.twitch.tv/kraken/users?login=" + name.lower()) as r1:
        if r1.status == 200:
            data = await r1.json()
            if not data["users"]:
                if name in Util.jsonData["twitch streamers"]:
                    if name.lower() in Util.liveTwitch:
                        await bunnyBot.delete_message(Util.liveTwitch[name.lower()])
                        del Util.liveTwitch[name.lower()]
                    del Util.jsonData["twitch streamers"][Util.jsonData["twitch streamers"].index(name.lower())]
                    with open("data.json", 'w') as outfile:
                        json.dump(Util.jsonData, outfile)

                    await bunnyBot.say("Removed from notifications.")
                else:
                    await bunnyBot.say("You are not in the database.")
            else:
                await bunnyBot.say("This account does not exist.")

bunnyBot.loop.create_task(check_picarto())
bunnyBot.loop.create_task(update_picarto())
bunnyBot.run("Mjk0MjM1NzE1MDU3ODc2OTk1.C73Aaw.x3E70_tq9S13B6sVODW7YkkgcOg")
