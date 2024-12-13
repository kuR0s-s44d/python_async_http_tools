import asyncio as _aio
import base64
from socket import socket as _socket
from threading import Thread
from typing import (
    Callable as _Callable,
    Self as _Self,
)

from .async_server_base import (
    BaseAsyncServerTemplate as _BaseAsyncServerTemplate,
)
from .__proxy_helper import Proxy_Helper as _Proxy_Helper
from .__request_parser import (
    all_good as _all_good,
    error_handler as _error_handler
)
from .__response_builder import build_response_meta
from .__response_listener import listen_response as _listen_response

__all__ = [
    "AsyncServer",
    "Connection",
    "HTTP_Response"
]

class Connection:

    """
    A class representing the wrapper for asyncronous connection, created
    via \"asyncio.open_connection()\".

    Hold all necessary information to open asyncronous connection in form of
    \"(asyncio.StreamReader, asyncio.StreamWriter)\" pair. The major
    modification is the ability to work with proxy. Currently only http/https
    proxies are supported.

    Most stated parameters are passed directly to the
    \"asyncio.open_connection()\"

    'proxy' should always be a dictionary or dictionary like object with
    'prox_type' and one of the following key-value pairs presented
    corresponing to the 'prox_type':
    1) \"http\": \"<proxy_server_adress>:<proxy_server_port>\"
    2) \"htts\": \"<proxy_server_adress>:<proxy_server_port>\"
    3) \"socks5\": \"<proxy_server_adress>:<proxy_server_port>\" - planned in
                                                                   future
    'proxy' optional keys are 'username', 'password' and 'key' (auth-key).
    If presented, 'key' should be preferable to the 'username', 'password'.

    \".open()\" and \".close()\" methods should be used to prevent possible
    bugs.
    """

    def __init__(
        self: _Self,
        host: str,
        port: int,
        loop: _aio.BaseEventLoop = None,
        limit: int = None,
        proxy: dict[str, str | int] = None,
        ssl: bool = False,
        *args, **kwargs
    ) -> None:
        self.__closed = True
        self.target_host = host
        self.target_port = port
        self.ssl = ssl
        if limit != None:
            self.limit = limit
        if loop != None:
            self.loop = None
        if proxy != None:
            self.proxy = _Proxy_Helper(**proxy)
            self.add_header = {**self.proxy.add_header}

    async def open(self: _Self):
        """
        Function to open the Connection instance
        """
        try:
            parsed_arguments = {"ssl": self.ssl}
            if hasattr(self, "proxy"):
                if self.ssl:
                    parsed_arguments["server_hostname"] = self.target_host
                self.proxy.connect_socket(self.target_host, self.target_port)
                parsed_arguments["sock"] = self.proxy.socket
            else:
                parsed_arguments["host"] = self.target_host
                parsed_arguments["port"] = self.target_port
            self.reader, self.writer = await _aio.open_connection(
                **parsed_arguments
            )
        except:
            raise
        else:
            self.__closed = False

    async def close(self: _Self):
        """
        Function to close the Connection instance
        """
        try:
            self.writer.close()
            await self.writer.wait_closed()
            if hasattr(self, "proxy"):
                self.proxy.socket.close()
        except:
            raise
        else:
            self.__closed = True

    def is_closed(self: _Self) -> bool:
        return self.__closed

    async def update_proxy_data(
        self: _Self,
        new_type: str,
        new_host: str,
        new_port: int,
        new_username: str = None,
        new_password: str = None
    ) -> None:
        if hasattr(self, "proxy"):
            await self.close()
            self.proxy.switch(
                new_type,
                new_host,
                new_port,
                target_host = self.target_host,
                target_port = self.target_port,
                new_username = new_username,
                new_password = new_password
            )
            self.add_header = {**self.proxy.add_header}
            await self.open()

    async def __aenter__(self: _Self) -> _Self:
        await self.open()
        return self

    async def __aexit__(
        self: _Self,
        exception_type,
        exception_value,
        exception_traceback
    ) -> None:
        await self.close()


class HTTP_Response:

    """
    Class representing the HTTP request response
    """

    def __init__(
        self: _Self,
        status: str = None,
        reason: str = None,
        headers: dict[str, str] = None,
        request: bytes = None,
        body: str = None,
        encoding: str = "utf_8",
        *args, **kwargs
    ) -> None:
        if None != kwargs.get("protocol"):
            self.__protocol = kwargs.get("protocol")
        if status != None:
            self.__status = int(status)
        else:
            self.__status = status
        self.__reason = reason
        self.__headers = headers
        self.__request = request
        self.__body = body
        self.__encoding = encoding

    @property
    def status(self: _Self) -> str:
        return self.__status

    @property
    def request(self: _Self) -> str:
        return self.__request.decode(self.__encoding)

    @property
    def b_request(self: _Self) -> str:
        return self.__request

    @property
    def result(self: _Self) -> str:
        return f"{self.__status}{self.__reason}"

    @property
    def body(self: _Self) -> str:
        return self.__body

    @property
    def headers(self: _Self) -> dict[str, str]:
        return self.__headers

    def formated(
        self: _Self
    ) -> str:
        return_string = f"[ {self.status} {self.__reason} ] " \
            f"{self.__protocol}\n\n"
        if self.__headers != None:
            return_string +="Headers:\n"
            for key, val in self.__headers.items():
                if 1 == len(val) and 0 == list(val.keys())[0]:
                    pval = val[0]
                else:
                    pval = val
                return_string += f"- {key}: {pval}\n"
            return_string += "\n"
        if self.__body != None:
            return_string += f"\n{self.__body}"
        return return_string

    def clear(self: _Self) -> None:
        if self.__protocol:
            self.__protocol = None
        self.__status = None
        self.__reason = None
        self.__headers = None
        self.__request = None
        self.__body = None
        self.__encoding = None


