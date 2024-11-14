import os
import sys
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
import requests
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Проверяем количество переданных аргументов
if len(sys.argv) != 7:
    print("Использование: python gemini.py <api_key> <system_instruction_file> <file_path_or_url> <output_file_path> <proxy> <model_name>")
    sys.exit(1)

# Получаем аргументы
api_key = sys.argv[1]
system_instruction_file = sys.argv[2]
file_path_or_url = sys.argv[3]
output_file_path = sys.argv[4]
proxy = sys.argv[5]
model_name = sys.argv[6]

# Установка прокси как переменных окружения
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# Функция для загрузки текста из URL или чтения из локального файла
def load_text(file_path_or_url):
    try:
        if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
            response = requests.get(file_path_or_url)
            response.raise_for_status()
            return response.text
        else:
            with open(file_path_or_url, 'r', encoding='utf-8') as file:
                return file.read()
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла: {str(e)}")
        sys.exit(1)

# Функция для разбиения текста на части
def split_text(text, max_length):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Загружаем системную инструкцию и пользовательский текст
try:
    with open(system_instruction_file, 'r', encoding='utf-8') as file:
        system_instruction = file.read().strip()
except Exception as e:
    logging.error(f"Ошибка при загрузке системной инструкции: {str(e)}")
    sys.exit(1)

user_message = load_text(file_path_or_url)

# Конфигурация API
genai.configure(api_key=api_key)

# Создание модели
generation_config = {
    "temperature": 1.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name=model_name,
    generation_config=generation_config,
    system_instruction=system_instruction,
)

# Разбиваем текст на части
text_chunks = split_text(user_message, 30000)  # Оставьте запас, если токены < символов
chat_session = model.start_chat(history=[])

# Обрабатываем каждую часть и сохраняем ответ
for chunk in text_chunks:
    try:
        response = model.generate_content(
            [chunk],
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        result_text = response.text
        with open(output_file_path, 'a', encoding='utf-8') as output_file:
            output_file.write(result_text + "\n\n")
        logging.info(result_text)
        logging.info(f"Часть успешно сохранена. Длина ответа: {len(result_text)} символов")
    except Exception as e:
        logging.error(f"Произошла ошибка при получении ответа: {str(e)}")
