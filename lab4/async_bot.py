import asyncio
from typing import Any, Dict, List, Optional
import aiohttp
from lab4.constants import (
    POLLING_TIMEOUT, REQUEST_TIMEOUT, SLEEP_TIME,
    SUCCESS_CODE, ADDITIONAL_WAIT_TIME, HEADLINE_URLS,
    OPENWEATHER_API_KEY, OPENWEATHER_URL, BARS_POLL_INTERVAL
)
from lab4.sync_bot import get_daily_quote, build_api_url
from lab4.bars_watcher import poll_bars_and_notify, PreviousState
from lab4.bars_db import add_subscription

user_states: Dict[int, str] = {}
previous_state: PreviousState = {}


async def send_message(session: aiohttp.ClientSession,
                       chat_id: int, text: str) -> bool:
    """ Асинхронно отправляет сообщение в чат """
    url: str = build_api_url("sendMessage")
    payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with (session.post(url, json=payload, timeout=timeout)
                    as response):
            if response.status != SUCCESS_CODE:
                print(f"HTTP error in send_message: {response.status}")
                return False

            result: Dict[str, Any] = await response.json()

        if result.get("ok"):
            print(f"Message sent to {chat_id}")
            return True

        print(f"Message failed to send to {chat_id}: "
              f"{result.get('description')}")
        return False

    except aiohttp.ClientError as e:
        print(f"Request failed in send_message: {e}")
        return False


async def get_updates(session: aiohttp.ClientSession,
                      offset: Optional[int] = None,
                      timeout: int = POLLING_TIMEOUT) -> Dict[str, Any]:
    """ Асинхронно получает обновления от Telegram Bot API """
    url: str = build_api_url("getUpdates")
    params: Dict[str, Any] = {"timeout": timeout}

    if offset is not None:
        params["offset"] = offset

    try:
        client_timeout = aiohttp.ClientTimeout(
            total=timeout + ADDITIONAL_WAIT_TIME
        )
        async with session.get(url, params=params,
                               timeout=client_timeout) as response:
            if response.status != SUCCESS_CODE:
                print(f"HTTP error in get_updates: {response.status}")
                return {"ok": False, "result": []}

            result: Dict[str, Any] = await response.json()
            return result

    except aiohttp.ClientError as e:
        print(f"Request failed in get_updates: {e}")
        return {"ok": False, "result": []}

    except asyncio.TimeoutError:
        print("Timeout in get_updates, retrying later...")
        return {"ok": False, "result": []}


async def main() -> None:
    """ Главный цикл асинхронного эхобота """
    offset: Optional[int] = None
    print("Async echo bot started")

    async with aiohttp.ClientSession() as session:
        bars_task = asyncio.create_task(
            poll_bars_and_notify(session, send_message,
                                 previous_state, interval=BARS_POLL_INTERVAL)
        )
        try:
            while True:
                result = await get_updates(session, offset=offset)

                if not result.get("ok"):
                    print(f"Error getting updates: {result}")
                    await asyncio.sleep(SLEEP_TIME)
                    continue

                updates: List[Dict[str, Any]] = result.get("result", [])

                for update in updates:
                    message = update.get("message")
                    if message is None:
                        continue

                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text")
                    user_id = message.get("from", {}).get("id")

                    if chat_id is None or text is None or user_id is None:
                        continue

                    print(f"Received from {chat_id}: {text}")

                    state = user_states.get(user_id)

                    if state == "waiting_for_city":
                        city_name = text.strip()
                        weather_text = await\
                            get_weather_for_city(session, city_name)
                        await send_message(session, chat_id, weather_text)
                        del user_states[user_id]

                    elif text == "/weather":
                        user_states[user_id] = "waiting_for_city"
                        await send_message(session, chat_id,
                                           "Введите название города..")

                    elif text == "/quote":
                        # выносим в отдельный поток синхронную функцию
                        quote = await asyncio.to_thread(get_daily_quote)
                        await send_message(session, chat_id, quote)
                    elif text == "/headlines":
                        headlines = await get_headlines(session)
                        await send_message(session, chat_id, headlines)

                    elif text.startswith("/set_isu "):
                        isu = text[len("/set_isu "):].strip()
                        if add_subscription(isu, chat_id):
                            await send_message(session, chat_id,
                                               f"ИСУ {isu} сохранён")
                        else:
                            await send_message(session, chat_id,
                                               "Ошибка при сохранении")

                    elif text.startswith("/set_fio "):
                        fio = text[len("/set_fio "):].strip()
                        if add_subscription(fio.lower(), chat_id):
                            await send_message(session, chat_id,
                                               f"ФИО '{fio}' сохранено")
                        else:
                            await send_message(session, chat_id,
                                               "Ошибка при сохранении")
                    else:
                        await send_message(session, chat_id, text)

                    update_id = update.get("update_id")
                    if update_id is not None:
                        offset = update_id + 1

        except KeyboardInterrupt:
            bars_task.cancel()
            print("\nAsync bot stopped")


async def _fetch_title(session: aiohttp.ClientSession,
                       url: str) -> str:
    """ Загружает страницу, возвращает её title """
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with session.get(url, timeout=timeout) as response:
            if response.status != SUCCESS_CODE:
                return f"{url}: HTTP {response.status}"

            html = await response.text()

    except aiohttp.ClientError as e:
        return f"{url}: request failed ({e})"

    start = html.find("<title>")
    end = html.find("</title>")

    if start == -1 or end == -1:
        return f"{url}: title not found"

    title_text = html[start + len("<title>"): end].strip()
    return f"{url}: {title_text}"


async def get_headlines(session: aiohttp.ClientSession) -> str:
    """ Получает несколько заголовков с разных сайтов конкурентно """
    tasks = [_fetch_title(session, url) for url in HEADLINE_URLS]
    # gather запускает все корутины одновременно и ждёт завершения всех
    results: List[str] = await asyncio.gather(*tasks)

    return "Headlines:\n" + "\n".join(f"- {line}" for line in results)


async def get_weather_for_city(session: aiohttp.ClientSession,
                               city: str) -> str:
    """ Асинхронно получает погоду для города через OpenWeatherMap """
    params = {
        "q": city, "appid": OPENWEATHER_API_KEY,
        "units": "metric", "lang": "ru",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with session.get(OPENWEATHER_URL,
                               params=params,
                               timeout=timeout) as response:
            if response.status != SUCCESS_CODE:
                return (f"Can't recieve weather for city {city}. "
                        f"Code {response.status}")

            data: Dict[str, Any] = await response.json()

    except aiohttp.ClientError as e:
        return f"Can't recieve weather {e}"

    if int(data.get("cod", 0)) != SUCCESS_CODE:
        message = data.get("message", "error")
        return f"City {city}: doesn't exist {message}"

    main = data.get("main", {})
    weather_list = data.get("weather", [])

    temp = main.get("temp")
    feels_like = main.get("feels_like")
    description = weather_list[0].get("description") if weather_list \
        else "No description"

    return (
        f"Температура в {city}:\n"
        f"- {description}\n"
        f"- Температура: {temp}\n"
        f"- Ощущается как: {feels_like}\n"
    )

if __name__ == "__main__":
    asyncio.run(main())
