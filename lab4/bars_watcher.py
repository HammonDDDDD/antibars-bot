import asyncio
from typing import Dict, List, Tuple
import aiohttp

from lab4.constants import (BARS_SHEETS, BarsSheetConfig,
                            BARS_POLL_INTERVAL, ADDITIONAL_WAIT_TIME)
from lab4.google_sheets_client import (
    get_sheet_rows,
    find_identifier_in_row,
    get_column_headers,
)
from lab4.bars_db import (
    init_db,
    get_all_subscriptions,
    log_change,
)

# ключ (table_id, row_index)
# значение {col_idx: cell_value} : состояние строки по столбцам
PreviousState = Dict[Tuple[str, int], Dict[int, str]]


async def poll_bars_and_notify(
        session: aiohttp.ClientSession,
        send_func,
        state: PreviousState,
        interval: int = BARS_POLL_INTERVAL) -> None:
    """
    Periodically monitors configured data sources for changes and sends notifications when updates are detected.
    
    This method continuously polls multiple data tables to detect modifications compared to the previous state. It maintains real-time synchronization between the data sources and notification system to ensure subscribers receive timely updates.
    
    Args:
        session: HTTP client session for making API requests
        send_func: Function responsible for delivering notifications
        state: Object storing previous state data for change detection
        interval: Polling interval in seconds (default: BARS_POLL_INTERVAL)
    
    Returns:
        None
    """
    try:
        init_db()
        print("БД инициализирована")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
        return

    print(f"BARS watcher запущен (интервал: {interval}s)")

    while True:
        try:
            subscriptions = get_all_subscriptions()

            # создание тасков до их ожидания
            tasks = [
                _check_sheet(cfg, session, send_func, subscriptions, state)
                for cfg in BARS_SHEETS]

            await asyncio.gather(*tasks, return_exceptions=True)

            await asyncio.sleep(interval)

        except Exception as e:
            print(f"Ошибка в poll_bars_and_notify: {e}")
            await asyncio.sleep(ADDITIONAL_WAIT_TIME)


async def _check_sheet(
        cfg: BarsSheetConfig,
        session: aiohttp.ClientSession,
        send_func,
        subscriptions: Dict[str, int],
        state: PreviousState) -> None:
    """
    Check a single spreadsheet for changes and notify subscribed users.
    
    This method monitors a specific Google Sheet for modifications in tracked rows,
    comparing current values with previous state to detect changes that require
    notification.
    
    Args:
        cfg: Configuration object containing sheet settings like table ID and columns to scan
        session: HTTP client session for making API requests
        send_func: Callback function for sending notifications
        subscriptions: Dictionary mapping identifiers to chat IDs for notification routing
        state: Previous state storage for change detection comparison
    
    Returns:
        None
    """
    rows = await asyncio.to_thread(get_sheet_rows, cfg)
    if rows is None:
        print(f"Не удалось прочитать {cfg['table_id']}")
        return

    start_row = cfg["header_rows"]
    columns_to_scan = cfg["columns_to_scan"]
    column_headers = await asyncio.to_thread(get_column_headers, cfg)

    for i, row in enumerate(rows[start_row:], start=start_row):
        # поиск ису/фио в первых N столбцах
        identifier = find_identifier_in_row(row, columns_to_scan)
        if not identifier:
            continue

        chat_id = subscriptions.get(identifier)
        if chat_id is None:
            chat_id = subscriptions.get(identifier.lower())
        if chat_id is None:
            continue

        key = (cfg["table_id"], i)
        old_state = state.get(key)

        if old_state is None:
            state[key] = _row_to_dict(row)
            continue

        # проверка изменений
        await _detect_and_notify(cfg,
                                 session,
                                 send_func,
                                 chat_id,
                                 identifier,
                                 row,
                                 old_state,
                                 column_headers)
        state[key] = _row_to_dict(row)


def _row_to_dict(row: List[str]) -> Dict[int, str]:
    """
    Convert a list into a dictionary mapping column indices to values.
    
    Args:
        row: A list of string values representing a row of data.
    
    Returns:
        A dictionary where keys are column indices (integers) and values are the corresponding elements from the input list.
    
    Why:
        This conversion enables efficient column-based access to row data by index, which is useful for spreadsheet operations where specific columns need to be referenced or processed individually.
    """
    return {idx: val for idx, val in enumerate(row)}


async def _detect_and_notify(
        cfg: BarsSheetConfig,
        session: aiohttp.ClientSession,
        send_func,
        chat_id: int,
        identifier: str,
        new_row: List[str],
        old_state: Dict[int, str],
        column_headers: Dict[int, str]) -> None:
    """
    Detects changes in a spreadsheet row and sends notifications about updates.
    
    Compares the current row state with the previous state to identify modified values,
    logs detected changes, and sends a formatted notification message if any changes are found.
    
    Args:
        cfg: Configuration object containing table settings
        session: HTTP client session for making requests
        send_func: Function responsible for sending notifications
        chat_id: Telegram chat identifier for the recipient
        identifier: Unique identifier for the row being monitored
        new_row: Current row data as a list of string values
        old_state: Previous row state as a dictionary mapping column indices to values
        column_headers: Dictionary mapping column indices to their header names
    
    Returns:
        None
    """
    new_state = _row_to_dict(new_row)

    changes: List[str] = []

    for col_idx, new_val in new_state.items():
        old_val = old_state.get(col_idx, "")

        if new_val != old_val:

            column_name = column_headers.get(col_idx, f"столбец {col_idx + 1}")

            changes.append(
                f"{column_name}: было '{old_val}', стало '{new_val}'"
            )
            log_change(cfg["table_id"], identifier,
                       column_name, old_val, new_val)

    if not changes:
        return

    text = (
        f"📊 {cfg['table_id']}\n\n"
        f"Обновлены баллы ({identifier}):\n"
        + "\n".join(f"* {c}" for c in changes)
    )

    await send_func(session, chat_id, text)
