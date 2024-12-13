from asyncio import StreamReader as _StreamReader
import tempfile as _tmp

__all__ = ["listen_response"]

response_ends: list[bytes|bool] = [
    b"</html>\r\n",
    b"\r\n",
    b"0\r\n",
    b"",
    False
]

# full_response_ends: list[bytes|bool] = [
#     b"</html>\r\n",
#     b"\r\n",
#     b"0\r\n",
#     b"",
#     False
# ]

_bodyless_methods: list[bytes] = [
    b"HEAD",
    b"CONNECT"
]


async def _read_exactly(
    reader: _StreamReader,
    size: int
) -> bytes:
    response_body = None
    try:
        line = await reader.readexactly(int(size))
    except IncompleteReadError as err:
        line = err.partial \
            + b"------#=Incomplete_stream_read=#--\r\n"
    finally:
        response_body = line
    return response_body


async def _chunked_reader(
    reader: _StreamReader,
    join_chunked: bool = True,
    encoding: str = "utf_8"
) -> bytes:
    result_body = []
    mark = True
    not_end = True
    if join_chunked:
        while not_end:
            if mark:
                line = await reader.readline()
                line = line.strip()
                size = int(line, 16)
                if 0 == size:
                    not_end = False
                mark = False
            else:
                line = await _read_exactly(reader, size+2)
                result_body.append(line)
                mark = True
    else:
        with _tmp.NamedTemporaryFile(
            mode="w+b",
            delete = join_chunked
        ) as resp_file:
            while not_end:
                if mark:
                    line = await reader.readline()
                    line = line.strip()
                    size = int(line, 16)
                    if 0 == size:
                        not_end = False
                    mark = False
                else:
                    line = await _read_exactly(reader, size+2)
                    resp_file.write(line)
                    mark = True
            result_body.append(
                b"You may find the response body at "
                + f"{resp_file.name}".encode(encoding)
            )
    return result_body


async def listen_response(
    reader: _StreamReader,
    wait_resp: bool = True,
    encoding: str = "utf_8",
    *args, **kwargs
) -> tuple[bytes|None, ...]:
    join_chunks = True
    if None != kwargs.get("join_chunks"):
        join_chunks = kwargs.get("join_chunks")

    status_line = None
    response_head = None
    response_body = None
    if wait_resp:
        content_length = False
        timeout = None  #TODO: decide whether keep or not
        chunked = False
        listen = True

        status_line = await reader.readline()
        bodyless = any(
            map(
                lambda x: x in status_line, _bodyless_methods
            )
        )
        

        # Listen to headers
        while listen:
            line = await reader.readline()
            if line in response_ends:
                listen = False
            if response_head != None:
                response_head += line
            else:
                response_head = line

            if b"Content-Length" in line:
                decoded_line = line.decode(encoding).strip()
                decoded_line = list(
                    map(lambda x: x.strip(), decoded_line.split(":"))
                )
                content_length = decoded_line[-1]
            if b"Transfer-Encoding" in line:
                decoded_line = line.decode(encoding).strip()
                decoded_line = list(
                    map(lambda x: x.strip(), decoded_line.split(":"))
                )
                chunked = decoded_line[-1]

        listen = True
        if 0 == int(content_length):
            listen = False
        #listen to body
        if bodyless:
            pass
        else:
            if content_length:
                response_body = [
                    await _read_exactly(reader, int(content_length))
                ]
            elif chunked:
                response_body = await _chunked_reader(
                    reader,
                    join_chunked = join_chunks,
                    encoding = encoding
                )
            else:
                response_body = []
                while listen:
                    line = await reader.readline()
                    if line in response_ends:
                        listen = False
                    response_body.append(line)
    
    return (status_line, response_head, response_body)
