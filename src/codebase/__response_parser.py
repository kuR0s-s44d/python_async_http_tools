import tempfile as _tmp

from .base_objects import HTTP_Response as _Response

__all__ = ["parse_response"]

def _str_split(target: str, sep: str) -> list[str]:
    return list(map(lambda x: x.strip(), target.split(sep)))

def _header_val_parse(header_key: str, header_value: str) -> dict[str, str]:
    val_type = 0
    result = dict()
    header_value = _str_split(header_value, ";")
    if 1 >= len(header_value):
        header_value = _str_split(header_value[0], ",")
        if 1 >= len(header_value):
            pair = _str_split(header_value[0], "=")
            if 1 == len(pair):
                result[val_type] = pair[0]
                val_type += 1
            else:
                result[pair[0]] = pair[1]
        else:
            for _ in header_value:
                pair = _str_split(_, "=")
                if 1 == len(pair):
                    result[val_type] = pair[0]
                    val_type += 1
                else:
                    result[pair[0]] = pair[1]
    else:
        for _ in header_value:
            pair = _str_split(_, "=")
            if 1 == len(pair):
                result[val_type] = pair[0]
                val_type += 1
            else:
                result[pair[0]] = pair[1]
    return result


def parse_response(
    request_passed: bytes|None,
    status_line: bytes|None,
    response_head: bytes|None,
    response_body: bytes|None,
    encoding: str = "utf_8",
    join_chunked: bool = True
) -> _Response:
    result = _Response(request = request_passed)
    if all(
        map(lambda x: x == None, (status_line, response_head, response_body))
    ):
        pass
    else:
        parsed: dict[str, None|bytes|str|int|dict[str, str]] = {
            "status": None,
            "reason": None,
            "headers": None,
            "body": None,
            "request": request_passed,
            "protocol": None
        }
        if status_line != None:
            status_line = status_line.decode(encoding).strip()
            try:
                protocol, status, reason = status_line.split(
                    sep = " ",
                    maxsplit = 2
                )
            except:
                raise
            else:
                parsed["status"] = int(status)
                parsed["reason"] = reason
                parsed["protocol"] = protocol

        if response_head != None:
            headers = dict()
            response_head = list(
                map(lambda x: x.strip(), response_head.split(b"\r\n"))
            )
            for part in response_head:
                if part != b"":
                    key, val = list(
                        map(
                            lambda x: x.decode(encoding).strip(),
                            part.split(b":", maxsplit=1)
                        )
                    )
                    headers[key] = _header_val_parse(key, val)
            parsed["headers"] = headers

        if response_body != None:
            if join_chunked:
                response_body = b"".join(response_body)
                result_body = b"".join(
                    map(lambda x: x.strip(), response_body.split(b"\r\n"))
                ).decode(encoding)
                parsed["body"] = result_body
            else:
                response_body = response_body[0].decode(encoding)
                parsed["body"] = response_body

        result = _Response(**parsed)

    return result
