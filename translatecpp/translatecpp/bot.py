from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from translator import translate_cpp, translate_variables
import os
from config import BOT_TOKEN

# Состояния для диалога
WAITING_FOR_FILENAME = 1
WAITING_FOR_FILE = 2

# Стартовая команда: просим пользователя ввести имя выходного файла
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Привет! Я бот для перевода C++ кода на русский язык.\n'
        'Для начала работы, пожалуйста, укажите желаемое имя выходного файла (без расширения):'
    )
    return WAITING_FOR_FILENAME

# Получаем имя файла от пользователя
async def get_filename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['output_filename'] = update.message.text
    await update.message.reply_text(
        'Отлично! Теперь отправьте мне .cpp файл для перевода.'
    )
    return WAITING_FOR_FILE

# Обработка присланного .cpp файла
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Проверяем расширение файла
    if not update.message.document.file_name.endswith('.cpp'):
        await update.message.reply_text('Пожалуйста, отправьте файл с расширением .cpp')
        return WAITING_FOR_FILE

    # Получаем имя выходного файла из контекста
    output_filename = context.user_data.get('output_filename')
    if not output_filename:
        await update.message.reply_text('Пожалуйста, сначала укажите имя файла используя команду /start')
        return ConversationHandler.END
    
    # Скачиваем файл во временное хранилище
    file = await update.message.document.get_file()
    await file.download_to_drive('temp.cpp')

    await update.message.reply_text('Начинаю перевод файла...')

    # Переводим имена переменных через OpenAI
    variables_translated = translate_variables('temp.cpp')
    with open('temp_vars.cpp', 'w', encoding='utf-8') as f:
        f.write(variables_translated)

    # Переводим ключевые слова и типы
    final_translated = translate_cpp('temp_vars.cpp')
    
    # Добавляем include для макросов
    final_translated = f'#include "{output_filename}.h"\n\n{final_translated}'
    
    cpp_output_path = f'{output_filename}.cpp'
    with open(cpp_output_path, 'w', encoding='utf-8') as f:
        f.write(final_translated)
    
    # Создаём файл с макросами для компиляции
    macro_content = (
        '#ifndef MACRO_H\n'
        '#define MACRO_H\n\n'
        '#define целое int\n'
        '#define дробное double\n'
        '#define главная main\n'
        '#define вернуть return\n'
        '#define если if\n'
        '#define иначе else\n'
        '#define строка string\n'
        '#define вывод cout\n'
        '#define ввод cin\n'
        '#define получить_строку getline\n'
        '#define пусто void\n\n'
        '#define логическое bool\n'
        '#define константа const\n'
        '#define изменяемое volatile\n'
        '#define шаблон template\n'
        '#define пространство_имен namespace\n'
        '#define структура struct\n'
        '#define перечисление enum\n'
        '#define попытка try\n'
        '#define поймать catch\n'
        '#define бросить throw\n'
        '#define новый new\n'
        '#define удалить delete\n'
        '#define оператор operator\n'
        '#define этот this\n'
        '#define прервать break\n'
        '#define продолжить continue\n'
        '#define вектор vector\n'
        '#define конецстроки endl\n'
        '#define вектор vector\n'
        '#define список list\n'
        '#define двусторонняя_очередь deque\n'
        '#define стек stack\n'
        '#define очередь queue\n'
        '#define ассоциативный_массив map\n'
        '#define множество set\n'
        '#define хеш_таблица unordered_map\n'
        '#define хеш_множество unordered_set\n'
        '#define пара pair\n'
        '#define кортеж tuple\n'
        '#define статический_массив array\n'
        '#define односвязный_список forward_list\n'
        '#define очередь_с_приоритетом priority_queue\n\n'
        '#endif // MACRO_H\n'

    )
    macro_output_path = f'{output_filename}.h'
    with open(macro_output_path, 'w', encoding='utf-8') as f:
        f.write(macro_content)

    # Отправляем пользователю переведённый файл и макросы
    with open(cpp_output_path, 'rb') as translated_file, open(macro_output_path, 'rb') as macro_file:
        await update.message.reply_document(
            document=translated_file,
            caption=f'Переведённый C++ файл: {cpp_output_path}'
        )
        await update.message.reply_document(
            document=macro_file,
            caption=f'Файл с макросами для компиляции: {macro_output_path}'
        )

    # Удаляем временные файлы
    os.remove('temp.cpp')
    os.remove('temp_vars.cpp')
    os.remove(cpp_output_path)
    os.remove(macro_output_path)

    await update.message.reply_text(
        'Перевод завершён! Чтобы перевести другой файл, используйте команду /start'
    )
    return ConversationHandler.END

# Обработка отмены операции
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Операция отменена. Для начала новой операции используйте команду /start'
    )
    return ConversationHandler.END

# Основная функция запуска бота
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_filename)],
            WAITING_FOR_FILE: [MessageHandler(filters.Document.FileExtension("cpp"), handle_document)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()