#bad code, but I'm tired of writing this bot

import discord
import asyncio
from discord.ext import commands
from twitch import TwitchClient

class Search:
    def __init__(self, bot):
        self.bot = bot
        self.messages = []
        self.client = TwitchClient(
            client_id='k4hjxhg1n3pxgfvv9e4zx59u1zn3ab'
            )

        #create background tasks
        self.bot.loop.create_task(self.turn_off_buttons())

    @commands.command(pass_context=True, name='search', aliases=['s'])
    async def _search(self, ctx, *, query):
        status = {
            'games': True,
            'streams': True,
            'channels': True
        }

        try:
            games = self.client.search.games(query)
            embed, emojis, max_page, selected = await self.games_search_list(games, 1)
            message = await self.bot.send_message(ctx.message.channel, embed=embed)
            if emojis != []:
                for emoji in emojis:
                    await self.bot.add_reaction(message, emoji)
            self.messages.append({
                'message': message,
                'type': 'games',
                'content': games,
                'page': 1,
                'max_page': max_page,
                'selected': selected,
                'emojis': emojis
            })
        except:
            status['games'] = False
        
        try:
            streams = self.client.search.streams(query)
            embed, emojis, max_page, selected = await self.streams_search_list(streams, 1)
            message = await self.bot.send_message(ctx.message.channel, embed=embed)
            if emojis != []:
                for emoji in emojis:
                    await self.bot.add_reaction(message, emoji)
            self.messages.append({
                'message': message,
                'type': 'streams',
                'content': streams,
                'page': 1,
                'max_page': max_page,
                'selected': selected,
                'emojis': emojis
            })
        except:
            status['streams'] = False
        
        try:
            channels = self.client.search.channels(query)
            embed, emojis, max_page, selected = await self.channels_search_list(channels, 1)
            message = await self.bot.send_message(ctx.message.channel, embed=embed)
            if emojis != []:
                for emoji in emojis:
                    await self.bot.add_reaction(message, emoji)
            self.messages.append({
                'message': message,
                'type': 'channels',
                'content': channels,
                'page': 1,
                'max_page': max_page,
                'selected': selected,
                'emojis': emojis
            })
        except:
            status['channels'] = False

        if status['games'] == status['streams'] == status['channels'] == False:
            await self.bot.send_message(ctx.message.channel, 'Nothing D;')
        
    async def games_search_list(self, games, page, selected=1):
        if len(games) == 1:
            game = games[0]

            title = game['name']
            description = f'''
            Viewers: ``{game['popularity']}``
            '''
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            embed.set_thumbnail(url=game['box']['medium'])
            return embed, [], None, None

        elif len(games) > 1 and len(games) <= 5:
            title = 'Games'
            description = ''
            n=0
            for game in games: 
                n+=1
                s = ''
                if selected == n:
                    s = '``|`` '
                description += f'''
                {s}*{n}.*
                {s}Name: **{game['name']}**
                {s}Viewers: ``{game['popularity']}``
                '''
            
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            return embed, ['⬇', '⬆' ,'🔎'], None, selected

        elif len(games) > 5:
            max_page = len(games) // 5
            if len(games) % 5 != 0:
                max_page = (len(games) // 5) + 1
            title = f'Games | {page}/{max_page}'
            description = ''
            n=0
            for game in games[(page-1)*5:page*5]:
                n+=1
                s = ''
                if selected == n:
                    s = '``|`` '
                description += f'''
                {s}*{n}.*
                {s}Name: **{game['name']}**
                {s}Viewers: ``{game['popularity']}``
                '''
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            return embed, ['⬅', '➡', '⬇', '⬆' ,'🔎'], max_page, selected

    async def streams_search_list(self, streams, page, selected=1):
        if len(streams) == 1:
            stream = streams[0]

            title = stream['channel']['status']
            description = f'''
            **{stream['channel']['url']}**
            Name: {stream['channel']['display_name']}
            Game: {stream['game']}
            Viewers: ``{stream['viewers']}``

            ``To see more - ``**``t?stream {stream['channel']['name']}``**``!``
            '''
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            embed.set_thumbnail(url=stream['preview']['medium'])
            return embed, [], None, None

        elif len(streams) > 1 and len(streams) <= 5:
            title = 'Streams'
            description = ''
            n=0
            for stream in streams:
                n+=1
                s = ''
                if selected == n:
                    s = '``|`` '
                description+= f'''
                {s}*{n}.*
                {s}**{stream['channel']['url']}**
                {s}Stream: **{stream['channel']['status']}**
                {s}Name: {stream['channel']['display_name']}
                {s}Game: {stream['game']}
                {s}Viewers: ``{stream['viewers']}``
                '''

            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            return embed, ['⬇', '⬆' ,'🔎'], None, selected

        elif len(streams) > 5:
            max_page = len(streams) // 5
            if len(streams) % 5 != 0:
                max_page = (len(streams) // 5) + 1

            title = f'Streams | {page}/{max_page}'
            description= ''
            n=0
            for stream in streams[(page-1)*5:page*5]:
                n+=1
                s = ''
                if selected == n:
                    s = '``|`` '
                description+= f'''
                {s}*{n}.*
                {s}**{stream['channel']['url']}**
                {s}Stream: **{stream['channel']['status']}**
                {s}Name: {stream['channel']['display_name']}
                {s}Game: {stream['game']}
                {s}Viewers: ``{stream['viewers']}``
                '''
            
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            return embed, ['⬅', '➡', '⬇', '⬆' ,'🔎'], max_page, selected

    async def channels_search_list(self, channels, page, selected=1):
        if len(channels) == 1:
            channel = channels[0]

            title = channel['display_name']
            description = f'''
            Views: ``{channel['views']}``
            Followers: ``{channel['followers']}``

            ``To see more - ``**``t?profile {channel['name']}``**``!``
            ''' 

            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            embed.set_thumbnail(url=channel['logo'])

            return embed, [], None, None 
        
        elif len(channels) > 1 and len(channels) <= 5:
            title = 'Channels'
            description = ''
            n=0
            for channel in channels:
                n+=1
                s = ''
                if selected == n:
                    s = '``|`` '
                description+= f'''
                {s}*{n}*.
                {s}Name: **{channel['name']}**
                {s}Views: ``{channel['views']}``
                {s}Followers: ``{channel['followers']}``
                '''

            embed = discord.Embed(title=title, description=description, color=0x6441A4)

            return embed, ['⬇', '⬆' ,'🔎'], None, selected
        
        elif len(channels) > 5:
            max_page = len(channels) // 5
            if len(channels) % 5 != 0:
                max_page = (len(channels) // 5) + 1
            
            title = f'Channels | {page}/{max_page}'
            description= ''
            n=0
            for channel in channels[(page-1)*5:page*5]:
                n+=1
                s = ''
                if selected == n:
                    s = '``|`` '
                description+= f'''
                {s}*{n}.*
                {s}Name: **{channel['name']}**
                {s}Views: ``{channel['views']}``
                {s}Followers: ``{channel['followers']}``
                '''
            
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            return embed, ['⬅', '➡', '⬇', '⬆' ,'🔎'], max_page, selected
    
    async def on_reaction_add(self, reaction, user):
        for message_info in self.messages:
            if reaction.message.timestamp == message_info['message'].timestamp and user != self.bot.user:
                await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                if reaction.emoji in message_info['emojis']:
                    if reaction.emoji == '🔎':
                        if message_info['type'] == 'games':
                            info = await self.games_search_list(
                                [message_info['content'][message_info['selected']-1 + (message_info['page']-1) * 5]], 
                                1
                            )
                        if message_info['type'] == 'streams':
                            info = await self.streams_search_list(
                                [message_info['content'][message_info['selected']-1 + (message_info['page']-1) * 5]], 
                                1
                            )
                        if message_info['type'] == 'channels':
                            info = await self.channels_search_list(
                                [message_info['content'][message_info['selected']-1 + (message_info['page']-1) * 5]], 
                                1
                            )
                        
                        await self.bot.send_message(message_info['message'].channel, embed=info[0])
                    
                    async def get_default_embed(message):
                        if message_info['type'] == 'games':
                            info = await self.games_search_list(
                                message_info['content'], 
                                message_info['page'], 
                                message_info['selected']
                            )
                        if message_info['type'] == 'streams':
                            info = await self.streams_search_list(
                                message_info['content'], 
                                message_info['page'], 
                                message_info['selected']
                            )
                        if message_info['type'] == 'channels':
                            info = await self.channels_search_list(
                                message_info['content'], 
                                message_info['page'], 
                                message_info['selected']
                            )

                        return info[0]

                    if reaction.emoji == '⬇':
                        message_info['selected'] += 1
                        if message_info['selected'] > 5:
                            message_info['selected'] = 1
                        
                        await self.bot.edit_message(
                            message_info['message'], 
                            embed=await get_default_embed(message_info)
                            )
                        
                    if reaction.emoji == '⬆':
                        message_info['selected'] -= 1
                        if message_info['selected'] < 1:
                            message_info['selected'] = 5
                        
                        await self.bot.edit_message(
                            message_info['message'], 
                            embed=await get_default_embed(message_info)
                        )

                    if reaction.emoji == '➡':
                        message_info['page'] += 1
                        if message_info['page'] > message_info['max_page']:
                            message_info['page'] = 1

                        await self.bot.edit_message(
                            message_info['message'], 
                            embed=await get_default_embed(message_info)
                        )
                    
                    if reaction.emoji == '⬅':
                        message_info['page'] -= 1
                        if message_info['page'] < 1:
                            message_info['page'] = message_info['max_page']

                        await self.bot.edit_message(
                            message_info['message'], 
                            embed=await get_default_embed(message_info)
                        )

    async def turn_off_buttons(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            if len(self.messages) > 50:
                self.messages = [self.messages.pop()]
                await self.bot.send_message(
                    self.messages[0]['message'].channel,
                    'Old emoji-buttons no longer work' 
                )
            await asyncio.sleep(60)

def setup(bot):
    bot.add_cog(Search(bot))