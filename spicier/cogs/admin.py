import logging

from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="admin", usage="[command]")
    @commands.is_owner()
    async def admin(self, ctx):
        pass

    @admin.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        try:
            self.bot.reload_extension(f"spicier.cogs.{cog}")
            await ctx.send(f"Reloaded {cog}")
        except Exception as e:
            logging.error(e)

    @admin.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx):
        try:
            await self.bot.tree.sync()
            await ctx.message.add_reaction("✅")
        except Exception as e:
            logging.error(e)
            await ctx.message.add_reaction("❌")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
