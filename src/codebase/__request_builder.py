from datetime import datetime as _dt
from hashlib import sha256 as _sha256
import json
import mimetypes as mime
# import platform  # TODO: add functionality
from typing import (
    Any as _Any,
    BinaryIO as _BinaryIO,
    TextIO as _TextIO
)

__all__ = ["prepare_request"]


def path_splitter() -> str:
    #TODO: Complete for all major pltforms
    #TODO: Replace placeholder
    platform_used = "Linux" # platform_used = platform.platform()
    splitters = {
        "Linux": "/"
    }
    return splitters[platform_used]

def _get_boundary() -> str:
    return str(
        _sha256(
            str(_dt.timestamp(_dt.now())).encode("utf_8")
        ).hexdigest()
    )

def _data_formater(data: dict[str, _Any], boundary: str) -> str:
    result = ""
    for key, val in data.items():
        result += f"--------{boundary}\r\n"
        result += f"Content-Disposition: form-data; name={key}\r\n"
        result += "\r\n"
        result += f"{val}\r\n"
    return result
        

def _data_handler(
    data: dict[str, _Any],
    form: bool,
    boundary: str,
    encoding: str = "utf_8"
) -> bytes|None:
    result = None
    temp = ""
    if form:
        temp = f"{_data_formater(data, boundary)}"
    else:
        temp = f"{json.dumps(data, separators=(',',':'))}"

    result = temp.encode(encoding)
    
    return result

def _file_reader(bin_file: _BinaryIO, chunk_size: int) -> bytes:
    result = b""
    repeat = True
    while repeat:
        data_chunk = bin_file.read(chunk_size)
        if data_chunk:
            result += data_chunk
        else:
            repeat = False
    return result
        

def _file_handler(
    file_input: dict[str, str],
    boundary: str,
    file_place: int,
    encoding: str = "utf_8"
) -> tuple[bytes, int]:
    """
    {
        "file": "/path/to/file",
        "type": "the_type_of_file",
        "field": "name_of_field"
    }
    """
    buffer_size = 8192
    file_path = file_input.get("file")
    file_name = file_path.split(path_splitter())[-1]

    content_type, content_encoding = None, None
    if None != file_input.get("type"):
        content_type = file_input.get("type")
    else:
        content_type, content_encoding = mime.guess_type(file_path)

    if content_type != None:
        if content_encoding != None:
            file_type_header = f"Content-Type: {content_type};"\
                f" encoding={content_encoding}\r\n"
        else:
            file_type_header = f"Content-Type: {content_type}\r\n"
    else:
        file_type_header = None

    if None != file_input.get("field"):
        field_name = file_input.get("field")
    else:
        field_name = f"field{file_place}"
        file_place += 1

    packed_file = f"--------{boundary}\r\n"
    packed_file += f"Content-Disposition: form-data; name={field_name};"\
        f" filename={file_name}\r\n"
    if None != file_type_header:
        packed_file += file_type_header
    packed_file += "\r\n"
    packed_file = packed_file.encode(encoding)
    
    with open(
        file_path,
        "rb",
        buffering = buffer_size
    ) as fbin:
        packed_file +=  _file_reader(fbin, buffer_size)

    return packed_file, file_place

def _bin_file_handler(
    file_input: dict[str, str|_BinaryIO],
    boundary: str,
    file_place: int,
    encoding: str = "utf_8"
) -> tuple[bytes, int]:
    """
    {
        "file": binary_file_representation,
        "file_name": "file_name",
        "type": "the_type_of_file",
        "field": "name_of_field"
    }
    """
    buffer_size = 8192
    fbin = file_input.get("file")
    file_name = file_input.get("file_name")

    content_type, content_encoding = None, None
    if None != file_input.get("type"):
        content_type = file_input.get("type")
    else:
        content_type, content_encoding = mime.guess_type(file_name)

    if content_type != None:
        if content_encoding != None:
            file_type_header = f"Content-Type: {content_type};"\
                f" encoding={content_encoding}\r\n"
        else:
            file_type_header = f"Content-Type: {content_type}\r\n"
    else:
        file_type_header = None

    if None != file_input.get("field"):
        field_name = file_input.get("field")
    else:
        field_name = f"field{file_place}"
        file_place += 1

    packed_file = f"--------{boundary}\r\n"
    packed_file += f"Content-Disposition: form-data; name={field_name};"\
        f" filename={fie_name}\r\n"
    if None != file_type_header:
        packed_file += file_type_header
    packed_file += "\r\n"
    packed_file = packed_file.encode(encoding)

    packed_file +=  _file_reader(fbin, buffer_size)

    return packed_file, file_place


