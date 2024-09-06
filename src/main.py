from discord.ext import commands, tasks
from dotenv import load_dotenv
import discord
import json
import time
import shutil
import state
import os
import uid_map
import aiohttp
import asyncio
from leaderboard_scraper import get_shit
from pb_img_gen import gen_pb

load_dotenv()

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
cache = state.State()

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
    [425, 1144733410728890369],
]

top_roles = [
    ["Top 3", 1142897619379695707],
    ["Top 10", 1142897869439893526],
    ["Top 25", 1142897909029945394],
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
    ordval = f"{value}"
    if value % 100 // 10 != 1:
        if value % 10 == 1:
            ordval += "st"
        elif value % 10 == 2:
            ordval += "nd"
        elif value % 10 == 3:
            ordval += "rd"
        else:
            ordval += "th"
    else:
        ordval += "th"

    return ordval


# leaderboard update funtion
async def lb_update():
    start_time = time.monotonic()
    # set old leaderboard as new one
    shutil.copyfile("lb_dict_new.json", "lb_dict_old.json")

    lb_dict = await get_shit()
    key_list = []
    for x in lb_dict:
        key_list.append([lb_dict[x]["score"], x])

    # update the new leaderboard dict
    with open("lb_dict_new.json", "w") as outfile:
        json.dump(lb_dict, outfile)

    # update the key list
    with open("key_list.json", "w") as outfile:
        json.dump(key_list, outfile)
    print(
        f"lb update took {round((time.monotonic() - start_time), 3)} seconds to execute"
    )


# 400 post function
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
        if round(float(lb_dict_new[user_key]["score"]), 4) > round(
            float(lb_dict_old[user_key]["score"]), 4
        ):
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

            score_new = format(score_new, ".3f")
            score_old = format(score_old, ".3f")
            score_dif = format(score_dif, ".3f")

            # send news post
            if new_wr == True:
                gen_pb(
                    "400_test_image.png", str(rank_new), str(username), str(score_new)
                )
                pb_img = discord.File("400_test_image.png")
                await hdnews.send(
                    f"Congratulations to {username} for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}. It's a new WR! :crown::tada:",
                    file=pb_img,
                )
            elif user_id == None and new_400 == False:
                gen_pb(
                    "400_test_image.png", str(rank_new), str(username), str(score_new)
                )
                pb_img = discord.File("400_test_image.png")
                await hdnews.send(
                    f"Congratulations to {username} for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}.",
                    file=pb_img,
                )
            elif user_id == None and new_400 == True:
                gen_pb(
                    "400_test_image.png", str(rank_new), str(username), str(score_new)
                )
                pb_img = discord.File("400_test_image.png")
                await hdnews.send(
                    f"Congratulations to {username} for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}. They are the {ordinal(howmany400)} 400 player!",
                    file=pb_img,
                )
            elif user_id != None and new_400 == False:
                gen_pb(
                    "400_test_image.png", str(rank_new), str(username), str(score_new)
                )
                pb_img = discord.File("400_test_image.png")
                await hdnews.send(
                    f"Congratulations to <@{user_id}> for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}.",
                    file=pb_img,
                )
            elif user_id != None and new_400 == True:
                gen_pb(
                    "400_test_image.png", str(rank_new), str(username), str(score_new)
                )
                pb_img = discord.File("400_test_image.png")
                await hdnews.send(
                    f"Congratulations to <@{user_id}> for getting a new PB of {score_new}! They beat their old PB of {score_old} (+{score_dif}), gaining {rank_change} {ranks}. They are the {ordinal(howmany400)} 400 player!",
                    file=pb_img,
                )

        x += 1
    print(
        f"400_post_update function took {round((time.monotonic() - start_time), 3)} seconds to execute"
    )


# role update function
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

    wr_role = ctx.guild.get_role(wr_role_id)
    top_3_role = ctx.guild.get_role(top_roles[0][1])
    top_10_role = ctx.guild.get_role(top_roles[1][1])
    top_25_role = ctx.guild.get_role(top_roles[2][1])
    extremely_close_role = ctx.guild.get_role(1176214681325674526)

    start_time = time.monotonic()
    top_role_buckets = [
        [1, wr_role],
        [3, top_3_role],
        [10, top_10_role],
        [25, top_25_role],
    ]

    next_to_400 = False

    for index, ele in enumerate(key_list[0:200]):
        rank = index + 1
        # get discord id from in game id, will return None if user is not registered
        if id_dict.get(ele[1]) != None:
            # grab their guild user data
            registered_user = ctx.guild.get_member(id_dict.get(ele[1]))
            # if that user data exists (ie: they are in the server), add them to the top_registered_users list
            if registered_user != None:
                # check if they are the registered user closest to getting 400
                if next_to_400 == False and float(ele[0]) < 400:
                    next_to_400 = True
                    if extremely_close_role not in registered_user.roles:
                        await registered_user.add_roles(extremely_close_role)

                # check if user is above 400 and has close role, meaning they pb'd and need it removed
                if (
                    next_to_400 == False
                    and extremely_close_role in registered_user.roles
                ):
                    await registered_user.remove_roles(extremely_close_role)

                # Do role checks here!
                for x in range(len(top_role_buckets)):
                    found_role = False
                    if rank <= top_role_buckets[x][0]:
                        # User is in this top player bucket, and should have the corresponding role
                        found_role = True
                        correct_role = top_role_buckets[x][1]
                        break
                    elif rank > 25:
                        correct_role = None
                        break

                if found_role == True and correct_role not in registered_user.roles:
                    for role in registered_user.roles:
                        if any(role in sublist for sublist in top_role_buckets):
                            await registered_user.remove_roles(role)
                    await registered_user.add_roles(correct_role)
                elif found_role == False:
                    # User is not in top 25, and should not have a top player role
                    for role in registered_user.roles:
                        if any(role in sublist for sublist in top_role_buckets):
                            await registered_user.remove_roles(role)

    print(
        f"     Adjusting top player roles took {round((time.monotonic() - start_time), 3)} seconds to execute"
    )

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
    print(
        f"     comparing role sets of user took {round((time.monotonic() - start_time), 3)} seconds to execute"
    )
    print(
        f"top_role update function took {round((time.monotonic() - total_start_time), 3)} seconds to execute"
    )
    return added_roles, removed_roles


# check for roles and new 400 pb's every 5 minutes
@tasks.loop(minutes=5)
async def maintain_hdpals(channel):
    # async def maintain_hdpals(channel, guild):
    await lb_update()
    # await top_role_update(guild)
    await auto_400_post(channel)


@bot.event
async def on_ready():
    guilds = [guild async for guild in bot.fetch_guilds(limit=150)]
    for guild in guilds:
        bot.tree.copy_global_to(guild=discord.Object(id=guild.id))
    await bot.tree.sync()

    channel = bot.get_channel(1047631851193368697)
    # guild = bot.get_guild(1141412260217114694)
    # maintain_hdpals.start(channel, guild)
    maintain_hdpals.start(channel)
    await cache.attach(bot)

# function for adding a role
async def remove_role(source, oldroleid):
    await source.interaction.user.remove_roles(
        discord.utils.get(source.interaction.user.guild.roles, id=oldroleid)
    )


# function for removing a role
async def add_role(source, newroleid):
    await source.interaction.user.add_roles(
        discord.utils.get(source.interaction.user.guild.roles, id=newroleid)
    )


@bot.tree.command(name="stats", description="Shows a user's stats")
async def stats(
    interaction: discord.Interaction,
    player: discord.Member = None,
):
    if not player:
        player = interaction.user

    # load the id dictionary
    id_lookup = uid_map.load_map_bidict()
    game_id = id_lookup.inverse[player.id]

    # open session with hyprd.mn
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://hyprd.mn/backend_dev/get_user_public.php?id={game_id}"
        ) as resp:
            # make local dict out of dict from hyprd.mn
            user_stats = await resp.json()
            # check if user has gotten deicide yet, then set check_deicide to corresponding emoji

        url = 'http://104.207.135.180:44454/vs/user_stats'
        params = {'user': f"{game_id}"}
        user_id_offset = 0
        elo_offset = 1
        rank_offset = 2
        async with session.post(url, data=params) as resp:
            data = await resp.content.read(4)
            test_array = []
            while data:
                int_val = int.from_bytes(data,"little")
                test_array.append(int_val)
                data = await resp.content.read(4)
            user_elo = test_array[elo_offset]/10000
            user_rank =  test_array[rank_offset]
            if user_elo >= 1000:
                description_string = f"{user_rank} | {str(user_elo)[:8]}"
            elif user_elo < 1000 and user_elo >=100:
                description_string = f"{user_rank} | {str(user_elo)[:7]}"
            elif user_elo < 100 and user_elo >=10:
                description_string = f"{user_rank} | {str(user_elo)[:6]}"
            else:
                description_string = f"{user_rank} | {str(user_elo)[:5]}"

        if user_stats["deicide"] == 1:
            check_deicide = ":white_check_mark:"
        else:
            check_deicide = ":cross_mark:"
        # parse playtime
        playtime_s = round(user_stats["playtime"] / 10000)
        playtime_m = round((playtime_s - playtime_s % 60) / 60)
        playtime_h = round((playtime_m - playtime_m % 60) / 60)
        # create embed object for the stats command
        stats_embed = discord.Embed(
            title=f"Stats for {user_stats['name']}",
            url=f"https://hyprd.mn/user/{game_id}",
            description=f"**Rank:** {user_stats['rank']}\n"
            + f"**Score:** [{round(user_stats['score']/10000, 3):.3f}](https://hyprd.mn/run/{user_stats['run_uid']})\n"
            + f"**Deaths:** {user_stats['deaths']}\n"
            + f"**Time Alive:** {playtime_h}h {playtime_m%60}m {round(playtime_s%60)}s\n"
            + f"**PVP Rank & ELO:** {description_string}\n"
            + f"**God Killer:** {check_deicide}",
        )
        stats_embed.set_thumbnail(url=player.display_avatar.url)
        await interaction.response.send_message(embed=stats_embed)


