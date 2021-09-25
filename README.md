
# SMARTLOCK_PROJECT
## Face_Recognition_system
opencv, face_recognition, json, ... etc
## 현재 진행 상황
## 2021.04.28 개발 환경 구축
Pycharm Edition, Anaconda, VNC Viewer, Putty, Raspberry Pi imager..
## 2021.05.15 얼굴 탐지 수행 완료
Python OpenCV ----- Cam Open, Image wirte 
Python Dlib ------- Face detection algorithm ..


## 2021.05.28 얼굴 인식 수행 완료
Python Face_Recognition-----Face_Recognition algorithm
[https://github.com/ageitgey/face_recognition/blob/master/README_Korean.md](https://github.com/ageitgey/face_recognition/blob/master/README_Korean.md "https://github.com/ageitgey/face_recognition/blob/master/README_Korean.md")

## 2021.07.02 Raspberry Pi에 적용 완료
camera.py 

-->self.video = cv2.VideoCapture(0)를

self.video = cv2.VideoCapture(-1)로 수정해야함

프레임 안정적

but, 라즈베리파이 소자 매우 뜨거움

-->방열판 혹은 쿨러 장착 필수

[Raspberry Pi SSH,RFB 프로토콜 원격접속방법](http://https://www.youtube.com/watch?v=2Ub4RL0AWvE&t=328s "Raspberry Pi SSH,RFB 프로토콜 원격접속")

## 2021.07.04 MQTT Test 완료

AWS에서 EC2 인스턴스를 생성한 후 가상 서버 구축

구축한 가상 서버를 이용 mosquitto 서버 구축

서버 외부 접속으로 서버 <> 라즈베리파이 간 통신 성공


## 2021.07.08 어플로 데이터 전송 완료
MQTT 프로토콜 이용해 라즈베리파이, 서버, 어플간 데이터 통신 완료

사용자 및 위험인물이 카메라에 인식될 경우 어플에 사진 및 문자열 전송

사진은 바이트 배열로 전송 후 비트맵 형식으로 띄운다.


## 2021.07.25 어플에서 장치로 사용자 변경 완료

MQTT 프로토콜 이용하여 어플에서 찍은 사진을 장치로 전송

장치에서 받은 사진을 인코딩 후 얼굴 인식 알고리즘

+추가적으로 다중 사용자 혹은 위험인물에 대한 코드 작성예정


## 2021.08.06 어플에서 MCU로 제어를 위한 데이터 수신 완료
MQTT 프로토콜 이용 어플 -> 라즈베리파이 방향으로 데이터 전송

보안 방식 변경으로 데이터 규약은 SLW이고 데이터 타입은 문자열

필요시 데이터 타입의 변환도 고려


## 2021.08.11 라즈베리파이 Uart 통신 구현 완료
데이터 통신 규약에 따라 MCU <-> Raspberry PI로 데이터 송수신 테스트 완료

--> MCU는 임시로 아두이노를 사용하여 test 진행

MCU와 앱 간 통신은 라즈베리파이를 통하여 진행하였고 모두 송수신 테스트 완료

 -> MCU에서 얼굴 인식 보안 해제 요청시 대략 20초 이내에 인증이 완료되어야 함

 -> MCU에서 어플 보안 해제 요청시 5회 이상 불일치하면 다시 시도해야 함

## 2021.08.21 위험인물 설정 코드 구현
앱에서 갤러리 혹은 사진촬영을 통하여 사용자/위험인물 구분하여 설정기능 구현

앱에서 구현된 기능에 따라 얼굴인식도 사용자와 위험인물 모두 인식 가능한 코드를 구현

But, 인물에 대한 설정시 OpenCV가 멈추는 현상은 동일 --> 멀티 프로세서 혹은 멀티 쓰레드 등 이용하여 해결 방안 고려


## 2021.09.22 얼굴인식 코드 수정
face-recognition의 경량화된 얼굴인식 코드로 수정 --> 얼굴인식 잘 되는 것 확인

이미지파일 인코딩하는 서브루틴 구축 --> 인코딩 하는데 메인 프로세스가 복잡해지는것을 방지

인코딩 값을 csv파일에 저장하여 다시 인코딩 값으로 불러오는 코드 작성 numpy이용

수정된 라즈베리파이는 Raspi_new.py에서 확인 가능


## 2021.09.24 사용자 & 위험인물 설정 test

기존 앱 상에서 Json을 통해 보낸 사용자 및 위험 인물 설정에 대한 데이터 오류 해결

--> Server의 Topic을 따로 생성하여 사용자 및 위험 인물의 데이터를 따로 받음

--> Json에서 Data의 value가 byte인데 toString하려고 하니까 b`1234 -> "1234"가 아닌 b'1234에 대한 문자열로 바뀌어서 오류 발생!

특정 환경에서 얼굴인식을 못하는 오류 해결책 필요

## 2021.09.26 사용자 & 위험인물 설정 test2

사용자 및 위험인물 설정 시 연산 속도 개선 작업

--> 앱에서 보낸 이미지에서 얼굴만 따로 잘라내어 face_encoding 연산 진행

--> face_encoding 연산은 빠르지만, 앞서 얼굴을 잘라내는 작업에서 시간 소요

--> 앱에서 보낼때 얼굴만 잘라서 전송하는 코드 작성 예정

--> 비콘 테스트 예정