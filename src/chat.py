from server import *
from client import *
from Peer import *
import threading

ip = socket.gethostbyname(socket.gethostname())

# sThread = threading.Thread(target=Server, args=(5001,))
# sThread.daemon = True
# sThread.start()
# client = Client((ip, 5001))

p = Peer(31001)

