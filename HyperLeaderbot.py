from discord.ext import commands, tasks
import discord
import json
import time
import shutil
import datetime
import asyncio
from leaderboard_scraper import *
from pb_img_gen import gen_pb

with open("bot_token.txt") as file:
    BOT_TOKEN = file.read()
    
CHANNEL_ID = 0
intents = discord.Intents.default()
intents.message_content = True

# array to store scores and their associated role id's
role_array = [
    ["Below 0", 1054219797514162238],
    [0, 1054232899936858133],
    [50, 1054219546841591808],
    [100, 1054219787485577267],
    [150, 1054219800462770186],
    [200, 1054219803138732074],
    [250, 1054219806133460992],
    [275, 1054219807383363614],
    [300, 1054219808792662066],
    [325, 1054219810562650192],
    [350, 1054219811917410424],
    [360, 1054219813108592750],
    [370, 1054220968236683355],
    [380, 1054220973462802483],
    [390, 1054220975174062190],
    [400, 1054220976553988136],
    [405, 1054220978143645728],
    [410, 1054220979796197406],
    [415, 1054220981088039052],
    [420, 1054220981994004520],
    [425, 1144733410728890369]
    ]

top_roles = [
    ["Top 3", 1142897619379695707],
    ["Top 10", 1142897869439893526],
    ["Top 25", 1142897909029945394]
]

wr_role_id = 1142895896372203550

bot = commands.Bot(command_prefix="+", intents=discord.Intents.all())

def update_dict(key, value, source_dict):
    with open(source_dict, "r") as json_file:
        my_dict = json.load(json_file)

    # make changes to myDict
    my_dict[key] = value

    with open(source_dict, "w") as json_file:
        json.dump(my_dict, json_file)

def ordinal(value):
    ordval = f'{value}'
    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval += 'st'
        elif value % 10 == 2:
            ordval += 'nd'
        elif value % 10 == 3:
            ordval += 'rd'
        else:
            ordval += 'th'
    else:
        ordval += 'th'

    return ordval

# leaderboard update funtion
async def lb_update():
    start_time = time.monotonic()
    #set old leaderboard as new one
    shutil.copyfile('lb_dict_new.json', 'lb_dict_old.json')

    lb_dict = await get_shit()
    key_list = []
    for x in lb_dict:
        key_list.append([lb_dict[x]['score'], x])

    # update the new leaderboard dict
    with open("lb_dict_new.json", "w") as outfile:
        json.dump(lb_dict, outfile)
    
    # update the key list 
    with open("key_list.json", "w") as outfile:
        json.dump(key_list, outfile)
    print(f"lb update took {round((time.monotonic() - start_time), 3)} seconds to execute")


