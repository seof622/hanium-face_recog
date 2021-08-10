import face_recognition
import cv2
import camera
import os
import numpy as np
import paho.mqtt.client as mqtt
import json
import io
from PIL import Image, ImageFile
import threading
import sys
import serial
import signal

ImageFile.LOAD_TRUNCATED_IMAGES = True


###########v.1


class FaceRecog():
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=0)
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
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = './knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    ###def __del__(self):
    ## del self.camera

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("set_user")
        # client.subscribe("pic_response")
        client.subscribe("TO_MCU")
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))

    def on_message_set_user(self, client, userdata, msg):
        print("msg set_user arrived")
        image = Image.open(io.BytesIO(msg.payload))
        image.save('./knowns/User.jpg', 'jpeg')
        self.__init__()

    def on_message_TO_MCU(self, client, userdata, msg):
        TO_MCU = msg.payload.decode()
        receive_app = ""
        if TO_MCU != "":
            self.ser.write(msg.payload)
        print(TO_MCU)

    def on_publish(self, client, userdata, mid):
        mola = 1

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def get_frame(self):
        # Grab a single frame of video
        frame = self.camera.get_frame()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                min_value = min(distances)

                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
                if min_value < 0.6:
                    index = np.argmin(distances)
                    name = self.known_face_names[index]
                    self.User_Flag = True
                    self.Not_Detect_Flag = False
                    if name == "dangerous":
                        self.Danger_Flag = True
                        self.Not_Detect_Flag = False
                else:
                    name = 'unknown'
                    self.Not_Detect_Falg = True

                self.face_names.append(name)

        self.process_this_frame = not self.process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

    def check_face(self):
        if self.User_Flag:
            client.publish('common', json.dumps({"Result": "Detect!"}), 1)
            if self.request_Flag:
                self.flag_danger_often = False
            if self.capture_Flag == False:
                self.capture(frame)



        elif self.Not_Detect_Flag:
            client.publish('common', json.dumps({"Result": "Not User!"}), 0)
            # self.Flag = ""
        elif self.Danger_Flag:
            client.publish('common', json.dumps({"Result": "Danger User!"}), 0)
            # self.Flag = ""

    def work(self):
        print("Timer on")
        self.capture_Flag = False
        self.recycle_uart = True
        if self.User_Flag:
            self.ser.write(b'GFSdanger\n')
        self.User_Flag = False
        self.Danger_Flag = False
        self.Not_detect_Flag = True
        self.time_request = self.time_request + 1
        threading.Timer(10, self.work).start()

    def check_uart_data(self, data):
        request_detect = ""
        if data == "RFL1\n":
            print("request_FLag")
            if self.User_Flag:
                request_detect = "SFSUser\n"
                self.ser.write(request_detect.encode())
                self.request_Flag = False
                print("here1")
            else:
                if self.time_request == 2:
                    self.time_request = 0
                    self.request_Flag = False
        elif data == "FAS1\n":
            client.publish('TO_APP', data)
            cap_access = self.camera.get_frame()
            self.capture(cap_access)
        else:
            client.publish('TO_APP', data.encode(), 0)

    def capture(self, frame_type):
        cv2.imwrite('TO_app/save.jpg', frame_type)
        img = Image.open('TO_app/save.jpg')
        bytearr = io.BytesIO()
        img.save(bytearr, format('jpeg'))
        client.publish('picture', bytearr.getvalue())
        self.capture_Flag = True


if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)
    url = "54.185.18.26"
    client = mqtt.Client()
    client.on_connect = face_recog.on_connect
    client.on_disconnect = face_recog.on_disconnect
    client.on_publish = face_recog.on_publish
    client.on_subscribe = face_recog.on_subscribe
    # client.on_message = face_recog.on_message
    # client.message_callback_add("pic_response", face_recog.on_message_pic_response)
    client.message_callback_add("set_user", face_recog.on_message_set_user)
    client.message_callback_add("TO_MCU", face_recog.on_message_TO_MCU)
    client.connect(url, 1883)
    client.connect_async(url, 1883)
    client.loop_start()
    face_recog.work()
    # uart_th = threading.Thread(face_recog.uart_func())
    # recog_th = threading.Thread(face_recog.frame_th())
    # uart_th.start()
    receive_data_full = ""
    while True:

        # recog_th.start()
        frame = face_recog.get_frame()
        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        #          if face_recog.recycle_uart == True:
        #          while face_recog.ser.readable():
        receive_data = face_recog.ser.read()
        receive_data_full += receive_data.decode()
        if receive_data == b'\n':
            print(receive_data_full)
            face_recog.check_uart_data(receive_data_full)
            if receive_data_full == "RFL1\n":
                face_recog.request_Flag = True
            receive_data_full = ""
        #             if receive_data_full == receive_data_full:
        #                 face_recog.recycle_uart = False
        #             elif receive_data_full != receive_data_full:
        #                 face_recog.recycle_uart = True
        #                 break
        face_recog.check_face()
        if face_recog.request_Flag:
            face_recog.check_uart_data("RFL1\n")

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            face_recog.client.loop_stop()
            face_recog.client.disconnect()

            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')

