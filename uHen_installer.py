import serial
import serial.tools.list_ports
from threading import Thread, Lock
from collections import deque
import sys
cache = deque()
lock = Lock()
def _record_data():
    while serial_connection.is_open:
        try:
            line = serial_connection.readline()
        except: pass
        if line:
            with lock:
                cache.append(line.decode())

try:
    port = input("Enter port > ")
except IndexError:
    print("Plug in your device")
    import sys
    sys.exit()

serial_connection = serial.Serial(
    port=port,
    baudrate=115200,
    timeout=1
)
record_thread = Thread(target=_record_data, daemon=True)
record_thread.start()

def _record_data():
    """
    Continuously record data from the serial port into a cache.
    """
    while serial_connection.is_open:
        line = serial_connection.readline()
        if line:
            with lock:
                cache.append(line.decode())

def send_data(data):
    print(data)
    if isinstance(data, str):
        data = data.encode()
    serial_connection.write(data)

def send_line(data,readfix=True):
    send_data(data + "\r\n")
    if readfix:
        data = None
        while data == None:
            data = receive_line()

def receive_line():
    with lock:
        if cache:
            result = cache.popleft()
            return result
        else:
            return None

if len(sys.argv) == 3:
    _,name,path = sys.argv
else:
    from tkinter import filedialog
    path = filedialog.askopenfilename(filetypes=[("uHen program",".u.py"),("Python files",".py"),("All files","*")])
    name = input("Install as > ")
with open(path,"r") as f:
    lines = f.read().splitlines()
print("Installing...")
send_data(chr(3))
send_data(chr(4))
send_line("installinterface")
send_line(name)
for line in lines:
    send_line(line)
send_data(chr(4))
serial_connection.close()
print("Installed! :D")