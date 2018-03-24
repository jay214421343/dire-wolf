import discord
import asyncio
import os
import aiohttp
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext.commands import CommandInvokeError
import platform
import random
from funcs import *
import simplejson
import re

client = Bot(description="Dire Wolf by Marcus#3244", command_prefix=";", pm_help = False)

@client.event
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('Add me to your server: https://discordapp.com/api/oauth2/authorize?client_id=425813218959556610&permissions=0&redirect_uri=https%3A%2F%2Finvite.direwolf.io%2F&scope=bot'.format(client.user.id))
    print('--------')
    print('Support Discord Server: https://discord.gg/D6DenCC')
    print('Github Link: https://github.com/Marc5567/dire-wolf')
    print('--------')
    print('You are running Dire Wolf v1.0.4')
    print('Created by Marcus#3244')
    print('--------')
    client.loop.create_task(update_sources_loop()) # creates update loop for data sources
    return await client.change_presence(game=discord.Game(name='Dungeon World'))

client.remove_command('help') # Overwrites the default discord help command so we can have a fancy embed one

# Lookup source data parsing/updating:
UPDATE_DELAY = 60 * 1440   # update once a day, probably.

ITEM_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/items.txt"
MONSTER_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/monsters"
SPELL_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/spells"
TAG_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/tags"
PLAYBOOK_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/playbooks.json"
ITEM_DIVIDER = "***"  # a string that divides distinct items.
META_LINES = 0  # the number of lines of meta info each item has
items = []
monsters = []
spells = []
tags = []
playbooks = []

@client.event #I'm not sure what this does? I think it's supposed to return "command not found" if user gives a command that doesn't exist? May have things that aren't defined here...
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, CommandInvokeError):
        error = error.original
    await client.send_message(ctx.message.channel, error)


async def update_sources_loop():
    try:
        await client.wait_until_ready()
        while not client.is_closed:
            await update_sources()
            await asyncio.sleep(UPDATE_DELAY)
    except asyncio.CancelledError:
        pass

