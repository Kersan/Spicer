from discord.ext import commands

from .handler import AdminHandler


class AdminService:
    def __init__(self, bot: commands.Bot, lang):
        self.bot = bot
        self.lang = lang
        self.handler = AdminHandler()

    async def message_reload(self, ctx: commands.Context, cogs: list):
        if not cogs:
            return await ctx.message.add_reaction("❌")
        await ctx.message.add_reaction("✅")

        if len(cogs) > 1:
            return self.lang["admin.reload.success.multiple"].format(len(cogs))
        return self.lang["admin.reload.success.single"].format(cogs[0])

    async def message_sync(self, ctx: commands.Context, values: tuple):
        if isinstance(values[1], int):
            return await ctx.send(f"Synced the tree to {values[0]}/{values[1]}.")

        return await ctx.send(
            f"Synced {values[0]} commands {'globally' if values[1] is None else 'to the current guild.'}"
        )
