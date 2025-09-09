# meta developer: @mofkomodules
# name: AllInOne

__version__ = (1, 0, 5)

from telethon import types
from .. import loader, utils

@loader.tds
class AllInOne(loader.Module):
    """Интерактивный модуль для чатов!"""
    strings = {"name": "AllInOne"}

    async def sborcmd(self, message):
        """<текст> - Общий сбор!"""
        args = utils.get_args_raw(message)
        chat = await message.get_chat()

        if not isinstance(chat, (types.Chat, types.Channel)):
            await message.edit("<b>🚫 Это не чат!</b>")
            return

        await message.edit("<b>Оповещаю...</b>")
        participants = await message.client.get_participants(chat)
        
        mentions = []
        for user in participants:
            if not user.bot:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                display_name = full_name or user.username or str(user.id)
                mentions.append(f"<a href='tg://user?id={user.id}'>{display_name}</a>")

        if not mentions:
            await message.edit("<b>🚫 У вас тут пусто...</b>")
            return

        text = args + "\n\n" if args else ""
        text += " ".join(mentions)
        await message.respond(text, parse_mode="HTML")
        await message.delete()