class AsyncServer(_BaseAsyncServerTemplate):

    async def close(self, *args, **kwargs) -> bool:
        # # Comment out the following line during implementation of method
        # raise NotImplemented("This method is currently not implemented.")

        if hasattr(self, "_server"):
            self._server.close()
            await self._server.wait_closed()
            self._server.close_clients()
            self._server.abort_clients()
            return True
        else:
            return False
            

    async def _default_connection_handler(
        self: _Self,
        stream_reader: _aio.StreamReader,
        stream_writer: _aio.StreamWriter,
        connection_worker: _Callable = None,
        *args, **kwargs
    )-> None:
        # # Comment out the following line during implementation of method
        # raise NotImplemented("This method is currently not implemented.")

        proceed = False
        start_line, headers, body = await _listen_response(stream_reader)
        body = b"".join(body)
        body = body.strip()
        if b"" == body:
            body = None

        start_line = start_line.decode(self.encoding)
        method, url_path, proto = start_line.split(" ", maxsplit = 2)
        method = method.upper()
        url_path = url_path.split("?", maxsplit = 1)
        if 2 == len(url_path):
            url_path, query = url_path
        else:
            url_path = url_path[0]


        if self.paths.get(method):
            if self.paths[method].get(url_path):
                passed, error = _all_good(start_line, headers, body)
                if passed:
                    proceed = True
                else:
                    status, reason, error_info, err_headers = _error_handler(
                        error
                    )
                    error_occured = self._response_status_builder(
                        status, reason,
                        body = error_details,
                        add_headers = err_headers
                    )
                    response = error_occured.encode(self.encoding)
            else:
                not_found_response_meta = self._response_status_builder(
                    404, "Not Found"
                )
                response = not_found_response_meta.encode(self.encoding)
        else:
            not_allowed_response = self._response_status_builder(
                405, "Method Not Allowed"
            )
            response = not_allowed_response.encode(self.encoding)

        # Need to change the order of reaction depending if needed/set up
        # during initialization:
        # - listener == True  -> immediate reaction and post-processing
        # - listener == False -> react-processing and post-reaction
        if self.listener:
            if proceed:
                ok200 = self._response_status_builder(
                    200, "OK"
                )
                response = ok200.encode(self.encoding)
            stream_writer.write(response)
            await stream_writer.drain()
            stream_writer.close()
            await stream_writer.wait_closed()

            if proceed:
                kwargs["server_instance"] = self
                if self.paths[method][url_path]["is_async"]:
                    result = await self.paths[method][url_path]["actor"](
                        start_line, headers, body,
                        *args, **kwargs
                    )
                else:
                    result = self.paths[method][url_path]["actor"](
                        start_line, headers, body,
                        *args, **kwargs
                    )
        else:
            if proceed:
                kwargs["server_instance"] = self
                if self.paths[method][url_path]["is_async"]:
                    result = await self.paths[method][url_path]["actor"](
                        start_line, headers, body,
                        *args, **kwargs
                    )
                else:
                    result = self.paths[method][url_path]["actor"](
                        start_line, headers, body,
                        *args, **kwargs
                    )
                if None != result:
                    response_body, addition_heads = result
                else:
                    response_body, addition_heads = None, None

                ok200 = self._response_status_builder(
                    200, "OK",
                    body = response_body,
                    add_headers = addition_heads
                )
                response = ok200.encode(self.encoding)
            stream_writer.write(response)
            await stream_writer.drain()
            stream_writer.close()
            await stream_writer.wait_closed()

    def _response_status_builder(
        self: _Self,
        status: int,
        reason: str,
        body: str = None,
        add_headers: dict[str, str] = None,
        *args, **kwargs
    ) -> str:
        # # Comment out the following line during implementation of method
        # raise NotImplemented("This method is currently not implemented.")
        headers_passed = {
            **self.server_headers
        }
        if None != add_headers:
            headers_passed.update(add_headers)
        return build_response_meta(
            self.protocol,
            self.protocol_version,
            str(status),
            reason,
            headers_passed,
            body_passed = body,
            *args, **kwargs
        )

    async def start_serving(
        self: _Self,
        connection_worker: _Callable = None,
        *args, **kwargs
    ) -> None:
        # # Comment out the following line during implementation of method
        # raise NotImplemented("This method is currently not implemented.")
        try:
            await self.close()
        except NotImplemented as err:
            print(
                "Cannot start serving due to"\
                " \".close()\" method was not specified.\n"\
                "Define \".close()\" method first."
            )
        else:
            if None == connection_worker:
                self._server = await _aio.start_server(
                    self._default_connection_handler,
                    self._BaseAsyncServerTemplate__server_details["host"],
                    self._BaseAsyncServerTemplate__server_details["port"]
                )
            else:
                self._server = await _aio.start_server(
                    connection_worker,
                    self._BaseAsyncServerTemplate__server_details["host"],
                    self._BaseAsyncServerTemplate__server_details["port"]
                )

            # Optional part
            addrs = ":".join(
                str(sock.getsockname()) for sock in self._server.sockets
            )
            print("Start_serving at: {}".format(addrs))

            await self._server.serve_forever()
