from discord.ext import commands

from spicier.manager import ServerManager

from .server import ServerManager


class ServerCog(commands.Cog):
    """Manage the server settings."""

    server_manager: ServerManager

    def __init__(self, bot: commands.Bot):
        self.server_manager = bot.server_manager
        self.config = bot.config
        self.bot = bot

    @commands.group(name="prefix", usage="[command]")
    @commands.has_guild_permissions(administrator=True)
    async def prefix_group(self, ctx):
        """
        Manage the prefix for the server.
        """
        if not ctx.invoked_subcommand:
            return await ctx.send_help(ctx.command)

    @prefix_group.command(name="set")
    @commands.has_guild_permissions(administrator=True)
    async def set_prefix_command(self, ctx, prefix: str):
        """
        Set the prefix for the server.
        """
        if len(prefix) > 10:
            return await ctx.reply("Prefixes can only be 10 characters long.")

        await self.server_manager.set_prefix(ctx.guild.id, prefix)
        return await ctx.reply(
            f"The prefix for this server has been set to `{prefix}`."
        )

    @prefix_group.command(name="reset", aliases=["clear"])
    @commands.has_guild_permissions(administrator=True)
    async def reset_prefix_command(self, ctx):
        """
        Reset the prefix for the server.
        """
        await self.server_manager.set_prefix(ctx.guild.id, self.config.prefix)

        return await ctx.reply(
            f"The prefix for this server has been reset to `{self.config.prefix}`."
        )

    @prefix_group.command(name="get", aliases=["show"])
    @commands.has_guild_permissions(administrator=True)
    async def get_prefix_command(self, ctx):
        """
        Get the prefix for the server.
        """
        prefix = await self.server_manager.get_prefix(ctx.guild.id)

        if not prefix:
            await self.server_manager.set_prefix(ctx.guild.id, self.config.prefix)
            prefix = self.config.prefix

        return await ctx.reply(f"The prefix for this server is `{prefix}`.")


async def setup(bot):
    await bot.add_cog(ServerCog(bot))
