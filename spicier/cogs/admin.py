import logging

from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="admin", usage="[command]", aliases=["a"])
    @commands.is_owner()
    async def admin(self, ctx):
        pass

    @admin.command(name="reload", aliases=["r"])
    @commands.is_owner()
    async def reload_command(self, ctx, cog: str = None):
        """Reloads a cog or all cogs."""

        async def reloads(cogs: list):
            for cog in cogs:
                await self.bot.reload_extension(f"spicier.cogs.{cog}")
            return (
                f"Reloaded {len(cogs)} cogs!"
                if len(cogs) > 1
                else f"Reloaded {cogs[0]}"
            )

        msg = None
        try:
            msg = await reloads(
                cog.split(",") if cog else [cog[:-3].lower() for cog in self.bot.cogs]
            )
        except Exception as e:
            logging.error(e)

        if not msg:
            return await ctx.message.add_reaction("❌")

        await ctx.message.add_reaction("✅")
        return await ctx.reply(msg)

    @admin.command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx):
        """Syncs the command tree."""
        try:
            await self.bot.tree.sync()
            await ctx.message.add_reaction("✅")
        except Exception as e:
            logging.error(e)
            await ctx.message.add_reaction("❌")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
