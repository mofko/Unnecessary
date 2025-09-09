# meta developer: @mofkomodules 
# name: AllInOne 

__version__ = (1, 0, 4) 
 
from telethon import types 
from .. import loader, utils 
 
 
@loader.tds 
class AllInOne(loader.Module): 
    """Интерактивный модуль для чата!""" 
 
    strings = {"name": "AllInOne"} 
 
    async def sborcmd(self, message): 
        """<текст> - Общий сбор.""" 
        args = utils.get_args_raw(message) 
        chat = await message.get_chat() 
        if not isinstance(chat, (types.Chat, types.Channel)): 
            await message.edit("🚫 Это не чат!") 
            return 
 
        await message.edit("Оповещаю...") 
 
        participants = await message.client.get_participants(chat) 
         
        mentions = [ 
            f"{' '.join(filter(None, [user.first_name, user.last_name])) or user.username or str(user.id)}"
            for user in participants 
            if not user.bot 
        ] 
 
        if not mentions: 
            await message.edit("🚫 У вас тут пусто...") 
            return 
 
        text = args + "\\n\\n" if args else "" 
        text += " ".join(mentions) 
        await message.respond(text, parse_mode="HTML") 
        await message.delete()
