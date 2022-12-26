#cooldown bot code
#written by sadie/kittmaus 12.20.22ish-12.25.22

import dotenv
dotenv.load_dotenv()

import pymongo 
import interactions 
import os

#shh dont tell anyone
bot = interactions.Client(token=os.getenv('BOT_TOKEN'),
                          default_scope=804491292405923841)
mongouri = os.getenv('URI')

#basic mongo setup
client = pymongo.MongoClient(mongouri)
db = client["Polynomers"]
col = db["Users/IDs"]



#ping command
@bot.command(name="ping", description="Sends ping")
async def ping(ctx: interactions.CommandContext):
  await ctx.send(f"Pong! Latency: {'%.3f'%(bot.latency)} ms.")




#cooldown command (adds cooldown role, removes everything else, stores old roles in database)
@bot.command(
  name="cooldown",
  description=
  "Gives the user the cooldown role, and takes away all other roles.",
  options=[
    interactions.Option(name="member",
                        description="Who are you giving the role to?",
                        type=interactions.OptionType.USER,
                        required=True)
  ])
async def giverole(ctx: interactions.CommandContext, member: any):
  targid = int(member.id)
  if (col.find_one({"id": targid}) != None): # "does the member have an entry in the database?"
    await ctx.send(content=f"{member.username} is already cooling down.",
                   ephemeral=True)
  else:
    cguild = await ctx.get_guild()
    targname = member.username 
    targroles = member.roles
    userdict = {"name": targname, "id": targid, "roles": targroles}
    col.insert_one(userdict)
    await member.add_role(await cguild.get_role(1051252322803646535), 804491292405923841)
    for i in member.roles: #cycles through member roles removing them one by one
      await member.remove_role(i,804491292405923841)
    await ctx.send(content=f"{targname} has been given the cooldown role.",
                   ephemeral=True)




#reverse cooldown command (removes cooldown role, finds old roles in database, adds roles back, deletes database entry)
@bot.command(
  name="uncooldown",
  description=
  "Remove the cooldown role from the targeted member, and returns their roles.",
  options=[
    interactions.Option(name="member",
                        description="Who are you removing the role from?",
                        type=interactions.OptionType.USER,
                        required=True)
  ])
async def removerole(ctx: interactions.CommandContext, member: any):
  targid = int(member.id)
  if (col.find_one({"id": targid}) == None): # "does the member not have an entry in the database?"
    await ctx.send(content=f"{member.username} is not cooling down.",
                   ephemeral=True)
  else:
    cguild = await ctx.get_guild()
    for i in ((col.find_one({"name": member.username}))["roles"]): #cycles through the database adding roles back one by one
      await member.add_role(i,804491292405923841)
    col.delete_one({"id": targid}) 
    await member.remove_role(await cguild.get_role(1051252322803646535), 804491292405923841)
    await ctx.send(
      content=f"The cooldown role has been removed from {member.username}",
      ephemeral=True)

bot.start()