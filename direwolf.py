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

client = Bot(description="Dire Wolf by Marcus#3244", command_prefix="!", pm_help = False)

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

client.remove_command('help') # removes the default discord help command so we can have a fancy embed one

# Lookup source data parsing/updating:
UPDATE_DELAY = 60 * 1440   # update once a day, probably.

ITEM_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/items.txt"
MONSTER_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/monsters"
SPELL_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/spells"
TAG_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/tags"
PLAYBOOK_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/playbooks.json"
MOVE_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/moves.json"
ROLLMOVE_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/rollmoves.json"
ITEM_DIVIDER = "***"  
META_LINES = 0  
items = []
monsters = []
spells = []
tags = []
playbooks = []
moves = []
rollmoves = []

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
    # move indexing
    async with aiohttp.ClientSession() as session:
        async with session.get(MOVE_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update moves: {text}")

            moves.clear()
            d = simplejson.loads(text)

            for key,value in d.items():

                moves.append(value)

            print("Updated moves!")

    async with aiohttp.ClientSession() as session:
        async with session.get(ROLLMOVE_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update rollmoves: {text}")

            rollmoves.clear()
            d = simplejson.loads(text)

            for key,value in d.items():

                rollmoves.append(value)

            print("Updated rollmoves!")



# Lookup commands:
@client.command(pass_context=True, name='item', aliases='i')
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

@client.command(pass_context=True, name='monster', aliases=['m'])
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

@client.command(pass_context=True, name='spell', aliases='s')
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

@client.command(pass_context=True, name='tag', aliases='t')
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

@client.command(pass_context=True, name='playbook', aliases='p')
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
    
@client.command(pass_context=True)
async def move(ctx, *, name=''):
    """Looks up a Dungeon World move."""
    result = search(moves, 'name', name)
    if result is None:
        return await client.say('Move not found.')
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
    desc = '\n'.join(result['desc'])
    source = '\n'.join(result['source'])
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=result['name'], description=desc, color=discord.Color(value=color))
    embed.set_footer(text=source)
    await client.say(embed=embed)
    #print(name, desc, source)

@client.command(pass_context=True, name='roll', aliases='r')
async def roll(ctx, *args):
    """Roll dice in standard notation"""
    # expects format to be 2d6 or 2d6+1 or 3d6k2 or 3d6k2+1
    print("ROLL", args)

    a = ' '.join(args)

    base = re.findall('([0-9]+)d([0-9]+)', a)
    best = re.search('(b)', a)
    worst = re.search('(w)', a)
    comment = re.search('#(.*.?)+', a)

    if a.count('+') >= 1:
        b,c = a.rsplit("d", 1)
        modifier = re.search('(\+|\-)([0-9]+)', c)

    else:
        modifier = ""

    raw_roll = []
    result = "Please use standard dice notation, i.e., 2d6 or 2d6+1."

    if base:
        for die_tuple in base:

            for i in range(int(die_tuple[0])):
                raw_roll.append(str(random.randint(1,int(die_tuple[1]))))

            print("raw", raw_roll)

            
            if best:
                int_roll.sort()

            if worst:
                int_roll.sort(reverse=True)

            if best or worst:
                raw_roll = []
                for x in int_roll[:-1]:
                    raw_roll.append("~~%s~~" % (str(x)))

                raw_roll.append("%s" % (str(int_roll[-1])))

                print("pared raw", raw_roll)

            math_roll = [int(s) for s in raw_roll if not "~~" in s]
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
        result = "(%s) %s %s = `%s`" % (', '.join(raw_roll), modifier.group(1), modifier.group(2), final_total) # added + cut_roll
    elif base:
        result = "(%s) = `%s`" % (', '.join(raw_roll), final_total)

    print(result)

    if comment:
        result = result + " " + comment.group()
    embed = EmbedWithAuthor(ctx)
    embed.title = "Rolling: " + args[0]
    embed.description = result
    await client.say(embed=embed)


@client.command(pass_context=True, name='moveroll', aliases=['mr'])
async def moveroll(ctx, name='', *args):
    """Rolls a move and gives the results"""
    result = search(rollmoves, 'name', name)
    if result is None:
        return await client.say('Move not found.')
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

    try:
        mod = int(args[0])
    except:
        mod = 0
    #try:
    #    dmgmod = int(args[1])
    #except:
    #    dmgmod = 0
    roll1 = random.randint(1,6)
    roll2 = random.randint(1,6)
    #chardmg =
    #dmg = random.randint(1,10)
    total = (roll1 + roll2 + mod)
    finalresult = "2d6 (%i, %i) + %i = %i" % (roll1, roll2, mod, total)
    #finaldamage = "%i (%i) + %i = %i" % (chardmg, dmg, dmgmod, dmg + dmgmod)
    desc = '\n'.join(result['desc'])
    hit = '\n'.join(result['hit'])
    partial = '\n'.join(result['partial'])
    miss = '\n'.join(result['miss'])
    source = '\n'.join(result['source'])
    results = hit if int(total) >= 10 else partial if 9 >= int(total) >= 7 else miss
    embed = EmbedWithAuthor(ctx)
    embed.title = result['name']
    embed.description = desc + "\n\n**Roll:** " + finalresult + "\n"
    embed.add_field(name="Results:", value=results, inline=False)
    embed.set_footer(text=source)
    await client.say(embed=embed)


# Help dialogue commands:
@client.group(pass_context=True)
async def help(ctx):
    if ctx.invoked_subcommand is None:
        color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        color = int(color, 16)
        embed=discord.Embed(title="", description="Dire Wolf, a Dungeon World utility bot created by Marcus#3244\nJoin the official support and testing server [here](https://discord.gg/D6DenCC)\nInvite Dire Wolf to your server [here](https://discordapp.com/api/oauth2/authorize?client_id=425813218959556610&permissions=0&redirect_uri=https%3A%2F%2Finvite.direwolf.io%2F&scope=bot)", color=discord.Color(value=color))
        embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
        embed.add_field(name="Help", value="**help** - Shows this message\n""**help <command>** - Shows syntax and more info for specific commands", inline=False)
        embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
        embed.add_field(name="Lookup", value="**monster** - Looks up a monster\n**spell** - Looks up a spell\n**item** - Looks up an item\n**tag** - Looks up tags\n**playbook** - Looks up core playbooks\n**move** - Looks up Basic, Special, and Class moves from the core book.", inline=False)
        embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
        embed.add_field(name="Rolls", value="**roll** - Rolls dice with standard notation\n**moveroll** - Rolls 2d6+[args] and tells you the results of the move", inline=False)
        embed.add_field(name="\u200b", value="\n__"+" "*200+"__", inline=False)
        embed.add_field(name="More Help", value="In specific command help a | indicates there are two commands that will call that function (e.g. `roll|r` mean either 'roll' OR 'r' will work)\nDo not include <> around your args.", inline=False)
        await client.say(embed=embed)

@help.command(pass_context=True, name="monster", aliases="m")
async def monster(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";monster|m <name>", description="\nLooks up a Dungeon World monster.\nSearch with environment name for list of monsters found in that environment.\n\"Environment List\" for a list of available environments.", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True, name="spell", aliases="s")
async def spell(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";spell|s <name>", description="Looks up a Dungeon World spell.\nSearch \"Wizard\" or \"Cleric\" for class spell lists.", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True, name="item", aliases="i")
async def item(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";item|i <name>", description="Looks up a Dungeon World item.\nLists by category available by searching \"Weapons\", \"Armor\", etc.\nFull list of categories can be viewed by searching \"Item Categories\".", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True, name="tag", aliases="t")
async def tag(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";tag|t <name>", description="Looks up a Dungeon World item tag.\nSearch \"Item Tags\" or \"Monster Tags\" to view respective lists.", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True, name="playbook", aliases="p")
async def playbook(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";playbook|p <name>", description="Looks up a Dungeon World playbook from the core book (and Barbarian and Immolator).", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True)
async def move(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";move <name>", description="Looks up a Dungeon World Basic, Special, or Class move from the core book (and Barbarian and Immolator).", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True, name="roll", aliases="r")
async def roll(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";roll|r <xdy+z>", description="Rolls dice using standard dice notation, i.e., 2d6 or 2d6+1.\nBonuses to rolls can be whole numbers or extra dice, but note that whole numbers must be last.\n\nUsage:\n    ;r 2d6 (basic roll)\n    ;r 2d6+1 (with flat bonus)\n    ;r 2d6+1d8 (with bonus dice)\n    ;r 2d6+1d8+1d4+3 (with bonus dice and flat bonus)\n    ;r b2d12 (`b` rolls all dice and chooses the highest one)\n    ;r w2d4 (`w` rolls all dice and choose the lowest one)", color=discord.Color(value=color))
    await client.say(embed=embed)

@help.command(pass_context=True, name="moveroll", aliases=['mr'])
async def moveroll(ctx):
    color = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
    color = int(color, 16)
    embed=discord.Embed(title=";moveroll|mr <name>", description="Rolls 2d6 and prints the results of the move based on the die roll.\nBonuses can be added to rolls by adding the number after the move name\n\nUsage:\n    ;moveroll discern (roll Discern Realities)\n    ;mr discern 2 (adds a +2 bonus to the roll)", color=discord.Color(value=color))
    await client.say(embed=embed)

client.run('NTgzOTMyMTUyMzkyMDU2ODQz.XPPDPg.TG05ULBmUsC8Bd-3XANKSxP_W5w')
