import discord
import requests
import json
import asyncio
import os
from discord.ext import commands
from io import StringIO
from urllib.request import urlopen
from twitch import TwitchClient

class Emojis:
    def __init__(self, bot):
        self.bot = bot
        self.messages = []
        self.client = TwitchClient(
            client_id= os.environ['twitch_key']
            )
        
        self.bot.loop.create_task(self.turn_off_buttons())
    
    @commands.command(pass_context=True, name='emojis', aliases=['e', 'emoji'])
    async def _emojis(self, ctx, name, mode='chat'):

        try:
            users = self.client.users.translate_usernames_to_ids([name])
            user = users[0]
        except:
            await self.bot.send_message(ctx.message.channel, 'Can\'t find user. Use ``t?search (query)`` to find streams, users and more!')
            return

        id = user['id']
        link = f'https://api.twitchemotes.com/api/v4/channels/{id}'
        response = requests.get(link)
        info = json.loads(response.text)
        
        if info == {"error":"Channel not found"}:
            await self.bot.send_message(ctx.message.channel, 'Channel not found')
        
    
        #Generate dict {'EMOJI NAME': EMOJI_IMAGE_LINK, ...}
        mode = mode.lower()
        if mode == 'chat':
            emojis = {}
            for item in info['emotes']:
                emojis[item['code']] = f'https://static-cdn.jtvnw.net/emoticons/v1/{item["id"]}/4.0'
        
        elif mode == 'sub':
            emojis = await self.get_emojis_links(info['channel_name'], info['subscriber_badges'])
            if emojis == None:
                await self.bot.send_message(ctx.message.channel, 'Subscriber emotes not found')
                return

        elif mode == 'bits':
            emojis = await self.get_emojis_links(info['channel_name'], info['bits_badges'])
            if emojis == None:
                await self.bot.send_message(ctx.message.channel, 'Cheer emotes not found')
                return
        else:
            await self.bot.send_message(ctx.message.channel, 'Unknown mode')
        
        #if emotes more then 50
        while len(emojis) > 50:   
            title = 'Error'
            description = f'''
            Too many emojis, write what you want to add like 6-11, 19, 20, 22-50
            *6-11 is 6, 7, 8, 9, 10, 11 (emojis)*
            '''
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            await self.bot.send_message(ctx.message.channel, embed=embed)

            answer = await self.bot.wait_for_message(author=ctx.message.author)
            text = answer.content.replace(' ', '')
            emojis_splited = []
            for item in text.split(','):
                if '-' in item:
                    first_num = int(item[:item.find('-')]) 
                    end_num = int(item[item.find('-')+1:])
                    for num in range(first_num, end_num+1):
                        #num-1 to change 0-49 > 1-50
                        emojis_splited.append(num-1)
                else:
                     #int(item)-1-1 to change 0,1,2 > 1,2,3
                    emojis_splited.append(int(item)-1)
            
            n=0
            emojis_copy = emojis.copy()
            for key in emojis_copy.keys():
                if n not in emojis_splited:
                    del emojis[key]
                n+=1

        title = 'Warning'
        description = f'Do you really want to add ``{len(emojis)}`` **{user["display_name"]}\'s** emojis to this server?'
        embed = discord.Embed(title=title, description=description, color=0x6441A4)
        
        message = await self.bot.send_message(ctx.message.channel, embed=embed)
        for emoji in ['❌', '✅']:
            await self.bot.add_reaction(message, emoji)
        answer = await self.bot.wait_for_reaction(['❌', '✅'], message=message, user=ctx.message.author)

        #Get emoji answers
        if answer.reaction.emoji == '❌':
            embed = discord.Embed(title=title, description='Canceled.', color=0x6441A4)
            await self.bot.edit_message(message, embed=embed)
            for emoji in ['❌', '✅']:
                await self.bot.remove_reaction(message, emoji, self.bot.user)
        
        elif answer.reaction.emoji == '✅':
            #Send loading message & remove reaction
            description='''
            Loading...
            *(if loading is infinte - wait ~30min, discord api can't load emoji after removing them)*'''
            embed = discord.Embed(title=title, description=description, color=0x6441A4)
            await self.bot.edit_message(message, embed=embed)
            for emoji in ['❌', '✅']:
                await self.bot.remove_reaction(message, emoji, self.bot.user)
            
            #Add emojis to server 
            n=0
            emojis_to_add = emojis.copy()
            for key in emojis_to_add.keys():
                try:
                    image = urlopen(emojis[key]).read()
                    await self.bot.create_custom_emoji(server=ctx.message.server, name=key, image=image)
                except Exception as e:
                    args = e.args
                    if args[0] == 'BAD REQUEST (status code: 400): Maximum number of emojis reached (50)':
                        description = 'Maximum number of emojis reached'
                        embed = discord.Embed(title=title, description=description, color=0x6441A4)
                        await self.bot.edit_message(message, embed=embed)
                        return
                    else:
                        del emojis[key]
                        await self.bot.send_message(ctx.message.channel, 'Сant load emoji')
                    
                #show percent
                n+=1
                percent = int(n / len(emojis) * 100)
                description = f'Loading... | ``{percent}% / 100%``'
                embed = discord.Embed(title=title, description=description, color=0x6441A4)
                await self.bot.edit_message(message, embed=embed)
            
            #Swap links to emojis
            for key in emojis.keys():
                for emoji in ctx.message.server.emojis:
                    if key == emoji.name:
                        emojis[key] = str(emoji)


            #Send done message
            embed = discord.Embed(title=title, description='Added!', color=0x6441A4)
            await self.bot.edit_message(message, embed=embed)

            #Create & send emojis list
            max_page = len(emojis) // 5
            if len(emojis) % 5 != 0:
                max_page = len(emojis) // 5 + 1
            embed, buttons = await self.generate_emoji_list(emojis, 1, max_page)
            message = await self.bot.send_message(ctx.message.channel, embed=embed)
            if buttons:
                for emoji in ['⬅','➡']:
                    await self.bot.add_reaction(message, emoji)

            self.messages.append({
                'message': message,
                'info': emojis,
                'page': 1,
                'max_page': max_page,
                'emojis': ['⬅','➡']
            })
    
        
    async def generate_emoji_list(self, emojis, page, max_page):
        description = ''
        if len(emojis) <= 5:
            buttons = False
            title = f'Emojis | ``{len(emojis)}``'
            for key in emojis.keys():
                description+= f'{key} | {emojis[key]}\n'
        else:
            buttons = True
            title = f'Emojis | {page}/{max_page}'
            emojis_keys = list(emojis.keys())
            for key in emojis_keys[(page-1)*5:page*5]:
                description+= f'{key} | {emojis[key]}\n'
        
        embed = discord.Embed(title=title, description=description, color=0x6441A4)
        return embed, buttons

    async def get_emojis_links(self, name, badges):
        emojis = {}
        if badges != None:
            for key in badges.keys():
                title = badges[key]['title'].lower().replace(' ', '_').replace('-','_').replace('.','_')
                emoji_name = f'{name}_{title}'
                emojis[emoji_name] = badges[key]['image_url_4x']
        else:
            return None
        return emojis
        
    async def on_reaction_add(self, reaction, user):
        for message_info in self.messages:
            if reaction.message.timestamp == message_info['message'].timestamp:
                if user != self.bot.user:
                    await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                    if reaction.emoji in message_info['emojis']:
                        if reaction.emoji == '➡':
                            message_info['page'] += 1
                            if message_info['page'] > message_info['max_page']:
                                message_info['page'] = 1
                            
                            embed, buttons = await self.generate_emoji_list(message_info['info'], message_info['page'], message_info['max_page'])
                            await self.bot.edit_message(message_info['message'], embed=embed)
                        if reaction.emoji == '⬅':
                            message_info['page'] -= 1
                            if message_info['page'] < 1:
                                message_info['page'] = message_info['max_page']
                            
                            embed, buttons = await self.generate_emoji_list(message_info['info'], message_info['page'], message_info['max_page'])
                            await self.bot.edit_message(message_info['message'], embed=embed)

    async def turn_off_buttons(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            if len(self.messages) > 10:
                self.messages = [self.messages.pop()]
                await self.bot.send_message(
                    self.messages[0]['message'].channel,
                    'Old emoji-buttons no longer work' 
                )
            await asyncio.sleep(60)

def setup(bot):
    bot.add_cog(Emojis(bot))
