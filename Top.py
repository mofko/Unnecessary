# meta developer: @mofkomodules 
# name: TopStat

__version__ = (1, 0, 0)

from telethon import events
from collections import defaultdict
from heroku.module_base import Module
from heroku.utils import register_cmd, register_message_handler

class TopStat(Module):
    """
    Стата чата.
    """
    def __init__(self):
        super().__init__()

    async def _get_chat_counts(self, chat_id):
        # DB structure: {'topstat_counts': {'chat_id_str': {'user_id_str': count}}}
        all_counts = await self.client.db.get('topstat_counts', {})
        return defaultdict(int, all_counts.get(str(chat_id), {}))

    async def _set_chat_counts(self, chat_id, chat_counts):
        all_counts = await self.client.db.get('topstat_counts', {})
        all_counts[str(chat_id)] = dict(chat_counts)
        await self.client.db.set('topstat_counts', all_counts)

    @register_message_handler(events.NewMessage(incoming=True, func=lambda e: e.is_group and e.message.text))
    async def _message_counter(self, event):
        sender = await event.get_sender()
        if not sender or sender.bot or sender.deleted:
            return

        chat_id = event.chat_id
        user_id = sender.id
        
        chat_counts = await self._get_chat_counts(chat_id)
        chat_counts[str(user_id)] += 1
        await self._set_chat_counts(chat_id, chat_counts)

    @register_cmd(pattern="^.top$", description="Показывает топ-10 пользователей по сообщениям в текущем чате.")
    async def msgtopcmd(self, event):
        if not event.is_group:
            await self.client.send_message(event.chat_id, "Эту команду можно использовать только в группах.", reply_to=event.id)
            return

        chat_id = event.chat_id
        chat_counts = await self._get_chat_counts(chat_id)
        
        if not chat_counts:
            await self.client.send_message(event.chat_id, "Пока нет статистики сообщений в этом чате. Начните общаться, чтобы собрать топ!", reply_to=event.id)
            return

        sorted_users = sorted(chat_counts.items(), key=lambda item: item[1], reverse=True)
        
        top_message = "📊 **Топ 10 по сообщениям в чате:**\n\n"
        
        for i, (user_id_str, count) in enumerate(sorted_users[:10]):
            try:
                user_id = int(user_id_str)
                user = await self.client.get_entity(user_id)
                
                display_name = user.first_name if user.first_name else ""
                if user.last_name:
                    display_name += f" {user.last_name}"
                if not display_name: 
                    display_name = user.username if user.username else str(user.id)
                
                user_link = f"[{display_name}](tg://user?id={user.id})"
                
                top_message += f"{i+1}. {user_link}: **{count}** сообщений\n"
            except Exception:
                top_message += f"{i+1}. Пользователь `{user_id_str}`: **{count}** сообщений (недоступен или удален)\n"
        await self.client.send_message(event.chat_id, top_message, reply_to=event.id, parse_mode='md')
