import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import random

client = Bot(description="Dire Wolf by Marcus#3244", command_prefix="!", pm_help = False)

@client.event
async def on_ready():
	print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
	print('--------')
	print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
	print('--------')
	print('Use this link to invite {}:'.format(client.user.name))
	print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
	print('--------')
	print('Support Discord Server: https://discord.gg/FNNNgqb')
	print('Github Link: https://github.com/Habchy/BasicBot')
	print('--------')
	print('You are running Dire Wolf v1')
	print('Created by Marcus#3244')
	return await client.change_presence(game=discord.Game(name='Dungeon World'))

@client.command()
async def ping(*args):

	await client.say(":ping_pong: Pong!")
	await asyncio.sleep(3)

@client.command()
async def hack(*args):
	try:
		mod = int(args[0])
	except:
		mod = 0
	try:
		dmgmod = int(args[1])
	except:
		dmgmod = 0
	roll1 = random.randint(1,6)
	roll2 = random.randint(1,6)
	dmg = random.randint(1,10)
	total = (roll1 + roll2 + mod)
	finalresult = "2d6 (%i, %i) + %i = %i" % (roll1, roll2, mod, roll1 + roll2 + mod)
	finaldamage = "1d10 (%i) + %i = %i" % (dmg, dmgmod, dmg + dmgmod)
	result = "On a 10+, you deal your damage to the enemy and avoid their attack. At your option, you may choose to do +1d6 damage but expose yourself to the enemy’s attack." if int(total) >= 10 else "On a 7–9, you deal your damage to the enemy and the enemy makes an attack against you." if 9 >= int(total) >= 7 else "Miss!"
	embed=discord.Embed(title="Hack and Slash", description="*When you attack an enemy in melee, roll+Str.*" "\n\n**Roll:** " + finalresult + "\n**Damage:** " + finaldamage + "\n", color=0xd6d136)
	embed.add_field(name="Results:", value=result, inline=False)
	embed.set_footer(text="Basic Move, 58")
	await client.say(embed=embed)

client.run('NDIwMDkxNDE2Mzc1NDU5ODcw.DX5p3A.s7Qla8wABEvNhaHP-AO2gvV3UKE')

# Please join this Discord server if you need help: https://discord.gg/FNNNgqb
# The help command is currently set to be not be Direct Messaged.
# If you would like to change that, change "pm_help = False" to "pm_help = True" on line 9.
