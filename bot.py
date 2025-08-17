import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from notion_client import Client

# Берём токены из environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
INOCEAN_TOKEN = os.getenv("INOCEAN_TOKEN")
INOCEAN_DATABASE_ID = os.getenv("INOCEAN_DATABASE_ID")

# Инициализация Notion клиента
notion = Client(auth=INOCEAN_TOKEN)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Notion подключён.")

# Команда /add — создаёт новую страницу в базе Notion
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        notion.pages.create(
            parent={"database_id": INOCEAN_DATABASE_ID},
            properties={
                "Name": {
                    "title": [{"text": {"content": "Новая запись от бота"}}]
                }
            }
        )
        await update.message.reply_text("Запись в Notion добавлена.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении: {e}")

# Создаём приложение бота и добавляем обработчики команд
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add))

# Запуск бота
if __name__ == "__main__":
    print("Бот запускается...")
    app.run_polling()
