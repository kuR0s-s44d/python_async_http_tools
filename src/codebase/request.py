from asyncio import (
    StreamReader as _StreamReader,
    StreamWriter as _StreamWriter
)
from typing import (
    Any as _Any,
    BinaryIO as _BinaryIO
)
from urllib.parse import urlencode as _urlencode

from .__request_builder import prepare_request as _prepare_request
from .__response_listener import listen_response as _listen_response
from .__response_parser import parse_response as _parse_response
from .base_objects import (
    Connection as _Connection,
    HTTP_Response as _HTTP_Response
)


class request:
    """
    The base class that allows to perform asyncronous HTTP/HTTPS requests.

    This class supports using simple one-time proxy redirection (only through
    one proxy node).
    For multi-node proxy (proxy-chaining), please, consider outside proxy
    management system. However, proxy can be changed at connection/stream
    reader + strem writer pair.
    """
    @staticmethod
    async def call(
        method: str = "GET",
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The base method to perform the HTTP/HTTPS request. Requires the
        specification of all request details in order to perform the request.

        This method can be used both for requests and as a base for other types
        of requests ("PUT", "POST", etc.)

        Parameters:
        - method (str)\n\t\t: the http/https method for the request performed
        \t  ("GET","POST", etc). Defaults to "GET" value.
        
        - host (str)\n\t\t: the target host of the request
        
        - url_path (str)\n\t\t: the URL-adress under the target host that is
        \t  targeted
        
        - port (int)\n\t\t: the targeted port of the target host. The value
        \t  depends on the type of request (HTTP/HTTPS) is senf. Defaults to
        \t  HTTPS port = 443 (in case the method is used outside of pre-
        \t  established connection either through 'connection' or 'st_reader'/
        \t  'st_writer' pair the 'ssl' parameter should be specified as 'True')
        
        - headers (dict[str, str])\n\t\t: the request headers that would be
        \t  used for request. The passed argument should be in form of a
        \t  dictionary with string key-value pairs
        
        - url_query (str)\n\t\t: the pre-formated string of query parameters
        \t  passed to request. Can be used in conjunction with the
        \t  '.url_query_format()' method for simple and fast url query building
        
        - body (str)\n\t\t: the body of the request to be sent in form of a
        \t  string. The body does not support chunk-loading and should be
        \t  loaded all at once. You can still preformat the body to be a
        \t  single string with chunk dividors included.

        \t  This parameter should not be use together with 'data' parameter -
        \t  this would cause a 'RuntimeError' exception as both parameters are
        \t  used to build one request body but 'body' accepts the ready-made
        \t  body and 'data' is used to build the body from '0'.

        \t  In case you need to pass parameters through request (either in from
        \t  of the JSON or multipart/form-data) - 'data' parameter should be
        \t  used.
        \t  In case you desire to send the ready made version of the body -
        \t  use 'body'.
        
        - data (dict[str, Any])\n\t\t: the data to be send through the request.
        \t  This paraeter should be used in case some request parameters should
        \t  be specified (for multipart/from-data of JSON).
        \t
        \t  This parameter should not be use together with 'body' parameter -
        \t  this would cause a 'RuntimeError' exception as both parameters are
        \t  used to build one request body but 'body' accepts the ready-made
        \t  body and 'data' is used to build the body from '0'.
        
        \t  In case you need to pass parameters through request (either in from
        \t  of the JSON or multipart/form-data) - 'data' parameter should be
        \t  used.
        \t  In case you desire to send the ready made version of the body -
        \t  use 'body'.
        
        - files (list[dict[str, str]])\n\t\t: the list of dictionaries that
        \t  contain the following information about files in the specified from:
        
        \t    {
        \t      "file": "/path/to/file",
        \t      "type": "the_type_of_file",
        \t      "field": "name_of_field"
        \t    }
        
        \t  Fields 'file' and 'field' are required fields for correct work of
        \t  the request and must always be specified.

        \t  This parameter is used for already-existing files on the pc/server.
        
        - bin_files (list[dict[str, str|BinaryIO]])\n\t\t: the list of 'opened'
        \t  files with associated information in the specified from:
        
        \t    {
        \t        "file": binary_file_representation,
        \t        "file_name": "file_name",
        \t        "type": "the_type_of_file",
        \t        "field": "name_of_field"
        \t    }
        
        \t  Fields 'file', 'file_name' and 'field' are required fields and must
        \t  always be specified.

        \t  The 'file' field contains the instance of the opened file in 'rb'
        \t  mode. This method can be used for passing temporary files, created
        \t  at runtime that should not be saved on the pc/server.
        
        - boundary (str)\n\t\t: the boundary that can be specified for POST
        \t  request that uploads files through the request of in case
        \t  multipart/form-data is used to perform "PUT"/"POST"/etc requests.
        
        - encoding (str)\n\t\t: the encoding used to encode the request into
        \t  byte form in order. Defaults to 'utf_8'.
        
        - proxy_data (dict[str, str|int])\n\t\t: the data used to connect to
        \t  the proxy server in case the predefined conneciton (either through
        \t  'connection' or 'st_reader'/'st_writer' pair) was not used for the
        \t  request.

        \t The argument should be a dictionary with the following keys:

        \t    {
        \t        "http": "proxy_ip:proxy_http_port",
        \t        "https": "proxy_ip:proxy_https_port",
        \t        "prox_type": <should be either 'http' or 'https'>, 
        \t        "username": "the_type_of_file",       # Optional
        \t        "password": "name_of_field"           # Optional
        \t    }
        
        - ssl (bool)\n\t\t: the parameter specifing the usage of SSL connection
        \t  type. Value 'True' is required to perform HTTPS requests.
        
        - connection (base_objects.Connection)\n\t\t: The preestablished
        \t  connection that would be used fro transporting requests from
        \t  client app to target server.

        \t  More information in the source file in './base_objects.py'
        
        - st_reader (asyncio.StreamReader)\n\t\t: asyncio StreamReader instance.
        \t  More infromation in the official documentation:
        \t  https://docs.python.org/3/library/asyncio-stream.html#asyncio.\
StreamReader
        
        - st_writer (asyncio.StreamWriter)\n\t\t: asyncio StreamWriter instance.
        \t  More information in the official documentation:
        \t  https://docs.python.org/3/library/asyncio-stream.html#asyncio.StreamWriter


        Optional parameters:
        - wait_resp (bool)
        - join_chunks (bool)
        - loop (asyncio.BaseEventLoop)
        - limit (int)
        """

        half_stream = any((
            all((None == st_reader, None != st_writer)),
            all((None != st_reader, None == st_writer))
        ))

        stream_and_connection_passed = all((
            all((None != st_reader, None != st_writer)),
            None != connection
        ))

        no_prior_connection = all(
            (
                None == connection,
                None == st_reader,
                None == st_writer
            )
        )

        if half_stream:
            raise RuntimeError(
                "Both 'st_reader' and 'st_writer' need to be either specified"\
                " or 'None'"
            )

        if stream_and_connection_passed:
            raise RuntimeError(
                "Can not use connection and stream ('st_reader' + "\
                "'st_writer') at the same time. Choose only one option."
            )

        if None != kwargs.get("wait_resp"):
            wait_response = kwargs.get("wait_resp")
        else:
            wait_response = True

        if None != kwargs.get("join_chunks"):
            join_chunks = kwargs.get("join_chunks")
        else:
            join_chunks = True

        response = _HTTP_Response()
        cooked_request = _prepare_request(
            method_passed = method,
            host_passed = host,
            url_path_passed = url_path,
            port_passed = port,
            headers_passed = headers,
            url_query_passed = url_query,
            body_passed = body,
            data_passed = data,
            files_passed = files,
            bin_files_passed = bin_files,
            boundary_str_passed = boundary,
            encoding_passed = encoding,
            *args, **kwargs
        )

        if no_prior_connection:
            if None != kwargs.get("loop"):
                conn_loop = kwargs.get("loop")
            else:
                conn_loop = None
            if None != kwargs.get("limit"):
                conn_limit = kwargs.get("limit")
            else:
                conn_limit = None

            async with _Connection(
                host = host,
                port = port,
                ssl = ssl,
                proxy = proxy_data,
                limit = conn_limit,
                loop = conn_loop
            ) as aconn:
                aconn.writer.write(cooked_request)
                await aconn.writer.drain()
                response = _parse_response(
                    cooked_request,
                    *await _listen_response(
                        reader = aconn.reader,
                        wait_resp = wait_response,
                        encoding = encoding,
                        join_chunks = join_chunks
                    ),
                    encoding = encoding,
                    join_chunked = join_chunks
                )
        elif None != connection:
            connection.writer.write(cooked_request)
            await connection.writer.drain()
            response = _parse_response(
                cooked_request,
                *await _listen_response(
                    reader = connection.reader,
                    wait_resp = wait_response,
                    encoding = encoding,
                    join_chunks = join_chunks
                ),
                encoding = encoding,
                join_chunked = join_chunks
            )
        elif None != st_reader and None != st_writer:
            st_writer.write(cooked_request)
            await st_writer.drain()
            response = _parse_response(
                cooked_request,
                *await _listen_response(
                    reader = st_reader,
                    wait_resp = wait_response,
                    encoding = encoding,
                    join_chunks = join_chunks
                ),
                encoding = encoding,
                join_chunked = join_chunks
            )
        return response

    @staticmethod
    async def get(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'GET' requests
        """
        return await request.call(
            method = "GET",
            host = host,
            url_path = url_path,
            port = port,
            headers = headers,
            url_query = url_query,
            body = body,
            data = data,
            files = files,
            bin_files = bin_files,
            boundary = boundary,
            encoding = encoding,
            proxy_data = proxy_data,
            ssl = ssl,
            connection = connection,
            st_reader = st_reader,
            st_writer = st_writer,
            *args, **kwargs
        )

    @staticmethod
    async def post(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'POST' requests
        """
        return await request.call(
            method = "POST",
            host = host,
            url_path = url_path,
            port = port,
            headers = headers,
            url_query = url_query,
            body = body,
            data = data,
            files = files,
            bin_files = bin_files,
            boundary = boundary,
            encoding = encoding,
            proxy_data = proxy_data,
            ssl = ssl,
            connection = connection,
            st_reader = st_reader,
            st_writer = st_writer,
            *args, **kwargs
        )

    @staticmethod
    async def put(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'PUT' requests
        """
        return await request.call(
            method = "PUT",
            host = host,
            url_path = url_path,
            port = port,
            headers = headers,
            url_query = url_query,
            body = body,
            data = data,
            files = files,
            bin_files = bin_files,
            boundary = boundary,
            encoding = encoding,
            proxy_data = proxy_data,
            ssl = ssl,
            connection = connection,
            st_reader = st_reader,
            st_writer = st_writer,
            *args, **kwargs
        )

    @staticmethod
    async def delete(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'DELETE' requests
        """
        return await request.call(
            method = "DELETE",
            host = host,
            url_path = url_path,
            port = port,
            headers = headers,
            url_query = url_query,
            body = body,
            data = data,
            files = files,
            bin_files = bin_files,
            boundary = boundary,
            encoding = encoding,
            proxy_data = proxy_data,
            ssl = ssl,
            connection = connection,
            st_reader = st_reader,
            st_writer = st_writer,
            *args, **kwargs
        )

    @staticmethod
    async def connect(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'CONNECT' requests
        """
        return await request.call(
            method = "CONNECT",
            host = host,
            url_path = url_path,
            port = port,
            headers = headers,
            url_query = url_query,
            body = body,
            data = data,
            files = files,
            bin_files = bin_files,
            boundary = boundary,
            encoding = encoding,
            proxy_data = proxy_data,
            ssl = ssl,
            connection = connection,
            st_reader = st_reader,
            st_writer = st_writer,
            *args, **kwargs
        )

    @staticmethod
    async def head(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'HEAD' requests
        """
        return await request.call(
            method = "HEAD",
            host = host,
            url_path = url_path,
            port = port,
            headers = headers,
            url_query = url_query,
            body = body,
            data = data,
            files = files,
            bin_files = bin_files,
            boundary = boundary,
            encoding = encoding,
            proxy_data = proxy_data,
            ssl = ssl,
            connection = connection,
            st_reader = st_reader,
            st_writer = st_writer,
            *args, **kwargs
        )

    @staticmethod
    async def patch(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'PATCH' requests.
        This method currently is not implemented.
        """
        raise NotImplementedError(
            "The 'patch' method feature is not implemented yet."
        )
        # return await request.call(
        #     method = "PATCH",
        #     host = host,
        #     url_path = url_path,
        #     port = port,
        #     headers = headers,
        #     url_query = url_query,
        #     body = body,
        #     data = data,
        #     files = files,
        #     bin_files = bin_files,
        #     boundary = boundary,
        #     encoding = encoding,
        #     proxy_data = proxy_data,
        #     ssl = ssl,
        #     connection = connection,
        #     st_reader = st_reader,
        #     st_writer = st_writer,
        #     *args, **kwargs
        # )

    @staticmethod
    async def trace(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'TRACE' requests.
        This method currently is not implemented.
        """
        raise NotImplementedError(
            "The 'trace' method feature is not implemented yet."
        )
        # return await request.call(
        #     method = "TRACE",
        #     host = host,
        #     url_path = url_path,
        #     port = port,
        #     headers = headers,
        #     url_query = url_query,
        #     body = body,
        #     data = data,
        #     files = files,
        #     bin_files = bin_files,
        #     boundary = boundary,
        #     encoding = encoding,
        #     proxy_data = proxy_data,
        #     ssl = ssl,
        #     connection = connection,
        #     st_reader = st_reader,
        #     st_writer = st_writer,
        #     *args, **kwargs
        # )

    @staticmethod
    async def options(
        host: str = None,
        url_path: str = "/",
        port: int = 443,
        headers: dict[str, str] = None,
        url_query: str = None,
        body: str = None,
        data: dict[str, _Any] = None,
        files: list[dict[str, str]] = None,
        bin_files: list[dict[str, str|_BinaryIO]] = None,
        boundary: str = None,
        encoding: str = "utf_8",
        proxy_data: dict[str, str|int] = None,
        ssl: bool = False,
        connection: _Connection = None,
        st_reader: _StreamReader = None,
        st_writer: _StreamWriter = None,
        *args, **kwargs
    ) -> _HTTP_Response:
        """
        \r
        The variation of '.call()' method specified for 'OPTIONS' requests.
        This method currently is not implemented.
        """
        raise NotImplementedError(
            "The 'options' method feature is not implemented yet."
        )
        # return await request.call(
        #     method = "OPTIONS",
        #     host = host,
        #     url_path = url_path,
        #     port = port,
        #     headers = headers,
        #     url_query = url_query,
        #     body = body,
        #     data = data,
        #     files = files,
        #     bin_files = bin_files,
        #     boundary = boundary,
        #     encoding = encoding,
        #     proxy_data = proxy_data,
        #     ssl = ssl,
        #     connection = connection,
        #     st_reader = st_reader,
        #     st_writer = st_writer,
        #     *args, **kwargs
        # )


    @staticmethod
    def url_query_builder(
        params: dict[str, str],
        special_params: dict[str, str] = None
    ) -> str:
        result = None
        start_build = {**params}
        if None != special_params:
            for key in special_params.keys():
                if None != start_build.get(key):
                    del start_build[key]
        result = _urlencode(start_build)
        if None != special_params:
            for key, val in special_params.items():
                result += f"&{key}={val.replace(' ', '+')}"
        
        return result
