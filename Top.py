# meta developer: @mofkomodules
# sosal? 
# name: TopStat
# da, sosal

__version__ = (1, 4, 8)

from .. import loader, utils
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TopStat(loader.Module):
    """
    Модуль чтобы поесть говна.
    """
    strings = {"name": "TopStat"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.command(
        ru_doc="Показывает топ пользователей по сообщениям в текущем чате.\n"
              ,
        en_doc="Shows top users by messages in the current chat.\n"
    )
    async def msgtopcmd(self, message):
        """
        Показывает топ говноедов по сообщениям в чате.
        """
        chat_entity = await message.get_chat()
        if not chat_entity:
            await message.edit(message, "Эта команда работает только в группах и каналах.")
            return

        processing_message = await message.edit(message, "Собираю статистику сообщений, это может занять некоторое время...")

        msg_counts = defaultdict(int)
        users_info = {}
        total_messages_scanned = 0

        messages_limit_default = 5000
        top_n_limit_default = 10
        
        min_messages_limit = 100
        max_messages_limit = 20000
        min_top_n = 1
        max_top_n = 50 

        current_messages_limit = messages_limit_default
        current_top_n_limit = top_n_limit_default

        args = utils.get_args(message)
        
        # Parse arguments: [messages_limit] [top_n_limit]
        if args:
            if len(args) >= 1 and args[0].isdigit():
                requested_messages_limit = int(args[0])
                if requested_messages_limit < min_messages_limit:
                    current_messages_limit = min_messages_limit
                    await utils.answer_message(message, f"Лимит сообщений слишком мал ({requested_messages_limit}), установлен минимум: {min_messages_limit}", reply_to=processing_message)
                elif requested_messages_limit > max_messages_limit:
                    current_messages_limit = max_messages_limit
                    await utils.answer_message(message, f"Лимит сообщений слишком велик ({requested_messages_limit}), установлен максимум: {max_messages_limit}", reply_to=processing_message)
                else:
                    current_messages_limit = requested_messages_limit

            if len(args) >= 2 and args[1].isdigit():
                requested_top_n_limit = int(args[1])
                if requested_top_n_limit < min_top_n:
                    current_top_n_limit = min_top_n
                    await utils.answer_message(message, f"Количество пользователей в топе слишком мало ({requested_top_n_limit}), установлен минимум: {min_top_n}", reply_to=processing_message)
                elif requested_top_n_limit > max_top_n:
                    current_top_n_limit = max_top_n
                    await utils.answer_message(message, f"Количество пользователей в топе слишком велико ({requested_top_n_limit}), установлен максимум: {max_top_n}", reply_to=processing_message)
                else:
                    current_top_n_limit = requested_top_n_limit
        
        try:
            async for msg in self.client.iter_messages(chat_entity, limit=current_messages_limit):
                total_messages_scanned += 1
                if msg.sender and msg.sender.id:
                    user_id = msg.sender.id
                    msg_counts[user_id] += 1
                    if user_id not in users_info:
                        users_info[user_id] = msg.sender
        except Exception as e:
            logger.error(f"Error collecting stats in chat {chat_entity.id}: {e}", exc_info=True)
            await utils.answer_message(message, f"Ошибка при сборе статистики: {e}", reply_to=processing_message)
            await processing_message.delete()
            return

        if not msg_counts:
            await utils.answer_message(message, f"Не удалось собрать статистику сообщений в этом чате или в заданном лимите ({current_messages_limit} сообщений).", reply_to=processing_message)
            await processing_message.delete()
            return

        sorted_users = sorted(msg_counts.items(), key=lambda item: item[1], reverse=True)

        top_count_actual = min(len(sorted_users), current_top_n_limit)
        
        top_message = f"**Топ {top_count_actual} пользователей по сообщениям " \
                      f"(просканировано {total_messages_scanned} сообщений):**\n\n"
        
        for i, (user_id, count) in enumerate(sorted_users[:top_count_actual]):
            user = users_info.get(user_id)
            user_name = "Неизвестный пользователь"
            if user:
                display_name = utils.get_display_name(user)
                if display_name:
                    user_name = display_name
                elif user.deleted:
                    user_name = "Удаленный аккаунт"
                elif user.bot:
                    user_name = f"Бот: {user.first_name or user.id}"
                else:
                    # Fallback if get_display_name is empty but user exists and is not deleted/bot
                    user_name = f"Пользователь {user.id}" 

            top_message += f"{i+1}. [{user_name}](tg://user?id={user_id}) - {count} сообщений\n"
        
        await utils.answer_message(message, top_message, parse_mode='md')
        await processing_message.delete()
