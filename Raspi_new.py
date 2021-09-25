import face_recognition
import picamera
import os
import numpy as np
from PIL import Image, ImageFile
import io
import paho.mqtt.client as mqtt


ImageFile.LOAD_TRUNCATED_IMAGES = True

import threading


class face_recog_pi():
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
            print("I see someone named {}!".format(name))
        camera.close()

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
        print(TO_MCU)

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

while True:
    face_recog.capture()
