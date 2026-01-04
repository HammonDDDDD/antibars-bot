from typing import List, Optional, Dict
import gspread
from google.oauth2.service_account import Credentials

from lab4.constants import GOOGLE_SHEETS_CREDENTIALS_FILE, BarsSheetConfig

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# кэш заголовков: (spreadsheet_id, sheet_name) -> список имён столбцов
_headers_cache: Dict[tuple, List[str]] = {}


def get_sheet_rows(config: BarsSheetConfig) -> Optional[List[List[str]]]:
    """
    Retrieve all rows from a Google Sheets worksheet.
    
    Args:
        config: Configuration object containing spreadsheet ID and worksheet name.
    
    Returns:
        List of lists containing all worksheet values if successful, None if an error occurs.
    
    This method handles authentication and API interactions with Google Sheets to fetch
    complete worksheet data. It returns None on errors to allow calling code to handle
    failures gracefully rather than raising exceptions.
    """
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
    """
    Extract column headers from the first row of a spreadsheet.
    
    This method retrieves column headers to establish a mapping between column indices and their corresponding names, enabling structured access to spreadsheet data. It implements caching to optimize performance by avoiding repeated API calls for the same spreadsheet.
    
    Args:
        config: Configuration object containing spreadsheet_id and sheet_name identifiers.
    
    Returns:
        Dictionary mapping column indices (int) to header names (str).
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
    """
    Searches for the first non-empty value in the first N columns of a row.
    
    This function is used to extract meaningful data from spreadsheet rows by skipping
    empty cells and returning the first available value. It helps identify rows that
    contain actual data entries rather than blank or placeholder values.
    
    Args:
        row: A list of strings representing a row from a spreadsheet or tabular data.
        columns_to_scan: The maximum number of columns to check from the beginning of the row.
                        Defaults to 50 columns.
    
    Returns:
        The first non-empty string value found in the specified columns, or None if 
        all scanned columns are empty.
    """
    for col_idx in range(min(columns_to_scan, len(row))):
        val = row[col_idx].strip()
        if val:
            return val
    return None
