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
import serial
import signal

ImageFile.LOAD_TRUNCATED_IMAGES = True

###########v.1



class FaceRecog():

    #ser =serial.Serial("/dev/ttyS0", 9600, timeout = 0)
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
        self.danger_face_encodings = []
        self.danger_face_names = []


        # Load sample pictures and learn how to recognize it.
        try:
           dirname = './set_user'
           files = os.listdir(dirname)
           for filename in files:
               name, ext = os.path.splitext(filename)
               if ext == '.jpg':
                   self.known_face_names.append(name)
                   pathname = os.path.join(dirname, filename)
                   img = face_recognition.load_image_file(pathname)
                   face_encoding = face_recognition.face_encodings(img)[0]
                   self.known_face_encodings.append(face_encoding)
        except:
           print("Don't have User Image Files")

        try:
           dirname_danger = './set_danger'
           files_danger = os.listdir(dirname_danger)
           for filename in files_danger:
               name, ext = os.path.splitext(filename)
               if ext == '.jpg':
                   self.danger_face_names.append(name)
                   pathname = os.path.join(dirname_danger, filename)
                   img = face_recognition.load_image_file(pathname)
                   face_encoding = face_recognition.face_encodings(img)[0]
                   self.danger_face_encodings.append(face_encoding)
        except:
           print("Don't have Danger Image Files")

        # Initialize some variables

        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True




    ###def __del__(self):
       ## del self.camera


    def on_connect(self,client, userdata, flags, rc):
        client.subscribe("set_face_user")
        client.subscribe("set_face_danger")
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
        user_path = "./set_user"
        user_file_idx = len(os.listdir(user_path))
        image.save('./set_user/User' + str(user_file_idx) + '.jpg', 'jpeg')
        # dirname_user = './set_user'
        # files = os.listdir(dirname_user)
        # for filename in files:
        #     name, ext = os.path.splitext(filename)
        #     if ext == '.jpg':
        #         self.known_face_names.append(name)
        #         pathname = os.path.join(dirname_user, filename)
        #         img = face_recognition.load_image_file(pathname)
        #         face_encoding = face_recognition.face_encodings(img)[0]
        #         self.known_face_encodings.append(face_encoding)
        # print("Complete Encoding_User")
        # print(self.known_face_names)
        self.__init__()


    def on_message_set_danger(self, client, userdata, msg):
        print("msg set_danger arrived")
        image = Image.open(io.BytesIO(msg.payload))
        danger_path = "./set_danger"
        danger_file_idx = len(os.listdir(danger_path))
        image_str ="./set_danger/Danger" +  str(danger_file_idx) + ".jpg"
        image.save(image_str, 'jpeg')
        # self.__init__()
        # dirname_danger = './set_danger'
        # files_danger = os.listdir(dirname_danger)
        # for filename in files_danger:
        #     name, ext = os.path.splitext(filename)
        #     if ext == '.jpg':
        #         self.danger_face_names.append(name)
        #         pathname = os.path.join(dirname_danger, filename)
        #         img = face_recognition.load_image_file(pathname)
        #         face_encoding = face_recognition.face_encodings(img)[0]
        #         self.danger_face_encodings.append(face_encoding)
        # print("Complete Encoding_dagner")
        # print(self.danger_face_names)
        self.__init__()

    def on_message_TO_MCU(self, client, userdata, msg):
        TO_MCU = msg.payload.decode()
        receive_app = ""
        if TO_MCU != "":
            self.ser.write(msg.payload)
            print(TO_MCU)


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
                try:
                    distances_knowns = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    min_value_knowns = min(distances_knowns)
                    if min_value_knowns < 0.6:
                        index = np.argmin(distances_knowns)
                        known_name = self.known_face_names[index]
                        self.User_Flag = True
                        self.Not_Detect_Flag = False
                        print(known_name)
                        self.known_face_names.append(known_name)
                except:
                    pass

                try:
                    distances_danger = face_recognition.face_distance(self.danger_face_encodings, face_encoding)
                    min_value_danger = min(distances_danger)
                    if min_value_danger < 0.6:
                        index = np.argmin(distances_danger)
                        danger_name = self.danger_face_names[index]
                        self.Danger_Flag = True
                        self.Not_Detect_Flag = False
                        print(danger_name)
                        self.danger_face_names.append(danger_name)
                except:
                    pass
                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.





        self.process_this_frame = not self.process_this_frame


        # Display the results
        """for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
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
        """
        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

    def check_face(self):
        if self.User_Flag:
            client.publish('common', json.dumps({"Result":"Detect!"}), 1)
            #if self.TO_MCU == "Connect_Request":
            #   client.publish("TO_APP", "Connect_Response")

        elif self.Not_Detect_Flag:
            client.publish('common', json.dumps({"Result":"Not User!"}), 0)
            #self.Flag = ""
        elif self.Danger_Flag:
            client.publish('common', json.dumps({"Result": "Danger User!"}), 0)
            if self.request_Flag:
                self.flag_danger_often = False
            if self.capture_Flag == False:
                self.capture(frame)
                client.publish('TO_APP',"Danger\n",1)

            #self.Flag = ""




    def work(self):
        print("Timer on")
        self.capture_Flag = False
        self.recycle_uart = True
        if self.Danger_Flag:
