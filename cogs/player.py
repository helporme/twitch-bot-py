import asyncio
import discord
import os
from discord.ext import commands
from twitch import TwitchClient

class Player:
    def __init__(self, bot):
        self.bot = bot
        self.current_player = {
            'play': False,
            'page': 0,
            'emojis': [],
            'message': None,
            'voice': None,
            'voice_channel_name': None
        }
        self.streams = []
        self.client = TwitchClient(
            client_id= os.environ['twitch_key']
            )
    
    @commands.command(pass_context=True, name='player', aliases=['pl'])
    async def _player(self, ctx, *users):
        users = self.client.users.translate_usernames_to_ids(list(users))

        for user in users:
            voice_channel = ctx.message.author.voice.voice_channel
            if voice_channel != None:
                stream = self.client.streams.get_stream_by_user(user['id'])
                if stream != None:
                    if not self.current_player['play']:
                        #Connect to a voice channel
                        voice = await self.bot.join_voice_channel(voice_channel)
                        
                        #Loading
                        title = f'``Player`` | *{stream["channel"]["status"]}*'
                        description = 'Loading...'
                        embed = discord.Embed(title=title, description=description, color=0x6441A4)
                        message = await self.bot.send_message(ctx.message.channel, embed=embed)

                        #Create player and start voice stream
                        player = await voice.create_ytdl_player(f'https://www.twitch.tv/{user["name"]}')
                        player.start()
                        
                        #Print connected
                        description = f'Connected to ``{voice_channel.name}``'
                        embed = discord.Embed(title=title, description=description, color=0x6441A4)
                        await self.bot.edit_message(message, embed=embed)
                        for emoji in ['❌', u'\u23F8']:
                            await self.bot.add_reaction(message, emoji)
                        
                        self.current_player['play'] = True
                        self.current_player['message'] = message
                        self.current_player['emojis'] = ['❌', u'\u23F8']
                        self.current_player['voice_channel_name'] = voice_channel
                        self.current_player['voice'] = voice

                        self.streams.append({
                            'stream': stream,
                            'player': player
                        })
                    else:
                        if self.current_player['emojis'] == ['❌', u'\u23F8']:
                            self.current_player['emojis'] = ['❌', u'\u23F8', '⬅','➡']
                            for emoji in ['⬅','➡']:
                                await self.bot.add_reaction(self.current_player['message'], emoji)
                        
                        #delete t?voice message
                        try:
                            await self.bot.delete_message(ctx.message)
                        except:
                            pass

                        #Stop old player
                        player = self.streams[self.current_player['page']]['player']
                        player.pause()

                        #Edit current page
                        self.current_player['page'] += 1

                        #Change to new page and start player
                        player = await self.stream_player(stream, 'create')

                        self.streams.append({
                            'stream': stream,
                            'player': player
                        })

                else:
                    await self.bot.send_message(ctx.message.channel, 'User offline')
            else:
                await self.bot.send_message(ctx.message.channel, 'You must be connected to a voice channel')
    
    async def stream_player(self, stream, state):
        message = self.current_player['message']

        #Loading
        title = f'``Player`` | *{stream["channel"]["status"]}*'
        description = 'Loading...'
        embed = discord.Embed(title=title, description=description, color=0x6441A4)
        await self.bot.edit_message(message, embed=embed)

        #Create player and start voice stream
        voice = self.current_player['voice']
        if state == 'create':
            player = await voice.create_ytdl_player(f'https://www.twitch.tv/{stream["channel"]["name"]}')
            player.start()

        #Change player and start voice stream
        elif state == 'swap':
            player = self.streams[self.current_player['page']]['player']
            player.resume()
        
        #Print connected
        description = f'Connected to ``{self.current_player["voice_channel_name"]}``'
        embed = discord.Embed(title=title, description=description, color=0x6441A4)
        await self.bot.edit_message(message, embed=embed)

        return player

    async def on_reaction_add(self, reaction, user):
        if self.current_player['message'] != None and reaction.message.timestamp == self.current_player['message'].timestamp:
            if user != self.bot.user:
                await self.bot.remove_reaction(reaction.message, reaction.emoji, user)
                if reaction.emoji in self.current_player['emojis']:
                    if reaction.emoji == '❌':
                        voice = self.current_player['voice']
                        await voice.disconnect()
                        await self.bot.delete_message(self.current_player['message'])
                        self.current_player = {
                            'play': False,
                            'page': 0,
                            'emojis': [],
                            'message': None,
                            'voice': None,
                            'voice_channel_name': None
                        }
                        self.streams = []
                    
                    if reaction.emoji == u'\u23F8':
                        player = self.streams[self.current_player['page']]['player']
                        if player.is_playing():
                            player.pause()
                        else:
                            player.resume()

                    if reaction.emoji == '➡':
                        #Stop old player
                        player = self.streams[self.current_player['page']]['player']
                        player.pause()
                        
                        self.current_player['page'] += 1
                        if self.current_player['page'] > len(self.streams)-1:
                            self.current_player['page'] = 0
                        
                        await self.stream_player(self.streams[self.current_player['page']]['stream'], 'swap')
                    
                    if reaction.emoji == '⬅':
                        #Stop old player
                        player = self.streams[self.current_player['page']]['player']
                        player.pause()

                        self.current_player['page'] -= 1
                        if self.current_player['page'] < 0:
                            self.current_player['page'] = len(self.streams)-1
                        
                        await self.stream_player(self.streams[self.current_player['page']]['stream'], 'swap')

def setup(bot):
    bot.add_cog(Player(bot))
