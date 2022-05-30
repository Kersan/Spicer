from discord.ext import commands
from typing import Optional

# Usunięcie wiadomości
class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = bot.config

        self.on = ['włącz', 'on', 'odpal', 'wlacz', 'włacz', 'wlącz']
        self.off = ['wyłącz', 'off', 'wylacz', 'wyłacz', 'wylącz', 'spierdalaj']


    @commands.command(name="nick")
    @commands.has_permissions(administrator=True)
    async def change_nick(self, ctx, suffix: str = "Kot"):
        
        for member in ctx.guild.members:
            try:
                if member.bot:
                    continue

                await member.edit(nick=f"{member.name} {suffix}")

                print(member.name)
            except Exception as e:
                pass

    @commands.command(name="debug", hidden=True)
    @commands.has_permissions(administrator=True)
    async def debug(self, ctx, arg: Optional[str] = None):
        if arg is None:
            if 'jishaku' in self.bot.extensions:
                await ctx.reply("Tryb debug jest obecnie włączony! ✅")
            else:
                await ctx.reply("Tryb debug jest obecnie wyłączony! 🛑")

        if arg in self.on:
            try:
                await self.bot.load_extension('jishaku')
                await ctx.message.add_reaction('🔛')
            except Exception as e:
                print(e)
        
        if arg in self.off:
            try:
                await self.bot.unload_extension('jishaku')
                await ctx.message.add_reaction('📴')
            except Exception as e:
                print(e)
