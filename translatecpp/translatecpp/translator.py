import openai
from config import OPENAI_API_KEY

# Функция для перевода имён переменных в C++ коде на русский язык с помощью OpenAI
def translate_variables(file_path):
    openai.api_key = OPENAI_API_KEY
    # Читаем исходный код из файла
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    # Формируем промпт для OpenAI
    prompt = (
        "Переведи все переменные в следующем коде на русский язык. "
        "Верни только код, без вступительного и заключительного текста. А так же внизу кода в /* */ был написан комментарий к тому как работает код"
        "Оставь названия функций и ключевые слова без изменений, изменяй только имена переменных.\n\n"
        f"{code}"
    )
    # Отправляем запрос к OpenAI
    response = openai.ChatCompletion.create(
         model="gpt-4o-mini",
         messages=[{"role": "user", "content": prompt}],
         temperature=0.2,
    )
    translated_code = response.choices[0].message.content

    # Удаляем возможные маркеры форматирования кода (```cpp и ```)
    translated_code = translated_code.replace("```cpp", "").replace("```", "") #Удаляет из ответа OpenAI
    # Удаляем лишние пробелы по краям
    translated_code = translated_code.strip()

    # Если в ответе есть фраза "Вот ваш код", пытаемся вытащить только сам код
    if "Вот ваш код" in translated_code:
        translated_code = translated_code.split("```")[1].strip()
    
    return translated_code

# Функция для перевода ключевых слов и типов данных в C++ коде на русский язык
def translate_cpp(file_path):
    translation_map = {
        'int': 'целое',
        'double': 'дробное',
        'main': 'главная',
        'return': 'вернуть',
        'if': 'если',
        'else': 'иначе',
        'string': 'строка',
        'cout': 'вывод',
        'cin': 'ввод',
        'getline': 'получить_строку',
        'void': 'пусто',
        'bool': 'логическое',
        'const': 'константа',
        'volatile': 'изменяемое',
        'template': 'шаблон',
        'namespace': 'пространство_имен',
        'struct': 'структура',
        'enum': 'перечисление',
        'try': 'попытка',
        'catch': 'поймать',
        'throw': 'бросить',
        'new': 'новый',
        'delete': 'удалить',
        'operator': 'оператор',
        'this': 'этот',
        'break': 'прервать',
        'continue': 'продолжить',
        'vector': 'вектор',
        'endl': 'конецстроки',
        'vector': 'вектор',
        'list': 'список',
        'deque': 'двусторонняя_очередь',
        'stack': 'стек',
        'queue': 'очередь',
        'map': 'ассоциативный_массив',
        'set': 'множество',
        'unordered_map': 'хеш_таблица',
        'unordered_set': 'хеш_множество',
        'pair': 'пара',
        'tuple': 'кортеж',
        'array': 'статический_массив',
        'forward_list': 'односвязный_список',
        'priority_queue': 'очередь_с_приоритетом'
    }

    # Читаем содержимое файла
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    result_lines = []
    for line in lines:
        # Если строка содержит #include <...>, не переводим её
        if line.strip().startswith('#include <'):
            result_lines.append(line)
            continue
        # Иначе переводим ключевые слова
        for english, russian in translation_map.items():
            line = line.replace(english, russian)
        result_lines.append(line)

    return ''.join(result_lines)