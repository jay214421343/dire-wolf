import asyncio
import os

import aiohttp
from discord.ext import commands
from discord.ext.commands import CommandInvokeError

from funcs import *

DESCRIPTION = "A proof-of-concept bot to look up homebrew items from a internet source."
TOKEN = os.environ.get("TOKEN")
UPDATE_DELAY = 60 * 30  # update every 30 minutes

ITEM_SOURCE = "https://raw.githubusercontent.com/tabletoptools/Hawthorne-Docs/develop/hawthorne/homebrew.md"
ITEM_DIVIDER = "***"  # a string that divides distinct items.
IGNORED_ENTRIES = 1  # a number of entries to ignore (in case of an index, etc)
META_LINES = 2  # the number of lines of meta info each item has

items = []


@client.event
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
    async with aiohttp.ClientSession() as session:
        async with session.get(ITEM_SOURCE) as resp:
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update items: {text}")

            raw_items = [t.strip() for t in text.split(ITEM_DIVIDER)][IGNORED_ENTRIES:]  # filter out index

            for item in raw_items:
                lines = item.split('\n')
                name = lines[0].strip('# ')
                meta = '\n'.join(lines[1:1 + META_LINES])
                desc = '\n'.join(lines[2 + META_LINES:])

                for dup in [i for i in items if name.lower() == i['name'].lower()]:
                    items.remove(dup)  # remove duplicates
                items.append({'name': name, 'meta': meta, 'desc': desc})
                print(f"Indexed item {name}.")

            print("Updated items!")


@client.command(pass_context=True)
async def homebrew(ctx, *, name):
    """Looks up a homebrew item."""
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

    embed = EmbedWithAuthor(ctx)
    embed.title = result['name']
    embed.description = result['meta']
    desc = result['desc']
    desc = [desc[i:i + 1024] for i in range(0, len(desc), 1024)]
    embed.add_field(name="Description", value=desc[0])
    for piece in desc[1:]:
        embed.add_field(name="\u200b", value=piece)

    await client.say(embed=embed)
