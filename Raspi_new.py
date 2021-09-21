import face_recognition
import picamera
import os
import numpy as np
import paho.mqtt.client as mqtt
import json
import io
from PIL import Image,ImageFile
import threading

ImageFile.LOAD_TRUNCATED_IMAGES = True

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
        # Initialize some variables

    def capture(self):
        face_locations = []
        face_encodings = []

        camera = picamera.PiCamera()
        camera.resolution = (320, 240)
        output = np.empty((240, 320, 3), dtype=np.uint8)
        #print("Capturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        #print("Found {} faces in image.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(output, face_locations)

        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "<Unknown Person>"

            if match[0]:
                name = self.known_face_names[0]

            print("I see someone named {}!".format(name))
        camera.close()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("TO_MCU")
        client.subscribe("set_person")

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

    def cal_encoding(self, client, userdata, msg):
        ##trans json type
        recv_json_data = msg.payload
        Json_Data = json.loads(recv_json_data)
        print(Json_Data["Data"])
        Image_Data = Image.open(io.BytesIO(Json_Data["Data"].encode()))
        idx_encoding_dir = len(os.listdir(self.path_encoding_dir))
        Image_Data.save(self.path_Picture_dir + "/" + Json_Data["Target"] + idx_encoding_dir, 'jpeg')
        proc = os.system('python3 save_encoding.py')
        if proc == 0:
            print("Subprocess start")
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
    client.message_callback_add("set_person", face_recog.cal_encoding)
    client.message_callback_add("TO_MCU", face_recog.on_message_TO_MCU)
    client.connect(url, 1883)
    client.connect_async(url, 1883)
    client.loop_start()

while True:
    face_recog.capture()