# 400 post function
@bot.command()
async def auto_400_post(hdnews: discord.channel):
    start_time = time.monotonic()
    # post format
    # Congratulations to *@user* for getting a new PB of *score*! They beat their old PB of *score_old* (*score_dif*), gaining *rank_dif* ranks. They are the *x* 400 player!

    # open the id dictionary for reference
    with open("id_dictionary.json", "r") as outfile:
        id_dict = json.load(outfile)
    with open("lb_dict_new.json", "r") as outfile:
        lb_dict_new = json.load(outfile)
    with open("lb_dict_old.json", "r") as outfile:
        lb_dict_old = json.load(outfile)
    with open("key_list.json", "r") as outfile:
        key_list = json.load(outfile)

    # compare old and new leaderboards to see if there are any new 400 scores
    x = 0
    while float(key_list[x][0]) >= 400:
        user_key = key_list[x][1]
        # check if there is a new PB
        if round(float(lb_dict_new[user_key]["score"]), 4) > round(float(lb_dict_old[user_key]["score"]), 4):

            # need to pull @username, new score, old score, change in score, rank changed, if new 400 player]]
            user_id = id_dict.get(key_list[x][1])
            username = lb_dict_new[user_key]["username"]
            score_new = round(float(lb_dict_new[user_key]["score"]), 3)
            score_old = round(float(lb_dict_old[user_key]["score"]), 3)
            rank_new = int(lb_dict_new[user_key]["rank"])
            rank_old = int(lb_dict_old[user_key]["rank"])
            score_dif = round((score_new - score_old), 3)
            rank_change = rank_old - rank_new
            howmany400 = int
            
            if score_old < 400:
                new_400 = True
                score_list = [sublist[0] for sublist in key_list]
                howmany400 = sum(float(score) >= 400 for score in score_list)
            else:
                new_400 = False

            if rank_new == 1:
                new_wr = True
            else:
                new_wr = False

            if rank_change == 1:
                ranks = "rank"
            else:
                ranks = "ranks"

            score_new = format(score_new, '.3f')
            score_old = format(score_old, '.3f')
            score_dif = format(score_dif, '.3f')

            # send news post
            if new_wr == True:
                gen_pb('400_test_image.png', str(rank_new), str(username), str(score_new))
                pb_img = discord.File('400_test_image.png')
                await hdnews.send(f"Congratulations to {username} for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}. It's a new WR! :crown::tada:", file = pb_img)
            elif user_id == None and new_400 == False:
                gen_pb('400_test_image.png', str(rank_new), str(username), str(score_new))
                pb_img = discord.File('400_test_image.png')
                await hdnews.send(f"Congratulations to {username} for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}.", file = pb_img)
            elif user_id == None and new_400 == True:
                gen_pb('400_test_image.png', str(rank_new), str(username), str(score_new))
                pb_img = discord.File('400_test_image.png')
                await hdnews.send(f"Congratulations to {username} for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}. They are the {ordinal(howmany400)} 400 player!", file = pb_img)
            elif user_id != None and new_400 == False:
                gen_pb('400_test_image.png', str(rank_new), str(username), str(score_new))
                pb_img = discord.File('400_test_image.png')
                await hdnews.send(f"Congratulations to <@{user_id}> for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}.", file = pb_img)               
            elif user_id != None and new_400 == True:
                gen_pb('400_test_image.png', str(rank_new), str(username), str(score_new))
                pb_img = discord.File('400_test_image.png')
                await hdnews.send(f"Congratulations to <@{user_id}> for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}. They are the {ordinal(howmany400)} 400 player!", file = pb_img)
            
        x += 1
    print(f"400_post_update function took {round((time.monotonic() - start_time), 3)} seconds to execute")


