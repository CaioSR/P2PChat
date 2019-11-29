from server import *
from client import *
from Peer import *
import threading

ip = socket.gethostbyname(socket.gethostname())

# sThread = threading.Thread(target=Server, args=(5002,))
# sThread.daemon = True
# sThread.start()
# client = Client((ip, 5002))

p = Peer(5002)