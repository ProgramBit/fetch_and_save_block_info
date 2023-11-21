import requests
import json
import os  # Добавлен импорт модуля os

def fetch_and_save_block_info(output_directory=None, last_processed_block=None):
    url_blocks = "https://api.blockchair.com/bitcoin/blocks"
    params = {"limit": 100, "offset": 0}

    # Если указан последний обработанный блок, устанавливаем смещение
    if last_processed_block is not None:
        params["offset"] = last_processed_block + 1

    try:
        while True:
            # Получаем информацию о блоках (100 блоков за раз)
            response_blocks = requests.get(url_blocks, params=params)
            response_blocks.raise_for_status()
            data_blocks = response_blocks.json()

            # Обработка данных о блоках
            for block in data_blocks["data"]:
                block_height = block["id"]
                block_hash = block["hash"]

                # Создаем имя файла для каждого блока
                file_name = f"{output_directory}/block_{block_height}_info.txt" if output_directory else f"block_{block_height}_info.txt"

                # Создаем директорию, если её нет
                os.makedirs(output_directory, exist_ok=True)

                # Открываем файл для записи
                with open(file_name, "w") as file:
                    file.write(f"Block Height: {block_height}, Block Hash: {block_hash}\n\n")

                    # Обработка данных о транзакциях
                    transactions = block.get("transactions", [])
                    for transaction in transactions:
                        tx_hash = transaction["hash"]
                        sender = transaction["inputs"][0]["output"]["address"]
                        receiver = transaction["outputs"][0]["address"]
                        file.write(f"  Transaction Hash: {tx_hash}\n")
                        file.write(f"    Sender: {sender}\n")
                        file.write(f"    Receiver: {receiver}\n\n")

            # Проверяем, есть ли еще блоки
            if not data_blocks["data"]:
                break

            # Устанавливаем последний обработанный блок для следующей итерации
            last_processed_block = data_blocks["data"][-1]["id"]

            # Увеличиваем смещение для получения следующей порции блоков
            params["offset"] += 100

    except requests.exceptions.RequestException as e:
        print(f"Error during API request for blocks: {e}")

    return last_processed_block

if __name__ == "__main__":
    output_directory = "block_info"  # Укажите папку для сохранения файлов
    last_processed_block = None  # Установите в None для начала с самого первого блока

    while True:
        last_processed_block = fetch_and_save_block_info(output_directory, last_processed_block)
        if not last_processed_block:
            break