# role update function
@bot.command()
async def top_role_update(ctx):
    total_start_time = time.monotonic()

    op = ctx.guild.get_member(ctx.interaction.user.id)

    invoker_roles_before = op.roles

    with open("lb_dict_new.json", "r") as outfile:
        lb_dict_new = json.load(outfile)
    with open("lb_dict_old.json", "r") as outfile:
        lb_dict_old = json.load(outfile)
    with open("id_dictionary.json", "r") as outfile:
        id_dict = json.load(outfile)
    with open("key_list.json", "r") as outfile:
        key_list = json.load(outfile)

    top_3_user_id = []
    top_10_user_id = []
    top_25_user_id = []

    wr_role = ctx.guild.get_role(wr_role_id)
    top_3_role = ctx.guild.get_role(top_roles[0][1])
    top_10_role = ctx.guild.get_role(top_roles[1][1])
    top_25_role = ctx.guild.get_role(top_roles[2][1])

    start_time = time.monotonic()
    # check rank 1 and see if there is a matching id
    wr_user_id = id_dict.get(key_list[0][1])
    # append top_3_id list with discord id's from id_dictionary
    for x in key_list[1:3]:
        top_3_user_id.append(id_dict.get(x[1]))
    # append top_10_id list with discord id's from id_dictionary
    for x in key_list[3:10]:
        top_10_user_id.append(id_dict.get(x[1]))
    # append top_25_id list with discord id's from id_dictionary
    for x in key_list[10:25]:
        top_25_user_id.append(id_dict.get(x[1]))
    print(f"     building lists of top user id's from id_dictionary took {round((time.monotonic() - start_time), 3)} seconds to execute")
    
    start_time = time.monotonic()
    top_registered_users = []
    for x in key_list[0:100]:
        # get discord id from in game id, will return None if user is not registered
        if id_dict.get(x[1]) != None:
            # grab their guild user data
            registered_user = ctx.guild.get_member(id_dict.get(x[1]))
            # if that user data exists (ie: they are in the server), add them to the top_registered_users list
            if registered_user != None:
                top_registered_users.append(registered_user) 
    print(f"     building list of top registered users in HDPals took {round((time.monotonic() - start_time), 3)} seconds to execute")
    
    # remove roles from anyone not in top lists
    start_time = time.monotonic()
    for user in top_registered_users:
        if wr_role in user.roles and user.id != wr_user_id:
            await user.remove_roles(wr_role)
        if top_3_role in user.roles and user.id not in top_3_user_id:
            await user.remove_roles(top_3_role)
        if top_10_role in user.roles and user.id not in top_10_user_id:
            await user.remove_roles(top_10_role)
        if top_25_role in user.roles and user.id not in top_25_user_id:
            await user.remove_roles(top_25_role)
    print(f"     removing roles from anyone not in top roles took {round((time.monotonic() - start_time), 3)} seconds to execute")

    start_time = time.monotonic()
    # check wr id and update if necessary
    if wr_user_id == None:
        pass
    elif ctx.guild.get_member(wr_user_id) is None:
            pass
    else:
        wr_user = ctx.guild.get_member(wr_user_id)
        await wr_user.add_roles(wr_role)

    # check top 3 ids and update if necessary
    for user in top_3_user_id:
        # first, check discord id value. If None, they have never been registered
        if user == None:
            pass
        # this means that they have been registered, so next, check their member object. If they have left the server, it will return None
        elif ctx.guild.get_member(user) is None:
            pass
        # finally, this means that the user is both registered, and in the server, so we should assign user top 3 role
        else:
            top_3_user = ctx.guild.get_member(user)
            await top_3_user.add_roles(top_3_role)

    # check top 10 ids and update if necessary
    for user in top_10_user_id:
        if user == None:
            pass
        elif ctx.guild.get_member(user) is None:
            pass
        else:
            top_10_user = ctx.guild.get_member(user)
            await top_10_user.add_roles(top_10_role)

    # check top 25 ids and update if necessary
    for user in top_25_user_id:
        if user == None:
            pass
        elif ctx.guild.get_member(user) is None:
            pass
        else:
            top_25_user = ctx.guild.get_member(user)
            await top_25_user.add_roles(top_25_role)
    print(f"     checking and updating top rank user roles took {round((time.monotonic() - start_time), 3)} seconds to execute")

    start_time = time.monotonic()
    invoker_roles_after = op.roles

    before_set = set(invoker_roles_before)
    after_set = set(invoker_roles_after)

    added_roles = []
    removed_roles = []

    if before_set == after_set:
        # no roles were changed
        pass
    elif before_set.issubset(after_set):
        # this means roles were added
        for role in invoker_roles_after:
            if role not in invoker_roles_before:
                added_roles.append(role.id)
    elif after_set.issubset(before_set):
        # this means roles were removed
        for role in invoker_roles_before:
            if role not in invoker_roles_after:
                removed_roles.append(role.id)
    else:
        # this means roles were both added and removed
        for role in invoker_roles_after:
            if role not in invoker_roles_before:
                added_roles.append(role.id)
        for role in invoker_roles_before:
            if role not in invoker_roles_after:
                removed_roles.append(role.id)
    print(f"     comparing role sets of user took {round((time.monotonic() - start_time), 3)} seconds to execute")
    print(f"top_role update function took {round((time.monotonic() - total_start_time), 3)} seconds to execute")
    return added_roles, removed_roles

# check for roles and new 400 pb's every 5 minutes
@tasks.loop(minutes = 5)
async def maintain_hdpals(channel):
#async def maintain_hdpals(channel, guild):
    await lb_update()
    #await top_role_update(guild)
    await auto_400_post(channel)

@bot.event
async def on_ready():
    channel = bot.get_channel(1047631851193368697)
    #guild = bot.get_guild(1141412260217114694)
    #maintain_hdpals.start(channel, guild)
    maintain_hdpals.start(channel)

# function for adding a role
@bot.command()
async def remove_role(source, oldroleid):
    await source.interaction.user.remove_roles(discord.utils.get(source.interaction.user.guild.roles, id = oldroleid))

# function for removing a role
@bot.command()
async def add_role(source, newroleid):
    await source.interaction.user.add_roles(discord.utils.get(source.interaction.user.guild.roles, id = newroleid))

