# +===================================================================================================================+
# ==   CHAUNCEY - A Discord Bot for ArlyDarkfire#4827 (twitch.tv/arlydarkfire)                                       ==
# ==   Created on April 2, 2021 by ShiinaBat                                                                         ==
# +===================================================================================================================+
#
#   bot.py is the heart of Chauncey and contains basic commands and configuration.
#
#   Copyright 2021 ShiinaBat <shiinabat.code@gmail.com>
#
#   Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby
#   granted, provided that the above copyright notice and this permission notice appear in all copies.
#
#   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING
#   ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
#   DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
#   PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
#   WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import discord
import asyncio

from discord.ext import commands
from utils.database import Postgres


def get_prefix(bot, message):
    """a customizable (per guild) prefix for our bot"""

    # set default prefix
    default_prefix = ';'

    # check if we're in a guild, if so, check if they have a custom prefix
    if message.guild:
        try:
            with Postgres() as db:
                prefix = db.query('SELECT prefix FROM prefixes WHERE guild_id = %s', (message.guild.id,))

                if prefix:
                    # return custom prefix
                    return commands.when_mentioned_or(str(*prefix[0]))(bot, message)
        # if the database can't be reached then default to the default prefix instead of outright breaking
        except TypeError:
            pass

    # otherwise return the default prefix
    return commands.when_mentioned_or(*default_prefix)(bot, message)


# declare which cogs to load on start up
initial_cogs = ['cogs.owner']

# declare our intents
intents = discord.Intents.default()
intents.members = True

# create our client and set our prefix, intents, and description
bot = commands.Bot(command_prefix=get_prefix, intents=intents, description='A bespoke bot for the KingOfArchers Discord server.')

# load our starting cogs (as per initial_cogs above)
if __name__ == '__main__':
    for extension in initial_cogs:
        bot.load_extension(extension)


@bot.command(name='ping')
async def ping(ctx):
    """returns Chauncey's latency in seconds"""

    # return ping
    await ctx.send(f':ping_pong:   **|**⠀Pong!⠀{round(bot.latency, 3)} seconds')


@bot.group(name='prefix', no_pm=True, pass_context=True)
async def prefix(ctx):
    """returns Chauncey's prefix for this guild"""

    # check that we're not in a subcommand
    if ctx.invoked_subcommand is None:
        # return prefix
        await ctx.send(f':information_source:   **|**⠀My prefix is:⠀`{get_prefix(bot, ctx.message)[2]}`')


@prefix.command(name='change', no_pm=True, hidden=True, pass_context=True, aliases=['set'])
@commands.has_guild_permissions(administrator=True)
async def change(ctx, new_prefix):
    """changes Chauncey's prefix for this guild"""

    # check to see if the new prefix is too long
    if len(new_prefix) > 3:
        await ctx.send("<:wrong:827283992654905407>   **|**⠀Oops! The new prefix is too long. (3 characters maximum)")
        return
    try:
        with Postgres() as db:
            # check if there's already an entry for this guild
            entry_exists = db.query('SELECT prefix FROM prefixes WHERE guild_id = %s', (ctx.guild.id,))

            # if there is, then update the entry
            if entry_exists:
                db.execute('UPDATE prefixes SET prefix=%s WHERE guild_id = %s', (new_prefix, ctx.guild.id))
            # else create a new entry for this guild
            else:
                db.execute('INSERT INTO prefixes VALUES (%s, %s)', (ctx.guild.id, new_prefix))

            # check to see if we successfully wrote to the database by checking if a row was modified
            if db.cursor.rowcount == 1:
                await ctx.send(f':white_check_mark:   **|**⠀Done! My prefix is now: `{new_prefix}`')
    # error handling for if the database couldn't be connected to
    except TypeError:
        await ctx.send("<:wrong:827283992654905407>   **|**⠀Oops! I couldn't connect to the database.")
    # error handling for any other database error
    except Exception as error:
        await ctx.send(f"<:wrong:827283992654905407>   **|**⠀Oops! An error has occurred: ```{error}```")


@bot.command(name='server')
async def server(ctx):
    await ctx.send("This command isn't ready yet!")


@bot.command(name='credits')
async def credits(ctx):
    await ctx.send("This command isn't ready yet!")


@bot.event
async def on_error(ctx, error):
    try:
        await ctx.message.delete()
    except discord.errors.NotFound:
        pass
    new_embed = discord.Embed(title=f'**[Error]** : {type(error).__name__}',
                              description=f'{error}')
    new_embed.set_footer(text=f'Use: [ {ctx.prefix}help ] for assistance')
    error = await ctx.send(embed=new_embed)
    await asyncio.sleep(5)
    await error.delete()


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    print(f'Successfully logged in and booted...!')


bot.run(os.environ.get("TOKEN"), bot=True, reconnect=True)