async def update_sources():
    # item indexing
    async with aiohttp.ClientSession() as session:
        async with session.get(ITEM_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update items: {text}")

            raw_items = [t.strip() for t in text.split(ITEM_DIVIDER)]  # filter out index

            for item in raw_items:
                lines = item.split('\n')
                name = lines[0].strip('### ')
                meta = '\n'.join(lines[1::])
                desc = '\n'.join(lines)
                for dup in [i for i in items if name.lower() == i['name'].lower()]:
                    items.remove(dup)  # remove duplicates

                items.append({'name': name, 'meta': meta, 'desc': desc})

            print("Updated items!")
    # monster indexing
    async with aiohttp.ClientSession() as session:
        async with session.get(MONSTER_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update monsters: {text}")

            raw_monsters = [t.strip() for t in text.split(ITEM_DIVIDER)]  # filter out index

            for monster in raw_monsters:
                lines = monster.split('\n')
                name = lines[0].strip('### ')
                meta = '\n'.join(lines[1::])
                desc = '\n'.join(lines)
                for dup in [i for i in monsters if name.lower() == i['name'].lower()]:
                    monsters.remove(dup)  # remove duplicates

                monsters.append({'name': name, 'meta': meta, 'desc': desc})

            print("Updated monsters!")
    # spell indexing
    async with aiohttp.ClientSession() as session:
        async with session.get(SPELL_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update spells: {text}")

            raw_spells = [t.strip() for t in text.split(ITEM_DIVIDER)]  # filter out index

            for spell in raw_spells:
                lines = spell.split('\n')
                name = lines[0].strip('### ')
                meta = '\n'.join(lines[1::])
                desc = '\n'.join(lines)
                for dup in [i for i in spells if name.lower() == i['name'].lower()]:
                    spells.remove(dup)  # remove duplicates

                spells.append({'name': name, 'meta': meta, 'desc': desc})

            print("Updated spells!")
    # tag indexing
    async with aiohttp.ClientSession() as session:
        async with session.get(TAG_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update tags: {text}")

            raw_tags = [t.strip() for t in text.split(ITEM_DIVIDER)]  # filter out index

            for tag in raw_tags:
                lines = tag.split('\n')
                name = lines[0].strip('### ')
                meta = '\n'.join(lines[1::])
                desc = '\n'.join(lines)
                for dup in [i for i in tags if name.lower() == i['name'].lower()]:
                    tags.remove(dup)  # remove duplicates

                tags.append({'name': name, 'meta': meta, 'desc': desc})

            print("Updated tags!")
    # playbook indexing
    async with aiohttp.ClientSession() as session:
        async with session.get(PLAYBOOK_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update playbooks: {text}")

            playbooks.clear()
            d = simplejson.loads(text)

            for key,value in d.items():

                playbooks.append(value)

            print("Updated playbooks!")

# Lookup commands:
@client.command(pass_context=True)
async def item(ctx, *, name=''):
    """Looks up a Dungeon World item.\nLists by category available by searching \"Weapons\", \"Armor\", etc.\nFull list of categories can be viewed by searching \"Item Categories\"."""
    result = search(items, 'name', name)
    if result is None:
        return await client.say('Item not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    meta = result['meta']
    meta2 = [meta[i:i + 1024] for i in range(2048, len(meta), 1024)]
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=result['name'], description=meta[0:2048], color=discord.Color(value=color))
    for piece in meta2:
        embed.add_field(name="\u200b", value=piece)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def monster(ctx, *, name=''):
    """Looks up a Dungeon World monster.\nSearch with environment name for list of monsters found in that environment.\n\"Environment List\" for a list of available environments."""
    result = search(monsters, 'name', name)
    if result is None:
        return await client.say('Monster not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    meta = result['meta']
    meta2 = [meta[i:i + 1024] for i in range(2048, len(meta), 1024)]
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=result['name'], description=meta[0:2048], color=discord.Color(value=color))
    for piece in meta2:
        embed.add_field(name="\u200b", value=piece)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def spell(ctx, *, name=''):
    """Looks up a Dungeon World spell.\nSearch \"Wizard\" or \"Cleric\" for class spell lists."""
    result = search(spells, 'name', name)
    if result is None:
        return await client.say('Spell not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    meta = result['meta']
    meta2 = [meta[i:i + 1024] for i in range(2048, len(meta), 1024)]
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=result['name'], description=meta[0:2048], color=discord.Color(value=color))
    for piece in meta2:
        embed.add_field(name="\u200b", value=piece)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def tag(ctx, *, name=''):
    """Looks up a Dungeon World item tag.\nSearch \"Item Tags\" or \"Monster Tags\" to view respective lists."""
    result = search(tags, 'name', name)
    if result is None:
        return await client.say('Tag not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    meta = result['meta']
    meta2 = [meta[i:i + 1024] for i in range(2048, len(meta), 1024)]
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=result['name'], description=meta[0:2048], color=discord.Color(value=color))
    for piece in meta2:
        embed.add_field(name="\u200b", value=piece)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def playbook(ctx, *, name=''):
    """Looks up a core Dungeon World playbook.\nSearch \"list\" a list of available playbooks."""

    result = search(playbooks, 'name', name)
    if result is None:
        return await client.say('Playbook not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    stats = result['maxhp'] + "\n" + result['basedmg']
    alignment = '\n'.join(result['align'])
    race = '\n'.join(result['race'])
    gear = '\n'.join(result['gear'])
    startingmoves = '\n'.join(result['starting']).replace('Starting Moves', '')
    advmoves1 = '\n'.join(result['master']).replace('2-5 Moves', '')
    advmoves2 = '\n'.join(result['advanced']).replace('6-10 Moves', '')
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=result['name'], description=stats, color=discord.Color(value=color))
    embed.add_field(name="Race", value=race, inline=True)
    embed.add_field(name="Alignment", value=alignment, inline=True)
    embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
    embed.add_field(name="Starting Moves", value=startingmoves, inline=True)
    embed.add_field(name="Level 2-5 Moves", value=advmoves1, inline=True)
    embed.add_field(name="Level 6-10 Moves", value=advmoves2, inline=True)
    embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
    embed.add_field(name="Gear", value=gear)
    await client.say(embed=embed)


    #cutup = [result['align'][i:i + 2] for i in range(0, len(result['align']), 2)] #x
    #for l in cutup: #x
        # each l is a list of the title + body of an alignment
        #embed.add_field(name=l[0], value=l[1], inline=True) #x

@client.command()
async def roll(*args):
    """Roll dice in standard notation"""

    # expects format to be 2d6 or 2d6+1 or 3d6k2 or 3d6k2+1
    print("ROLL", args)

    a = ' '.join(args)

    base = re.findall('([0-9]+)d([0-9]+)', a)
    keep = re.search('(k)([0-9]+)',a)
    comment = re.search('#(.*.?)+',a)

    if a.count('+') > 1:
        b,c = a.rsplit("d", 1)
        modifier = re.search('(\+|\-)([0-9]+)',c)
    else:
        modifier = ""

    print("mod", modifier)

    raw_roll = []

    result = "Please use standard dice notation, i.e., 2d6 or 2d6+1."

    if base:
        # this is a correctly formatted roll string
        for die_tuple in base:
            print("count", die_tuple[0])  # count
            print("sides", die_tuple[1])  # sides

            for i in range(int(die_tuple[0])):
                raw_roll.append(str(random.randint(1,int(die_tuple[1]))))

            print("raw", raw_roll)

            if keep:
                print(keep.group(1))
                print(keep.group(2))
                if int(die_tuple[0]) - int(keep.group(2)) >= 1:
                    r = int(die_tuple[0]) - int(keep.group(2))
                    print("r", r)
                    for i in range(r):
                        raw_roll[i] = "~%s~" % (raw_roll[i])

                print("raw", raw_roll)

            # now sum that up (requires stripping and converting to int)
            math_roll = [int(s) for s in raw_roll if not "~" in s]
            print("math", math_roll)
            total = sum(math_roll)
            print("total", total)

            final_total = total

        if modifier:
            print(modifier.group(1))
            print(modifier.group(2))
            if modifier.group(1) == '+':
                final_total = total + int(modifier.group(2))
            else:
                final_total = total - int(modifier.group(2))

        print(final_total)

    if base and modifier:
        result = "[%s] %s %s = %s" % (' '.join(raw_roll), modifier.group(1), modifier.group(2), final_total)
    elif base:
        result = "[%s] = %s" % (' '.join(raw_roll), final_total)

    print(result)

    if comment:
        result = result + " " + comment.group()

    embed=discord.Embed()
    embed.title = "Roll Result"
    embed.description = "Rolling!\n\n" + result
    await client.say(embed=embed)

@client.command()
async def hack(*args):
    """Rolls Hack and Slash""" # to be rewritten as move with subcommands for all moves
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


# Help dialogue commands:
@client.group(pass_context=True)
async def help(ctx):
    if ctx.invoked_subcommand is None:
        embed = EmbedWithAuthor(ctx)
        embed.title = ""
        embed.description = "Dire Wolf, a Dungeon World utility bot created by Marcus#3244\nJoin the official support and testing server [here](https://discord.gg/D6DenCC)\nInvite Dire Wolf to your server [here](https://discordapp.com/api/oauth2/authorize?client_id=425813218959556610&permissions=0&redirect_uri=https%3A%2F%2Finvite.direwolf.io%2F&scope=bot)"
        embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
        embed.add_field(name="Help", value="**help** - Shows this message\n""**help <command>** - Shows syntax and more info for specific commands", inline=False)
        embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
        embed.add_field(name="Lookup", value="**monster** - Looks up a monster\n**spell** - Looks up a spell\n**item** - Looks up an item\n**tag** - Looks up tags\n**playbook** - looks up core playbooks", inline=False)
        await client.say(embed=embed)

@help.command(pass_context=True)
async def monster(ctx):
    embed = EmbedWithAuthor(ctx)
    embed.title = "Help"
    embed.add_field(name=";monster <name>", value="__"+" "*200+"__"+"Looks up a Dungeon World monster.\n\nSearch with environment name for list of monsters found in that environment.\n\n\"Environment List\" for a list of available environments.")
    await client.say(embed=embed)

@help.command(pass_context=True)
async def spell(ctx):
    embed = EmbedWithAuthor(ctx)
    embed.title = "Help"
    embed.add_field(name=";spell <name>", value="__"+" "*200+"__"+"Looks up a Dungeon World spell.\n\nSearch \"Wizard\" or \"Cleric\" for class spell lists.")
    await client.say(embed=embed)

@help.command(pass_context=True)
async def item(ctx):
    embed = EmbedWithAuthor(ctx)
    embed.title = "Help"
    embed.add_field(name=";item <name>", value="__"+" "*200+"__"+"Looks up a Dungeon World item.\n\nLists by category available by searching \"Weapons\", \"Armor\", etc.\n\nFull list of categories can be viewed by searching \"Item Categories\".")
    await client.say(embed=embed)

@help.command(pass_context=True)
async def tag(ctx):
    embed = EmbedWithAuthor(ctx)
    embed.title = "Help"
    embed.add_field(name=";tag <name>", value="__"+" "*200+"__"+"Looks up a Dungeon World item tag.\n\nSearch \"Item Tags\" or \"Monster Tags\" to view respective lists.")
    await client.say(embed=embed)

client.run('TOKEN')
