# SCUBE_setting

import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import pandas as pd
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore

from PyQt5.QtWidgets import QListView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
import datetime
import time
import requests, json
import threading
import matplotlib.pyplot as plt

# 가속도 변위 함수관련 #####################


Fs = 100  # Sampling frequency
T = 1 / Fs  # Sample interval time

import math

S_sensor_type = '1'
S_Sample_Rate = '100'
S_S_filter = '0'
S_Sensitivity = '1000'
S_Capacity = '1.2'
S_AMP_CAL = '1.0'
S_Offset = '0.0'
S_Range = '1.1'
S_EXC_voltage = '5500'
S_G_factor = '2.1'
S_Trigger_value = '20'
S_T_P = '2'
S_D_A_M = '3'
S_F_T = '10'
S_Analysis_main = 'P2P'
S_Analysis_sub = 'RMS'

S_Save_file_type = '1'
S_Used_camera = '0'
S_NPT_period = '10'

S_RST_type = '0'  # 0: Warm boot  1: Cold boot

# -------------------------------------------------------
Save_time = []
R_sensor_type = '1'
R_Sample_Rate = '100'
R_S_filter = '0'
R_Sensitivity = '1000'
R_Capacity = '1.2'
R_AMP_CAL = '1.0'
R_Offset = '0.0'
R_Range = '1.1'
R_EXC_voltage = '3300'
R_G_factor = '2.1'
R_Trigger_value = '20'
R_T_P = '2'
R_D_A_M = '3'
R_F_T = '10'
R_Analysis_main = 'P2P'
R_Analysis_sub = 'RMS'

R_Save_file_type = '1'
R_Used_camera = '0'
R_NPT_period = '10'

R_RST_type = '0'  # 0: Warm boot  1: Cold boot

# -----------------------------------------------------------
ip = "210.105.85.3"

command_REQ = 'REQ0'

timedelay_value = 2

header_post = {
    "accept": "application/json",
    "content-type": "application/vnd.onem2m-res+xml; ty=4",
    "x-m2m-origin": "/0.2.481",
    "x-m2m-ri": "12345",
    "locale": "ko",
    "nmtype": "short",
    "cache-control": "no-cache",
    "Content-Length": "189",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "ko-KR,en,*",
    "User-Agent": "Mozilla/5.0"
}

header_get = {
    "accept": "application/xtml",
    "x-m2m-origin": "/0.2.481.1.21160310105204806",
    "x-m2m-ri": "12345",
    "nmtype": "long",
    "cache-control": "no-cache",
}

header_AE_DEL = {
    "Accept": "application/json",
    "x-m2m-origin": "/0.2.481",
    "x-m2m-ri": "12345"
}


def AE_Delet(ip, DeviceID, AEName, sel):  # 0:정상, 1:비정상 등록된 AE 삭제
    if sel == 0:
        url = URL_make(ip, DeviceID, AEName, 0)
    else:
        url = 'http://' + ip + ":7579" + AEName

    params_ae = {"rcn": "0"}
    res = requests.delete(url, headers=header_AE_DEL, params=params_ae)
    code = res.status_code  # 응답 코드
    status = res.raise_for_status()  # 200 OK 코드가 아닌 경우 에러 발동
    response_result = res.text  #
    return code, status, response_result


def URL_make(ip, DeviceID, AEName, ContainerName):
    '''
    DeviceID=0 : None
    DeviceID=1 : S_cube
    DeviceID=2 : iLOG-GW
    DeviceID=3 : OMS


    ContainerName=0 : None
    ContainerName=1 : ctrl
    ContainerName=2 : DeviceID=1 -> anal,    DeviceID=2 -> s-v,     DeviceID=3 -> s-v
    ContainerName=3 : DeviceID=1 -> rawe,                           DeviceID=3 -> d-inf
    ContainerName=4 : DeviceID=1 -> config,  DeviceID=2 ->config,   DeviceID=3 ->config

    '''
    url_init = 'http://' + ip + ":7579/mobius-yt"  # if DeviceID==0:

    if DeviceID == 1:  # S_cube
        url_init += "/smartcs:1:" + AEName  # if ContainerName==0:
        if ContainerName == 1:
            url_init += "/ctrl"
        elif ContainerName == 2:
            url_init += "/anal"
        elif ContainerName == 3:
            url_init += "/rawe"
        elif ContainerName == 4:  # 디바이스에 관련없이 config는 4로 고정
            url_init += "/config"
    if DeviceID == 2:  # iLOG-Beacon
        url_init += "/smartcs:2:" + AEName  # if ContainerName==0:
        if ContainerName == 1:
            url_init += "/ctrl"
        elif ContainerName == 2:
            url_init += "/s-v"
        elif ContainerName == 4:
            url_init += "/config"
    if DeviceID == 3:  # OMS
        url_init += "/smartcs:3:" + AEName  # if ContainerName==0:
        if ContainerName == 1:
            url_init += "/ctrl"
        elif ContainerName == 2:
            url_init += "/s-v"
        elif ContainerName == 3:
            url_init += "/d-inf"
        elif ContainerName == 4:
            url_init += "/config"
    return url_init


def make_post_command_body(command_string):
    body = '<?xml version="1.0" encoding="UTF-8"?><m2m:cin xmlns:m2m="http://www.onem2m.org/xml/protocols" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><cnf>text</cnf><con>'
    body = body + command_string + '</con></m2m:cin>'
    return body


def res_post(ip, DeviceID, AEName, command_string, timeout):
    res = requests.post(URL_make(ip, DeviceID, AEName, 1), headers=header_post,
                        data=make_post_command_body(command_string), timeout=timeout)
    code = res.status_code  # 응답 코드
    status = res.raise_for_status()  # 200 OK 코드가 아닌 경우 에러 발동
    response_result = res.text  #

    return code, status, response_result


