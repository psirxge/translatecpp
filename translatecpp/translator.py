import openai
from config import OPENAI_API_KEY

def translate_variables(file_path):
    openai.api_key = OPENAI_API_KEY
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    prompt = (
        "Переведи все переменные в следующем коде на русский язык. "
        "Верни только код, без вступительного и заключительного текста. А так же внизу кода в /* */ был написан комментарий к тому как работает код"
        "Оставь названия функций и ключевые слова без изменений, изменяй только имена переменных.\n\n"
        f"{code}"
    )
    response = openai.ChatCompletion.create(
         model="gpt-4o-mini",
         messages=[{"role": "user", "content": prompt}],
         temperature=0.2,
    )
    translated_code = response.choices[0].message.content

    translated_code = translated_code.replace("```cpp", "").replace("```", "")
    translated_code = translated_code.strip()

    if "Вот ваш код" in translated_code:
        translated_code = translated_code.split("```")[1].strip()
    
    return translated_code

def translate_cpp(file_path):
    translation_map = {
        'int': 'целое',
        'double': 'дробное',
        'main': 'главная',
        'return': 'вернуть',
        'if': 'если',
        'else': 'иначе',
        'std::string': 'строка',
        'std::cout': 'вывод',
        'std::cin': 'ввод',
        'std::getline': 'получить_строку',
        'void': 'пусто'
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for english, russian in translation_map.items():
        content = content.replace(english, russian)

    return content