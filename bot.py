#Developer šaH 
#https://github.com/sah-py/

import discord
import requests
import os
import asyncio
import datetime
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('t?'))
bot.remove_command('help')

DEVS = ['255723371994546178']
extetensions = ['profile','search','emojis','player','team']
error_messages = []

for extenstion in extetensions:
    bot.load_extension(f'cogs.{extenstion}')

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='t?help or t?'))
    
@bot.command(pass_context=True, name='help', aliases=['h',''])
async def _help(ctx, command=None):
    if command == None:
        title= 'All commands'
        description= '''
                **t?profile** *<channel name>* | View user profile
                **t?stream** *<channel name>* | View info about stream
                **t?clips** *<channel name>* | View user clips
                **t?search** *<query>* | Search games, channels and streams
                **t?emojis**  *<channel name>* | Import emojis from twitch channel
                **t?player** *<channel name>* | Listen to stream
                **t?team** *<team name>* | View info about team
                
                Wrtie ``t?help <command>`` to get more information!

            '''
        
        #send message
        await bot.send_message(
            ctx.message.channel,
            embed=discord.Embed(
                title=title,
                description=description,
                color=0x6441A4
            )
        )

    else:
        command.lower()

        if command in 'profile':
            title = 'Profile'
            description = '''
            **t?profile *<channel name or names>***

            Examples:
            1. t?profile jesusaverfegn
            2. t?profile igmtv, ninja

            Aliases:
            t?p, t?profiles
            '''
            image = 'https://imgur.com/BjnE6a2.gif'
        
        elif command in 'stream':
            title = 'Stream'
            description = '''
            **t?stream *<channel name or names>***
            
            Examples:
            1. t?stream jesusavgn
            2. t?stream igmtv, ninja
            
            Aliases:
            t?st, t?streams
            '''
            image = 'https://imgur.com/EDGsy16.gif'
        
        elif command in 'clips':
            title = 'Clips'
            description = '''
            **t?clips *<channel name or names> <period (default is "week")> <limit (default is 25)>***

            Examples:
            1. t?clips jesusavgn
            2. t?clips igmtv week 50

            Aliases:
            t?cl, t?clip
            '''
            image = 'https://imgur.com/4EuKW8V.gif'
        
        elif command in 'search':
            title = 'Search'
            description = '''
            **t?search *<game, stream or channel>***

            Examples:
            1. t?search Fortnite
            2. t?search jesus
            3. t?search Playing in Dota 2 with followers

            Aliases:
            t?s
            '''
            image = 'https://imgur.com/luFPrUF.gif'
        
        elif command in 'emojis':
            title = 'Emojis'
            description = '''
            **t?emojis *<channel name> <mode (default is "chat")>***
            
            Modes:
            chat - import chat emoticons for subscribers
            bits - import bits emoticons
            sub - import sub emoticons that are in front of a nickname

            Examples:
            1. t?emojis jesusavgn
            2. t?emojis ninja sub
            3. t?emojis karmkikkoala bits

            Aliases:
            t?e, t?emoji
            '''
            image = ''
        
        elif command in 'player':
            title = 'Player'
            description = '''
            **t?player *<channel name or names>***
            
            You can add channels to the player, just write again t?player <...>

            Examples:
            1. t?player jesusavgn
            2. t?player mexaak, adam1tbc
            3. t?player mexaak *after this* t?player adam1tbc 
            '''
            image = 'https://imgur.com/x54FIUh.gif' 
        
        elif command in 'team':
            title = 'Team'
            description = '''
            **t?team *<team name>***

            Examples:
            t?team 89squad

            Aliases:
            t?t, t?teams
            '''
            image = 'https://i.imgur.com/dE0naJ5.gif'    
        
        else:
            await bot.send_message(
                ctx.message.channel,
                f'Error, unknown command "{command}"'
            )
            return
        
        #Embed
        embed = discord.Embed(
            title = title,
            description = description,
            color = 0x6441A4
        )
        embed.set_image(url=image)

        #Send message
        await bot.send_message(
            ctx.message.channel,
            embed=embed
        )

@bot.command(pass_context=True, name='report', aliases=['reports','rep','r'])
async def _report(ctx, *, reason=''):
    if ctx.message.author.id not in DEVS:
        if reason == None:
            await bot.send_message(
                ctx.message.channel,
                'Error, write t?report ``<reason>``'
            )
            return
        
        info = {
            'reason': reason,
            'author': ctx.message.author.name,
            'channel': ctx.message.channel.id,
            'server': ctx.message.server.id if ctx.message.server != None else 'None',
            'time': ctx.message.timestamp
        } 

        file = open('reports', 'r', encoding='utf8')

        reason_list = eval(file.read())
        reason_list.append(info)

        file.close()
        file = open('reports', 'w', encoding='utf8')
        file.write(str(reason_list))

        await bot.send_message(
            ctx.message.channel,
            embed = discord.Embed(
                title = 'Thanks!',
                description = 'Thanks for reporting the error',
                color = 0x6441A4
            )
        )

    else:
        if reason == '':
            file = open('reports', 'r', encoding='utf8')
            
            reasons = eval(file.read())
            if reasons == []:
                await bot.send_message(
                    ctx.message.channel,
                    'No errors'
                )
                return
            
            for reason in reasons:
                message = await bot.send_message(
                    ctx.message.channel,
                    embed = discord.Embed(
                        title = f"{reason['author']}",
                        description = reason['reason'],
                        color = 0x6441A4
                    )
                )
                
                for emoji in ['❌', 'ℹ', '✅']:
                    await bot.add_reaction(message, emoji)

                global error_messages
                error_messages.append({
                    'message': message,
                    'info': reason
                })
        
        elif reason == 'clear':

            file = open('reports', 'w', encoding='utf8')
            file.write('[]')
            file.close()

            error_messages = []

            await bot.send_message(
                ctx.message.channel,
                'Cleared'
            )

