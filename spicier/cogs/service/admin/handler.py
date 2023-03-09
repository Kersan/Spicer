from typing import Union

from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

from spicier.errors import WrongArgument


class AdminHandler:
    def __init__(self):
        pass

    async def reload(self, bot: commands.Bot, cogs: list[str]):
        if not cogs:
            cogs = [c[:-3].lower() for c in bot.cogs if "cog" in c.lower()]
            await self._reload_cogs(bot, cogs)
        else:
            await self._reload_cogs(bot, cogs)

        return cogs

    async def _reload_cogs(self, bot, cogs: list):
        try:
            for cog in cogs:
                await bot.reload_extension(f"spicier.cogs.{cog}")
        except ExtensionNotLoaded:
            raise WrongArgument("Cog with given name does not exist.")

    async def sync(self, ctx: commands.Context, guilds: list, spec: str) -> tuple:
        if guilds:
            return await self._handle_sync_guilds(ctx, guilds)
        return await self._handle_sync_spec(ctx, spec)

    async def _handle_sync_guilds(self, ctx, guilds: list) -> tuple:
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except HTTPException:
                pass
            else:
                ret += 1

        return (ret, len(guilds))

    async def _handle_sync_spec(self, ctx, spec: str) -> tuple:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        return (len(synced), spec)
