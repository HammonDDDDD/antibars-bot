from typing import List, Optional, Dict
import gspread
from google.oauth2.service_account import Credentials

from lab4.constants import GOOGLE_SHEETS_CREDENTIALS_FILE, BarsSheetConfig

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# кэш заголовков: (spreadsheet_id, sheet_name) -> список имён столбцов
_headers_cache: Dict[tuple, List[str]] = {}


def get_sheet_rows(config: BarsSheetConfig) -> Optional[List[List[str]]]:
    """Вернуть все строки листа или None при ошибке."""
    try:
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS_FILE,
            scopes=_SCOPES,
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(config["spreadsheet_id"])
        sheet = spreadsheet.worksheet(config["sheet_name"])

        return sheet.get_all_values()

    except Exception as e:
        print(f"Error reading sheet {config['table_id']}: {e}")
        return None


def get_column_headers(config: BarsSheetConfig) -> Dict[int, str]:
    """ Получить заголовки столбцов из первой строки таблицы.
    :returns: {col_idx: col_name}.
    """
    cache_key = (config["spreadsheet_id"], config["sheet_name"])

    if cache_key in _headers_cache:
        headers = _headers_cache[cache_key]
    else:
        rows = get_sheet_rows(config)
        if rows is None or len(rows) == 0:
            return {}

        headers = rows[0]
        _headers_cache[cache_key] = headers

    return {idx: name for idx, name in enumerate(headers)}


def find_identifier_in_row(row: List[str],
                           columns_to_scan: int = 50) -> Optional[str]:
    """ Ищет ИСУ или ФИО в первых N столбцах строки.
    :returns: первое непустое значение либо None.
    """
    for col_idx in range(min(columns_to_scan, len(row))):
        val = row[col_idx].strip()
        if val:
            return val
    return None
