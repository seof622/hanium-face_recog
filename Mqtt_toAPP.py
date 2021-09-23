import os
from PIL import Image, ImageFile
import io
import paho.mqtt.client as mqtt
ImageFile.LOAD_TRUNCATED_IMAGES = True
class Mqtt_toAPP():

    def __init__(self):
        url = "54.201.98.240"
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_publish = self.on_publish
        client.on_subscribe = self.on_subscribe
        client.message_callback_add("set_person_user", self.user_encoding)
        client.message_callback_add("set_person_danger", self.danger_encoding)
        client.message_callback_add("TO_MCU", self.on_message_TO_MCU)
        client.connect(url, 1883)
        client.connect_async(url, 1883)

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

    def user_encoding(self, client, userdata, msg):
        User_Image = msg.payload
        User_Image_data = Image.open(io.BytesIO(User_Image))
        idx_User_Image = 0
        files = os.listdir(self.path_Picture_dir)
        if len(files) > 0 :
            for filename in files:
                name, ext = os.path.splitext(filename)
                if name.find('User') > 0:
                    if ext == '.jpg':
                        idx = name.split('User')
                        if idx_User_Image <= idx:
                            idx_User_Image = idx
        User_Image_data.save(self.path_Picture_dir + "/User" + str(idx_User_Image + 1) + ".jpg", 'jpeg')
        proc = os.system('python3 save_encoding.py')
        if proc == 0:
            print("Subprocess start")
        self.img_encoding()

    def danger_encoding(self, client, userdata, msg):
        Danger_Image = msg.payload
        Danger_Image_daga = Image.open(io.BytesIO(Danger_Image))
        idx_Danger_Image = 0
        files = os.listdir(self.path_Picture_dir)
        if len(files) > 0 :
            for filename in files:
                name, ext = os.path.splitext(filename)
                if name.find('Danger') > 0:
                    if ext == '.jpg':
                        idx = name.split('Danger')
                        if idx_Danger_Image <= idx:
                            idx_Danger_Image = idx
        Danger_Image_daga.save(self.path_Picture_dir + "/Danger" + str(idx_Danger_Image + 1) + ".jpg", 'jpeg')
        proc = os.system('python3 save_encoding.py')
        if proc == 0:
            print("Subprocess start")
        self.img_encoding()