def res_get_Instance_inform(ip, DeviceID, AEName, timeout, instance, data_num):
    url_get_root = URL_make(ip, DeviceID, AEName, instance)
    params_ae = {"rcn": "4", "ty": "4", "lim": str(data_num)}
    res = requests.get(url_get_root, headers=header_get, params=params_ae, timeout=timeout)

    code = res.status_code  # 응답 코드
    status = res.raise_for_status()  # 200 OK 코드가 아닌 경우 에러 발동
    text = res.text  #
    if text:
        y = json.loads(text)
        ff = y.get('m2m:cin')
        # print('ff=',text)
        if len(text) > 50:
            con = ff[0]['con']
            config_inform = con.split(',')
            ct = ff[0]['ct']
        else:
            con = '-'
            config_inform = '-'
            ct = '19990101T111111'
    else:
        config_inform = 'Error'
        ct = '19990101T111111'

    return code, status, config_inform, ct


def time_str_convert(time_str):
    yy = time_str[0:4]
    mm = time_str[4:6]
    dd = time_str[6:8]
    HH = time_str[9:11]
    MM = time_str[11:13]
    SS = time_str[13:15]
    temp = yy + '-' + mm + '-' + dd + ' ' + HH + ':' + MM + ':' + SS

    dt1 = datetime.datetime.strptime(temp, '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    result = now - dt1  # +datetime.timedelta(hours=9)
    return result, dt1


######################################################################################################################################################################################################

AE_name = 'cs300'

anal_data_fst = np.zeros(10)
anal_data_snd = np.zeros(10)
AE_Temp = np.zeros(10)
AE_Humi = np.zeros(10)
gg = 0


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        global curve2, curve1
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Smart c&S...S_CUBE Setting  v0.1')
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.login_widget = LoginWidget(self)

        self.login_widget.label_image.setPixmap(QtGui.QPixmap("smartcs.png"))

        self.login_widget.button_Setting_Value_Call.clicked.connect(self.button_Setting_Value_Call)

        self.login_widget.button_CMD0.clicked.connect(self.button_CMD0_Call)

        self.login_widget.button_CMD1.clicked.connect(self.button_CMD1_Call)

        self.login_widget.button_CMD2.clicked.connect(self.button_CMD2_Call)

        self.login_widget.button_CMD3.clicked.connect(self.button_CMD3_Call)

        self.login_widget.button_RST.clicked.connect(self.button_RST_Call)

        self.login_widget.button_TEST.clicked.connect(self.button_TEST_Call)

        data = pd.read_csv("SCUBE_LIST.csv", engine='python')
        ff = data.shape
        for i in range(0, ff[0]):
            data1 = data['ID'][i] + ',' + data['DES'][i]
            self.login_widget.ComboBox_AE_list.addItems([data1])

        self.login_widget.ComboBox_AE_list.currentIndexChanged.connect(self.ComboBox_AE_list_selectionchange)

        curve1 = self.login_widget.plot1.plot(pen='y')
        curve1 = self.login_widget.plot2.plot(pen='y')
        self.central_widget.addWidget(self.login_widget)

    def ComboBox_AE_list_selectionchange(self):
        C_AE_Name = self.login_widget.ComboBox_AE_list.currentText().split(',')
        self.login_widget.lineEdit_AE_name.setText(C_AE_Name[0])

    def anal_data_call(self):
        global anal_data_fst, anal_data_snd, AE_Humi, AE_Temp, rawe_data_list, rawe_data, nowdate, nowtime, F_T_reponse_time, gg, Pre_time, F_T_reponse_onoff
        global current_ana1_value, current_ana2_value, current_temp_value, current__Humi_value, current__event_value, device_setting_time

        AE_name = self.login_widget.lineEdit_AE_name.text()
        print('AE_name', AE_name)
        c = datetime.time(hour=0, minute=0, second=int(R_F_T))

        F_T_reponse_onoff = "N.G"
        try:
            code, status, config_inform, ct = res_get_Instance_inform(ip, 1, AE_name, 50, 2,
                                                                      1)  # “ 시간, P-P, RMS, S-E, GPS-L, S-T-V, S-H-V, D-inf”

            if len(config_inform) > 10:

                # self.login_widget.textEdit_command.append('>> Analysis Data << '+ AE_name+': '+str(config_inform))

                result, dt = time_str_convert(config_inform[0])

                if gg == 0:
                    Pre_time = dt
                    gg = 1
                else:
                    F_T_reponse_time = dt - Pre_time

                    print(F_T_reponse_time, c, F_T_reponse_time.seconds)

                    if F_T_reponse_time.seconds == int(R_F_T):
                        F_T_reponse_onoff = "O.K"
                        self.login_widget.textEdit_command.append(
                            '>> Analysis Data << ' + AE_name + ': ' + '현재시간과의 차이 :' + str(
                                result) + '  데이터 저장 시간 간격(sec) :' + str(F_T_reponse_time) + '.....' + F_T_reponse_onoff)
                    else:
                        self.login_widget.textEdit_command.append(
                            '>> Analysis Data << ' + AE_name + ': ' + '현재시간과의 차이 :' + str(
                                result) + '  데이터 저장 시간 간격(sec) :' + str(F_T_reponse_time) + '.....' + F_T_reponse_onoff)

                    gg = 0

                device_setting_time = result

                anal_data_fst = np.roll(anal_data_fst, -1)
                anal_data_fst[-1] = float(config_inform[1])
                current_ana1_value = float(config_inform[1])

                anal_data_snd = np.roll(anal_data_snd, -1)
                anal_data_snd[-1] = float(config_inform[2])
                current_ana2_value = float(config_inform[2])

                AE_Temp = np.roll(AE_Temp, -1)
                AE_Temp[-1] = float(config_inform[8])
                current_temp_value = float(config_inform[8])

                AE_Humi = np.roll(AE_Humi, -1)
                AE_Humi[-1] = float(config_inform[9])
                current__Humi_value = float(config_inform[9])
                current__event_value = int(config_inform[3])
                if int(config_inform[3]) == 1:

                    code, status, rawe_data, ct = res_get_Instance_inform(ip, 1, AE_name, 50, 3, 1)
                    if len(rawe_data) > 100:
                        self.login_widget.plot4.clear()
                        event_time = rawe_data[0]
                        del rawe_data[0]
                        rawe_data_list = []
                        for item in rawe_data:
                            rawe_data_list.append(float(item))
                        try:
                            self.login_widget.plot4.plot(rawe_data_list, pen='y')
                            self.login_widget.plot4.enableAutoRange('xy', True)
                        except ValueError:  # raised if `y` is empty.
                            pass

            self.login_widget.plot1.clear()
            self.login_widget.plot2.clear()
            self.login_widget.plot3.clear()
            try:
                self.login_widget.plot1.plot(anal_data_fst, pen='y')
            except ValueError:  # raised if `y` is empty.
                pass
            '''
            for i in range(len(anal_data_fst)):

                    ## Draw an arrowhead next to the text box
                    arrow = pg.ArrowItem(pos=(i,anal_data_fst[i]), angle=-45)
                    self.login_widget.plot1.addItem(arrow)
                    text = pg.TextItem(str(round(anal_data_fst[i],4)))
                    self.login_widget.plot1.addItem(text)
                    text.setPos(i, anal_data_fst[i])
            '''
            try:
                self.login_widget.plot2.plot(anal_data_snd, pen='y')
            except ValueError:  # raised if `y` is empty.
                pass
            '''
            for i in range(len(anal_data_snd)):

                    ## Draw an arrowhead next to the text box
                    arrow = pg.ArrowItem(pos=(i,anal_data_snd[i]), angle=-45)
                    self.login_widget.plot2.addItem(arrow)
                    text = pg.TextItem(str(round(anal_data_snd[i],4)))
                    self.login_widget.plot2.addItem(text)
                    text.setPos(i, anal_data_snd[i])
            '''
            try:
                self.login_widget.plot3.plot(AE_Temp, pen='y')
            except ValueError:  # raised if `y` is empty.
                pass
            '''
            for i in range(len(AE_Temp)):

                    ## Draw an arrowhead next to the text box
                    arrow = pg.ArrowItem(pos=(i,AE_Temp[i]), angle=-45)
                    self.login_widget.plot3.addItem(arrow)
                    text = pg.TextItem(str(round(AE_Temp[i],4)))
                    self.login_widget.plot3.addItem(text)
                    text.setPos(i, AE_Temp[i])
            '''
            # self.login_widget.plot2.plot(AE_Humi,pen='y')
            ptr = 0
            if ptr == 0:
                self.login_widget.plot1.enableAutoRange('xy',
                                                        True)  ## stop auto-scaling after the first data set is plotted
                self.login_widget.plot2.enableAutoRange('xy', True)
                self.login_widget.plot3.enableAutoRange('xy', True)

            ptr += 1

            QtCore.QCoreApplication.processEvents()

        except requests.Timeout as err:  # The request timed out.
            self.login_widget.textEdit_command.append('>> Timeout Error ')
        except requests.HTTPError as err:
            self.login_widget.textEdit_command.append('>> HTTP Error ')

        threading.Timer(int(R_F_T), self.anal_data_call).start()

    def button_TEST_Call(self):

        AE_name = self.login_widget.lineEdit_AE_name.text()

        # '시스템 시간, 프랫폼 연결,디바이스 연결,온도값,습도값'
        threading.Timer(int(R_F_T), self.anal_data_call).cancel()

        self.login_widget.textEdit_command.append('>> TEST: ' + AE_name + '   Step #1 : Config setting test >> CMD0')

        config_setting_relsut = 0

        for i in range(2):
            self.login_widget.ComboBox_Sensor_Type.setCurrentIndex(i)
            QtCore.QCoreApplication.processEvents()
            self.login_widget.textEdit_command.append(
                '>> Sensor type change : ' + self.login_widget.ComboBox_Sensor_Type.currentText())
            QtCore.QCoreApplication.processEvents()
            time.sleep(timedelay_value)
            result, result_test = self.button_CMD0_Call()
            time.sleep(timedelay_value)
            self.login_widget.textEdit_command.append('>> result : ' + result_test)
            QtCore.QCoreApplication.processEvents()
        for i in range(2):
            self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(i)
            QtCore.QCoreApplication.processEvents()
            self.login_widget.textEdit_command.append(
                '>> Sampling Rate change : ' + self.login_widget.ComboBox_Sample_Rate.currentText())
            QtCore.QCoreApplication.processEvents()
            time.sleep(timedelay_value)
            result, result_test = self.button_CMD0_Call()
            time.sleep(timedelay_value)
            self.login_widget.textEdit_command.append('>> result : ' + result_test)
            QtCore.QCoreApplication.processEvents()

        '''    
        for i in range(3):
            k=50+i*50
            self.login_widget.lineEdit_Sensitivity.setText(str(k))
            QtCore.QCoreApplication.processEvents()
            self.login_widget.textEdit_command.append('>> Sampling Rate change : '+self.login_widget.lineEdit_Sensitivity.text())
            QtCore.QCoreApplication.processEvents()
            time.sleep(timedelay_value)
            result,result_test=self.button_CMD0_Call()
            time.sleep(timedelay_value)
            self.login_widget.textEdit_command.append('>> result : '+result_test) 
            QtCore.QCoreApplication.processEvents()
         '''
        self.login_widget.textEdit_command.append('>> TEST: ' + AE_name + '   Step #2 : Config setting test >> CMD1')

        for i in range(2):
            self.login_widget.ComboBox_F_T.setCurrentIndex(i + 1)
            self.login_widget.ComboBox_D_A_D.setCurrentIndex(i)
            QtCore.QCoreApplication.processEvents()
            self.login_widget.textEdit_command.append(
                '>> F-T & D_A_D change : ' + self.login_widget.ComboBox_F_T.currentText())
            QtCore.QCoreApplication.processEvents()
            time.sleep(timedelay_value)
            result, result_test = self.button_CMD1_Call()
            time.sleep(timedelay_value)
            self.login_widget.textEdit_command.append('>> result : ' + result_test)
            QtCore.QCoreApplication.processEvents()

        self.login_widget.textEdit_command.append('>> TEST: ' + AE_name + '   Step #2 : Config setting test >> CMD2')
        for i in range(2):
            self.login_widget.ComboBox_Trigger_value.setCurrentIndex(i + 2)
            QtCore.QCoreApplication.processEvents()
            self.login_widget.textEdit_command.append(
                '>> Trigger_value change : ' + self.login_widget.ComboBox_Trigger_value.currentText())
            QtCore.QCoreApplication.processEvents()
            time.sleep(timedelay_value)
            result, result_test = self.button_CMD2_Call()
            time.sleep(timedelay_value)
            self.login_widget.textEdit_command.append('>> result : ' + result_test)
            QtCore.QCoreApplication.processEvents()

            # CMDO 디폴트 세팅
        self.login_widget.ComboBox_Sensor_Type.setCurrentIndex(0)
        self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(1)
        self.login_widget.lineEdit_Sensitivity.setText('1000.0')
        self.login_widget.lineEdit_AMP_CAL.setText('1.0')
        self.login_widget.lineEdit_Offset.setText('0.0')
        self.login_widget.lineEdit_Range.setText('1.2')
        self.login_widget.lineEdit_Capacity.setText('1.2')
        result, result_test = self.button_CMD0_Call()
        time.sleep(timedelay_value)
        # CMD1 디폴트 세팅
        self.login_widget.ComboBox_F_T.setCurrentIndex(1)
        self.login_widget.ComboBox_D_A_D.setCurrentIndex(2)
        result, result_test = self.button_CMD1_Call()
        time.sleep(timedelay_value)
        # CMD1 디폴트 세팅
        self.login_widget.ComboBox_Trigger_value.setCurrentIndex(4)
        self.login_widget.ComboBox_T_P.setCurrentIndex(1)
        self.login_widget.ComboBox_Analysis_Main.setCurrentIndex(1)
        self.login_widget.ComboBox_Analysis_Sub.setCurrentIndex(2)
        result, result_test = self.button_CMD2_Call()
        time.sleep(timedelay_value)

        # current_temp_value,current__Humi_value,current__event_value,device_setting_time,current_ana1_value,current_ana2_value
        # 온도 데이터 체크
        if current_temp_value >= 10 and current_temp_value < 50:
            self.login_widget.textEdit_command.append('>> 온도 데이터 체크 : ' + str(current_temp_value) + '.......O.K')
        else:
            self.login_widget.textEdit_command.append('>> 온도 데이터 체크 : ' + str(current_temp_value) + '.......N.G')
            # 습도 데이터 체크
        if current__Humi_value >= 10 and current__Humi_value < 90:
            self.login_widget.textEdit_command.append('>> 습도 데이터 체크 : ' + str(current__Humi_value) + '.......O.K')
        else:
            self.login_widget.textEdit_command.append('>> 습도 데이터 체크 : ' + str(current__Humi_value) + '.......N.G')

        print(current_ana2_value)

        ### ACC의  Off-set, 데이터 품질 테스트
        self.login_widget.lineEdit_Offset.setText(str(current_ana2_value))
        QtCore.QCoreApplication.processEvents()
        time.sleep(timedelay_value)
        result, result_test = self.button_CMD0_Call()

        while True:
            if current_ana2_value > 0.005:
                self.login_widget.textEdit_command.append(
                    '>> off set & data 노이즈 레벨 TEST : AVG =' + str(current_ana2_value) + '.......N.G')
            else:
                self.login_widget.textEdit_command.append(
                    '>> off set & data 노이즈 레벨 TEST : AVG =' + str(current_ana2_value) + '.......O.K')
                break
            time.sleep(timedelay_value)

            ### Sensor type 설정 Test

        self.anal_data_call()

    def button_RST_Call(self):
        AE_name = self.login_widget.lineEdit_AE_name.text()

        self.login_widget.textEdit_command.append('>> ' + AE_name + '   Reset [Warm or Cool] :')

        R_RST_type = str(self.login_widget.ComboBox_RST.currentIndex())  # 0: Warm boot  1: Cold boot

        command_str = 'RST0' + ',' + R_RST_type

        code, status, response_result = res_post(ip, 1, AE_name, command_str, 20)

        self.login_widget.textEdit_command.append('>> ' + command_str)
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        code, status, response_result = res_post(ip, 1, AE_name, command_REQ, 20)
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   REQ0 :')
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        time.sleep(timedelay_value)
        self.button_Setting_Value_Call()

    def button_CMD3_Call(self):
        AE_name = self.login_widget.lineEdit_AE_name.text()

        self.login_widget.textEdit_command.append('>> ' + AE_name + '   CMD3 :')

        S_Save_file_type = str(self.login_widget.ComboBox_F_S_T.currentIndex())  # ["저장안함", "CSV","Bin"]

        S_Used_camera = str(self.login_widget.ComboBox_Camera.currentIndex())  # ["사용안함", "사용"]

        S_NPT_period = str(self.login_widget.ComboBox_NTP.currentIndex())  # ["10", "20", "30", "40", "50","60"]

        command_str = 'CMD3' + S_Save_file_type + ',' + S_Used_camera + ',' + S_NPT_period

        code, status, response_result = res_post(ip, 1, AE_name, command_str, 20)

        self.login_widget.textEdit_command.append('>> ' + command_str)
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        code, status, response_result = res_post(ip, 1, AE_name, command_REQ, 20)
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   REQ0 :')
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        time.sleep(timedelay_value)
        self.button_Setting_Value_Call()

    def button_CMD2_Call(self):
        AE_name = self.login_widget.lineEdit_AE_name.text()

        self.login_widget.textEdit_command.append('>> ' + AE_name + '   CMD2 :')

        S_Trigger_value = self.login_widget.ComboBox_Trigger_value.currentText()  # ["1", "3", "5","8","10","20","30","40","50","60","70","80","90","100"]

        S_T_P = str(self.login_widget.ComboBox_T_P.currentIndex() + 1)

        S_Analysis_main = self.login_widget.ComboBox_Analysis_Main.currentText()

        S_Analysis_sub = self.login_widget.ComboBox_Analysis_Sub.currentText()

        command_str = 'CMD2' + S_Trigger_value + ',' + S_T_P + ',' + S_Analysis_main + ',' + S_Analysis_sub

        code, status, response_result = res_post(ip, 1, AE_name, command_str, 20)

        self.login_widget.textEdit_command.append('>> ' + command_str)
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        code, status, response_result = res_post(ip, 1, AE_name, command_REQ, 20)
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   REQ0 :')
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        time.sleep(timedelay_value)
        self.button_Setting_Value_Call()

        result = 0
        if S_Trigger_value == R_Trigger_value:
            result = result + 1
        if S_T_P == R_T_P:
            result = result + 1

        print('CMD2 result:', result)
        if result == 2:
            self.login_widget.textEdit_command.append('>> Result :  O.K')
            result_test = 'O.K'
        else:
            self.login_widget.textEdit_command.append('>> Result :  N.G')
            result_test = 'N.G'

        return result, result_test

    def button_CMD1_Call(self):
        AE_name = self.login_widget.lineEdit_AE_name.text()
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   CMD1 :')

        S_D_A_M = str(self.login_widget.ComboBox_D_A_D.currentIndex() + 1)

        S_F_T = self.login_widget.ComboBox_F_T.currentText()  # ["1","5", "10", "20","30","60","5분","10분","30분","1시간"]

        command_str = 'CMD1' + S_D_A_M + ',' + S_F_T

        code, status, response_result = res_post(ip, 1, AE_name, command_str, 20)

        self.login_widget.textEdit_command.append('>> ' + command_str)
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        code, status, response_result = res_post(ip, 1, AE_name, command_REQ, 20)
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   REQ0 :')
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)
        time.sleep(timedelay_value)
        self.button_Setting_Value_Call()

        result = 0
        if S_D_A_M == R_D_A_M:
            result = result + 1
        if S_F_T == R_F_T:
            result = result + 1

        print('CMD1 result:', result)
        if result == 2:
            self.login_widget.textEdit_command.append('>> Result :  O.K')
            result_test = 'O.K'
        else:
            self.login_widget.textEdit_command.append('>> Result :  N.G')
            result_test = 'N.G'

        return result, result_test

    def button_CMD0_Call(self):
        AE_name = self.login_widget.lineEdit_AE_name.text()

        self.login_widget.textEdit_command.append('>> ' + AE_name + '   CMD0 :')

        S_sensor_type = str(self.login_widget.ComboBox_Sensor_Type.currentIndex())

        S_Sample_Rate = self.login_widget.ComboBox_Sample_Rate.currentText()

        S_S_filter = str(self.login_widget.ComboBox_Filter_Onoff.currentIndex())

        S_Sensitivity = self.login_widget.lineEdit_Sensitivity.text()
        S_Capacity = self.login_widget.lineEdit_Capacity.text()
        S_AMP_CAL = self.login_widget.lineEdit_AMP_CAL.text()
        S_Offset = self.login_widget.lineEdit_Offset.text()
        S_Range = self.login_widget.lineEdit_Range.text()
        S_EXC_voltage = self.login_widget.lineEdit_EXC_voltage.text()
        S_G_factor = self.login_widget.lineEdit_G_factor.text()

        command_str = 'CMD0' + S_Sample_Rate + '-' + S_sensor_type + '-' + S_S_filter + ',' + S_Sensitivity + ',' + S_Capacity + ',' + S_AMP_CAL + ',' + S_Offset + ',' + S_Range + ',' + S_EXC_voltage + ',' + S_G_factor

        code, status, response_result = res_post(ip, 1, AE_name, command_str, 20)

        self.login_widget.textEdit_command.append('>> ' + command_str)
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        self.login_widget.textEdit_command.append('>> ' + response_result)

        code, status, response_result = res_post(ip, 1, AE_name, command_REQ, 20)
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   REQ0 :')
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        # self.login_widget.textEdit_command.append('>> '+response_result)

        time.sleep(timedelay_value)
        self.button_Setting_Value_Call()

        result = 0
        if S_sensor_type == R_sensor_type:
            result = result + 1
        if S_Sample_Rate == R_Sample_Rate:
            result = result + 1
        if S_Sensitivity == R_Sensitivity:
            result = result + 1
        if S_S_filter == R_S_filter:
            result = result + 1
        if S_Sensitivity == R_Sensitivity:
            result = result + 1
        if S_Capacity == R_Capacity:
            result = result + 1
        if S_AMP_CAL == R_AMP_CAL:
            result = result + 1
        if S_Offset == R_Offset:
            result = result + 1

        if S_Range == R_Range:
            result = result + 1
        if S_EXC_voltage == R_EXC_voltage:
            result = result + 1
        if S_G_factor == R_G_factor:
            result = result + 1

        print('CMD0 result:', result)
        if result == 11:
            self.login_widget.textEdit_command.append('>> Result :  O.K')
            result_test = 'O.K'
        else:
            self.login_widget.textEdit_command.append('>> Result :  N.G')
            result_test = 'N.G'

        return result, result_test

    def button_Setting_Value_Call(self):

        global Save_time, R_sensor_type, R_Sample_Rate, R_S_filter, R_Sensitivity, R_Capacity, R_AMP_CAL, R_Offset, R_Range, R_EXC_voltage, R_G_factor, R_Trigger_value
        global R_T_P, R_D_A_M, R_F_T, R_Analysis_main, R_Analysis_sub, R_Save_file_type, R_Used_camera, R_NPT_period, R_RST_type, config_settinf_reponse_time

        AE_name = self.login_widget.lineEdit_AE_name.text()
        code, status, response_result = res_post(ip, 1, AE_name, command_REQ, 20)
        self.login_widget.textEdit_command.append('>> ' + AE_name + '   REQ0 :')
        self.login_widget.textEdit_command.append('>> code :' + str(code))
        # self.login_widget.textEdit_command.append('>> '+response_result)

        self.login_widget.textEdit_command.append('>> ' + AE_name + '   get setting value :')
        try:
            code, status, config_inform, ct = res_get_Instance_inform(ip, 1, AE_name, 20, 4, 1)

            self.login_widget.textEdit_command.append('>> code :' + str(code))
            self.login_widget.textEdit_command.append('>> status :' + str(status))
            self.login_widget.textEdit_command.append('>> Data value or setting :' + str(config_inform))
            print(ct)

            result, dt1 = time_str_convert(ct)
            dt1 = dt1 + datetime.timedelta(hours=9)
            config_setting_reponse_time = datetime.datetime.now() - dt1
            self.login_widget.textEdit_command.append(
                '>> Config file last update time :' + str(dt1) + "    현재로부터 : " + str(config_setting_reponse_time))

            print('config_inform', config_inform)
            if len(config_inform) > 10:
                self.login_widget.textEdit_command.append('>> Config file call : Success!!')
                Save_time = config_inform[0]
                R_sensor_type = config_inform[1]
                R_Sample_Rate = config_inform[2]
                R_S_filter = config_inform[3]
                R_Sensitivity = config_inform[4]
                R_Capacity = config_inform[5]
                R_AMP_CAL = config_inform[6]
                R_Offset = config_inform[7]
                R_Range = config_inform[8]
                R_EXC_voltage = config_inform[9]
                R_G_factor = config_inform[10]
                R_Trigger_value = config_inform[11]
                R_T_P = config_inform[12]
                R_D_A_M = config_inform[13]
                R_F_T = config_inform[14]
                print('R_F_T', R_F_T)

                R_Analysis_main = 'P2P'
                R_Analysis_sub = 'RMS'

                R_Save_file_type = '1'
                R_Used_camera = '0'
                R_NPT_period = '10'

                R_RST_type = '0'  # 0: Warm boot  1: Cold boot

                self.login_widget.ComboBox_Sensor_Type.setCurrentIndex(int(R_sensor_type))
                if int(R_Sample_Rate) == 10:
                    self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(0)
                elif int(R_Sample_Rate) == 50:
                    self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(1)
                elif int(R_Sample_Rate) == 100:
                    self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(2)
                elif int(R_Sample_Rate) == 150:
                    self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(3)
                elif int(R_Sample_Rate) == 200:
                    self.login_widget.ComboBox_Sample_Rate.setCurrentIndex(4)

                if int(R_S_filter) == 0:
                    self.login_widget.ComboBox_Filter_Onoff.setCurrentIndex(0)
                elif int(R_S_filter) == 1:
                    self.login_widget.ComboBox_Filter_Onoff.setCurrentIndex(1)

                self.login_widget.lineEdit_Sensitivity.setText(R_Sensitivity)
                self.login_widget.lineEdit_Capacity.setText(R_Capacity)
                self.login_widget.lineEdit_AMP_CAL.setText(R_AMP_CAL)
                self.login_widget.lineEdit_Offset.setText(R_Offset)
                self.login_widget.lineEdit_Range.setText(R_Range)
                self.login_widget.lineEdit_EXC_voltage.setText(R_EXC_voltage)
                self.login_widget.lineEdit_G_factor.setText(R_G_factor)

                if int(R_F_T) == 1:  # ["1","5", "10", "20","30","60","5분","10분","30분","1시간"]
                    self.login_widget.ComboBox_F_T.setCurrentIndex(0)
                elif int(R_F_T) == 5:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(1)
                elif int(R_F_T) == 10:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(2)
                elif int(R_F_T) == 20:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(3)
                elif int(R_F_T) == 30:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(4)
                elif int(R_F_T) == 60:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(5)
                elif int(R_F_T) == 300:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(6)
                elif int(R_F_T) == 600:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(7)
                elif int(R_F_T) == 1800:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(8)
                elif int(R_F_T) == 3600:
                    self.login_widget.ComboBox_F_T.setCurrentIndex(9)

                    # ["realtime(MQTT)", "NodeZip(DB)", "MQTT+DB","KT(IoTMakers)","MQTT+IoTMakers","DB+IoTMakers","디바이스 정지"]
                self.login_widget.ComboBox_D_A_D.setCurrentIndex(int(R_D_A_M) - 1)
                print(int(R_D_A_M))
                if int(R_Trigger_value) == 1:  # ["1", "3", "5","8","10","20","30","40","50","60","70","80","90","100"]
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(0)
                elif int(R_Trigger_value) == 3:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(1)
                elif int(R_Trigger_value) == 5:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(2)
                elif int(R_Trigger_value) == 20:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(3)
                elif int(R_Trigger_value) == 30:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(4)
                elif int(R_Trigger_value) == 40:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(5)
                elif int(R_Trigger_value) == 50:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(6)
                elif int(R_Trigger_value) == 60:
                    self.login_widget.ComboBox_Trigger_value.setCurrentIndex(7)

                if int(R_T_P) == 1:  # ["트리거 이벤트 발생시", "주기적으로"]
                    self.login_widget.ComboBox_T_P.setCurrentIndex(0)
                elif int(R_T_P) == 2:
                    self.login_widget.ComboBox_T_P.setCurrentIndex(1)

                '''
                self.login_widget.ComboBox_Analysis_Main.addItems(["P to P", "RMS", "AVG", "STD"])
                self.login_widget.ComboBox_Analysis_Sub.addItems(["P to P", "RMS", "AVG", "STD"])


                self.login_widget.ComboBox_F_S_T.addItems(["저장안함", "CSV","Bin"])
                self.login_widget.ComboBox_Camera.addItems(["사용안함", "사용"])
                self.login_widget.ComboBox_NTP.addItems(["10", "20", "30", "40", "50","60"])

                self.login_widget.ComboBox_RST.addItems(["Warm", "Cool"])
                '''
            else:
                self.login_widget.textEdit_command.append('>> Config file call : Fail')
        except requests.Timeout as err:  # The request timed out.
            self.login_widget.textEdit_command.append('>> Timeout Error ')
        except requests.HTTPError as err:
            self.login_widget.textEdit_command.append('>> HTTP Error ')
        return config_setting_reponse_time.seconds


class LoginWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)

        self.setWindowTitle('Smart c&S...File load for display and analysis v0.1')

        self.label_AE_list = QtGui.QLabel('S-Cube List :')
        self.ComboBox_AE_list = QtGui.QComboBox()
        layoutH0 = QtGui.QHBoxLayout()
        layoutH0.addWidget(self.label_AE_list)
        layoutH0.addWidget(self.ComboBox_AE_list)

        self.lineEdit_AE_name = QtGui.QLineEdit('cs300')

        self.button_Setting_Value_Call = QtGui.QPushButton('Setting Value Call')

        self.label_Sensor_Type = QtGui.QLabel('Sensor type :')
        self.ComboBox_Sensor_Type = QtGui.QComboBox()
        self.ComboBox_Sensor_Type.addItems(
            ["Acc-x", "Acc-y", "Acc-z", "Acc-3A", "변혈율 센서", "변위센서P", "하중계", "기울기 센서", "ACC-Strain", "ACC-IEPE", "수위계",
             "지중경사계", "풍압계", "풍향풍속"])
        self.ComboBox_Sensor_Type.setCurrentIndex(0)
        layoutH1 = QtGui.QHBoxLayout()
        layoutH1.addWidget(self.label_Sensor_Type)
        layoutH1.addWidget(self.ComboBox_Sensor_Type)

        self.label_Sample_Rate = QtGui.QLabel('Sample Rate :')
        self.ComboBox_Sample_Rate = QtGui.QComboBox()
        self.ComboBox_Sample_Rate.addItems(["10", "50", "100", "150", "200"])
        self.ComboBox_Sample_Rate.setCurrentIndex(1)
        layoutH2 = QtGui.QHBoxLayout()
        layoutH2.addWidget(self.label_Sample_Rate)
        layoutH2.addWidget(self.ComboBox_Sample_Rate)

        self.label_Filter_Onoff = QtGui.QLabel('Filter :')
        self.ComboBox_Filter_Onoff = QtGui.QComboBox()
        self.ComboBox_Filter_Onoff.addItems(["Off", "On"])
        self.ComboBox_Filter_Onoff.setCurrentIndex(0)
        layoutH3 = QtGui.QHBoxLayout()
        layoutH3.addWidget(self.label_Filter_Onoff)
        layoutH3.addWidget(self.ComboBox_Filter_Onoff)

        self.label_Sensitivity = QtGui.QLabel('Sensitivity :')
        self.lineEdit_Sensitivity = QtGui.QLineEdit('1000')
        layoutH4 = QtGui.QHBoxLayout()
        layoutH4.addWidget(self.label_Sensitivity)
        layoutH4.addWidget(self.lineEdit_Sensitivity)

        self.label_Capacity = QtGui.QLabel('Capacity :')
        self.lineEdit_Capacity = QtGui.QLineEdit('0.0')
        layoutH5 = QtGui.QHBoxLayout()
        layoutH5.addWidget(self.label_Capacity)
        layoutH5.addWidget(self.lineEdit_Capacity)

        self.label_AMP_CAL = QtGui.QLabel('AMP.CAL :')
        self.lineEdit_AMP_CAL = QtGui.QLineEdit('1.0')
        layoutH6 = QtGui.QHBoxLayout()
        layoutH6.addWidget(self.label_AMP_CAL)
        layoutH6.addWidget(self.lineEdit_AMP_CAL)

        self.label_Offset = QtGui.QLabel('Offset :')
        self.lineEdit_Offset = QtGui.QLineEdit('0.0')
        layoutH7 = QtGui.QHBoxLayout()
        layoutH7.addWidget(self.label_Offset)
        layoutH7.addWidget(self.lineEdit_Offset)

        self.label_Rang = QtGui.QLabel('Range :')
        self.lineEdit_Range = QtGui.QLineEdit('50.0')
        layoutH8 = QtGui.QHBoxLayout()
        layoutH8.addWidget(self.label_Rang)
        layoutH8.addWidget(self.lineEdit_Range)

        self.label_EXC_voltage = QtGui.QLabel('EXC voltage :')
        self.lineEdit_EXC_voltage = QtGui.QLineEdit('3300')
        layoutH9 = QtGui.QHBoxLayout()
        layoutH9.addWidget(self.label_EXC_voltage)
        layoutH9.addWidget(self.lineEdit_EXC_voltage)

        self.label_G_factor = QtGui.QLabel('G-factor :')
        self.lineEdit_G_factor = QtGui.QLineEdit('2.1')
        layoutH10 = QtGui.QHBoxLayout()
        layoutH10.addWidget(self.label_G_factor)
        layoutH10.addWidget(self.lineEdit_G_factor)

        self.button_CMD0 = QtGui.QPushButton('적용(CMD0)')

        layoutV1 = QtGui.QVBoxLayout()
        layoutV1.addLayout(layoutH0)
        layoutV1.addSpacing(20)
        layoutV1.addWidget(self.lineEdit_AE_name)
        layoutV1.addSpacing(20)
        layoutV1.addWidget(self.button_Setting_Value_Call)
        layoutV1.addSpacing(10)
        layoutV1.addLayout(layoutH1)
        layoutV1.addLayout(layoutH2)
        layoutV1.addLayout(layoutH3)
        layoutV1.addLayout(layoutH4)
        layoutV1.addLayout(layoutH5)
        layoutV1.addLayout(layoutH6)
        layoutV1.addLayout(layoutH7)
        layoutV1.addLayout(layoutH8)
        layoutV1.addLayout(layoutH9)
        layoutV1.addLayout(layoutH10)
        layoutV1.addSpacing(10)
        layoutV1.addWidget(self.button_CMD0)
        layoutV1.addSpacing(10)

        # ----------------------------------------------------------------------------
        self.label_F_T = QtGui.QLabel('F-T(sec) :')
        self.ComboBox_F_T = QtGui.QComboBox()
        self.ComboBox_F_T.addItems(["1", "5", "10", "20", "30", "60", "300", "600", "1800", "3600"])
        self.ComboBox_F_T.setCurrentIndex(2)
        layoutH11 = QtGui.QHBoxLayout()
        layoutH11.addWidget(self.label_F_T)
        layoutH11.addWidget(self.ComboBox_F_T)

        self.label_D_A_D = QtGui.QLabel('D-A-M :')
        self.ComboBox_D_A_D = QtGui.QComboBox()
        self.ComboBox_D_A_D.addItems(
            ["realtime(MQTT)", "NodeZip(DB)", "MQTT+DB", "KT(IoTMakers)", "MQTT+IoTMakers", "DB+IoTMakers", "디바이스 정지",
             "ALL_only test"])
        self.ComboBox_D_A_D.setCurrentIndex(2)
        layoutH12 = QtGui.QHBoxLayout()
        layoutH12.addWidget(self.label_D_A_D)
        layoutH12.addWidget(self.ComboBox_D_A_D)

        self.button_CMD1 = QtGui.QPushButton('적용(CMD1)')

        layoutV1.addLayout(layoutH11)
        layoutV1.addLayout(layoutH12)
        layoutV1.addSpacing(10)
        layoutV1.addWidget(self.button_CMD1)
        layoutV1.addSpacing(10)
        # ----------------------------------------------------------------------------

        self.label_Trigger_value = QtGui.QLabel('Trigger value(%) :')
        self.ComboBox_Trigger_value = QtGui.QComboBox()
        self.ComboBox_Trigger_value.addItems(
            ["1", "3", "5", "8", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"])
        self.ComboBox_Trigger_value.setCurrentIndex(4)
        layoutH21 = QtGui.QHBoxLayout()
        layoutH21.addWidget(self.label_Trigger_value)
        layoutH21.addWidget(self.ComboBox_Trigger_value)

        self.label_T_P = QtGui.QLabel('전송방식 :')
        self.ComboBox_T_P = QtGui.QComboBox()
        self.ComboBox_T_P.addItems(["트리거 이벤트 발생시", "주기적으로"])
        self.ComboBox_T_P.setCurrentIndex(1)
        layoutH22 = QtGui.QHBoxLayout()
        layoutH22.addWidget(self.label_T_P)
        layoutH22.addWidget(self.ComboBox_T_P)

        self.label_Analysis_Main = QtGui.QLabel('Analysis Item(Main) :')
        self.ComboBox_Analysis_Main = QtGui.QComboBox()
        self.ComboBox_Analysis_Main.addItems(["P2P", "RMS", "AVG", "STD"])
        self.ComboBox_Analysis_Main.setCurrentIndex(0)
        layoutH23 = QtGui.QHBoxLayout()
        layoutH23.addWidget(self.label_Analysis_Main)
        layoutH23.addWidget(self.ComboBox_Analysis_Main)

        self.label_Analysis_Sub = QtGui.QLabel('Analysis Item(Main) :')
        self.ComboBox_Analysis_Sub = QtGui.QComboBox()
        self.ComboBox_Analysis_Sub.addItems(["P2P", "RMS", "AVG", "STD"])
        self.ComboBox_Analysis_Sub.setCurrentIndex(1)
        layoutH24 = QtGui.QHBoxLayout()
        layoutH24.addWidget(self.label_Analysis_Sub)
        layoutH24.addWidget(self.ComboBox_Analysis_Sub)

        self.button_CMD2 = QtGui.QPushButton('적용(CMD2)')

        layoutV1.addLayout(layoutH21)
        layoutV1.addLayout(layoutH22)
        layoutV1.addLayout(layoutH23)
        layoutV1.addLayout(layoutH24)
        layoutV1.addSpacing(20)
        layoutV1.addWidget(self.button_CMD2)
        layoutV1.addSpacing(40)

        # ----------------------------------------------------------------------------

        self.label_F_S_T = QtGui.QLabel('파일 저장 형식 :')
        self.ComboBox_F_S_T = QtGui.QComboBox()
        self.ComboBox_F_S_T.addItems(["저장안함", "CSV", "Bin"])
        self.ComboBox_F_S_T.setCurrentIndex(1)
        layoutH31 = QtGui.QHBoxLayout()
        layoutH31.addWidget(self.label_F_S_T)
        layoutH31.addWidget(self.ComboBox_F_S_T)

        self.label_Camera = QtGui.QLabel('카메라 사용 :')
        self.ComboBox_Camera = QtGui.QComboBox()
        self.ComboBox_Camera.addItems(["사용안함", "사용"])
        self.ComboBox_Camera.setCurrentIndex(0)
        layoutH32 = QtGui.QHBoxLayout()
        layoutH32.addWidget(self.label_Camera)
        layoutH32.addWidget(self.ComboBox_Camera)

        self.label_NTP = QtGui.QLabel('시간 동기 주기(NTP)(min) :')
        self.ComboBox_NTP = QtGui.QComboBox()
        self.ComboBox_NTP.addItems(["10", "20", "30", "40", "50", "60"])
        self.ComboBox_NTP.setCurrentIndex(0)
        layoutH33 = QtGui.QHBoxLayout()
        layoutH33.addWidget(self.label_NTP)
        layoutH33.addWidget(self.ComboBox_NTP)

        self.button_CMD3 = QtGui.QPushButton('적용(CMD3)')

        layoutV1.addLayout(layoutH31)
        layoutV1.addLayout(layoutH32)
        layoutV1.addLayout(layoutH33)

        layoutV1.addSpacing(10)
        layoutV1.addWidget(self.button_CMD3)
        layoutV1.addSpacing(20)
        # ----------------------------------------------------------------------------
        self.label_RST = QtGui.QLabel('Reboot Type :')
        self.ComboBox_RST = QtGui.QComboBox()
        self.ComboBox_RST.addItems(["Warm", "Cool"])
        self.ComboBox_RST.setCurrentIndex(0)
        layoutH41 = QtGui.QHBoxLayout()
        layoutH41.addWidget(self.label_RST)
        layoutH41.addWidget(self.ComboBox_RST)

        self.button_RST = QtGui.QPushButton('Device ReBoot')

        self.button_TEST = QtGui.QPushButton('TEST')

        layoutV1.addLayout(layoutH41)
        layoutV1.addSpacing(10)
        layoutV1.addWidget(self.button_RST)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.button_TEST)
        layoutV1.addSpacing(20)
        self.label_image = QtGui.QLabel()
        layoutV1.addWidget(self.label_image)

        layoutPH2 = QtGui.QHBoxLayout()
        self.plot1 = pg.PlotWidget(title="1st Analysis value")
        self.plot2 = pg.PlotWidget(title="2nd Analysis value")
        layoutPH2.addWidget(self.plot1)
        layoutPH2.addWidget(self.plot2)

        layoutPH3 = QtGui.QHBoxLayout()
        self.plot3 = pg.PlotWidget(title="Device Temperature(deg)")
        self.plot4 = pg.PlotWidget(title="Trigger Event Data ")
        layoutPH3.addWidget(self.plot3)
        layoutPH3.addWidget(self.plot4)

        layoutV2 = QtGui.QVBoxLayout()
        layoutV2.addLayout(layoutPH2)
        layoutV2.addLayout(layoutPH3)

        self.textEdit_command = QtGui.QTextEdit()
        layoutV2.addWidget(self.textEdit_command)

        layout = QtGui.QHBoxLayout()
        layout.addLayout(layoutV1)
        layout.addLayout(layoutV2)

        layout.setStretchFactor(layoutV1, 0)
        layout.setStretchFactor(layoutV2, 1)

        self.setLayout(layout)

        '''
        self.label = pg.LabelItem(justify='right')
        self.label.setText('ssssssfdsjkgjdfksghnkjdf')
        self.plot3.addItem(self.label)
        '''


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.anal_data_call()
    window.show()
    app.exec_()