@bot.command(pass_context=True, name='changegame', aliases=['chg'])
async def _changegame(ctx, *, game):
    if ctx.message.author.id in DEVS:
        await bot.change_presence(game=discord.Game(name=game))
        await bot.send_message(
            ctx.message.channel,
            f'Game changed to {game}'
        )
    else:
        await bot.send_message(
            ctx.message.channel,
            'No access'
        )

@bot.command(pass_context=True, name='shutdown', aliases=['sd'])
async def _shutdown(ctx, mode):
    if ctx.message.author.id in DEVS:
        if mode in 'stop':
            await bot.send_message(
                ctx.message.channel,
                'Shutting down'
            )
            await bot.logout()
        
        if mode in 'restart':
            await bot.send_message(
                ctx.message.channel,
                'Restart'
            ) 
            bot.run(os.environ['token'])
    
    else:
        await bot.send_message(
            ctx.message.channel,
            'No access'
        )

@bot.command(pass_context=True, name='cogs', aliases=['cg'])
async def _cogs(ctx, mode, *, path):
    if ctx.message.author.id in DEVS:
        if mode in 'load':
            try:
                bot.load_extension(path)
                await bot.send_message(
                    ctx.message.channel,
                    f'{path} loaded'
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )
        
        if mode in 'unload':
            try:
                bot.unload_extension(path)
                await bot.send_message(
                    ctx.message.channel,
                    f'{path} unloaded'
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )
        
        if mode in 'reload':
            try:
                bot.unload_extension(path)
                bot.load_extension(path)

                await bot.send_message(
                    ctx.message.channel,
                    f'{path} reloaded'
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )
            
    else:
        await bot.send_message(
            ctx.message.channel,
            'No access'
        )

@bot.command(pass_context=True, name='file', aliases=['fl'])
async def _file(ctx, mode, *, value):
    if ctx.message.author.id in DEVS:
        if mode in 'read':
            file = open(value, 'r', encoding='utf8')
            text = file.read()

            await bot.send_message(
                ctx.message.channel,
                text
            )

            file.close()
        if mode in 'get':
            try:
                await bot.send_file(
                    ctx.message.channel,
                    value
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )   

        if mode in 'remove':
            try:
                os.rename(value, os.path.join(os.path.dirname(__file__), 'removed', value))
                await bot.send_message(
                    ctx.message.channel,
                    f'{value} removed'
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )   
        
        if mode in 'return':
            try:
                os.rename(
                    os.path.join(os.path.dirname(__file__), 'removed', value),
                    os.path.join(os.path.dirname(__file__), value)
                )
                await bot.send_message(
                    ctx.message.channel,
                    f'{value} returned'
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )   

        if mode in 'add':
            try:
                r = requests.get(ctx.message.attachments[0]['url'])

                file = open(value, 'wb', encoding='utf8')
                file.write(r.content)
                file.close()

                await bot.send_message(
                    ctx.message.channel,
                    'Successful'
                )
        
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Something go wrong'
                )
        
        if mode in 'mkdir':
            try:
                os.mkdir(value)
                await bot.send_message(
                    ctx.message.channel,
                    f'{value} created.'
                )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Error'
                )

    else:
        await bot.send_message(
            ctx.message.channel,
            'No access'
        )

@bot.event
async def on_reaction_add(reaction, user):
    for info in error_messages.copy():
        if reaction.message.timestamp == info['message'].timestamp and user != bot.user:
            try:
                await bot.remove_reaction(reaction.message, reaction.emoji, user)
            except:
                pass
            
            if reaction.emoji == '❌':
                file = open('reports', 'r', encoding='utf8')
                reports = eval(file.read())
                file.close()

                file = open('reports', 'w', encoding='utf8')
                reports.pop(reports.index(info['info']))
                file.write(str(reports))
                file.close()

                error_messages.remove(info)
                await bot.delete_message(info['message'])
            
            if reaction.emoji == 'ℹ':
                await bot.send_message(
                    reaction.message.channel,
                    embed = discord.Embed(
                        title = 'Info',
                        description = '\n'.join([f"**{key}**: {info['info'][key]}" for key in info['info'].keys() if key != 'reason']),
                        color = 0x6441A4
                    )
                )
            
            if reaction.emoji == '✅':
                await bot.send_message(
                    reaction.message.channel,
                    f"Replying to {info['info']['author']}"
                )
                text = await bot.wait_for_message()

                await bot.send_message(
                    discord.Object(id=info['info']['channel']),
                    text.content
                )

                await bot.send_message(
                    reaction.message.channel,
                    'Sended'
                )

bot.run(os.environ['token'])
