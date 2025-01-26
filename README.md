# JRPCpy

a python port of the jrpc dll.  
made quite a while ago, thought about keeping this project personal and not publishing, but i need some stuff for my github

## Features
- fully functional port of the jrpc dll for python (some missing features)
- simple and lightweight
- no unnecessary bloat

## Installation
Clone repo, i most likely wont upload to pip

## Example

```
from jrpc import JRPC
import struct

xbox_ip = "192.168.1.2"
xbox = JRPC.connect(xbox_ip, debug=False)

print(f"xbox ip: {JRPC.get_ip(xbox)}")

JRPC.write_float(xbox, 3307598716, 2000.0)
byte_array = bytes([96, 0, 0, 0])
JRPC.write_memory(xbox, 2195250372, byte_array)

```
