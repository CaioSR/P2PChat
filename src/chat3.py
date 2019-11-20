from server import *
from client import *
import threading

ip = socket.gethostbyname(socket.gethostname())

sThread = threading.Thread(target=Server, args=(5003,))
sThread.daemon = True
sThread.start()
client = Client((ip, 5003))

