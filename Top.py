# meta developer: @mofkomodules 
# name: TopStat

__version__ = (2, 0, 0)

from heroku.module_base import Module
from telethon import events
import asyncio

class TopStat(Module):
    def __init__(self, client, db):
        super().__init__(client, db)
        self.message_counts = self.db.get("message_counts", {})
        self.lock = asyncio.Lock()

    async def _update_message_count(self, user_id):
        async with self.lock:
            user_id_str = str(user_id)
            if user_id_str not in self.message_counts:
                self.message_counts[user_id_str] = 0
            self.message_counts[user_id_str] += 1
            self.db["message_counts"] = self.message_counts

    @events.NewMessage()
    async def msg_handler(self, event):
        if event.sender_id and not event.outgoing:
            await self._update_message_count(event.sender_id)

    @events.NewMessage(pattern=r"^\.msgtop(?: (\d+))?$", outgoing=True)
    async def msgtopcmd(self, event):
        args = event.pattern_match.group(1)
        top_n = int(args) if args else 10

        if not self.message_counts:
            await event.reply("📊 Статистика сообщений пока пуста.")
            return

        sorted_users = sorted(self.message_counts.items(), key=lambda item: item[1], reverse=True)
        top_users = sorted_users[:top_n]

        if not top_users:
            await event.reply("📊 Статистика сообщений пока пуста.")
            return

        response_lines = [f"📊 **Топ-{top_n} пользователей по сообщениям:**\n"]
        for i, (user_id_str, count) in enumerate(top_users):
            user_id = int(user_id_str)
            try:
                user = await self.client.get_entity(user_id)
                
                display_name = user.full_name.strip()
                if not display_name:
                    display_name = user.username or f"ID: {user_id}"

                if user.username:
                    user_link = f"[{display_name}](t.me/{user.username})"
                else:
                    user_link = f"[{display_name}](tg://user?id={user_id})"
            except Exception:
                display_name = f"Удалённый пользователь ({user_id})"
                user_link = display_name

            response_lines.append(f"**{i+1}.** {user_link}: `{count}` сообщений")

        await event.reply("\n".join(response_lines))