# ran when a message is posted
@bot.event
async def on_message(message):
    start_time = time.monotonic()

    channel = bot.get_channel(CHANNEL_ID)

    # prevents infinite loop from bot responding to itself
    if message.author == bot.user:
        return

    # register command
    #if message.content.startswith('register'):
        #register_id = str(message.content.split()[1])
        #update_dict(register_id, message.author.id, 'id_dictionary.json')

    # checks if message is from SORATH bot, and it is the "/hyperdemon pb" command
    if message.author.id == 798042141988618251 and message.interaction.name == "hyperdemon pb":

        embed_description = message.embeds[0].description
        embed_op_id = int(message.interaction.user.id)
        embed_type = message.interaction.name
        description = embed_description.splitlines()

        # parse embed information and store variables
        score_new = round(float(description[1].split()[1].strip("*")), 3)
        score_dif = round(float(description[1].split()[2].strip("()+")), 3)
        score_old = round(score_new-score_dif, 3)
        rank = int(description[0].split()[1].strip("*"))

        # update id dictionary
        if rank <= 1000:
            lb_dict = await get_shit()
            update_dict(list(lb_dict.keys())[rank-1], embed_op_id, 'id_dictionary.json')

        await lb_update()
        added_roles, removed_roles = await top_role_update(message)
        await auto_400_post(bot.get_channel(1047631851193368697))

        # find users old role
        old_role_id = "no score assigned"
        for user_role in message.interaction.user.roles:
            for score_role_pair in role_array:
                if user_role.id == score_role_pair[1]:
                    old_role_id = user_role.id
        
        # find users new role
        # check if score is below 0
        if score_new < 0:
            new_role_id = role_array[0][1]
            next_score = role_array[1]

        # check if score is above 425
        elif score_new >= 425:
            new_role_id = role_array[20][1]
            next_score = None

        # determine which role is correct for new score
        else:
            x = 1
            while not (score_new >= role_array[x][0] and score_new < role_array[x+1][0]):
                x += 1
            else:
                new_role_id = role_array[x][1]
                next_score = role_array[x+1]

        # check if this is their first time triggering bot and update role
        if old_role_id == "no score assigned":
            await add_role(message, new_role_id)
            added_roles.append(new_role_id)
            embed_role_update = discord.Embed(title=f"Updated roles for {message.interaction.user.name}")
            if added_roles != []:
                addstring = f""
                for addedroleid in added_roles:
                    addstring = f"{addstring}<@&{addedroleid}>\n"
                embed_role_update.add_field(name="**Added:**", value=addstring, inline=True)
            await message.channel.send(embed=embed_role_update)
        
        # check if new role is the same as old role and do nothing
        elif old_role_id == new_role_id:
            embed_role_update = discord.Embed(title=f"Updated roles for {message.interaction.user.name}")
            if removed_roles != []:
                removestring = f""
                for removedroleid in removed_roles:
                    removestring = f"{removestring}<@&{removedroleid}>\n"
                embed_role_update.add_field(name="**Removed:**", value=removestring, inline=True)
            if added_roles != []:
                addstring = f""
                for addedroleid in added_roles:
                    addstring = f"{addstring}<@&{addedroleid}>\n"
                embed_role_update.add_field(name="**Added:**", value=addstring, inline=True)
            if added_roles != [] or removed_roles != []:
                await message.channel.send(embed=embed_role_update)
            if next_score != []:
                dist_next_role = round(next_score[0]-score_new, 3)
                await message.channel.send(f"You're **{dist_next_role}** points away from the next role: <@&{next_score[1]}>")
            else:
                await message.channel.send(f"You are a god, {message.interaction.user.name}. No higher role left")

        # replace old role with new role
        else:
            # remove old role
            await remove_role(message, old_role_id)
            removed_roles.append(old_role_id)
            # add new role
            await add_role(message, new_role_id)
            added_roles.append(new_role_id)
            # post embed with role changes
            embed_role_update = discord.Embed(title=f"Updated roles for {message.interaction.user.name}")
            if removed_roles != []:
                removestring = f""
                for removedroleid in removed_roles:
                    removestring = f"{removestring}<@&{removedroleid}>\n"
                embed_role_update.add_field(name="**Removed:**", value=removestring, inline=True)
            if added_roles != []:
                addstring = f""
                for addedroleid in added_roles:
                    addstring = f"{addstring}<@&{addedroleid}>\n"
                embed_role_update.add_field(name="**Added:**", value=addstring, inline=True)
            await message.channel.send(embed=embed_role_update)
    print(f"on demand function took {round((time.monotonic() - start_time), 3)} seconds to execute")

bot.run(BOT_TOKEN)
