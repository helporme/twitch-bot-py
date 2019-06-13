#Developer šaH
#version 1.2 

import discord
import os
from discord.ext import commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('t?'))
bot.remove_command('help')

extetensions = ['profile','search','emojis','player','team']

for extenstion in extetensions:
    bot.load_extension(f'cogs.{extenstion}')

@bot.event
async def on_ready():
    await bot.change_presence(game= discord.Game(name='t?help or t?'))
    
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
async def _report(ctx, *, reason=None):
    if ctx.message.author.id != '255723371994546178':
        if reason == None:
            await bot.send_message(
                ctx.message.channel,
                'Error'
            )
            return
        
        file = open('reports', 'a')
        file.write(reason.replace('\n', ' ') + '\n')
        file.close()

        await bot.send_message(
            ctx.message.channel,
            'Thanks for reporting the error'
        )

    else:
        if reason == None:
            file = open('reports', 'r+')
            
            text = file.read().split('\n')
            try:
                for n in range(len(text) // 5 if len(text) % 5 == 0 else len(text) // 5 + 1):
                    await bot.send_message(
                        ctx.message.channel,
                        '\n'.join(text[5*n: 5*(n+1)])
                    )
            except:
                await bot.send_message(
                    ctx.message.channel,
                    'Empity message'
                )
        
        elif reason == 'clear':
            file = open('reports', 'w')
            file.write('')

            await bot.send_message(
                ctx.message.channel,
                'Cleared'
            )
        
bot.run(os.environ['token'])
