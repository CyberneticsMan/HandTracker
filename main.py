from cvzone.HandTrackingModule import HandDetector
import cv2

import threading 
import datetime


import win32api
from win32con import VK_MEDIA_PLAY_PAUSE, KEYEVENTF_EXTENDEDKEY

import socket

import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]





detector = HandDetector(detectionCon=0.8, maxHands=2)



s = socket.socket()        
print ("Socket successfully created")
 
# reserve a port on your computer in our
# case it is 12345 but it can be anything
port = 12345               
 
# Next bind to the port
# we have not typed any ip in the ip field
# instead we have inputted an empty string
# this makes the server listen to requests
# coming from other computers on the network
s.bind(('', port))        
print ("socket binded to %s" %(port))
 
# put the socket into listening mode
s.listen(5)    
print ("socket is listening")           
def serverLoop():
    while True:
        sock, addr = s.accept()
        global c
        c = sock
        print ('Got connection from', addr )

def processLoop():
    start = datetime.datetime.now()
    last = start
    i = 0

    lightStatus = False
    while True:
    
        # Get image frame
        success, img = cap.read()
        # Find the hand and its landmarks
        hands, img = detector.findHands(img)  # with draw
        # hands = detector.findHands(img, draw=False)  # without draw

        if hands:
            # Hand 1
            for hand in hands:
                lmList = hand["lmList"]  # List of 21 Landmark points
                bbox = hand["bbox"]  # Bounding box info x,y,w,h
                centerPoint = hand['center']  # center of the hand cx,cy
                handType = hand["type"]  # Handtype Left or Right

                fingers = detector.fingersUp(hand)

                finger_count = fingers.count(1)

                # Sound Control
                if handType == "Right":

                    if(finger_count==2 and fingers == [1, 1, 0, 0, 0]):
                        length, info, img = detector.findDistance(lmList[8], lmList[4], img)  # with draw
                        length = length - 50
                        volBar = np.interp(length, [0, 100], [400, 150])
                        volPer = np.interp(length, [0, 100], [0, 100])
                        vol = np.interp(length, [0, 100], [minVol, maxVol])
                        volume.SetMasterVolumeLevel(vol, None)
                        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
                        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
                        cv2.putText(img, f'{int(volPer)} %', 
                                    (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

                    if(fingers == [0, 0, 1, 0, 0]):
                        break
                    
                    try:
                        if(fingers == [0, 1, 0, 0, 0]):
                            c.send("test".encode())
                            if lightStatus != True:
                                print("Lights On")
                                lightStatus = True
                                c.send(f'{lightStatus}'.encode())

                        
                        if(fingers == [0, 1, 1, 0, 0]):
                            c.send("test".encode())
                            if lightStatus:
                                print("Lights Off")
                                lightStatus = False
                                c.send(f'{lightStatus}'.encode())

                    except NameError:
                        print("server not yet connected")

                    
                    if(fingers == [0, 0, 0, 0, 1]):
                        i += 1
                        now = datetime.datetime.now()
                        if now - last > datetime.timedelta(seconds=5):
                            last = now
                            win32api.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
                            print("pause/play")
                else:
                    pass
                    #  if(fingers == [0, 1, 0, 0, 0]):
                    #     win32api.SetCursorPos((lmList[8][0], lmList[8][1]))

                    

            
        # Display
        cv2.imshow("Image", img)
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break



    cap.release()
    cv2.destroyAllWindows()




threading.Thread(target=processLoop).start()
threading.Thread(target=serverLoop).start()
