import logging
import emoji
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Шаги в разговоре
FIRST_QUESTION, SECOND_QUESTION, CHANNEL_INVITE = range(3)

# Функция старт с кнопкой "Далее"
async def start(update: Update, context: CallbackContext) -> int:
    logger.info("Запуск команды /start от пользователя %s", update.message.from_user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("Далее", callback_data='next')]  # Кнопка "Далее"
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        emoji.emojize(':bell:') + f'{update.message.from_user.first_name}, добро пожаловать в CHILL BOT\n\n' +
        emoji.emojize(':open_file_folder:') + 'Для дальнейшей работы с нами, вам потребуется заполнить анкету.',
        reply_markup=reply_markup  # Добавляем клавиатуру
    )
    return FIRST_QUESTION

# Обработка нажатия кнопки "Далее"
async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки
    logger.info("Пользователь нажал кнопку 'Далее'")
    
    await query.edit_message_text(emoji.emojize(':black_nib:') + 'Откуда вы узнали о нашем проекте?')
    return SECOND_QUESTION

# Первый вопрос
async def first_question(update: Update, context: CallbackContext) -> int:
    user_name = update.message.text  # Сохраняем имя пользователя, полученное от сообщения
    context.user_data['name'] = user_name  # Сохраняем имя в данных пользователя
    logger.info("Пользователь ответил на первый вопрос: %s", user_name)
    
    await update.message.reply_text(emoji.emojize(':money_bag:') + 'Есть ли у вас опыт работы?')
    return SECOND_QUESTION

# Второй вопрос
async def second_question(update: Update, context: CallbackContext) -> int:
    user_experience = update.message.text  # Сохраняем ответ на вопрос о опыте
    context.user_data['experience'] = user_experience  # Сохраняем ответ в данных пользователя
    logger.info("Пользователь ответил на второй вопрос: %s", user_experience)
    
    await update.message.reply_text(
        emoji.emojize(':bell:') + 'Теперь вы можете вступить в наш канал!',
        reply_markup=InlineKeyboardMarkup([  # Кнопка для вступления в канал с url
            [InlineKeyboardButton("Вступить в канал", url="https://t.me/+X17dA8mtG840Y2Iy")],  # Ссылка на канал
            [InlineKeyboardButton("Я вступил, сообщите администрации", callback_data="join_channel")]  # Кнопка для уведомления
        ])
    )
    return CHANNEL_INVITE

# Обработчик нажатия кнопки "Я вступил, сообщите администрации"
async def join_channel(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки
    logger.info("Пользователь нажал кнопку 'Я вступил, сообщите администрации'")
    
    await query.edit_message_text(
        emoji.emojize(':rocket:') + 'Ваша заявка отправлена администрации проекта.\n\n' +
        emoji.emojize(':watch:') + 'Примерное время рассмотрения 1-10 часов'
    )  # Новый текст после вступления в канал
    return ConversationHandler.END

# Главная функция, которая запускает бота
def main():
    application = Application.builder().token("7896306313:AAErvipbUxclxdf4zt-nnd8zog6g94LDyTY").build()
    
    # Конфигурируем разговор
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],  # Начинаем с команды /start
        states={
            FIRST_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_question)],  # Обработка первого вопроса
            SECOND_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_question)],  # Обработка второго вопроса
            CHANNEL_INVITE: [CallbackQueryHandler(join_channel, pattern="join_channel")]  # Обработчик кнопки "Я вступил"
        },
        fallbacks=[],
    )
    
    # Обработчик нажатия кнопки "Далее"
    application.add_handler(CallbackQueryHandler(button, pattern='next'))
    # Добавляем ConversationHandler
    application.add_handler(conversation_handler)
    
    # Запуск бота
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()
