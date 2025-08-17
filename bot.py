import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from notion_client import Client

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
INOCEAN_TOKEN = os.getenv("INOCEAN_TOKEN")
INOCEAN_DATABASE_ID = os.getenv("INOCEAN_DATABASE_ID")

# Initialize Notion client
notion = Client(auth=INOCEAN_TOKEN)

# Состояния для ConversationHandler
(
    NAME, NICKNAME, TASK_NAME, DESCRIPTION, DEADLINE, PROBLEM,
    INITIATOR, GOAL, TEMPLATE_SOLUTION, LPR, OS, TECH_PARAMS,
    RESTRICTIONS, REFERENCES, STOP_FACTORS, MEETINGS, CONFIRM
) = range(17)

# Временное хранилище ответов
user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Давай создадим новую задачу в Backlog. "
        "Сначала введи своё имя."
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['name'] = update.message.text
    await update.message.reply_text("Теперь введи свой никнейм в Telegram.")
    return NICKNAME

async def get_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['nickname'] = update.message.text
    await update.message.reply_text("Название задачи? (_пример: Dtask-170825_)")
    return TASK_NAME

async def get_task_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['task_name'] = update.message.text
    await update.message.reply_text("Описание задачи (_пример: Нужно улучшить дизайн игровых зон для кампусов_)")
    return DESCRIPTION

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['description'] = update.message.text
    await update.message.reply_text("Дедлайн (DDL) и комментарий при высоком приоритете (_пример: 01.09.2025_)")
    return DEADLINE

async def get_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['deadline'] = update.message.text
    await update.message.reply_text("Какую проблему решаем? (_пример: Недостаток уюта игровых зон_)")
    return PROBLEM

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['problem'] = update.message.text
    await update.message.reply_text("Кто или что является инициатором? (_пример: Отзывы 10 родителей_)")
    return INITIATOR

async def get_initiator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['initiator'] = update.message.text
    await update.message.reply_text("Что даст новый дизайн? (_пример: Рост лояльности_)")
    return GOAL

async def get_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['goal'] = update.message.text
    await update.message.reply_text("Можно ли решить шаблонным решением? (_пример: Да, можно сделать ресайз макета_)")
    return TEMPLATE_SOLUTION

async def get_template_solution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['template_solution'] = update.message.text
    await update.message.reply_text("Кто ЛПР задачи? (_пример: @mishaphc_)")
    return LPR

async def get_lpr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['lpr'] = update.message.text
    await update.message.reply_text("Кто даёт ОС и сроки согласования? (_пример: @имя — согласует финальный результат_)")
    return OS

async def get_os(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['os'] = update.message.text
    await update.message.reply_text("Технические параметры (формат, бюджет, материалы) (_пример: 2,15х3,5м, белая бетонная стена_)")
    return TECH_PARAMS

async def get_tech_params(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['tech_params'] = update.message.text
    await update.message.reply_text("Ограничения (_пример: Только ч/б печать, нельзя сверлить стену_)")
    return RESTRICTIONS

async def get_restrictions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['restrictions'] = update.message.text
    await update.message.reply_text("Референсы / стилистика (_пример: Если пожеланий нет, можно не заполнять_)")
    return REFERENCES

async def get_references(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['references'] = update.message.text
    await update.message.reply_text("Стоп-факторы (_пример: Ждем уточнения от центра в НН_)")
    return STOP_FACTORS

async def get_stop_factors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['stop_factors'] = update.message.text
    await update.message.reply_text("Регулярные встречи (_пример: Не нужны_)")
    return MEETINGS

async def get_meetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answers['meetings'] = update.message.text

    # Собираем текст карточки
    card_text = f"""
**Название задачи:** {user_answers['task_name']}
**Описание:** {user_answers['description']}
**Дедлайн:** {user_answers['deadline']}
**Проблема:** {user_answers['problem']}
**Инициатор:** {user_answers['initiator']}
**Что даст новый дизайн:** {user_answers['goal']}
**Можно решить шаблонным решением:** {user_answers['template_solution']}
**ЛПР:** {user_answers['lpr']}
**Кто даёт ОС и сроки:** {user_answers['os']}
**Технические параметры:** {user_answers['tech_params']}
**Ограничения:** {user_answers['restrictions']}
**Референсы / стилистика:** {user_answers['references']}
**Стоп-факторы:** {user_answers['stop_factors']}
**Регулярные встречи:** {user_answers['meetings']}
**Отправитель:** {user_answers['name']} ({user_answers['nickname']})
"""

    # Создаём карточку в Notion в Backlog
    try:
        notion.pages.create(
            parent={"database_id": INOCEAN_DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": user_answers['task_name']}}]},
                "Status": {"select": {"name": "Backlog"}},
                "Description": {"rich_text": [{"text": {"content": card_text}}]}
            }
        )
        await update.message.reply_text("Задача успешно добавлена в Backlog Notion!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении: {e}")

    user_answers.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Создание задачи отменено.")
    user_answers.clear()
    return ConversationHandler.END

# Создаём приложение и обработчики
app = ApplicationBuilder().token(BOT_TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('newtask', start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nickname)],
        TASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_task_name)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
        DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_deadline)],
        PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_problem)],
        INITIATOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_initiator)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal)],
        TEMPLATE_SOLUTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_template_solution)],
        LPR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_lpr)],
        OS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_os)],
        TECH_PARAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tech_params)],
        RESTRICTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_restrictions)],
        REFERENCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_references)],
        STOP_FACTORS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stop_factors)],
        MEETINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_meetings)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    print("Бот запускается...")
    app.run_polling()
