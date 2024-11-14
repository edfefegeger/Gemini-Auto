import os
import sys
import requests
import logging
from io import BytesIO
import google.generativeai as genai


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Проверка количества переданных аргументов
if len(sys.argv) < 6:
    print("Использование: python gemini.py <api_key> <promt> <trascript> <model_name> <output_file_path> <proxy>")
    sys.exit(1)

# Получение аргументов
api_key = sys.argv[1]
promt = sys.argv[2]
file_path_or_url = sys.argv[3]  # Путь к изображению или текстовый промт
output_file_path = sys.argv[4]  # Путь для сохранения результата
proxy = sys.argv[5]             # Прокси
model_name = sys.argv[6]        # Имя модели

# Установка прокси
proxies = {
    "http": proxy,
    "https": proxy
}

headers = {
    "Authorization": f"Bearer {api_key}"
}

# Тестируем подключение к API через прокси
try:
    test_response = requests.get("https://api.openai.com/v1/models", headers=headers, proxies=proxies)
    test_response.raise_for_status()
    logging.info("Прокси соединение успешно установлено.")
except requests.RequestException as e:
    print(f"Ошибка при установлении соединения через прокси: {str(e)}")
    logging.error(f"Proxy error: {str(e)}")
    sys.exit(1)

# Загрузка изображения из URL


# Отправка запроса к API OpenAI для создания вариаций изображения
try:
    if model_name != "":
        # try:
        #     if os.path.isfile(file_path_or_url):
        #         with open(file_path_or_url, 'rb') as file:
        #             image_data = BytesIO(file.read())  # Загружаем изображение в BytesIO
        # except requests.RequestException as e:
        #     print(f"Не преобразовать изображение по пути: {str(e)}")
        #     logging.error(f"Image download error: {str(e)}")
        #     sys.exit(1)

        # files = {
        #     "image": ("image.png", image_data, "image/png"),
        # }
        # data = {
        #     "n": 2,
        #     "size": "1024x1024"
        # }
        # response = requests.post(
        #     "https://api.openai.com/v1/images/variations",
        #     headers=headers,
        #     files=files,
        #     data=data,
        #     proxies=proxies
        # )
        # response.raise_for_status()
        
        # # Проверка результата
        # if response.status_code == 200:
        #     image_url = response.json()['data'][0]['url']
        #     print(f"URL изображения: {image_url}")
        # else:
        #     print("Произошла ошибка: ", response.text)
        # Загружаем текст из файла или URL
        user_message = file_path_or_url

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
            system_instruction="Ты — ассистент, отвечающий только простым текстом без форматирования. Увеличьте количество символов на 10%, чтобы текст стал более содержательным и увлекательным, сохраняя оригинальный смысл и стиль. Переведите текст на русский язык. Разбей текст на короткие, смысловые абзацы, каждый из которых посвящен одной законченной мысли или идее. Соблюдай правила пунктуации и грамматики.Формат ответа:АбзацАбзацАбзацАбзац (и так далее, по необходимости)",
        )

        # Запуск сессии чата
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_message)
        result_text = response.text

    # else:
    #     data = {
    #         "model": model_name,
    #         "messages": [
    #             {"role": "system", "content": "You are a helpful assistant."},
    #             {"role": "user", "content": file_path_or_url}
    #         ]
    #     }
    #     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, proxies=proxies)
    #     response.raise_for_status()
        

    #     if response.status_code == 200:
    #         message = response.json()['choices'][0]['message']['content']
    #         print(f"Ответ модели: {message}")
    #         image_url = message
    #     else:
    #         print("Произошла ошибка: ", response.text)


    with open(output_file_path, 'a', encoding='utf-8') as output_file:
        output_file.write(result_text + '\n' +'\n')


    print(f"Результат сохранён в файл: {output_file_path}")
except requests.RequestException as e:
    print(f"Произошла ошибка при получении ответа: {str(e)}")
    logging.error(f"Error: {str(e)}")
    if 'response' in locals():
        logging.error(f"Ответ сервера: {response.text}")  