@bot.tree.command(name="queue", description="Shows the current multiplayer queue")
async def queue(
    interaction: discord.Interaction,
):
    queue_userids: list[int] = await cache.get_pvp_queue()

    # create embed object for the queue command
    description_string = "```\n"
    if len(queue_userids) == 0:
        description_string += "No players in queue."
    else:
        for index, item in enumerate(queue_userids):
            rank = index + 1
            user = await cache.get_user(item)
            description_string += f"{rank:02d} | {user['name']}\n"

    description_string += "```"
    queue_embed = discord.Embed(
        title="Current Multiplayer Queue", description=description_string
    )
    await interaction.response.send_message(embed=queue_embed)

@bot.tree.command(name="pvpleaderboard", description="Shows the current multiplayer top 10 leaderboard")
async def pvpleaderboard(
    interaction: discord.Interaction,
):
    url = 'http://104.207.135.180:44454/vs/leaderboard'
    params = {'begin': '0', 'count': '10'}
    version_offset = 0
    count_begin_offset = 1
    count_total_offset = 2
    leaderboard_offset = 3
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as resp:
            data = await resp.content.read(4)
            test_array = []
            while data:
                int_val = int.from_bytes(data,"little")
                test_array.append(int_val)
                data = await resp.content.read(4)
            version_number = test_array[version_offset]
            count_begin = test_array[count_begin_offset]
            count_total =  test_array[count_total_offset]
            leaderboard_raw = test_array[leaderboard_offset:]

    description_string = "```\n"
    index = 0

    while index < len(leaderboard_raw) - 1:
        rank = int((index / 2) + 1)
        user_id = leaderboard_raw[index]
        user = await cache.get_user(user_id)
        elo = (leaderboard_raw[index + 1]/10000)
        if elo >= 1000:
            description_string += f"{rank:02d} {str(elo)[:8]} {user['name']}"
        elif elo < 1000 and elo >=100:
            description_string += f"{rank:02d} {str(elo)[:7]} {user['name']}"
        elif elo < 100 and elo >=10:
            description_string += f"{rank:02d} {str(elo)[:6]} {user['name']}"
        else:
            description_string += f"{rank:02d} {str(elo)[:5]} {user['name']}"
        index += 2

    description_string += f"```"
    pvpleaderboard_embed = discord.Embed(
        title="Global PVP Leaderboard Top 10", description=description_string
    )
    await interaction.response.send_message(embed=pvpleaderboard_embed)


