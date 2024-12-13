from typing import Any as _Any


def all_good(
    start_line: str,
    headers: bytes,
    body: list[bytes]|None
) -> tuple[bool, _Any]:
    result = True
    error = None

    ...

    return (result, error)

def error_handler(
    error: _Any
) -> tuple[int, str, str|None, dict[str, str]|None]:
    status = 500
    reason = "Internal Server Error"
    error_info = None
    err_headers = None

    ...

    return (status, reason, error_info, err_headers)