def _body_prep(
    body: str = None,
    data: dict[str, _Any] = None,
    files: list[dict[str, str]] = None,
    bin_files: list[dict[str, str|_BinaryIO]] = None,
    boundary: str = None,
    encoding: str = "utf_8",
    chunk: bool = False,
    form: bool = False,
    *args, **kwargs
) -> str|None:
    prepared_body = None
    additional_headers = None
    place = 1
    empty = all(map(lambda x: x == None, (data, files, bin_files)))
    no_files = all(map(lambda x: x == None, (files, bin_files)))
    
    if None != body:
        prepared_body = f"{body}\r\n\r\n".encode(encoding)
    elif not empty and no_files:
        prepared_body = _data_handler(
            data,
            form,
            boundary,
            encoding
        )
        if None != additional_headers:
            additional_headers["Content-Length"] = len(prepared_body)
        else:
            additional_headers = {"Content-Length": len(prepared_body)}
    elif not empty and not no_files:
        
        prepared_body = b""
        additional_headers = {
            "Content-Type": f"multipart/form-data;boundary={boundary}"
        }
        
        if None != data:
            cooked_body = _data_handler(
                data,
                form,
                boundary,
                encoding
            )
            prepared_body += cooked_body

        if None != files:
            for fin in files:
                cooked_file, place = _file_handler(
                    fin,
                    boundary,
                    place,
                    encoding
                )
                prepared_body += cooked_file

        if None != bin_files:
            for fin in bin_files:
                cooked_bin_file, place = _bin_file_handler(
                    fin,
                    boundary,
                    place,
                    encoding
                )
                prepared_body += cooked_bin_file

        prepared_body += f"--------{boundary}--\r\n\r\n".encode(encoding)
    return prepared_body, additional_headers

def _header_prep(headers_passed: dict[str, str]) -> str:
    headers_packed = None
    if None != headers_passed:
        headers_packed = ""
        for key, val in headers_passed.items():
            headers_packed += f"{key}: {val}\r\n"
    return headers_packed

def prepare_request(
    method_passed: str = "GET",
    host_passed: str = None,
    url_path_passed: str = "/",
    port_passed: int = 443,
    headers_passed: dict[str, str] = None,
    url_query_passed: str = None,
    body_passed: str = None,
    data_passed: dict[str, _Any] = None,
    files_passed: list[dict[str, str]] = None,
    bin_files_passed: list[dict[str, str|_BinaryIO]] = None,
    boundary_str_passed: str = None,
    encoding_passed: str = "utf_8",
    *args, **kwargs
) -> bytes|None:
    result = None

    if body_passed != None and data_passed != None:
        raise RuntimeError(
            "\n\n  You should not use 'body' and 'data' parameters at the "\
            "same time.\n\n  Choose 'body' for:\n  - direct 'body'-string "\
            "sending\n\n  Choose 'data' dict for:\n  - form-data\n  - JSON"\
            " data\n  - additional details when uploading files."
        )

    chunked = False
    form_data = False
    proto = "HTTP"
    proto_ver = "1.1"
    if kwargs.get("proto"):
        proto = kwargs.get("proto")
    if kwargs.get("proto_ver"):
        proto_ver = kwargs.get("proto_ver")

    if None == boundary_str_passed:
        boundary_str_passed = _get_boundary()

    url_path = url_path_passed
    if None != url_query_passed:
        url_path += f"?{url_query_passed}"

    request_line = f"{method_passed} {url_path} {proto}/{proto_ver}\r\n"

    if None == headers_passed:
        headers_passed = {"Host": None}
    if None == headers_passed.get("Host"):
        if kwargs.get("use_port"):
            headers_passed["Host"] = f"{host_passed}:{port_passed}"
        else:
            headers_passed["Host"] = f"{host_passed}"

    if "chunked" == headers_passed.get("Transfer-Encoding"):
        chunked = True
    if None != headers_passed.get("Content-Type"):
        if "multipart/form-data" in headers_passed.get("Content-Type"):
            form_data = True
    elif any(
        (
            files_passed != None,
            bin_files_passed != None
        )
    ):
        form_data = True

    # preparing the request body
    prepared_body, body_headers = _body_prep(
        body = body_passed,
        data = data_passed,
        files = files_passed,
        bin_files = bin_files_passed,
        boundary = boundary_str_passed,
        chunk = chunked,
        form = form_data,
        encoding = encoding_passed
    )
    if None != body_headers:
        for key, val in body_headers.items():
            headers_passed[key] = val

    headers_packed = _header_prep(headers_passed)

    meta = request_line
    if None != headers_packed:
        meta += headers_packed
    meta += "\r\n"
    meta = meta.encode(encoding_passed)

    if None != prepared_body:
        result = meta + prepared_body
    else:
        result = meta
    
    return result
