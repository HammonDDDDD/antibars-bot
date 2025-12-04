import time
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, Optional, List
from lab4.constants import (
    QUOTES_URL, BOT_TOKEN, API_BASE_URL,
    POLLING_TIMEOUT, REQUEST_TIMEOUT, SLEEP_TIME,
    ADDITIONAL_WAIT_TIME
)


def build_api_url(method_name: str) -> str:
    """ Строит URL для запроса к API Telegram
    :param method_name: название метода API (getMe, sendMessage)
    :returns: готовый URL для запроса
    """
    return f"{API_BASE_URL}{BOT_TOKEN}/{method_name}"


def check_token() -> None:
    """ Проверка корректности токена, вывод информации о боте в консоль
    :raises: requests.exceptions.RequestException при ошибке запроса
    """
    url: str = build_api_url("getMe")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # проверка на статус 2xx
        bot_info: Dict[str, Any] = response.json()  # json -> dict

        if bot_info.get("ok"):
            # get безопаснее bot_info["result"] т.к. не выбрасывает исключения
            result = bot_info.get("result", {})
            print("Bot is working!")
            print(f"Bot ID: {result.get('id')}")
            print(f"Bot username: {result.get('username')}")
            print(f"Bot first name: {result.get('first_name')}")
        else:
            print(f"Error: {bot_info.get('description')}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def send_message(chat_id: int, text: str) -> bool:
    """ Отправить сообщение в чат по id chat_id
    Отправляет POST-запрос к методу send_message с текстом
    :param chat_id: ID чата для отправки сообщения
    :param text: текст сообщения
    :returns: True если удача, False если фэйл
    :raises: requests.exceptions.RequestException при ошибке запроса
    """
    url: str = build_api_url("sendMessage")
    payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        result: Dict[str, Any] = response.json()

        if result.get("ok"):
            print(f"Message sent to {chat_id}")
            return True
        else:
            print(f"Failed to send message to {chat_id}"
                  f": {result.get('description')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False


def get_updates(offset: Optional[int] = None,
                timeout: int = POLLING_TIMEOUT) -> Dict[str, Any]:
    """ Получить обновления от TG Bot API
    Использует метод getUpdates для получения новых сообщений
    Если offset не указан, получает все сообщения
    :param offset: последнее полученное update_id + 1, если None то все
    :param timeout: время ожидания ответа
    :returns: словарь с результатом запроса - список обновлений
    :raises: requests.exceptions.RequestException при ошибке запроса
    """
    url: str = build_api_url("getUpdates")
    params: Dict[str, Any] = {"timeout": timeout}

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params,
                                timeout=timeout + ADDITIONAL_WAIT_TIME)
        response.raise_for_status()
        result: Dict[str, Any] = response.json()
        return result
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"ok": False, "result": []}


def _extract_message_data(update: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """ Извлекает данные из сообщения
    :param update: словарь с данными обновления от API
    :returns: словарь с chat_id и text если сообщение, иначе None
    """
    message = update.get("message")
    if message is None:
        return None

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if chat_id is not None and text is not None:
        return {"chat_id": chat_id, "text": text}

    return None


def run_echo_bot() -> None:
    """ Запускает эхо-бота """
    offset: Optional[int] = None
    print("Echo bot started!")

    try:
        while True:
            result = get_updates(offset=offset)

            if not result.get("ok"):
                print(f"Error getting updates: {result}")
                time.sleep(SLEEP_TIME)
                continue

            updates: List[Dict[str, Any]] = result.get("result", [])

            for update in updates:
                message_data = _extract_message_data(update)

                if message_data is not None:
                    chat_id = message_data["chat_id"]
                    text = message_data["text"]

                    print(f"Recieved message from: {chat_id}, {text}")

                    if text == "/quote":
                        quote = get_daily_quote()
                        send_message(chat_id, quote)
                    else:
                        send_message(chat_id, text)

                update_id = update.get("update_id")
                if update_id is not None:
                    offset = update_id + 1

    except KeyboardInterrupt:
        print("\nEcho bot stopped!")


def get_daily_quote() -> str:
    """ Получает цитату дня с сайта quotes.toscrape.com"""
    try:
        response = requests.get(QUOTES_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Quote request failed: {e}")
        return "I cant get a quote right now"

    soup = BeautifulSoup(response.text, "html.parser")

    first_quote_block = soup.find("div", class_="quote")
    if first_quote_block is None:
        return "No quote found"

    text_tag = first_quote_block.find("span", class_="text")
    author_tag = first_quote_block.find("small", class_="author")

    if text_tag is None or author_tag is None:
        return "Quote parse error"

    quote_text = text_tag.get_text(strip=True)
    author_name = author_tag.get_text(strip=True)

    return f'{quote_text} — {author_name}'


if __name__ == "__main__":
    check_token()
    print()

    run_echo_bot()
