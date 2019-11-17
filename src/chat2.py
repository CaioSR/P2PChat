from server import *
from client import *
import threading

sThread = threading.Thread(target=Server, args=(5002,))
sThread.daemon = True
sThread.start()
client = Client(('127.0.0.1', 5002))

