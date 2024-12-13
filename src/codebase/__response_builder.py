from .__request_builder import _header_prep


def build_response_meta(
    protocol_passed: str,
    protocol_version: str,
    status_passed: str,
    reason_passed: str,
    response_headers_passed: dict[str, str],
    body_passed: str = None,
    *args, **kwargs
) -> str:
    response_headers = {
        "Content-Length": 0
    }
    if None != body_passed:
        response_headers["Content-Length"] = len(body_passed.encode())
    if None != response_headers_passed:
        for key, val in response_headers_passed.items():
            response_headers[key] = val
    response_meta = "".join(
        (
            f"{protocol_passed}/{protocol_version} "\
            f"{status_passed} {reason_passed}\r\n",
            _header_prep(response_headers)
        )
    )
    if None != body_passed:
        response_meta += f"\r\n{body_passed}"
    return response_meta
