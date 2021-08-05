import face_recognition
import cv2
import camera
import os
import numpy as np
import paho.mqtt.client as mqtt
import json
import io
from PIL import Image,ImageFile
import threading
import sys

ImageFile.LOAD_TRUNCATED_IMAGES = True


###########v.1



class FaceRecog():
    Flag = "No Detect"
    capture_Flag = False
    SLW = False
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


    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("set_user")
        # client.subscribe("pic_response")
        client.subscribe("TO_MCU")
        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self,client, userdata, flags, rc=0):
        print(str(rc))

    def on_message_set_user(self, client, userdata, msg):
        print("msg set_user arrived")
        image = Image.open(io.BytesIO(msg.payload))
        image.save('./knowns/User.jpg','jpeg')
        self.__init__()

    def on_message_TO_MCU(self, client, userdata, msg):
        lock_way = msg.payload.decode()
        print(lock_way)


    def on_publish(self,client, userdata, mid):
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
                if min_value < 0.5:
                    index = np.argmin(distances)
                    name = self.known_face_names[index]
                    self.Flag = "User Detect"
                    if name == "dangerous":
                        self.Flag = "Dangerous"
                else:
                    name = 'unknown'
                    self.Flag = "Not user"

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
        if self.Flag == "User Detect":
            client.publish('common', json.dumps({"Result":"Detect!"}), 1)
            self.Flag = ""
            if self.capture_Flag == False:
                cv2.imwrite('TO_app/pic_danger.jpg', frame)

                img = Image.open('TO_app/pic_danger.jpg')
                bytearr = io.BytesIO()
                img.save(bytearr, format('jpeg'))
                client.publish('picture', bytearr.getvalue())
                self.capture_Flag = True


        elif self.Flag == "Not user":
            client.publish('common', json.dumps({"Result":"Not User!"}), 0)
            self.Flag = ""
        elif self.Flag == "Dangerous":
            client.publish('common', json.dumps({"Result": "Danger User!"}), 0)
            self.Flag = ""

        else:
            client.publish('common', json.dumps({"Result":"Not Detect"}),0)


    def work(self):
        print("Timer on")
        self.capture_Flag = False


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
    timer = threading.Timer(10, face_recog.work)
    timer.start()
    while True:
        frame = face_recog.get_frame()
        # show the frame
        cv2.imshow("Frame", frame)
        face_recog.check_face()

        key = cv2.waitKey(1) & 0xFF


        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            face_recog.client.loop_stop()
            face_recog.client.disconnect()
            timer.cancel()
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')

