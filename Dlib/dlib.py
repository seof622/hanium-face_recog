import os
import cv2
import dlib
import time
import numpy as np
import shutil
import pickle
import openface

class FaceDetector:
    def __init__(self, torch_net_model=None, img_dim=96, use_cuda=False, verbose=True):

        # 레이블과 index를 연결해주는 dictionary.
        self.label_dict = {}
        # 학습에 사용할 레이블들
        self.label = []
        # 학습에 사용할 데이터들
        self.data = []
        # 다음 번 레이블에 할당할 인덱스
        self.index = 0
        # 만약 True라면 실행되면서 로그를 출력한다.
        self.verbose = verbose

        # 만약 embedding추출용 토치 신경망을 설정하지 않으면 기본으로 설정한다.
        if torch_net_model is None:
            model = openface.TorchNeuralNet.defaultModel
        else:
            model = torch_net_model

        # 만약 토치 신경망이 존재하지 않으면 Exception을 발생시킨다.
        if not os.path.exists(model):
            raise Exception('Model does not exist.(' + model + ')')

        # 토치 신경망을 불러옴.
        self.log("Set torch net :", model)
        self.torch_net = openface.TorchNeuralNet(model=model, imgDim=img_dim, cuda=use_cuda)

        # 나중에 객체를 저장하고 불러올 때 사용하기 위해 파라매터를 저장해놓는다.
        self.torch_params = [model, img_dim, use_cuda]

        # 선형 분류기를 생성함.
        svm = cv2.ml.SVM_create()
        svm.setType(cv2.ml.SVM_C_SVC)
        svm.setKernel(cv2.ml.SVM_RBF)
        svm.setC(12.5)
        svm.setGamma(0.5)
        self.svm = svm
        self.log("Detector created")

    # 사용자가 직접 SVM을 설정할 수도 있음.
    def set_svm(self, svm):
        self.svm = svm

    # 주어진 디렉토리에 있는 모든 (정렬된)이미지에서 embedding을 추출하여 저장함.
    def append_dir(self, label, dir):
        self.log("Append directory :", dir)
        self.label_dict[self.index] = label

        count = 0

        for file_name in os.listdir(dir):
            file_path = os.path.join(dir, file_name)
            # embedding 추출
            feature = self.torch_net.forwardPath(file_path)
            self.data.append(feature)
            self.label.append(self.index)
            count += 1

        self.log(count, "data appended")
        self.log("Label :", label)
        self.log("Index :", self.index)
        self.log("")
        self.index += 1

    # 주어진 데이터에 레이블을 붙여서 저장함.
    def append_data(self, label, datas):
        self.label_dict[self.index] = label

        for data in datas:
            self.label.append(self.index)
            self.data.append(data)

        self.log(len(datas), "data appended")
        self.log("Label :", label)
        self.log("Index :", self.index)
        self.log("")
        self.index += 1

    # 모델을 학습시킴.
    def train_model(self):
        self.log("Start training...")
        start = time.time()

        assert len(self.data) is len(self.label)

        train_data = np.array(self.data, dtype=np.float32)
        train_label = np.array(self.label, dtype=np.int32)
        self.svm.train(train_data, cv2.ml.ROW_SAMPLE, train_label)
        self.log("Training finished in {0:.2f} second.\n".format(time.time() - start))

    # 주어진 정렬된 사진에 대해서 레이블을 반환함.
    def predict(self, img):
        assert img is not None
        feature = np.array([self.torch_net.forward(img)], dtype=np.float32)
        index = self.svm.predict(feature)[1][0][0]
        return self.label_dict[index]

    # 본 객체를 저장함. 파일을 나눠 저장하므로 dir에는 폴더 이름이 들어가야 함.
    # svm은 pickle로 저장이 안 되므로, 따로 저장함.
    # torch 역시 로드할 때 필요한 파라매터만 저장하고, 신경망 자체는 객체를 로드할 때 불러옴.
    def save(self, dir):
        if not os.path.exists(dir):
           os.mkdir(dir)
        self.svm.save(os.path.join(dir, 'svm'))
        svm_temp = self.svm
        torch_temp = self.torch_net
        self.svm = None
        self.torch_net = None
        with open(os.path.join(dir, 'detector'), 'wb') as file:
            pickle.dump(self, file)
        self.svm = svm_temp
        self.torch_net = torch_temp

    # 모델을 불러옴.
    @staticmethod
    def load(dir):
        assert os.path.exists(dir)
        with open(os.path.join(dir, 'detector'), 'rb') as file:
            detector = pickle.load(file)
            detector.svm = cv2.ml.SVM_load(os.path.join(dir, 'svm'))

            torch_params = detector.torch_params
            detector.torch_net = openface.TorchNeuralNet(torch_params[0], torch_params[1], torch_params[2])
            return detector

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.log('Exit')
        self.torch_net.__exit__(None, None, None)

    def log(self, *log):
        if self.verbose:
            for text in log:
                print(text, end=' ')
            print()