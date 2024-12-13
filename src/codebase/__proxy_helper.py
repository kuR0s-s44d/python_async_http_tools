from abc import ABC, abstractmethod
import base64
import socket
from typing import (
    Callable,
    Self
)

def _addr_port_conf(ip_port_combo: str) -> tuple[str, int]:
    ip, port = ip_port_combo.split(":")
    port = int(port)
    return ip, port


def _basic_b64_key(proxy_login: str, proxy_passwd: str) -> str:
    return base64.b64encode(
        f"{proxy_login}:{proxy_passwd}".encode("ascii")
    ).decode("ascii")


class Abstract_Proxy_Helper(ABC):

    """
    Abstract class to be a minimal template to create the real class
    """

    @abstractmethod
    def connect_socket(self: Self, *args, **kwargs) -> None:
        pass
        
    @abstractmethod
    def switch(self: Self, *args, **kwargs) -> None:
        pass


class Proxy_Helper(Abstract_Proxy_Helper):

    """
    A class representing the wrapper for low-level socket module to allow usage
    of proxies with with the asyncio module's Streams.

    By default uses the '.default_type' type of proxy as was specified at
    initialization.
    Currently supported types:
    - 'http'
    - 'https'
    - 'socks5' - planned in the future

    To change the type of proxy and/or the proxy server, use '.switch()' method
    if you're using this class by itself, but using the method in higher-level
    abstraction is preferable.
    """

    def __init__(
        self: Self,
        http: str = None,
        https: str = None,
        socks5: str = None,
        username: str = None,
        password: str = None,
        key: str = None,
        prox_type: str = "http",
        key_gen_func: Callable = _basic_b64_key,
        *args, **kwargs
    ) -> None:
        self.default_type = prox_type
        self.key_gen_func = key_gen_func
        if http != None:
            self.__http_host, self.__http_port = _addr_port_conf(http)
        if https != None:
            self.__https_host, self.__https_port = _addr_port_conf(https)
        if socks5 != None:
            self.__socks5_host, self.__socks5_port = _addr_port_conf(socks5)
        if None == prox_type:
            prox_type = "http"
        if "http" == prox_type:
            self.__host = self.__http_host
            self.__port = self.__http_port
        elif "https" == prox_type:
            self.__host = self.__https_host
            self.__port = self.__https_port
        elif "socks5" == prox_type:
            self.__host = self.__socks5_host
            self.__port = self.__socks5_port
        if username != None and password != None:
            self.__username = username
            self.__password = password
            self.__key = key_gen_func(self.__username, self.__password)
            self.add_header = {"Proxy-Authorization": f"Basic {self.__key}"}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def gen_conn_request(
        self: Self,
        target_host: str,
        target_port: int,
        *args, **kwargs
    ):
        types = {
            "http": "HTTP",
            "https": "HTTP"
        }
        
        if kwargs.get("protocol"):
            proto = kwargs.get("protocol")
        elif kwargs.get("proto"):
            proto = kwargs.get("proto")
        else:
            proto = types[self.default_type]
            
        if kwargs.get("protocol_version"):
            type_ver = kwargs.get("protocol_version")
        elif kwargs.get("proto_ver"):
            type_ver = kwargs.get("proto_ver")
        else:
            type_ver = "1.1"
            
        con_req = f"CONNECT {target_host}:{target_port} {proto}/{type_ver}\r\n"
        con_req += f"Host: {self.__host}:{self.__port}\r\n"
        if hasattr(self, "add_header"):
            headers = [(item[0], item[1]) for item in self.add_header.items()]
            key, val = headers[0]
            con_req += f"{key}: {val}\r\n"
        con_req += "\r\n"
        return con_req

    def connect_socket(
        self: Self,
        target_host: str,
        target_port: int,
        *args, **kwargs
    ) -> None:
        if kwargs.get("encoding"):
            encoding = kwargs.pop("encoding")
        else:
            encoding = "utf_8"
        connect_request = self.gen_conn_request(
            target_host,
            target_port,
            *args, **kwargs
        ).encode(encoding)
        self.socket.connect((self.__host, self.__port))
        self.socket.send(connect_request)
        self.socket.recv(1024)
        
    def switch(
        self: Self,
        new_type: str,
        new_host: str,
        new_port: int,
        target_host: str,
        target_port: int,
        new_username: str = None,
        new_password: str = None,
        *args, **kwargs
    ) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.default_type = new_type
        if "http" == new_type:
            self.__http_host, self.__http_port = new_host, new_port
            self.__host = self.__http_host
            self.__port = self.__http_port
        elif "https" == new_type:
            self.__https_host, self.__https_port = new_host, new_port
            self.__host = self.__https_host
            self.__port = self.__https_port
        elif "socks5" == new_type:
            self.__socks5_host, self.__socks5_port = new_host, new_port
            self.__host = self.__socks5_host
            self.__port = self.__socks5_port
        else:
            print(
                "Proxy information change failed. No acceptanle proxy type"\
                " was specified. Please, choose 'http', 'https' or 'socks5'"\
                " (currently anavailable)."
            )
            return
        if new_username != None and new_password != None:
            self.__username = new_username
            self.__password = new_password
            self.__key = self.key_gen_func(self.__username, self.__password)
            self.add_header = {"Proxy-Authorization": f"Basic {self.__key}"}
