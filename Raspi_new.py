import face_recognition
import picamera
import os
import numpy as np
from PIL import Image, ImageFile
import io
import paho.mqtt.client as mqtt
import serial
from time import sleep

ImageFile.LOAD_TRUNCATED_IMAGES = True

import threading


class face_recog_pi():
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=1)
    receive_flag = False
    User_Flag = False
    Danger_Flag = False
    Not_Detect_Flag = True
    capture_Flag = False
    SLW = False
    request_Flag = False
    recycle_uart = True
    flag_danger_often = False
    time_request = 0;

    def __init__(self):
        # Get a reference to the Raspberry Pi camera.
        # If this fails, make sure you have a camera connected to the RPi and that you
        # enabled your camera in raspi-config and rebooted first.
        self.known_face_names = []
        self.known_face_encodings = []

        # Load a sample picture and learn how to recognize it.

    def img_encoding(self):
        print("Loading known face image(s)")
        self.path_encoding_dir = "./encoding_list"
        self.path_Picture_dir = "./encoding_image"
        self.idx_encoding = len(os.listdir(self.path_encoding_dir))
        if self.idx_encoding != 0:
            files = os.listdir(self.path_encoding_dir)
            for filename in files:
                name, ext = os.path.splitext(filename)
                if ext == '.csv':
                    self.known_face_names.append(name)
                    pathname = os.path.join(self.path_encoding_dir, filename)
                    face_encoding = np.loadtxt(pathname, delimiter=",")
                    self.known_face_encodings.append(face_encoding)
        print("Complete encoding of " + str(self.idx_encoding) + "person")
        # Initialize some variables

    def capture(self):
        face_locations = []
        face_encodings = []

        camera = picamera.PiCamera()
        camera.resolution = (320, 240)
        output = np.empty((240, 320, 3), dtype=np.uint8)
        # print("Capturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        # print("Found {} faces in image.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(output, face_locations)

        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.45)
            name = "<Unknown Person>"
            try:
                for idx in range(self.idx_encoding):
                    if match[idx]:
                        name = self.known_face_names[idx]
            except:
                print("Recognite error!")
            if "User" in name:
                print("Appear User")
                self.User_Flag = True
                self.Danger_Flag = False
                self.Not_Detect_Flag = False
            elif "Danger" in name:
                print("Appear Danger")
                camera.capture('TO_app/Danger.jpg')
                self.Danger_capture()
                self.User_Flag = False
                self.Danger_Flag = True
                self.Not_Detect_Flag = False
                if self.request_Flag:
                    self.flag_danger_often = False
                    # if self.capture_Flag == False:
                    #    client.publish('TO_APP',"Danger\n",1)
            else:
                print("Appear Unknown")
                self.User_Flag = False
                self.Danger_Flag = False
                self.Not_Detect_Flag = True
            print("I see someone named {}!".format(name))
        camera.close()

    """
    def check_face(self):
        if self.User_Flag:
            pass 
        elif self.Not_Detect_Flag:
            pass
        elif self.Danger_Flag:
            if self.request_Flag:
                self.flag_danger_often = False
            if self.capture_Flag == False:

                client.publish('TO_APP',"Danger\n",1)
    """

    def Danger_capture(self):
        img = Image.open('TO_app/Danger.jpg')
        bytearr = io.BytesIO()
        img.save(bytearr, format('jpeg'))
        client.publish('picture', bytearr.getvalue())
        client.publish('TO_APP', "Danger\n", 1)
        self.capture_Flag = True

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("TO_MCU")
        client.subscribe("set_person_user")
        client.subscribe("set_person_danger")
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("disconnect: ")
        print(str(rc))

    def on_message_TO_MCU(self, client, userdata, msg):
        TO_MCU = msg.payload.decode()
        receive_app = ""
        if TO_MCU != "":
            self.ser.write(msg.payload)
            print(TO_MCU)

    def check_uart_data(self, data):
        request_detect = ""
        if data == "RFU\n":
            if self.User_Flag:
                request_detect = "FURu\n"
            if self.Danger_Flag:
                request_detect = "FURd\n"
            if self.Not_Detect_Flag:
                request_detect = "FURn\n"
            self.ser.write(request_detect.encode())
            self.request_Flag = False
        else:
            print("To_APP")
            client.publish('TO_APP', data.encode(), 0)

    def uart_therad(self):
        receive_data_full = ""
        while self.ser.readable():
            receive_data = self.ser.read()
            if receive_data != b'':
                print(receive_data)
                try:
                    receive_data_full += receive_data.decode()
                except:
                    receive_data_full = ""
                    print("Uart Error")

                if receive_data == b'\n':
                    print(receive_data_full)
                    self.check_uart_data(receive_data_full)
                    if receive_data_full == "RFU\n":
                        self.request_Flag = True
                    receive_data_full = ""

                    if receive_data_full == receive_data_full:
                        self.recycle_uart = False
                    elif receive_data_full != receive_data_full:
                        self.recycle_uart = True
                        break
            else:
                break

    def work(self):
        print("Timer on")
        self.capture_Flag = False
        self.recycle_uart = True
        if self.Danger_Flag:
            self.ser.write(b'DRP\n')
            pass
        self.User_Flag = False
        self.Danger_Flag = False
        self.Not_detect_Flag = True
        self.time_request = self.time_request + 1
        threading.Timer(10, self.work).start()

    def on_publish(self, client, userdata, mid):
        mola = 1

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def user_encoding(self, client, userdata, msg):
        User_Image = msg.payload
        User_Image_data = Image.open(io.BytesIO(User_Image))
        idx_User_Image = 0
        files = os.listdir(self.path_Picture_dir)
        if len(files) > 0:
            for filename in files:
                name, ext = os.path.splitext(filename)
                check_user = "User" not in name
                if check_user != 1:
                    print("set User!")
                    if ext == '.jpg':
                        idx = name.split('User')[1]
                        print(idx)
                        if idx_User_Image <= int(idx):
                            idx_User_Image = int(idx)
        save_image_path = self.path_Picture_dir + "/User" + str(idx_User_Image + 1) + ".jpg"
        User_Image_data.save(save_image_path, 'jpeg')
        print("subprocess Start!")
        proc = os.system('python3 save_encoding.py')
        if proc == 0:
            pass
        self.img_encoding()

    def danger_encoding(self, client, userdata, msg):
        Danger_Image = msg.payload
        Danger_Image_daga = Image.open(io.BytesIO(Danger_Image))
        idx_Danger_Image = 0
        files = os.listdir(self.path_Picture_dir)
        if len(files) > 0:
            for filename in files:
                name, ext = os.path.splitext(filename)
                check_danger = "Danger" not in name
                if check_danger != 1:
                    print("set Dagner")
                    if ext == '.jpg':
                        idx = name.split('Danger')[1]
                        print(idx)
                        if idx_Danger_Image <= int(idx):
                            idx_Danger_Image = int(idx)
        Danger_Image_daga.save(self.path_Picture_dir + "/Danger" + str(idx_Danger_Image + 1) + ".jpg", 'jpeg')
        proc = os.system('python3 save_encoding.py')
        print("subprocess Start")
        if proc == 0:
            pass
        self.img_encoding()


if __name__ == "__main__":
    face_recog = face_recog_pi()
    face_recog.img_encoding()
    url = "54.201.98.240"
    client = mqtt.Client()
    client.on_connect = face_recog.on_connect
    client.on_disconnect = face_recog.on_disconnect
    client.on_publish = face_recog.on_publish
    client.on_subscribe = face_recog.on_subscribe
    client.message_callback_add("set_person_user", face_recog.user_encoding)
    client.message_callback_add("set_person_danger", face_recog.danger_encoding)
    client.message_callback_add("TO_MCU", face_recog.on_message_TO_MCU)
    client.connect(url, 1883)
    client.connect_async(url, 1883)
    client.loop_start()
    face_recog.work()
    # receive_data_full = ""
    face_recog.ser.write(b'RIC\n')

while True:
    try:
        face_recog.capture()
    except:
        print("capture error")

    try:
        uart_th = threading.Thread(target=face_recog.uart_therad())
        uart_th.start()
    except:
        print("uart error")

    # face_recog.check_face()
    if face_recog.request_Flag:
        face_recog.check_uart_data("RFU\n")
