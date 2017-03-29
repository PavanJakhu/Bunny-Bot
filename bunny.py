import time
import random
import discord
from discord.ext.commands import Bot


class Util:
    prevAccessPet = 0
    prevAccessCarrot = 0


bunnyBot = Bot(command_prefix="bunbun.")
badWords = ["nigger", "nigga", "faggot", "fag", "retard", "retarded"]
petSayings = ["*Nuzzles hand*", "*Ears twitch*", "H-hey!", "*Tail twitches*", "*Tail wiggles*",
              "\"C-can I have a carrot now?\"", "*puffs cheeks*", "\"Eep! That tickles!\"", "\"N-not there!\"",
              "*Scurries and hides*", "\"Sure just.. softly ok?\"", "\"Not the tail!\"",
              "\"You messed up my hair!\" *puffs cheeks*", "\"Where do you think you\'re touching?!\"",
              "*Hops in place*", "*Wiggles*", "*Nuzzles*", "*Ears pull back* \"M-mebbe later?\"", "\"Thank you ~<3\"",
              ">:T", "Eek, your hand is sticky D:!", "Too hard D:!", "^_^ it feels nice.", "You're sweet :>",
              "T-that's a bit more than petting >o<", "Only Foxy can touch there >:T", "Hhhmmmm! :>", "*pets back*",
              "Just wait till you see my new commands!", "Y-you're not Foxy! >:O"]
carrotSayings = ["Yay!", "Thank youuu! ~", "Just one?", "<3!", "Yum!", "T-that's not a carrot!", "^___^", "I did good?",
                 "Totally worth it!", "*drool* \"S-sorry!\"", "*wiggles*", "You're nice. I like you!", "YES!",
                 "T-this one smells funny...", "*grabs and scurries off*", "Wheeee!", "Thanks!", "*noms*",
                 "That's a big one! :O!", "W-where are you trying to put that? >:T"]
util = Util()


@bunnyBot.event
async def on_server_join(server):
    botChannel = discord.utils.get(server.channels, name="bot_commands", type=discord.ChannelType.text)
    if botChannel is None:
        everyone = discord.PermissionOverwrite(read_messages=True, send_messages=False)
        bunnyBot.create_channel(server, "bot_commands", everyone)


@bunnyBot.event
async def on_message(msg):
    for x in badWords:
        if x in msg.content.casefold():
            await bunnyBot.delete_message(msg)

            fmt = '{0.author} said a bad word: \"{0.content}\" at {0.timestamp} in {0.channel.name}'
            fmt = fmt.format(msg)
            print(fmt)
            fmt = fmt.casefold()
            for x in badWords:
                fmt = fmt.replace(x, "BAD WORD")
            await bunnyBot.send_message(
                discord.utils.get(msg.server.channels, name="bot_commands", type=discord.ChannelType.text),
                fmt)

            break

    await bunnyBot.process_commands(msg)


@bunnyBot.command(description="Let's you pet the adorable Bunny Bot!")
async def pet():
    if time.time() - util.prevAccessPet > 60:
        await bunnyBot.say(random.choice(petSayings))
        util.prevAccessPet = time.time()


@bunnyBot.command(description="Let's you give a carrot to Bunny!")
async def carrot():
    if time.time() - util.prevAccessCarrot > 60:
        await bunnyBot.say(random.choice(carrotSayings))
        util.prevAccessCarrot = time.time()

bunnyBot.run("MjkzMTM0NTYyOTkxNTM4MTc2.C7CRxQ.tZQySLrg1dTTYCn60Pf06l25KbQ")
