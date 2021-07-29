#rock kun discord bot study log level system
#credit to various internet references 

import math
import discord
import os
import asyncio
import asyncpg
from discord.ext import commands

my_secret = os.environ['TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.multiplier = 1

#database
async def initialize():
    await bot.wait_until_ready()
    conn = await async.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    await cur.execute("CREATE TABLE IF NOT EXISTS guildData (guild_id int, user_id int, study_time int, PRIMARY KEY (guild_id, user_id))")

@bot.event
async def on_ready():
    print(bot.user.name + " is online.")


@bot.command()
async def studying(ctx, start_hr: int, start_min: int, stop_hr: int, stop_min: int, member: discord.Member=None):
  if member is None: member = ctx.author

  async with cur.execute("INSERT OR IGNORE INTO guildData (guild_id, user_id, study_time) VALUES (?,?,?)", (ctx.guild.id, ctx.author.id, 0)) as cursor:

#lvl and exp before latest studying sesh
#retrieve study time from database
    cur = await cur.execute("SELECT study_time FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id))
    data = await cur.fetchone()
    old_study_time = data[0]
    old_exp = math.floor(old_study_time/60)  #exp gained every 60 mins study time
    old_lvl = math.sqrt(old_exp) / bot.multiplier

#calculate study sesh mins
    if stop_hr >= start_hr:
        if stop_min >= start_min :
            study_hr = stop_hr - start_hr
            study_min = stop_min - start_min
        else:
            study_min = 60 - start_min + stop_min
            study_hr = stop_hr - 1 - start_hr
        total_mins = study_hr * 60 + study_min
    else: total_mins = 0

#update data
    await cur.execute("UPDATE guildData SET study_time = study_time + ? WHERE guild_id = ? AND user_id = ?", (total_mins, ctx.guild.id, ctx.author.id))

#calculate exp and level to check if levelled up
    cur = await cur.execute("SELECT study_time FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id))
    data = await cur.fetchone()
    new_study_time = data[0]
    new_exp = math.floor(new_study_time/60)  #exp gained every 60 mins study time
    lvl = math.sqrt(new_exp) / bot.multiplier

    if lvl > old_lvl:
        new_lvl = math.floor(lvl)
        await ctx.send(f"{ctx.author.mention} Level up! Current level: {int(lvl)}")


#lvl roles 
    if lvl >= 20:
      if (new_role := discord.utils.get(member.guild.roles, id = 870051979114737674)) not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 870052123012911175))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    elif 15 <= lvl < 20:
      if (new_role := discord.utils.get(member.guild.roles, id = 870052123012911175)) not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 870052192021774346))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")  
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    elif 10 <= lvl < 15:
      if (new_role := discord.utils.get(member.guild.roles, id = 870052192021774346)) not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 870052254143639663))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    elif 5 <= lvl < 10:
      if (new_role := discord.utils.get(member.guild.roles, id = 870052254143639663)) not in member.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 870052296254443551))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    elif 2 <= lvl < 5:
      if (new_role := discord.utils.get(member.guild.roles, id = 870052296254443551)) not in member.roles:
        await member.add_roles(new_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name} title!")


    await cur.commit()


#stats commands
@bot.command()
async def stats(ctx, member: discord.Member=None):
    if member is None: member = ctx.author

    # get user exp
    async with cur.execute("SELECT study_time FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
        data = await cur.fetchone()
        study_time = data[0]
    
    exp = math.floor(study_time/60)
    lvl = math.sqrt(exp) / bot.multiplier


    # calculate rank
    async with cur.execute("SELECT study_time FROM guildData WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
        rank = 1
        async for value in cursor:
            if exp < value[0]:
                rank += 1

    lvl = int(math.sqrt(exp)//bot.multiplier)

    current_lvl_exp = (bot.multiplier*(lvl))**2
    next_lvl_exp = (bot.multiplier*((lvl+1)))**2

    lvl_percentage = ((exp-current_lvl_exp) / (next_lvl_exp-current_lvl_exp)) * 100

#total study time calculations
    total_days = math.floor(study_time/(24 * 60))
    total_hrs =  math.floor((study_time - (total_days*1440))/60)
    total_mins = study_time - total_hrs*60 - total_days*1440

    embed = discord.Embed(title=f"Stats for {member.name}", colour=discord.Colour.blue())
    embed.add_field(name="Level", value=str(lvl))
    embed.add_field(name="XP", value=f"{exp}/{next_lvl_exp}")
    embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}")
    embed.add_field(name="Level Progress", value=f"{round(lvl_percentage, 2)}%")
    embed.add_field(name="Total Study Time", value=f"{total_days}days {total_hrs}hrs {total_mins}mins")

    await ctx.send(embed=embed)


#leaderboard 
@bot.command()
async def leaderboard(ctx): 
    buttons = {}
    for i in range(1, 6):
        buttons[f"{i}\N{COMBINING ENCLOSING KEYCAP}"] = i 

    previous_page = 0
    current = 1
    index = 1
    entries_per_page = 10

    embed = discord.Embed(title=f"Leaderboard Page {current}", description="", colour=discord.Colour.blue())
    msg = await ctx.send(embed=embed)

    for button in buttons:
        await msg.add_reaction(button)

    while True:
        if current != previous_page:
            embed.title = f"Leaderboard Page {current}"
            embed.description = ""

            async with cur.execute(f"SELECT user_id, study_time FROM guildData WHERE guild_id = ? ORDER BY study_time DESC LIMIT ? OFFSET ? ", (ctx.guild.id, entries_per_page, entries_per_page*(current-1),)) as cursor:
                index = entries_per_page*(current-1)

                async for entry in cursor:
                    index += 1
                    member_id, study_time = entry
                    member = ctx.guild.get_member(member_id)
                    embed.description += f"{index}) {member.mention} : {study_time}\n"

                await msg.edit(embed=embed)

        try:
            reaction, user = await bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author and reaction.emoji in buttons, timeout=60.0)

        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        else:
            previous_page = current
            await msg.remove_reaction(reaction.emoji, ctx.author)
            current = buttons[reaction.emoji]


TOKEN = os.environ['TOKEN']
bot.loop.create_task(initialize())
bot.run(TOKEN)
asyncio.run(cur.close())
