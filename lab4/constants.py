from typing import Final, List, TypedDict

# ссылка на сайт с цитатами
QUOTES_URL: Final[str] = "https://quotes.toscrape.com/"

# токен для моего бота. не смотреть!!
BOT_TOKEN = "8530256771:AAFgOsnFR3sAq-SUQ1vVcbnf2zt0kLg_Cf4"

# базовая url для api
API_BASE_URL = "https://api.telegram.org/bot"

# timeout для polling (в секундах)
POLLING_TIMEOUT = 30

# timeout для request (в секундах)
REQUEST_TIMEOUT = 10

# время ожидания
SLEEP_TIME = 1

ADDITIONAL_WAIT_TIME = 5

SUCCESS_CODE = 200

HEADLINE_URLS: Final[List[str]] = [
    "https://example.com/",
    "https://news.ycombinator.com/",
    "https://habr.com/ru/",
]
OPENWEATHER_API_KEY: Final[str] = "7be346fb6d6bc09104d5fa3ddcbb69e2"

OPENWEATHER_URL: Final[str] = "https://api.openweathermap.org/data/2.5/weather"


GOOGLE_SHEETS_CREDENTIALS_FILE: Final[str] = "antibars-credentials.json"


class BarsSheetConfig(TypedDict):
    table_id: str  # Название таблицы
    spreadsheet_id: str  # Google Sheets ID
    sheet_name: str  # имя листа
    header_rows: int  # сколько верхних строк — заголовок
    columns_to_scan: int  # в скольких первых столбцах искать ИСУ/ФИО


BARS_SHEETS: Final[List[BarsSheetConfig]] = [
    {
        "spreadsheet_id": "1PTcXL_lbTWRSjAZNERmJexXVhD7JVPFOrRa0-dW1jtA",
        "sheet_name": "Общая",
        "header_rows": 1,
        "table_id": "Матан J3115",
        "columns_to_scan": 50,
    },
    {
        "spreadsheet_id": "1Fha4ldCfLlnwNlUCuQb-gFq8-nn6F9GDq7APhJf10Gk",
        "sheet_name": "Общая таблица",
        "header_rows": 1,
        "table_id": "АВС",
        "columns_to_scan": 50,
    },
    {
        "spreadsheet_id": "1KUH81HklgwwEv_mxMPxJFBGKs0lsiXKc7skDx-YS_8M",
        "sheet_name": "Лабораторные",
        "header_rows": 1,
        "table_id": "Python",
        "columns_to_scan": 50,
    },
    {
        "spreadsheet_id": "1n_SvWtdtmraxkdv8xP4nLQKbGhX7Jzv-QD0m2ldR1CY",
        "sheet_name": "Лабораторные",
        "header_rows": 1,
        "table_id": "Алгосы",
        "columns_to_scan": 50,
    },
    {
        "spreadsheet_id": "1wCloJTkipOac4PqvBbSEFChhWEZKdJliY_U1jvficRI",
        "sheet_name": "J3115",
        "header_rows": 1,
        "table_id": "Алгебра J3115",
        "columns_to_scan": 50,
    },
    {
        "spreadsheet_id": "1eO63Eb0gRw9Rcc8yYMjK4EHu_x5d0Hh-Jb9zDDUo-U8",
        "sheet_name": "Лист1",
        "header_rows": 1,
        "table_id": "Тестовая",
        "columns_to_scan": 50,
    }
]

DATABASE_FILE: Final[str] = "bars_db.sqlite"

BARS_POLL_INTERVAL: Final[int] = 30
