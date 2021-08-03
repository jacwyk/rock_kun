#rock kun discord bot study log level system
#credit to various internet references 

import math
import discord
import os
import asyncio
import asyncpg
from discord.ext import commands

TOKEN = os.environ['TOKEN']
DATABASE_URL = os.environ['DATABASE_URL'] #Heroku

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.multiplier = 1


#database
async def initialize():
    await bot.wait_until_ready()
    bot.db = await asyncpg.connect(DATABASE_URL)
    await bot.db.execute('''CREATE TABLE IF NOT EXISTS guildData (guild_id bigint, user_id bigint PRIMARY KEY, study_time int)''')


@bot.event
async def on_ready():
    print(bot.user.name + " is online.")


#-------------studying command main function--------------------
#studying command to log in study time
@bot.command()
async def studying(ctx, start_hr: int, start_min: int, stop_hr: int, stop_min: int, member: discord.Member=None):
    if member is None: member = ctx.author
    await bot.db.execute('''INSERT INTO guildData(guild_id, user_id, study_time) VALUES($1::bigint, $2::bigint, $3) ON CONFLICT (user_id) DO NOTHING''', ctx.guild.id, ctx.author.id, 0)
    #calculate old lvl
    old_xp_lvl = await calculate_xp_lvl(ctx)
    old_lvl = old_xp_lvl[1]
    #calculate new total study time after latest session logged
    study_time = calculate_studytime(start_hr, start_min, stop_hr, stop_min)
    #update data
    await bot.db.execute('''UPDATE guildData SET study_time = study_time + $1::int WHERE guild_id = $2::bigint AND user_id = $3::bigint''', study_time, ctx.guild.id, ctx.author.id)
    #check level up after latest session, assign new level roles
    new_xp_lvl = await calculate_xp_lvl(ctx)
    lvl = new_xp_lvl[1]
    await lvlup_announcement(ctx, lvl, old_lvl)
    await assign_lvlroles(ctx, member, lvl)



#-------------studying command functions---------------------
#calculate old level before new study session logged 
async def calculate_xp_lvl(ctx):
    #retrieve study time from database
    data = await bot.db.fetchval('''SELECT study_time::int FROM guildData WHERE guild_id = $1::bigint AND user_id = $2::bigint''', ctx.guild.id, ctx.author.id)
    study_time = int(data)
    #lvl and exp before latest studying sesh
    xp = math.floor(study_time/60)  #1xp every 60mins
    lvl = math.floor(math.sqrt(xp) / bot.multiplier)
    return xp, lvl, study_time



#calculate study sesh mins
def calculate_studytime(start_hr, start_min, stop_hr, stop_min):
    if stop_hr >= start_hr:
        if stop_min >= start_min :
            study_hr = stop_hr - start_hr
            study_min = stop_min - start_min
        else:
            study_min = 60 - start_min + stop_min
            study_hr = stop_hr - 1 - start_hr
        total_mins = study_hr * 60 + study_min
    else: total_mins = 0
    return total_mins



#calculate new exp and level to check if levelled up
async def lvlup_announcement(ctx, lvl, old_lvl):
    if lvl > old_lvl:
        new_lvl = math.floor(lvl)
        await ctx.send(f"{ctx.author.mention} Level up! Current level: {int(lvl)}")



#assigning new level roles/deleting old lvl roles
async def assign_lvlroles(ctx, member, lvl):
    await bot.db.execute('''SELECT study_time::int FROM guildData WHERE guild_id = $1::bigint AND user_id = $2::bigint''', ctx.guild.id, ctx.author.id)

    if lvl >= 20:
      new_role = discord.utils.get(member.guild.roles, id = 872119399014871080)
      old_role = discord.utils.get(member.guild.roles, id = 872119375983956068)
      if new_role not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(old_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")

    elif 15 <= lvl < 20:
      new_role = discord.utils.get(member.guild.roles, id = 872119375983956068)
      old_role = discord.utils.get(member.guild.roles, id = 872119353112395886)
      if new_role not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(old_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")  

    elif 10 <= lvl < 15:
      new_role = discord.utils.get(member.guild.roles, id = 872119353112395886)
      old_role = discord.utils.get(member.guild.roles, id = 872119331947962448)
      if new_role not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(old_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")

    elif 5 <= lvl < 10:
      new_role = discord.utils.get(member.guild.roles, id = 872119331947962448)
      old_role = discord.utils.get(member.guild.roles, id = 872119289568690226)
      if new_role not in member.roles:
        await member.add_roles(new_role)
        await member.remove_roles(old_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")

    elif 2 <= lvl < 5:
      new_role = discord.utils.get(member.guild.roles, id = 872119289568690226)
      if new_role not in member.roles:
        await member.add_roles(new_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name} title!")





#-------------------stats command-------------------------------
@bot.command()
async def stats(ctx, member: discord.Member=None):
    if member is None: member = ctx.author
    # get user xp, lvl, study time
    xp_lvl_study_time = await calculate_xp_lvl(ctx)
    xp = xp_lvl_study_time[0]
    lvl = xp_lvl_study_time[1]
    study_time = xp_lvl_study_time[2]
    
    #calculate rank **require edit
    #result = await bot.db.fetch('''SELECT user_id::bigint FROM guildData WHERE guild_id = $1::bigint ORDER BY GREATEST(study_time) DESC''', ctx.guild.id)
    #rank = result.index(ctx.author.id) + 1

    #calculate lvl progress
    current_lvl_xp = (bot.multiplier*(lvl))**2
    next_lvl_xp = (bot.multiplier*((lvl+1)))**2

    lvl_percentage = ((xp - current_lvl_xp) / (next_lvl_xp - current_lvl_xp)) * 100

    #total study time calculations
    total_days = math.floor(study_time/(24 * 60))
    total_hrs =  math.floor((study_time - (total_days*1440))/60)
    total_mins = study_time - total_hrs*60 - total_days*1440

    #send stats
    embed = discord.Embed(title=f"Stats for {member.name}", colour=discord.Colour.blue())
    embed.add_field(name="Level", value=str(lvl))
    embed.add_field(name="XP", value=f"{xp}/{next_lvl_xp}")
    #embed.add_field(name="Rank", value=f"{rank}/{ctx.guild.member_count}")
    embed.add_field(name="Level Progress", value=f"{round(lvl_percentage, 2)}%")
    embed.add_field(name="Total Study Time", value=f"{total_days}days {total_hrs}hrs {total_mins}mins")

    await ctx.send(embed=embed)





#----------------leaderboard command-----------------------------
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

            await bot.db.execute(f'''SELECT user_id::bigint, study_time::int FROM guildData WHERE guild_id = $1::bigint ORDER BY study_time::int DESC LIMIT ($2) OFFSET ($3)''', ctx.guild.id, entries_per_page, entries_per_page*(current-1))
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


bot.loop.create_task(initialize())
bot.run(TOKEN)
asyncio.run(bot.db.close())
