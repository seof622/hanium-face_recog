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
import subprocess
ImageFile.LOAD_TRUNCATED_IMAGES = True


###########v.1


class FaceRecog():
    #ser = serial.Serial("/dev/ttyS0", 9600, timeout=0)
    receive_flag = False
    User_Flag = False
    Danger_Flag = False
    Not_Detect_Flag = True
    capture_Flag = False
    SLW = False
    request_Flag = False
    recycle_uart = True
    flag_danger_often = False
    time_request = 0
    TO_APP = True
    idx = 0
    IMG_SEQ = 0

    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.


        self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []
        self.danger_face_encodings = []
        self.danger_face_names = []

        self.path_encoding_dir = "./encoding_list"
        self.path_Picture_dir = "./encoding_image"
        self.idx_encoding = len(os.listdir(self.path_encoding_dir))
        # Load sample pictures and learn how to recognize it.
        """
        dirname = './set_user/Picture'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)
        """

        if self.idx_encoding != 0:
            files_danger = os.listdir(self.path_encoding_dir)
            for filename in files_danger:
                name, ext = os.path.splitext(filename)
                if ext == '.csv':
                    self.danger_face_names.append(name)
                    pathname = os.path.join(self.path_encoding_dir, filename)
                    #img = face_recognition.load_image_file(pathname)
                    #face_encoding = face_recognition.face_encodings(img)[0]
                    face_encoding = np.loadtxt(pathname, delimiter=",")
                    self.danger_face_encodings.append(face_encoding)
        else:
            print("Don't Exist Encoding File")
        #         print(face_encoding)
        #
        # file_idx = 0
        # np.savetxt("./encoding_list/face" + str(file_idx) + ".csv", face_encoding,delimiter=',')
        # read_data = np.loadtxt("./encoding_list/face0.csv",delimiter=',',dtype=np.float32)
        # print(read_data)




        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    ###def __del__(self):
    ## del self.camera

    def on_connect(self, client, userdata, flags, rc):
        #client.subscribe("set_user")
        # client.subscribe("pic_response")
        client.subscribe("TO_MCU")
        client.subscribe("set_person")
        """
        client.subscribe("set_face_user")
        client.subscribe("set_face_danger")
        """

        if rc == 0:
            print("connected OK")
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        print("disconnect: ")
        print(str(rc))

    def cal_encoding(self,client, userdata, msg):
        ###받은 데이터를 JSON형태로 변환
        recv_json_data = msg.payload.decode('utf-8')
        print(recv_json_data)

        Json_Data = json.load(recv_json_data)

        ###Data라는 Key를 가진 값을 이미지로 변환 후 저장
        Image_Data = Image.open(io.BytesIO(Json_Data["Data"]))
        ###엔코딩 된 파일 개수 확인 --> 이것을 통해 다음 set될 encoding파일의 이름으로 지정
        idx_encoding_dir = len(os.listdir(self.path_encoding_dir))
        Image_Data.save(self.path_Picture_dir + "/" + Json_Data["Target"] + idx_encoding_dir,'jpeg')
        subprocess.call('./save_encoding.py')


    """
    def on_message_set_user(self, client, userdata, msg):

        print("msg set_user arrived")
        image = Image.open(io.BytesIO(msg.payload))
        image.save('./set_user/User' + str(self.idx) + '.jpg', 'jpeg')
        self.idx = self.idx + 1
        dirname_user = './set_user'
        files = os.listdir(dirname_user)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname_user, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # self.__init__()


    def on_message_set_danger(self, client, userdata, msg):
        print("msg set_danger arrived")
        image = Image.open(io.BytesIO(msg.payload))
        image_str ="./set_danger/Danger" +  str(self.IMG_SEQ) + ".jpg"
        image.save(image_str, 'jpeg')
        self.IMG_SEQ = self.IMG_SEQ + 1
        # self.__init__()
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
    """

    def on_message_TO_MCU(self, client, userdata, msg):
        TO_MCU = msg.payload.decode()
        print(TO_MCU)

    def on_message_pic_response(self, client, userdata, msg):
        response = msg.payload.decode()
        if response == "OK":
            print(response)
            self.TO_APP = False



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

                try:
                    distances_knowns = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    min_value_knowns = min(distances_knowns)
                    if min_value_knowns < 0.6:
                        index = np.argmin(distances_knowns)
                        known_name = self.known_face_names[index]
                        self.User_Flag = True
                        self.Not_Detect_Flag = False
                        self.face_names.append(known_name)

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
                        self.face_names.append(danger_name)
                except:
                    pass
                # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                # 0.6 is typical best performance.
        self.process_this_frame = not self.process_this_frame

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
        # Display the results



    def get_jpg_bytes(self):
        frame = self.get_frame()
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

    def check_face(self):
        if self.User_Flag:
            client.publish('common', json.dumps({"Result": "Detect!"}), 1)
            # if self.TO_MCU == "Connect_Reqeust":
            #     client.publish("TO_APP", "Connect_Response")

        elif self.Not_Detect_Flag:
            client.publish('common', json.dumps({"Result": "Not User!"}), 0)
            # self.Flag = ""
        elif self.Danger_Flag:
            if self.request_Flag:
                self.flag_danger_often = False
            if self.capture_Flag == False:
                self.capture(frame)
                client.publish("TO_APP", "Danger\n");

            # self.Flag = ""

    def work(self):
        print("Timer on")
        self.capture_Flag = False
        self.recycle_uart = True
        # if self.User_Flag:
        #      self.ser.write(b'GFSdanger\n')
        #
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
            cap_access = self.camera.get_frame()
            self.capture(cap_access)
            client.publish('TO_APP', data)
        else:
            client.publish('TO_APP', data.encode(), 0)

    def capture(self, frame_type):
        cv2.imwrite('TO_app/save.jpg', frame_type)
        img = Image.open('TO_app/save.jpg')
        bytearr = io.BytesIO()
        img.save(bytearr, format('jpeg'))
        client.publish('picture', bytearr.getvalue())
        print("send pic data")
        self.capture_Flag = True



if __name__ == '__main__':
    face_recog = FaceRecog()
    print(face_recog.known_face_names)
    print(face_recog.danger_face_names)

    url = "54.201.98.240"
    client = mqtt.Client()
    client.on_connect = face_recog.on_connect
    client.on_disconnect = face_recog.on_disconnect
    client.on_publish = face_recog.on_publish
    client.on_subscribe = face_recog.on_subscribe
    # client.on_message = face_recog.on_message

    client.message_callback_add("set_person", face_recog.cal_encoding)
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
        if face_recog.idx_encoding != 0:
            frame = face_recog.get_frame()
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                face_recog.client.loop_stop()
                face_recog.client.disconnect()
                break
        else:
            pass

        # show the frame



        #          if face_recog.recycle_uart == True:
        #          while face_recog.ser.readable():
        # receive_data = face_recog.ser.read()
        # receive_data_full += receive_data.decode()
        # if receive_data == b'\n':
        #     print(receive_data_full)
        #     face_recog.check_uart_data(receive_data_full)
        #     if receive_data_full == "RFL1\n":
        #         face_recog.request_Flag = True
        #     receive_data_full = ""
        #             if receive_data_full == receive_data_full:
        #                 face_recog.recycle_uart = False
        #             elif receive_data_full != receive_data_full:
        #                 face_recog.recycle_uart = True
        #                 break
        face_recog.check_face()
        if face_recog.request_Flag:
            face_recog.check_uart_data("RFL1\n")

        # if the `q` key was pressed, break from  the loop




    # do a bit of cleanup
    cv2.destroyAllWindows()
    print('finish')

