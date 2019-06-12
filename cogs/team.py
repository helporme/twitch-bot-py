import discord
import asyncio
import sys
from os import path
from discord.ext import commands
from twitch import TwitchClient

#set default folder
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from tools.tools import cleartext

class Team:
    def __init__(self, bot):
        self.bot = bot
        self.messages = []
        self.client = TwitchClient(
            client_id='k4hjxhg1n3pxgfvv9e4zx59u1zn3ab'
            )

        #create background task
        self.bot.loop.create_task(self.turn_off_buttons())

    @commands.command(pass_context=True, name='team', aliases=['teams','t'])
    async def _team(self, ctx, *names):
        for name in names:
            #get info
            try:
                team = self.client.teams.get(name)
            except:
                await self.bot.send_message(
                    ctx.message.channel,
                    'Unknown team'
                )
                return
            
            #clear html parts
            team['info'] = cleartext(team['info'])
            
            #Embed
            embed = discord.Embed(
                description = team['info'],
                url = team['logo'],
                color = 0x6441A4
            )
            embed.set_author(
                name = team['display_name'],
                url = f"https://www.twitch.tv/team/{team['name']}"#,
                #icon_url = team['logo']
            )
            embed.set_thumbnail(
                url = team['logo']
            )

            #Send messages
            for embed in [embed, await self.create_users(team['users'])]:
                message = await self.bot.send_message(
                    ctx.message.channel,
                    embed=embed
                )
            
            #add emojis
            for emoji in ['⬅','➡']:
                await self.bot.add_reaction(message, emoji)

            #add last message
            self.messages.append({
                'message': message,
                'emojis': ['⬅','➡'],
                'info': team,
                'page': 1
            })


    async def create_users(self, users, page=1):
        #Title
        max_page = len(users) // 10 if len(users) % 10 == 0 else len(users) // 10 + 1
        title = f'Users | {page} / {max_page}'

        #Description
        description = '\n'.join(
            [f"**{n+1}.** ``{users[n]['display_name']}`` | {users[n]['status']}"
            for n in range(len(users))[(page-1)*10 : page*10]]
        )
        
        #Embed
        embed = discord.Embed(
            title = title,
            description = description,
            color = 0x6441A4
        )
        
        return embed

    async def on_reaction_add(self, reaction, user):
        for info in self.messages:
            if reaction.message.timestamp == info['message'].timestamp and user != self.bot.user:
                #remove added emoji on bot message
                await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                if reaction.emoji in info['emojis']:
                    #buttons code
                    if reaction.emoji in ['⬅', '➡']:
                        users = info['info']['users']
                        max_page = len(users) // 10 if len(users) % 10 == 0 else len(users) // 10 + 1

                        if reaction.emoji == '➡':
                            info['page'] += 1
                            if info['page'] > max_page:
                                info['page'] = 1
                        
                        if reaction.emoji == '⬅':
                            info['page'] -= 1
                            if info['page'] <= 0:
                                info['page'] = max_page

                        await self.bot.edit_message(
                            info['message'], 
                            embed = await self.create_users(info['info']['users'], info['page'])
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
    bot.add_cog(Team(bot))
