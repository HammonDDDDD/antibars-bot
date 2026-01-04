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
    """
    Builds a complete API URL for making Telegram Bot API requests.
    
    This method constructs the full endpoint URL by combining the base API URL, 
    bot token, and specific method name to form a valid Telegram Bot API call.
    
    Args:
        method_name: Name of the Telegram Bot API method (e.g., 'getMe', 'sendMessage')
    
    Returns:
        str: Complete URL string ready for HTTP requests to the Telegram API
    """
    return f"{API_BASE_URL}{BOT_TOKEN}/{method_name}"


def check_token() -> None:
    """
    Validates the bot's authentication token by testing API connectivity and displays bot information.
    
    This method performs a health check of the bot's API connection by making a test request
    to verify the token is valid and retrieve basic bot details. It ensures the bot is properly
    configured before proceeding with other operations.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        requests.exceptions.RequestException: If the API request fails due to network issues
            or invalid response.
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
    """
    Send a message to a Telegram chat by chat_id.
    
    This method sends a POST request to the Telegram Bot API's sendMessage endpoint 
    to deliver text messages to specified chat recipients.
    
    Args:
        chat_id: Unique identifier for the target chat
        text: Content of the message to be sent
    
    Returns:
        bool: True if message was successfully delivered, False if delivery failed
    
    Raises:
        requests.exceptions.RequestException: If network request encounters an error
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
    """
    Fetch updates from the Telegram Bot API.
    
    This method retrieves new messages and events from Telegram using long polling.
    It implements the getUpdates method to receive updates with optional offset
    for handling previously processed messages.
    
    Args:
        offset: The update_id to start fetching from (last processed update_id + 1).
            If None, retrieves all available updates.
        timeout: Maximum time to wait for new updates in seconds.
    
    Returns:
        Dictionary containing API response with list of updates under 'result' key.
        Returns {'ok': False, 'result': []} on request failure.
    
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
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
    """
    Extracts message data from a Telegram update payload.
    
    This method processes incoming Telegram API updates to identify valid text messages
    and extract essential components needed for bot response handling.
    
    Args:
        update: A dictionary containing the Telegram API update payload.
    
    Returns:
        A dictionary with 'chat_id' and 'text' keys if the update contains a valid message,
        otherwise None.
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
    """
    Starts an echo bot that listens for incoming messages and responds accordingly.
    
    The bot continuously polls for new messages and handles two types of responses:
    - For the '/quote' command, it fetches and sends a daily quote
    - For all other messages, it echoes back the received text
    
    Args:
        None
    
    Returns:
        None
    """
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
    """
    Fetches the daily quote from quotes.toscrape.com.
    
    This method retrieves inspirational content to provide users with engaging and thought-provoking messages as part of the bot's information services.
    
    Args:
        None
    
    Returns:
        str: The formatted quote text with author name, or an error message if the request fails.
        
    Raises:
        None - exceptions are handled internally and returned as error messages.
    """
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
