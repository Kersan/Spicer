import logging
from typing import Literal, Optional

from discord import HTTPException, Object
from discord.ext import commands
from discord.ext.commands import Context, Greedy


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lang = self.bot.config.lang("en")

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
                self.lang["admin.reload.success.multiple"].format(len(cogs))
                if len(cogs) > 1
                else self.lang["admin.reload.success.single"].format(cogs[0])
            )

        msg = None
        try:
            msg = await reloads(
                cog.split(",")
                if cog
                else [cog[:-3].lower() for cog in self.bot.cogs if "cog" in cog.lower()]
            )
        except Exception as e:
            logging.error(e)

        if not msg:
            return await ctx.message.add_reaction("❌")

        await ctx.message.add_reaction("✅")
        return await ctx.reply(msg)

    @admin.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: Context,
        guilds: Greedy[Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        if not guilds:
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

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