#            self.ser.write(b'DRP\n')
            pass
        self.User_Flag = False
        self.Danger_Flag = False
        self.Not_detect_Flag = True
        self.time_request = self.time_request + 1
        threading.Timer(10, self.work).start()


    def check_uart_data(self,data):
        request_detect = ""
        if data == "RFU\n":
            if self.User_Flag:
                request_detect = "FURu\n"

            else:
                if self.time_request == 2:
                    self.time_request = 0
            if self.Danger_Flag:
                request_detect = "FURd\n"
            if self.Not_Detect_Flag:
                request_detect = "FURn\n"
            self.ser.write(request_detect.encode())
            self.request_Flag = False

        else :
            print("To_APP")
            client.publish('TO_APP',data.encode(),0)

    def capture(self, frame_type):
        cv2.imwrite('TO_app/save.jpg', frame_type)
        img = Image.open('TO_app/save.jpg')
        bytearr = io.BytesIO()
        img.save(bytearr, format('jpeg'))
        client.publish('picture', bytearr.getvalue())
        self.capture_Flag = True

if __name__ == '__main__':
    global frame
    face_recog = FaceRecog()
    print(face_recog.known_face_names)
    print(face_recog.danger_face_names)
    url = "35.166.121.20"
    client = mqtt.Client()
    client.on_connect = face_recog.on_connect
    client.on_disconnect = face_recog.on_disconnect
    client.on_publish = face_recog.on_publish
    client.on_subscribe = face_recog.on_subscribe
    client.message_callback_add("set_face_user", face_recog.on_message_set_user)
    client.message_callback_add("set_face_danger", face_recog.on_message_set_danger)
    client.message_callback_add("TO_MCU", face_recog.on_message_TO_MCU)
    client.connect(url, 1883)
    client.connect_async(url, 1883)
    client.loop_start()
    face_recog.work()
    receive_data_full = ""
    global frame
    try:
        frame = face_recog.get_frame()
    except:
        print("Frame Can't Load")
    while True:

        #recog_th.start()

         try:
             frame = face_recog.get_frame()
             #cv2.imshow("Frame", frame)
             key = cv2.waitKey(1) & 0xFF

             if key == ord("q"):
                face_recog.client.loop_stop()
                face_recog.client.disconnect()
                #timer.cancel()
                break
         except:
             pass
         # show the frame



          if face_recog.recycle_uart == True:
          while face_recog.ser.readable():
         try:
             receive_data = face_recog.ser.read()
         except:
             receive_data = 0;
             receive_data_full += receive_data.decode()
         if receive_data == b'\n':
             print(receive_data_full)
             face_recog .check_uart_data(receive_data_full)
             if receive_data_full == "RFU\n":
                 face_recog.request_Flag = True
             receive_data_full = ""

             if receive_data_full == receive_data_full:
                 face_recog.recycle_uart = False
             elif receive_data_full != receive_data_full:
                 face_recog.recycle_uart = True
                 break
         face_recog.check_face()
         if face_recog.request_Flag:
             face_recog.check_uart_data("RFU\n")


        # if the `q` key was pressed, break from the loop


    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')
