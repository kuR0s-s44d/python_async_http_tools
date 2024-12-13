from abc import (
    ABC as _ABC,
    abstractmethod as _abstractmethod
)
from asyncio import (
    StreamReader as _StreamReader,
    StreamWriter as _StreamWriter
)
from datetime import datetime as _dt
from ssl import SSLContext as _SSLContext
from typing import (
    Callable as _Callable,
    Self as _Self,
)

def _decor_logic(
    target_dict: dict[str, dict[str, dict[str, bool|_Callable]]],
    target_method: str,
    target_path: str,
    target_actor: _Callable,
    is_async: bool,
    *args, **kwargs
) -> None:
    result = {
        "is_async": is_async,
        "actor": target_actor
    }
    if None == target_dict.get(target_method):
        target_dict[target_method] = dict()
    target_dict[target_method][target_path] = result

        

class BaseAsyncServerTemplate(_ABC):

    def __init__(
        self: _Self,
        host: str,
        port: int,
        ssl: bool = False,
        protocol: str = "HTTP",
        protocol_ver: str = "1",
        encoding: str = "utf_8",
        server_headers: dict[str, str] = None,
        listener: bool = True
    ) -> None:
        self.listener = listener
        self.encoding = encoding
        self.protocol = protocol
        self.protocol_version = protocol_ver
        self.paths = dict()
        self.__serve = True
        self.__server_details = {
            "host": host,
            "port": port
        }
        if ssl:
            self.__server_details["ssl"] = _SSLContext()
        self.server_headers = server_headers
            

    def get(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result
                    
            _decor_logic(
                target_dict = self.paths,
                target_method = "GET",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def post(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result
                
            _decor_logic(
                target_dict = self.paths,
                target_method = "POST",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def put(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result

            _decor_logic(
                target_dict = self.paths,
                target_method = "PUT",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def delete(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result
                
            _decor_logic(
                target_dict = self.paths,
                target_method = "DELETE",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def options(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result

            _decor_logic(
                target_dict = self.paths,
                target_method = "OPTIONS",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def trace(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result

            _decor_logic(
                target_dict = self.paths,
                target_method = "TRACE",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def patch(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result

            _decor_logic(
                target_dict = self.paths,
                target_method = "PATCH",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def head(
        self: _Self,
        path: str,
        is_async: bool = False
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result

            _decor_logic(
                target_dict = self.paths,
                target_method = "HEAD",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator

    def connect(
        self: _Self,
        path: str,
        is_async: bool = False 
    ) -> _Callable:
        def decorator(func: _Callable) -> _Callable:
            if is_async:
                async def inner(*args, **kwargs):
                    
                    ...
                    result = await func(*args, **kwargs)
                    ...

                    return result
            else:
                def inner(*args, **kwargs):
                    
                    ...
                    result = func(*args, **kwargs)
                    ...

                    return result

            _decor_logic(
                target_dict = self.paths,
                target_method = "CONNECT",
                target_path = path,
                target_actor = inner,
                is_async = is_async
            )
            return inner
        return decorator    

    @_abstractmethod
    async def close(*args, **kwargs):
        pass

    @staticmethod
    @_abstractmethod
    async def _default_connection_handler(
        stream_reader: _StreamReader,
        stream_writer: _StreamWriter,
        *args, **kwargs
    ) -> None:
        pass

    @_abstractmethod
    def _response_status_builder(*args, **kwargs):
        pass

    @_abstractmethod
    async def start_serving(*args, **kwargs):
        pass
