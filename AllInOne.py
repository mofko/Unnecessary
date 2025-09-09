# meta developer: @mofkomodules
# name: AllInOne

__version__ = (1, 0, 0)

from telethon import types
from .. import loader, utils

@loader.tds
class AllInOne(loader.Module):
    """Интерактивный модуль для чатов!"""
    strings = {"name": "AllInOne"}

    async def sborcmd(self, message):
        """<текст> - Общий сбор."""
        args = utils.get_args_raw(message)
        chat = await message.get_chat()

        if not isinstance(chat, (types.Chat, types.Channel)):
            await message.edit("<b>Команда доступна только в чатах</b>")
            return

        await message.edit("<b>Оповещаю каждого...</b>")
        participants = await message.client.get_participants(chat)

        mentions = []
        for user in participants:
            if user.bot:
                continue
            mentions.append(f"<a href='tg://user?id={user.id}'>{user.first_name}</a>")

        if not mentions:
            await message.edit("<b>Некого собирать.</b>")
            return

        await message.respond(text, parse_mode="HTML")
        await message.delete()
