# Client #
import socket
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

class Client:
    HOST = "192.168.3.2" # Your IP of course
    PORT = 12345
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.HOST, self.PORT))
        self.recv()        

    def recv(self):
        while True:
            data = self.sock.recv(1024).decode()
            try:
                vol = float(data)
                volume.SetMasterVolumeLevel(vol, None)
                print(data)
            except ValueError:
                pass

c = Client()