@bot.tree.command(
    name="remindme",
    description="Pings you when you are 1 spot away from playing on the queue",
)
async def reminder(interaction: discord.Interaction):
    id_lookup = uid_map.load_map_bidict()
    userid = id_lookup.inverse[interaction.user.id]

    user_was_added_to_reminders = await cache.add_user_to_queue_reminders(userid)

    if user_was_added_to_reminders:
        await interaction.response.send_message(
            f"Got it. I'll ping you the next time you're 3rd in queue.", ephemeral=True
        )

    else:
        await interaction.response.send_message(
            "You've already asked for a reminder!", ephemeral=True
        )


""" @bot.event
async def on_raw_reaction_add(payload):
    # check if reaction was added to a message in clips channel, and emoji was sorath eye
    if payload.channel_id == 1021473919716302888 and payload.emoji.id == 1277487425962115144:
        # check if 10 or more sorath eye reactions
        channel = bot.get_channel(1021473919716302888)
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        reaction = discord.utils.get(message.reactions, emoji='<:sorath_eye:1277487425962115144>')
        if reaction.count >= 10: """


# ran when a message is posted
@bot.event
async def on_message(message):
    start_time = time.monotonic()

    channel = bot.get_channel(CHANNEL_ID)
    channel_log = bot.get_channel(1153802687054364673)

    # prevents infinite loop from bot responding to itself
    if message.author == bot.user:
        return

    # register command
    # if message.content.startswith('register'):
    # register_id = str(message.content.split()[1])
    # update_dict(register_id, message.author.id, 'id_dictionary.json')

    # checks if message is from SORATH bot, and it is the "/hyperdemon pb" command
    if (
        message.author.id == 798042141988618251
        and message.interaction.name == "hyperdemon pb"
    ):
        embed_description = message.embeds[0].description
        embed_op_id = int(message.interaction.user.id)
        embed_type = message.interaction.name
        description = embed_description.splitlines()

        # parse embed information and store variables
        score_new = round(float(description[1].split()[1].strip("*")), 3)
        score_dif = round(float(description[1].split()[2].strip("()+")), 3)
        score_old = round(score_new - score_dif, 3)
        rank = int(description[0].split()[1].strip("*"))

        # update id dictionary
        # if rank <= 1000:
        # lb_dict = await get_shit()
        # update_dict(list(lb_dict.keys())[rank-1], embed_op_id, 'id_dictionary.json')

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://hyprd.mn/backend_dev/get_scores_public.php?start={rank-1}&count=1"
            ) as resp:
                user_lb_stats = await resp.json()
                update_dict(user_lb_stats[0]["user"], embed_op_id, "id_dictionary.json")

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
            while not (
                score_new >= role_array[x][0] and score_new < role_array[x + 1][0]
            ):
                x += 1
            else:
                new_role_id = role_array[x][1]
                next_score = role_array[x + 1]

        # check if this is their first time triggering bot and update role
        if old_role_id == "no score assigned":
            await add_role(message, new_role_id)
            added_roles.append(new_role_id)
            embed_role_update = discord.Embed(
                title=f"Updated roles for {message.interaction.user.name}"
            )
            if added_roles != []:
                addstring = f""
                for addedroleid in added_roles:
                    addstring = f"{addstring}<@&{addedroleid}>\n"
                embed_role_update.add_field(
                    name="**Added:**", value=addstring, inline=True
                )
            await message.channel.send(embed=embed_role_update)

        # check if new role is the same as old role and do nothing
        elif old_role_id == new_role_id:
            embed_role_update = discord.Embed(
                title=f"Updated roles for {message.interaction.user.name}"
            )
            if removed_roles != []:
                removestring = f""
                for removedroleid in removed_roles:
                    removestring = f"{removestring}<@&{removedroleid}>\n"
                embed_role_update.add_field(
                    name="**Removed:**", value=removestring, inline=True
                )
            if added_roles != []:
                addstring = f""
                for addedroleid in added_roles:
                    addstring = f"{addstring}<@&{addedroleid}>\n"
                embed_role_update.add_field(
                    name="**Added:**", value=addstring, inline=True
                )
            if added_roles != [] or removed_roles != []:
                await message.channel.send(embed=embed_role_update)
            if next_score != []:
                dist_next_role = round(next_score[0] - score_new, 3)
                await message.channel.send(
                    f"You're **{dist_next_role}** points away from the next role: <@&{next_score[1]}>"
                )
            else:
                await message.channel.send(
                    f"You are a god, {message.interaction.user.name}. No higher role left"
                )

        # replace old role with new role
        else:
            # remove old role
            await remove_role(message, old_role_id)
            removed_roles.append(old_role_id)
            # add new role
            await add_role(message, new_role_id)
            added_roles.append(new_role_id)
            # post embed with role changes
            embed_role_update = discord.Embed(
                title=f"Updated roles for {message.interaction.user.name}"
            )
            if removed_roles != []:
                removestring = f""
                for removedroleid in removed_roles:
                    removestring = f"{removestring}<@&{removedroleid}>\n"
                embed_role_update.add_field(
                    name="**Removed:**", value=removestring, inline=True
                )
            if added_roles != []:
                addstring = f""
                for addedroleid in added_roles:
                    addstring = f"{addstring}<@&{addedroleid}>\n"
                embed_role_update.add_field(
                    name="**Added:**", value=addstring, inline=True
                )
            await message.channel.send(embed=embed_role_update)
        print(
            f"on demand function took {round((time.monotonic() - start_time), 3)} seconds to execute"
        )
        await channel_log.send(message.jump_url)
        await channel_log.send(
            f"Execution took {round((time.monotonic() - start_time)*1000)}ms"
        )


bot.run(BOT_TOKEN)
