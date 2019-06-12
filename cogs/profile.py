import discord
import asyncio
import requests
import sys
from os import path, environ
from discord.ext import commands
from twitch import TwitchClient

#set default folder
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from tools.tools import csplit

class Profile:
    def __init__(self, bot):
        self.bot = bot
        self.sended_messages = []
        self.update_messages = []
        self.follows = []
        self.client = TwitchClient(
            client_id= environ['twitch_key']
            )
        
        #create background tasks
        self.bot.loop.create_task(self.stream_notification())
        self.bot.loop.create_task(self.recreate_message())
        self.bot.loop.create_task(self.turn_off_buttons())

    @commands.command(pass_context=True, name='profile', aliases=['profiles','p'])
    async def _profile(self, ctx, *names):
        #get all users
        users = self.client.users.translate_usernames_to_ids(list(names))
        
        for user in users:
            if user == []:
                await self.bot.send_message(
                    ctx.message.channel, 
                    'Can\'t find user. Use ``t?search (query)`` to find streams, users and more!'
                )
                continue

            #get info about user
            info = self.client.search.channels(user['name'])[0]

            #add bio to info
            info['bio'] = user['bio']

            #change followers & views to readable values
            info['views'], info['followers'] = csplit(info['views'], info['followers'])

            #send message
            message = await self.bot.send_message(
                ctx.message.channel,
                embed=await self.create_profile(info)
            )
            
            #add buttons
            for emoji in ['❤', '📺','🔄']:
                await self.bot.add_reaction(message, emoji)
            
            #append message info in list. 
            #I do this to use in on_reaction_add
            #for use emoji-buttons in all messages
            self.sended_messages.append({
                'message': message,
                'info': info,
                'type': 'profile',
                'emojis': ['❤', '📺','🔄']
            }) 

    @commands.command(pass_context=True, name='stream', aliases=['streams', 'st'])
    async def _stream(self, ctx, *names):
        #get all users
        users = self.client.users.translate_usernames_to_ids(list(names))

        for user in users:
            if user == []:
                await self.bot.send_message(
                ctx.message.channel, 
                'Can\'t find user. Use ``t?search (query)`` to find streams, users and more!'
            )
            continue

            #get info about stream
            info = self.client.streams.get_stream_by_user(user['id'])

            if info == None:
                await self.bot.send_message(
                    ctx.message.channel, 
                    'User don\'t streams'
                )
                continue

            #change viewers to readable values
            info['viewers'] = csplit(info['viewers'])

            #send message
            message = await self.bot.send_message(
                ctx.message.channel,
                embed=await self.create_stream(info)
            )

            #add reaction
            await self.bot.add_reaction(message, '🔄')
            
            #append message info in list. 
            #I do this to use in on_reaction_add
            #for use emoji-buttons in all messages
            self.sended_messages.append({
                'message': message,
                'type': 'stream',
                'info': info,
                'emojis': ['🔄']
            })

    
    @commands.command(pass_context=True, name='clips', aliases=['clip','cl'])
    async def _clip(self, ctx, *names, period='week', limit=25):
        for name in names:
            #get clips
            clips = self.client.clips.get_top(
                channel=name, 
                limit=limit % 100, 
                period=period
            )
        
            if clips == []:
                await self.bot.send_message(
                    ctx.message.channel, 
                    'No clips D:'
                )
                continue
            
            #create count of all pages
            pages = len(clips) // 5 if len(clips) % 5 == 0 else len(clips) // 5 + 1

            #change views to readable values
            for clip in clips: clip['views'] = csplit(clip['views'])

            #send message
            message = await self.bot.send_message(
                ctx.message.channel,
                embed=await self.create_clips(clips, 1, pages)
            )

            #add emojis
            emojis = ['🔄'] if pages <= 1 else ['⬅','➡', '🔄']
            for emoji in emojis:
                await self.bot.add_reaction(message, emoji)
            
            #append message info in list. 
            #I do this to use in on_reaction_add
            #for use emoji-buttons in all messages
            self.sended_messages.append({
                'message': message,
                'type': 'clip',
                'info': clips,
                'emojis': emojis,
                'page': 1,
                'pages': pages,
                'limit': limit
            })

    async def create_profile(self, info):
        #get stream state
        stream = False if self.client.streams.get_stream_by_user(info['id']) == None else True

        #Title
        title = info['display_name']
        #if user streams
        if stream:
            title += ' ``Live now!``'
        #if user has a follows
        if info['id'] in [follow['id'] for follow in self.follows]:
            title += ' ``followed``'''
        
        #Description
        description = f"""
            {
            f'''**{info['game']} | {info['status']}**
            **{info['url']}**''' 
            if stream else ''
            }
            
            {info['bio']}

            Followers: ``{info['followers']}``
            Views: ``{info['views']}``
            *Name: {info['name']}*
            *Id: {info['id']}*
            *Created at: {info['created_at']}*

            ``To un/follow press on the ❤``
            {
            f'''``Use ``**``t?stream {info['name']}``**`` to open info about stream!``''' 
            if stream else ''
            }
            """

        #Embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x6441A4
        )
        embed.set_thumbnail(url = info['logo'])

        return embed
        
    async def create_stream(self, info):
        title = f"{info['channel']['name']} is now *streaming*!"

        description = f"""
        **{info['channel']['status']}**
        **{info['channel']['url']}**
        
        Game: {info['game']}
        Viewers: ``{info['viewers']}``
        """

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x6441A4
        )
        embed.set_thumbnail(
            url = info['channel']['video_banner']
            if info['channel']['video_banner'] != None
            else info['channel']['logo']
        )

        return embed
    
    async def create_clips(self, clips, page, pages):
        #Title
        title = f'Clips | ``{page}/{pages}``'
        
        #Description
        description = ''
        for clip in clips[(page-1)*5 : page*5]:
            description += f"""
            **{clip['title']}**
            **{clip['url']}**
            Views : ``{clip['views']}``
            *by {clip['curator']['display_name']}*
            """
        
        #Emned
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x6441A4
        )

        embed.set_thumbnail(
            url = clips[0]['thumbnails']['medium']
            if len(clips) == 1
            else clips[0]['broadcaster']['logo']
        )

        return embed

    async def on_reaction_add(self, reaction, user):
        for info in self.sended_messages:
            if reaction.message.timestamp == info['message'].timestamp and user != self.bot.user:
                #remove added emoji on bot message
                await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                if reaction.emoji in info['emojis']:
                    #buttons code
                    if reaction.emoji == '❤':
                        #create info to follow
                        info_to_follow = ({
                            'id': info['info']['id'],
                            'channel': info['message'].channel,
                            'notification': True
                        })

                        #check if user has a follows
                        check = True if info['info']['id'] in [follow['id'] for follow in self.follows] else False

                        #append or remove follow on user
                        self.follows.append(info_to_follow) if not check else self.follows.remove(
                            *[follow for follow in self.follows if follow['id'] == info['info']['id']]
                            )

                        #recreate message with follow/unfollow type
                        await self.bot.edit_message(
                            info['message'], 
                            embed=await self.create_profile(info['info'])
                        )
                    
                    if reaction.emoji == '📺':
                        #get clips
                        clips = self.client.clips.get_top(
                            channel=info['info']['name'], 
                            limit=25
                        )
                        if clips == []:
                            await self.bot.send_message(
                                reaction.message.channel, 
                                'No clips D;'
                            )
                            return
                        
                        #create count of all pages
                        pages = len(clips) // 5 if len(clips) % 5 == 0 else len(clips) // 5 + 1

                        #change views to readable values
                        for clip in clips: clip['views'] = csplit(clip['views'])

                        #send message
                        message = await self.bot.send_message(
                            reaction.message.channel, 
                            embed= await self.create_clips(clips, 1, pages)
                        )
                        
                        #add emojis
                        emojis = ['🔄'] if pages <= 1 else ['⬅','➡', '🔄']
                        for emoji in emojis:
                            await self.bot.add_reaction(message, emoji)
                        
                        #append message info in list. 
                        #I do this to use in on_reaction_add
                        #for use emoji-buttons in all messages
                        self.sended_messages.append({
                            'message': message,
                            'type': 'clip',
                            'info': clips,
                            'emojis': emojis,
                            'page': 1,
                            'pages': pages,
                            'limit': 25
                        })
                    
                    if reaction.emoji in ['⬅', '➡']:
                        if reaction.emoji == '➡':
                            #turn page right
                            info['page'] += 1
                            if info['page'] > info['pages']:
                                info['page'] = 1
                        
                        if reaction.emoji == '⬅':
                            #turn page left
                            info['page'] -= 1
                            if info['page'] < 1:
                                info['page'] = info['pages']
                        
                        #edit message with new page
                        await self.bot.edit_message(
                            info['message'],
                            embed=await self.create_clips(info['info'], info['page'], info['pages'])
                        )
                    
                    if reaction.emoji == '🔄':
                        #add message in update list 
                        if info in self.update_messages:
                            self.update_messages.remove(info)
                        else:
                            self.update_messages.append(info)
                    
    
    async def recreate_message(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            #create copy to remove items from main list
            update_messages_copy = self.update_messages

            for update_message in update_messages_copy:
                if update_message['type'] == 'profile':
                    #get info about user
                    try:
                        user = self.client.users.get_by_id(update_message['info']['id'])
                    except:
                        await self.bot.send_message(
                            update_message['message'].channel, 
                            'No user D:'
                        )
                        continue
                    
                    #get info
                    info = self.client.search.channels(user['name'])[0]

                    #add bio to info
                    info['bio'] = user['bio']

                    #change followers & views to readable values
                    info['views'], info['followers'] = csplit(info['views'], info['followers'])
                    
                    #send message
                    await self.bot.edit_message(
                        update_message['message'],
                        embed = await self.create_profile(update_message['info'])
                    )

                    #update message info
                    update_message['info'] = info
                
                if update_message['type'] == 'stream':
                    #get info
                    try:
                        info = self.client.streams.get_stream_by_user(update_message['info']['channel']['id'])
                    except:
                        await self.bot.send_message(
                            update_message['message'].channel, 
                            'Can\'t find user/s. Use ``t?search (query)`` to find streams, users and more!'
                        )
                        continue
                    
                    if info == None:
                        await self.bot.send_message(
                            update_message['message'].channel, 
                            'No stream D:'
                        )
                        self.update_messages.remove(update_message)
                        continue
                    
                    await self.bot.edit_message(
                        update_message['message'], 
                        embed=await self.create_stream(info)
                    )

                    #update message info
                    update_message['info'] = info

                if update_message['type'] == 'clip':
                    #get clips
                    try:
                        clips = self.client.clips.get_top(
                            channel=update_message['info'][0]['broadcaster']['name'], 
                            limit=update_message['limit']
                        )
                    except:
                        await self.bot.send_message(
                            update_message['message'].channel, 
                            'Can\'t find user/s. Use ``t?search (query)`` to find streams, users and more!'
                        )
                        continue
                    
                    if clips == None:
                        await self.bot.send_message(
                            update_message['message'].channel, 
                            'No clips D:'
                        )
                        self.update_messages.remove(update_message)
                        continue
                    
                    #create count of all pages
                    pages = len(clips) // 5 if len(clips) % 5 == 0 else len(clips) // 5 + 1

                    #change views to readable values
                    for clip in clips: clip['views'] = csplit(clip['views'])
                    
                    await self.bot.edit_message(
                        update_message['message'], 
                        embed=await self.create_clips(
                            clips, 
                            update_message['page'], 
                            update_message['pages']
                        )
                    )

                    #update message info
                    update_message['info'] = clips

            #give new information to update_messages
            self.update_messages = update_messages_copy

            await asyncio.sleep(3)

    async def stream_notification(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            for follow in self.follows:
                #get info about stream
                info = self.client.streams.get_stream_by_user(follow['id'])

                if info != None:
                    #if notification don't sended
                    if follow['notification'] == False:
                        #change views to readable values
                        info['viewers'] = csplit(info['viewers'])

                        #send message
                        message = await self.bot.send_message(
                            follow['channel'],
                            embed= await self.create_stream(info)
                        )

                        #add reaction
                        await self.bot.add_reaction(message, '🔄')
                        
                        #append message info in list. 
                        #I do this to use in on_reaction_add
                        #for use emoji-buttons in all messages
                        self.sended_messages.append({
                            'info': info,
                            'type': 'stream',
                            'message': message,
                            'emojis': ['🔄']
                        })
                        
                        follow['notification'] = True
                else:
                    #when stream end change value of notification
                    follow['notification'] = False
            
            await asyncio.sleep(10)

    async def turn_off_buttons(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            if len(self.sended_messages) > 50:
                self.sended_messages = [self.sended_messages.pop()]
                await self.bot.send_message(
                    self.sended_messages[0]['message'].channel,
                    'Old emoji-buttons no longer work' 
                )
            await asyncio.sleep(60)
            

def setup(bot):
    bot.add_cog(Profile(bot))
