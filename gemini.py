import os
import sys
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
system_instruction_file = sys.argv[2]  # Файл, содержащий системные инструкции
file_path_or_url = sys.argv[3]  # Путь к локальному файлу или URL
output_file_path = sys.argv[4]  # Путь для сохранения результата
proxy = sys.argv[5]  # Прокси передается как 5-й аргумент
model_name = sys.argv[6]  # Имя модели передаётся как 6-й аргумент

# Установка прокси как переменных окружения
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# Функция для загрузки текста из URL или чтения из локального файла
def load_text(file_path_or_url):
    try:
        if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
            # Загружаем текст из URL
            response = requests.get(file_path_or_url)
            response.raise_for_status()  # Проверка на наличие ошибок в запросе
            return response.text
        else:
            # Читаем текст из локального файла
            with open(file_path_or_url, 'r', encoding='utf-8') as file:
                return file.read()
    except Exception as e:
        print(f"Ошибка при загрузке файла: {str(e)}")
        logging.error(f"Ошибка при загрузке файла: {str(e)}")
        sys.exit(1)

# Загружаем текст системной инструкции из файла
try:
    with open(system_instruction_file, 'r', encoding='utf-8') as file:
        system_instruction = file.read().strip()
except Exception as e:
    print(f"Ошибка при загрузке системной инструкции: {str(e)}")
    logging.error(f"Ошибка при загрузке системной инструкции: {str(e)}")
    sys.exit(1)

# Загружаем текст из файла или URL
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
    model_name=model_name,  # Используем переданное имя модели
    generation_config=generation_config,
    system_instruction=system_instruction,
)

# Запуск сессии чата
chat_session = model.start_chat(history=[])

# Отправка сообщения и вывод ответа
try:
    response = chat_session.send_message(user_message)
    result_text = response.text

    # Сохранение результата в указанный файл
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(result_text)
    
    print(f"Результат успешно сохранён в файл: {output_file_path}")
    print(f"Ответ: {result_text}")  # Выводим ответ на экран
except Exception as e:
    print(f"Произошла ошибка при получении ответа: {str(e)}")
    logging.error(f"Error: {str(e)}")  # Логируем ошибку
