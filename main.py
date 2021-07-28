import math
import aiosqlite
import discord
import os
from discord.ext import commands


my_secret = os.environ['TOKEN']

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.multiplier = 1


#database
async def initialize():
    await bot.wait_until_ready()
    bot.db = await aiosqlite.connect("expData.db")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS guildData (guild_id int, user_id int, study_time int, PRIMARY KEY (guild_id, user_id))")

@bot.event
async def on_ready():
    print(bot.user.name + " is online.")


@bot.command()
async def studying(ctx, start_hr: int, start_min: int, stop_hr: int, stop_min: int, member: discord.Member=None):
  if member is None: member = ctx.author

  async with bot.db.execute("INSERT OR IGNORE INTO guildData (guild_id, user_id, study_time) VALUES (?,?,?)", (ctx.guild.id, ctx.author.id, 0)) as cursor:

#calculate study sesh mins
    if stop_min >= start_min :
      study_hr = stop_hr - start_hr
      study_min = stop_min - start_min
    else:
      study_min = 60 - start_min + stop_min
      study_hr = stop_hr - 1 - start_hr

    total_mins = study_hr * 60 + study_min

#update data
    await bot.db.execute("UPDATE guildData SET study_time = study_time + ? WHERE guild_id = ? AND user_id = ?", (total_mins, ctx.guild.id, ctx.author.id))

#calculate exp and level to check if levelled up
#retrieve study time from database
    cur = await bot.db.execute("SELECT study_time FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id))
    data = await cur.fetchone()
    study_time = data[0]

#exp gained every 60 mins study time
    exp = math.floor(study_time/60)
    lvl = math.sqrt(exp) / bot.multiplier

    if lvl.is_integer():
        await ctx.send(f"{ctx.author.mention} Level up! Current level: {int(lvl)}.")


#lvl roles 
    if 20 <= lvl <15:
      if (new_role := discord.utils.get(member.guild.roles, id = 868368401612038186)) not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 868368367818522644))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")    
    if 15 <= lvl <10:
      if (new_role := discord.utils.get(member.guild.roles, id = 868368401612038186)) not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 868368367818522644))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    if 10 <= lvl <15:
      if (new_role := discord.utils.get(member.guild.roles, id = 868368401612038186)) not in ctx.author.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 868368367818522644))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    elif 5 <= lvl < 10:
      if (new_role := discord.utils.get(member.guild.roles, id = 868368367818522644)) not in member.roles:
        await member.add_roles(new_role)
        await member.remove_roles(discord.utils.get(member.guild.roles, id = 868368310025203733))
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name}  title!")
    elif 2 <= lvl <5:
      if (new_role := discord.utils.get(member.guild.roles, id = 868368310025203733)) not in member.roles:
        await member.add_roles(new_role)
        await ctx.send(f"{ctx.author.mention} Unlocked {new_role.name} title!")


    await bot.db.commit()


#stats commands
@bot.command()
async def stats(ctx, member: discord.Member=None):
    if member is None: member = ctx.author

    # get user exp
    async with bot.db.execute("SELECT study_time FROM guildData WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id)) as cursor:
        data = await cursor.fetchone()
        study_time = data[0]
    
    exp = math.floor(study_time/60)
    lvl = math.sqrt(exp) / bot.multiplier


    # calculate rank
    async with bot.db.execute("SELECT study_time FROM guildData WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
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
    total_mins = study_time - total_hrs*60

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

            async with bot.db.execute(f"SELECT user_id, study_time FROM guildData WHERE guild_id = ? ORDER BY study_time DESC LIMIT ? OFFSET ? ", (ctx.guild.id, entries_per_page, entries_per_page*(current-1),)) as cursor:
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
asyncio.run(bot.db.close())
