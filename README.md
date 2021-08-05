
# SMARTLOCK_PROJECT
## Face_Recognition_system
opencv, face_recognition, json, ... etc
## 현재 진행 상황
## 2021.04.28 개발 환경 구축
Pycharm Edition, Anaconda, VNC Viewer, Putty, Raspberry Pi imager..
## 2021.05.15 얼굴 탐지 수행 완료
Python OpenCV ----- Cam Open, Image wirte 
Python Dlib ------- Face detection algorithm ..


##2021.05.28 얼굴 인식 수행 완료
Python Face_Recognition-----Face_Recognition algorithm
[https://github.com/ageitgey/face_recognition/blob/master/README_Korean.md](https://github.com/ageitgey/face_recognition/blob/master/README_Korean.md "https://github.com/ageitgey/face_recognition/blob/master/README_Korean.md")

##2021.07.02 Raspberry Pi에 적용 완료
camera.py 
-->self.video = cv2.VideoCapture(0)를
self.video = cv2.VideoCapture(-1)로 수정해야함
프레임 안정적
but, 라즈베리파이 소자 매우 뜨거움
-->방열판 혹은 쿨러 장착 필수
[Raspberry Pi SSH,RFB 프로토콜 원격접속방법](http://https://www.youtube.com/watch?v=2Ub4RL0AWvE&t=328s "Raspberry Pi SSH,RFB 프로토콜 원격접속")

##2021.07.04 MQTT Test 완료
AWS에서 EC2 인스턴스를 생성한 후 가상 서버 구축
구축한 가상 서버를 이용 mosquitto 서버 구축
서버 외부 접속으로 서버 <> 라즈베리파이 간 통신 성공

##2021.07.08 어플로 데이터 전송 완료
MQTT 프로토콜 이용해 라즈베리파이, 서버, 어플간 데이터 통신 완료
사용자 및 위험인물이 카메라에 인식될 경우 어플에 사진 및 문자열 전송
사진은 바이트 배열로 전송 후 비트맵 형식으로 띄운다.

##2021.07.25 어플에서 장치로 사용자 변경 완료
MQTT 프로토콜 이용하여 어플에서 찍은 사진을 장치로 전송
장치에서 받은 사진을 인코딩 후 얼굴 인식 알고리즘
+추가적으로 다중 사용자 혹은 위험인물에 대한 코드 작성예정

##2021.08.06 어플에서 MCU로 제어를 위한 데이터 수신 완료
MQTT 프로토콜 이용 어플 -> 라즈베리파이 방향으로 데이터 전송
보안 방식 변경으로 데이터 규약은 SLW이고 데이터 타입은 문자열
필요시 데이터 타입의 변환도 고려

