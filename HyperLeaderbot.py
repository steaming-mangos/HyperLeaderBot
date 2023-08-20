from discord.ext import commands
import discord

BOT_TOKEN = # **Insert Token**
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
    [420, 1054220981994004520]
    ]

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# function for when a message is posted
@bot.event
async def on_message(message):
    channel = bot.get_channel(CHANNEL_ID)

    # prevents infinite loop from bot responding to itself
    if message.author == bot.user:
        return

    # checks if message is from SORATH bot, and it is the "/hyperdemon pb" command
    if message.author.id == 798042141988618251 and message.interaction.name == "hyperdemon pb":
        embed_description = message.embeds[0].description
        embed_op_id = message.interaction.user.id
        embed_type = message.interaction.name
        description = embed_description.splitlines()
       
        # parse embed information and store variables
        score_new = round(float(description[1].split()[1].strip("*")), 3)
        score_dif = round(float(description[1].split()[2].strip("()+")), 3)
        score_old = round(score_new-score_dif, 3)

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

        # check if score is above 420
        elif score_new >= 420:
            new_role_id = role_array[19][1]

        # determine which role is correct for new score
        else:
            x = 1
            while not (score_new >= role_array[x][0] and score_new < role_array[x+1][0]):
                x += 1
            else:
                new_role_id = role_array[x][1]

        # check if this is their first time triggering bot and update role
        if old_role_id == "no score assigned":
            await message.interaction.user.add_roles(discord.utils.get(message.interaction.user.guild.roles, id = new_role_id))
        
        # check if new role is the same as old role and do nothing
        elif old_role_id == new_role_id:
            print("no role update was needed")

        # replace old role with new role
        else:
            # remove old role
            await message.interaction.user.remove_roles(discord.utils.get(message.interaction.user.guild.roles, id = old_role_id))
            # add new role
            await message.interaction.user.add_roles(discord.utils.get(message.interaction.user.guild.roles, id = new_role_id))




bot.run(BOT_TOKEN)
    
