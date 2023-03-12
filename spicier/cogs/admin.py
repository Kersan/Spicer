from typing import Literal, Optional

from discord import Object
from discord.ext import commands
from discord.ext.commands import Context, Greedy

from .service import AdminService


class AdminCog(commands.Cog, AdminService):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        super().__init__(bot, self.bot.config.lang("en"))

    @commands.group(name="admin", usage="[command]", aliases=["a"])
    @commands.is_owner()
    async def admin(self, ctx):
        pass

    @admin.command(name="reload", aliases=["r"])
    @commands.is_owner()
    async def reload_command(self, ctx, *cogs: str):
        """Reloads a cog or all cogs."""
        final_cogs = await self.handler.reload(self.bot, cogs)
        return await self.message_reload(ctx, final_cogs)

    @admin.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: Context,
        guilds: Greedy[Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        values = await self.handler.sync(ctx, guilds, spec)
        return await self.message_sync(ctx, values)

    @admin.command(name="cache")
    @commands.is_owner()
    async def cache_command(self, ctx):
        await ctx.reply(self.bot.cache._servers)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
