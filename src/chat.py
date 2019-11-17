from server import *
from client import *
from tracker import *
import threading

tThread = threading.Thread(target=Tracker)
tThread.daemon = True
tThread.start()
sThread = threading.Thread(target=Server, args=(5001,))
sThread.daemon = True
sThread.start()
client = Client(('127.0.0.1', 5001))

