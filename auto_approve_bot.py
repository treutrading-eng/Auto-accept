"""
Бот для автоматического приёма заявок на вступление в группу/канал Telegram.

Как это работает:
- В группе/канале должна быть включена настройка "Заявки на вступление"
  (Approve new members / Join requests), иначе заявок просто не будет —
  люди будут вступать сразу.
- Бот должен быть администратором в этой группе/канале с правом
  "Добавление участников" (Add Users / Invite via Link).
- Когда приходит новая заявка (ChatJoinRequest), бот сразу её одобряет.

Установка зависимостей:
    pip install python-telegram-bot --upgrade

Запуск:
    python auto_approve_bot.py
"""

import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    ChatJoinRequestHandler,
    ContextTypes,
)

# Токен берётся из переменной окружения BOT_TOKEN (задайте её в Railway -> Variables).
# Для локального запуска можно временно подставить токен напрямую как строку.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН_ЕСЛИ_ЗАПУСКАЕТЕ_ЛОКАЛЬНО")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Автоматически одобряет любую заявку на вступление."""
    join_request = update.chat_join_request
    user = join_request.from_user
    chat = join_request.chat

    try:
        await context.bot.approve_chat_join_request(
            chat_id=chat.id,
            user_id=user.id,
        )
        logger.info("Одобрена заявка: %s (id=%s) -> %s", user.full_name, user.id, chat.title)

        # Опционально: приветственное сообщение пользователю в личку.
        # Сработает, только если пользователь раньше писал боту/нажимал Start.
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Привет, {user.first_name}! Ваша заявка в «{chat.title}» одобрена ✅",
            )
        except Exception:
            # Если у пользователя закрыты личные сообщения от бота — просто пропускаем
            pass

    except Exception as e:
        logger.error("Не удалось одобрить заявку от %s: %s", user.id, e)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(ChatJoinRequestHandler(auto_approve))

    logger.info("Бот запущен и ожидает заявки на вступление...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
