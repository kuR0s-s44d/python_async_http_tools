import asyncio as _aio
from typing import Self

from .base_objects import (
    Connection, HTTP_Response
)

class Async_Connector:
    """
    The base class to create and control Async Connections.

    Before sending the request, a connection should be established similar to
    basid 'asyncio.open_connection()'. This class allows to create and manage
    multiple connections at once.

    All connections are stored in dicttionary and can be accessed through its
    key in '.connections' attribute.
    """
    def __init__(
        self: Self,
        target_host: str,
        target_port: int,
        num_conn: int = 1,
        conn_names: list[str] = None,
        loop: _aio.BaseEventLoop = None,
        limit: int = None,
        proxy: dict[str, str | int] = None,
        ssl: bool = False,
        *args, **kwargs
    ) -> None:
        self.connections = dict()
        for _ in range(num_conn):
            self.connections[_] = Connection(
                target_host,
                target_port,
                loop,
                limit,
                proxy,
                ssl,
                *args, **kwargs
            )
        if conn_names:
            if len(conn_names) > num_conn:
                max_range = num_conn
            else:
                max_range = len(conn_names)
            for _ in range(max_range):
                self.connections[conn_names[_]] = self.connections[_]
                del self.connections[_]

    async def __aenter__(self: Self) -> dict[str|int, Connection]:
        tasks = [conn.open() for conn in self.connections.values()]
        await _aio.gather(*tasks)
        return self.connections

    async def __aexit__(
        self: Self,
        exception_type,
        exception_value,
        exception_traceback
    ) -> None:
        tasks = [value.close() for value in self.connections.values()]
        await _aio.gather(*tasks)
