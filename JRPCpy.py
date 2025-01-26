import struct
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
from typing import Optional

class XboxConsole: # JRPC.connect(XBOXIP, debug=True)
    def __init__(self, ip: str, port: int = 730, debug: bool = False):
        self.ip = ip
        self.port = port
        self.debug = debug
        self.connected = False
        self.socket = None

    def connect(self):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
            response = self.socket.recv(1024)
            if response.decode("cp1252").startswith("201-"):
                self.connected = True
            else:
                raise ValueError("Invalid address")
        except:
            raise ValueError("Invalid address")
        
    def send_command(self, command: str) -> Optional[bytes]:
        if not self.connected:
            raise ValueError("Not connected to any console")
        
        print(f"Sending command: {command}")  # Debug output
        self.socket.send(bytes(command, "cp1252"))
        data = self.socket.recv(1024)
        sleep(0.1)
        
        # Log the raw response
        if self.debug:
            print(f"Sent: {command}")
            print(f"Received: {data.decode('cp1252')}")  # Decode for readability
        
        return data

    def close(self):
        if self.socket:
            self.socket.close()
        self.connected = False

class JRPC:
    JRPCVersion = "2"

    @staticmethod
    def connect(ip: str, port: int = 730, debug: bool = False) -> XboxConsole:
        console = XboxConsole(ip, port, debug)
        console.connect()
        return console

    @staticmethod
    def set_memory(console: XboxConsole, address: str, data: str):
        console.send_command(f"setmem addr={address} data={data}\r\n")

    @staticmethod
    def get_memory(console: XboxConsole, address: int, length: int) -> bytes:
        command = f"getmem addr={address:X} length={length}\r\n"
        return console.send_command(command)

    @staticmethod
    def write_float(console: XboxConsole, address: int, value: float):
        bytes_value = struct.pack('>f', value)  # Big-endian float
        hex_data = bytes_value.hex().upper()
        command = f"setmem addr=0x{address:X} data={hex_data}\r\n"
        response = console.send_command(command)
        return response.startswith(b"200-")  # Return True if successful

    @staticmethod
    def read_memory(console: XboxConsole, address: int, length: int) -> Optional[bytes]:
        command = f"getmem addr=0x{address:X} length={length}\r\n"
        response = console.send_command(command)
        if response.startswith(b"200-"):
            return response.split(b'\n')[1].strip()  # Return the actual memory content
        return None


    @staticmethod
    def close(console: XboxConsole):
        console.close()

    @staticmethod
    def write_float_array(console: XboxConsole, address: int, values: list):
        byte_array = bytearray()
        for value in values:
            byte_array.extend(struct.pack('>f', value))  # Big-endian float
        console.send_command(f"setmem addr={address:X} data={byte_array.hex().upper()}\r\n")

    @staticmethod
    def set_memory(console: XboxConsole, address: int, data: bytes):
        hex_data = data.hex().upper()
        command = f"setmem addr={address:X} data={hex_data}\r\n"
        return console.send_command(command)

    @staticmethod
    def call(console: XboxConsole, address: int, *args) -> Optional[bytes]:
        command = f"consolefeatures ver=2 type=1 params=\"A\\0\\A\\{len(args) + 1}\\1\\{address}"
        for arg in args:
            command += f"\\1\\{arg}"
        command += "\"\r\n"
        return console.send_command(command)

    @staticmethod
    def write_memory(console: XboxConsole, address: int, data: bytes):
        hex_data = data.hex().upper()
        command = f"setmem addr=0x{address:X} data={hex_data}\r\n"
        response = console.send_command(command)
        return response.startswith(b"200-")  # Return True if successful

    @staticmethod
    def get_ip(console: XboxConsole) -> str:
        return console.ip
    
    @staticmethod
    def connected(console: XboxConsole) -> bool:
        return console.connected
    
    @staticmethod
    def resolve_function(console: XboxConsole, module_name: str, ordinal: int) -> int:
        command = (
            f"consolefeatures ver={JRPC.JRPCVersion} "
            f"type=9 params=\"A\\0\\A\\2\\{len(module_name)}\\"
            f"{module_name.encode('cp1252').hex().upper()}\\"
            f"{ordinal}\\\""
        )
        response = console.send_command(command)
        response_str = response.decode("cp1252")
        return int(response_str.split(" ")[1], 16)

class XNotifyLogos:
    XBOX_LOGO = 0
    NEW_MESSAGE_LOGO = 1
    FRIEND_REQUEST_LOGO = 2
    UPDATING = 76 # too lazy to actually add all of these
