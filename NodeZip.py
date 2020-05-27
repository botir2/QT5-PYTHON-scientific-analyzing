import pymysql

# import traits.api as trapi

import datetime as dt
import sys

from pandas import Series, DataFrame
from scipy import signal


from PyQt5.QtWidgets import QDateEdit, QPushButton, QLabel, QLineEdit
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import pandas as pd
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import datetime
import requests, json
from PyQt5.QtCore import QDate
from sklearn.cluster import KMeans

# 가속도 변위 함수관련 #####################
# sys.path.append("C:/Users/Administrator/Desktop/python_test/ACCTODIS")
# import ACC_TO_DIS

# filter_data=pd.read_csv('C:/Users/Administrator/Desktop/python_test/ACCTODIS/FFIR_coefficients_5_0Hz.csv')
# acc_data=pd.read_csv('C:/Users/Administrator/Desktop/python_test/ACCTODIS/acceleration.csv')

# f_data=filter_data['DIS']
##########################################

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


fname = ' '

Fs = 100  # Sampling frequency
T = 1 / Fs  # Sample interval time


# DB_sock= pymysql.connect(host='210.105.85.7', port=3306, user='root', passwd='smart2016', db='mobiusdb', charset='utf8')


class GateWay_Set_Info:
    def __init__(self, host_IP, USER_ID, USER_PW, AE_name, Device_type, CT_name, CH_number, Start_date, End_date,
                 DB_sock):
        self.host_IP = host_IP
        self.USER_ID = USER_ID
        self.USER_PW = USER_PW
        self.Device_type = Device_type
        self.AE_name = AE_name
        self.Cont_name = CT_name
        self.CH_number = CH_number
        # self.sensor_name=sensor_name
        self.Start_date = Start_date
        self.End_date = End_date
        self.DB_sock = DB_sock
        

    def DB_Login(self):
        self.DB_sock = pymysql.connect(host=self.host_IP, port=3306, user=self.USER_ID, passwd=self.USER_PW,
                                       db='mobiusdb', charset='utf8')
        # db = pymysql.connect(host=self.host_IP, port=self.port, user=self.user_ID, passwd=self.passwd, db='mobiusdb', charset='utf8')


def loading_to_DB(Start_date, End_date, DB_socket, Device_type, AE_name, Cont_name):
    # peroid_date=np.arange('2018-09-10','2018-10-10',dtype='datetime64')
    rowall_con = []
    cursor_DB = DB_socket.cursor()

    if Start_date == End_date:
        cursor_DB.execute(
            'SELECT  con FROM `mobiusdb`.`cin` WHERE ri like \'/mobius-yt/smartcs:' + Device_type + ':' + AE_name + '/' + Cont_name + '/4-' + Start_date.replace(
                '-', '') + '%\' ORDER BY `con`;')
        rowall_con.extend(cursor_DB.fetchall())
    else:
        peroid_date = np.arange(Start_date, End_date, dtype='datetime64')
        peroid_date_string = np.datetime_as_string(peroid_date)

        for i in range(0, len(peroid_date_string)):
            cursor_DB.execute(
                'SELECT  con FROM `mobiusdb`.`cin` WHERE ri like \'/mobius-yt/smartcs:' + Device_type + ':' + AE_name + '/' + Cont_name + '/4-' +
                peroid_date_string[i].replace('-', '') + '%\' ORDER BY `con`;')
            rowall_con.extend(cursor_DB.fetchall())

    DB_socket.close()
    return rowall_con


def DATA_PARSING_GW(t_num, Beacon_num, rowall_con):
    global date, date1
    date = ['']
    date_int = [0]
    # date1=['']
    global x
    global CH_data
    global CH_t
    global GW_DF

    x = [0]
    y = [0]
    t = [0]

    CH_data = [0]
    CH_t = [0]

    CH_data_temp = [0]
    CH_t_temp = [0]

    index = 6  # CH-num
    index_next = 11  # ch-interval
    print('index=', index)
    # for iii in range(Beacon_num,Beacon_num):
    iii = Beacon_num  # 현재 채널
    print('t_num=', t_num)
    print('Beacon_num=', Beacon_num)
    for kk in range(1, len(rowall_con)):
        x.append(0);
        date.append(0);
        date_int.append(0);
        CH_data.append(0);
        CH_t.append(0);

    GW_DF = pd.DataFrame()

    for jj in range(1, t_num + 1):

        print('jj=', jj)
        for ii in range(1, len(rowall_con)):

            x[ii] = (ii);
            y_a = rowall_con[ii];

            y_b = y_a[0].split(',');
            # print(y_b)
            date[ii] = np.datetime64(pd.Timestamp(y_b[0]));
            dtt = (np.datetime64(pd.Timestamp(y_b[0])) - np.datetime64('1970-01-01 00:00:00'))
            dtt = dtt.item().total_seconds()
            date_int[ii] = int(dtt)
            # print(date[ii],date_int[ii])
            # date1.append(y_b[0])
            # GW_DF=pd.DataFrame(index=pd.DatetimeIndex(date))

            if len(y_b) >= (index + 6 + index_next * (jj - 1)) and ii > 1:

                if int(y_b[index + 1 + index_next * (jj - 1)]) >= 1 and int(
                        y_b[index + index_next * (jj - 1)]) + 1 == jj:
                    CH_data[ii] = (float(y_b[index + 3 + index_next * (jj - 1)]))
                    CH_t[ii] = (float(y_b[index + 6 + index_next * (jj - 1)]))

                else:
                    CH_data[ii] = (CH_data[ii - 1])
                    CH_t[ii] = (CH_t[ii - 1])

            else:
                CH_data[ii] = (CH_data[ii - 1])
                CH_t[ii] = (CH_t[ii - 1])

                # date[0]= date[1]

        # CH_data[0]= CH_data[1]

        # CH_t[0]= CH_t[1]
        GW_DF[str(jj) + '_date'] = date[2:-1]
        GW_DF[str(jj) + '_data'] = CH_data[2:-1]
        GW_DF[str(jj) + '_Temp'] = CH_t[2:-1]
        GW_DF[str(jj) + '_date_int'] = date_int[2:-1]
    GW_DF['index'] = x[2:-1]

    return len(rowall_con) - 1


def DATA_PARSING_S_CUBE(Container_name, rowall_con):
    global date3
    global raw_data_date
    global X
    global data_ANAL_1
    global data_ANAL_2
    global data_EVENT
    global data_TEMP
    global data_HUMI
    global raw_data
    global date3_int
    date3_int = [0]

    date3 = ['']
    raw_data_date = ['']
    data_ANAL_1 = [0]
    data_ANAL_2 = [0]
    data_EVENT = [0]
    data_TEMP = [0]
    data_HUMI = [0]
    raw_data = [0]
    ROWE_DF = pd.DataFrame()
    ROWE_datetime_DF = pd.DataFrame()

    if Container_name == 'anal' and len(rowall_con) > 0:
        for ii in range(1, len(rowall_con)):
            y_a = rowall_con[ii];
            y_b = y_a[0].split(',');

            date3.append(np.datetime64(pd.Timestamp(y_b[0])));
            dtt = (np.datetime64(pd.Timestamp(y_b[0])) - np.datetime64('1970-01-01 00:00:00'))
            dtt = dtt.item().total_seconds()
            date3_int.append(int(dtt))

            if len(y_b) == 11:
                data_ANAL_1.append(float(y_b[1]))
                data_ANAL_2.append(float(y_b[2]))
                data_EVENT.append(float(y_b[3]))
                data_TEMP.append(float(y_b[8]))
                data_HUMI.append(float(y_b[9]))

        date3[0] = date3[1]
        date3_int[0] = date3_int[1]
        data_ANAL_1[0] = data_ANAL_1[1]
        data_ANAL_2[0] = data_ANAL_2[1]
        data_EVENT[0] = data_EVENT[1]
        data_TEMP[0] = data_TEMP[1]
        data_HUMI[0] = data_HUMI[1]

    if Container_name == 'rawe' and len(rowall_con) > 0:
        maxYb = 0
        for y_a in rowall_con:
            y_b = y_a[0].split(',')

            if maxYb < len(y_b):
                maxYb = len(y_b)
        # print(maxYb)

        raw_data = []
        for ii in range(0, maxYb + 1):
            raw_data.append(0)
        print('len(raw_data)', len(raw_data))

        te = len(raw_data) * T  # End of time
        t = np.arange(0, te, T)  # Time vector
        # print('len(t)',len(t))
        ROWE_DF = pd.DataFrame(index=t)

        for i in range(0, len(rowall_con)):
            y_a = rowall_con[i];
            y_b = y_a[0].split(',');
            print('y_b=', len(y_b))

            date3.append(np.datetime64(pd.Timestamp(y_b[0])));
            print('Date=', date3[-1])
            for ii in range(1, len(y_b)):
                raw_data[ii - 1] = round(float(y_b[ii]), 4)

            print('raw_data=', len(raw_data))

            if abs(np.max(raw_data) - np.min(raw_data)) < 0.3:  #################데이터 정리
                ROWE_DF[date3[-1]] = raw_data
                # raw_data.clear()
                # raw_data=[0]
                for ii in range(0, maxYb + 1):
                    raw_data[ii] = 0

        ROWE_DF.to_csv('rawe.csv')

    return len(rowall_con)


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='lowpass', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


def norm(x):
    _max = x.max()
    _min = x.min()
    _denom = _max - _min
    return (x - _min) / _denom


def invers_norm(x):
    x = -(x - x.mean())
    _max = x.max()
    _min = x.min()
    _denom = _max - _min
    return ((x - _max) / _denom) + 1


def Back_norm(x, y):
    _max = x.max()
    _min = x.min()
    _denom = _max - _min
    return (y * _denom) + _min


###
from collections import deque

import pytz

UNIX_EPOCH_naive = datetime.datetime(1970, 1, 1, 0, 0)  # offset-naive datetime
UNIX_EPOCH_offset_aware = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=pytz.utc)  # offset-aware datetime
UNIX_EPOCH = UNIX_EPOCH_naive

TS_MULT_us = 1
global G_AE_name
G_AE_name = 'anal'


def now_timestamp(ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    return (int((datetime.datetime.utcnow() - epoch).total_seconds() * ts_mult))


def int2dt(ts, ts_mult=TS_MULT_us):
    return (datetime.datetime.utcfromtimestamp(float(ts) / ts_mult))


def dt2int(dt, ts_mult=TS_MULT_us, epoch=UNIX_EPOCH):
    delta = dt - epoch
    return (int(delta.total_seconds() * ts_mult))


def td2int(td, ts_mult=TS_MULT_us):
    return (int(td.total_seconds() * ts_mult))


def int2td(ts, ts_mult=TS_MULT_us):
    return (datetime.timedelta(seconds=float(ts) / ts_mult))


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        # return [QTime().addMSecs(value).toString('mm:ss') for value in values]
        # [print(int2dt(value)) for value in values]

        if values[-1] >= 13000:
            return [int2dt(value).strftime("%y-%m-%d %H:%M:%S") for value in values]
        else:
            return values


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Smart c&S...File load for display and analysis v0.1')
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.login_widget = LoginWidget(self)

        self.login_widget.pushButton_call.clicked.connect(self.pushButton_call_Clicked)
        self.login_widget.pushButton_Plot.clicked.connect(self.pushButton_Plot_Clicked)
        self.login_widget.pushButton_Save.clicked.connect(self.pushButton_Save_Clicked)
        self.login_widget.ComboBox_CT_name.currentIndexChanged.connect(self.ComboBox_CT_name_selectionchange)
        self.login_widget.ComboBox_Device_type.currentIndexChanged.connect(self.ComboBox_Device_type_selectionchange)

        data = pd.read_csv("SCUBE_LIST.csv", engine='python')
        ff = data.shape
        for i in range(0, ff[0]):
            data1 = data['ID'][i] + ',' + data['DES'][i]
            self.login_widget.ComboBox_AE_list.addItems([data1])

        self.login_widget.ComboBox_AE_list.currentIndexChanged.connect(self.ComboBox_AE_list_selectionchange)

        self.central_widget.addWidget(self.login_widget)

    def ComboBox_CT_name_selectionchange(self):

        G_AE_name = self.login_widget.ComboBox_CT_name.currentText()

    def ComboBox_AE_list_selectionchange(self):

        C_AE_Name = self.login_widget.ComboBox_AE_list.currentText().split(',')
        self.login_widget.lineEdit_AE_name.setText(C_AE_Name[0])

    def ComboBox_Device_type_selectionchange(self):
        self.login_widget.ComboBox_CT_name.clear()
        if self.login_widget.ComboBox_Device_type.currentIndex() == 0:
            self.login_widget.ComboBox_CT_name.addItems(["anal", "rawe"])
            self.login_widget.ComboBox_AE_list.clear()
            data = pd.read_csv("SCUBE_LIST.csv", engine='python')
            ff = data.shape
            for i in range(0, ff[0]):
                data1 = data['ID'][i] + ',' + data['DES'][i]
                self.login_widget.ComboBox_AE_list.addItems([data1])
        if self.login_widget.ComboBox_Device_type.currentIndex() == 1:
            self.login_widget.ComboBox_CT_name.addItems(["s-v"])
            self.login_widget.ComboBox_AE_list.clear()
            data = pd.read_csv("GW_LIST.csv", engine='python')
            ff = data.shape
            for i in range(0, ff[0]):
                data1 = data['ID'][i] + ',' + data['DES'][i]
                self.login_widget.ComboBox_AE_list.addItems([data1])

    def pushButton_call_Clicked(self):

        global t_CH_NUM
        GateWay_Set = GateWay_Set_Info(self.login_widget.lineEdit_IP.text(), self.login_widget.lineEdit_ID.text(), \
                                       self.login_widget.lineEdit_PW.text(), self.login_widget.lineEdit_AE_name.text(), \
                                       str(self.login_widget.ComboBox_Device_type.currentIndex() + 1),
                                       self.login_widget.ComboBox_CT_name.currentText(), \
                                       int(self.login_widget.ComboBox_CH_num.currentText()),
                                       self.login_widget.DateEdit_Start_date.date().toPyDate(), \
                                       str(self.login_widget.DateEdit_End_date.date().toPyDate()), 'DB_sock')

        GateWay_Set.DB_Login()
        rowall_con_DB = loading_to_DB(GateWay_Set.Start_date, GateWay_Set.End_date, GateWay_Set.DB_sock,
                                      GateWay_Set.Device_type, GateWay_Set.AE_name, GateWay_Set.Cont_name)
        # print(rowall_con_DB)
        gg = self.login_widget.ComboBox_CH_num.currentIndex()
        try:
            code, status, config_inform, ct = res_get_Instance_inform(self.login_widget.lineEdit_IP.text(), 2,
                                                                      self.login_widget.lineEdit_AE_name.text(), 20, 4,
                                                                      1)
            self.login_widget.ComboBox_CH_num.clear()
            for i in range(int(config_inform[1])):
                # print(int(config_inform[1]))
                self.login_widget.ComboBox_CH_num.addItems([str(i + 1)])
            self.login_widget.ComboBox_CH_num.setCurrentIndex(gg)
            t_CH_NUM = int(config_inform[1])
        except:
            t_CH_NUM = 3
            pass

        if int(GateWay_Set.Device_type) == 2:
            DATA_Total_num = DATA_PARSING_GW(t_CH_NUM, GateWay_Set.CH_number, rowall_con_DB)

        else:
            DATA_Total_num = DATA_PARSING_S_CUBE(GateWay_Set.Cont_name, rowall_con_DB)
        self.login_widget.data_num_Label.setText('DATA NUM : ' + str(DATA_Total_num))

    def pushButton_Plot_Clicked(self):

        if int((self.login_widget.ComboBox_Device_type.currentIndex() + 1)) == 2:  # GW

            # GW_DF=pd.DataFrame(index=pd.DatetimeIndex(date))
            # GW_DF['x_count']=x
            # GW_DF['CH-DATA']=CH_data
            # GW_DF['CH-TEMP']=CH_t

            import math

            win = int(self.login_widget.lineEdit_AVG_win.text())

            for i in range(1, t_CH_NUM + 1):

                # moving_avg = ts_log.rolling(12).mean()
                GW_DF[str(i) + '_Move_AVG'] = GW_DF[str(i) + '_data'].rolling(win).mean()
                GW_DF[str(i) + '_Move_AVG_Temp'] = GW_DF[str(i) + '_Temp'].rolling(win).mean()

                ddd = GW_DF[str(i) + '_Move_AVG']
                Data_fitted = norm(ddd)

                ttt = GW_DF[str(i) + '_Move_AVG_Temp']
                Temp_fitted = norm(ttt)

                hhh = Data_fitted - Temp_fitted

                if hhh.max() > 0.6:
                    Data_fitted = invers_norm(ddd)
                    hhh = Data_fitted - Temp_fitted

                ffff = Back_norm(ddd, hhh)

                GW_DF[str(i) + '_Nomal_Move_AVG'] = Data_fitted
                GW_DF[str(i) + '_Nomal_Move_AVG_Temp'] = Temp_fitted
                GW_DF[str(i) + '_Nomal_Only_Data'] = hhh

                ffff = ffff - ffff[win]

                GW_DF[str(i) + '_Only_Data'] = ffff

                # GW_DF[str(i)+'_Move_STD']=GW_DF[str(i)+'_data'].rolling(win).std()*math.sqrt(win)

            # f_coherence,CH_coherence = signal.coherence(GW_DF['CH-DATA'], GW_DF['CH-TEMP'])
            # f_csd,CH_csd = signal.csd(GW_DF['CH-DATA'], GW_DF['CH-TEMP'])
            # print('Correlation Coef[DATA-TEMP.]= :',GW_DF['CH-DATA'].corr(GW_DF['CH-TEMP']))

            # reg=np.polyfit(x,GW_DF[(self.login_widget.ComboBox_CH_num.currentText())+'_data'],deg=1)
            # GW_DF['Move_REG']=reg[1]+reg[0]*np.arange(0,len(x))

            # GW_DF['CH-DATA'].hist(bins=int(win/10))

            self.login_widget.plot1.clear()
            # ret = []
            # for idx, itm in enumerate(GW_DF[(self.login_widget.ComboBox_CH_num.currentText())+'_date']):
            #     ret.append(itm.strftime('%Y-%m-%d %H:%M:%S'))

            # xdict = dict(enumerate(ret))
            # stringaxis = pg.AxisItem(orientation='bottom')
            # stringaxis.setTicks([xdict.items()])

            # self.login_widget.plot1.plot(list(xdict.keys()),GW_DF[(self.login_widget.ComboBox_CH_num.currentText())+'_data'],pen=(225,0,0),name="DATA")
            # self.login_widget.plot1.plot(list(xdict.keys()),GW_DF[(self.login_widget.ComboBox_CH_num.currentText())+'_Move_AVG'], pen=(0,225,0),name="Moving AVG")
            self.login_widget.plot1.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_data'],
                                         pen=(225, 0, 0), name="DATA")
            self.login_widget.plot1.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_Move_AVG'],
                                         pen=(0, 225, 0), name="Moving AVG")
            # self.login_widget.plot1.plot(GW_DF['Move_STD'], pen=(0,0,255),name="Moving STD")
            # self.login_widget.plot1.plot(GW_DF.index,GW_DF['CH-DATA'], pen=(0,225,0),name="Moving AVG")
            # self.login_widget.plot1.plot(GW_DF.index,GW_DF['Move_REG'], pen=(0,0,255),name="Moving STD")
            self.login_widget.plot1.setLabel('left', "Data Value", units='a.u')
            self.login_widget.plot1.setLabel('bottom', "time", units='date')
            self.login_widget.plot1.setLabel('top', ' iLOG-Beacon DATA PLOT ')

            self.login_widget.plot2.clear()
            self.login_widget.plot2.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_Temp'],
                                         pen=(255, 0, 0), name="TEMPERATURE")
            self.login_widget.plot2.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_Move_AVG_Temp'],
                                         pen=(0, 255, 0), name="Moving AVG")
            self.login_widget.plot2.setLabel('left', "TEMPERATURE Value", units='DEG')
            self.login_widget.plot2.setLabel('bottom', "time", units='date')
            self.login_widget.plot2.setLabel('top', ' iLOG-Beacon TEMPERATURE PLOT ')

            self.login_widget.plot3.clear()

            self.login_widget.plot3.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[self.login_widget.ComboBox_CH_num.currentText() + '_Nomal_Move_AVG'],
                                         pen=(0, 0, 255), name="DATA")
            self.login_widget.plot3.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'], GW_DF[
                self.login_widget.ComboBox_CH_num.currentText() + '_Nomal_Move_AVG_Temp'], pen=(250, 0, 0), name="Temp")
            self.login_widget.plot3.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[self.login_widget.ComboBox_CH_num.currentText() + '_Nomal_Only_Data'],
                                         pen=(0, 250, 0), name="D")
            # self.login_widget.plot3.setLabel('left', "Coherence", units='DEG')
            # self.login_widget.plot3.setLabel('bottom', "Frequency", units='Hz')
            self.login_widget.plot3.setLabel('top', ' DATA-TEMPERATURE Scaled PLOT ')

            self.login_widget.plot4.clear()
            self.login_widget.plot4.plot(GW_DF[(self.login_widget.ComboBox_CH_num.currentText()) + '_date_int'],
                                         GW_DF[self.login_widget.ComboBox_CH_num.currentText() + '_Only_Data'],
                                         pen=(0, 0, 255), name="C_DATA")
            self.login_widget.plot4.setLabel('top', ' Data excluding temperature effect PLOT ')
            GW_DF.to_csv('data' + '.csv')

        if int((
                       self.login_widget.ComboBox_Device_type.currentIndex() + 1)) == 1 and self.login_widget.ComboBox_CT_name.currentText() == 'anal':
            SCUBE_DF = pd.DataFrame(index=pd.DatetimeIndex(date3))
            SCUBE_DF['date_int'] = date3_int
            SCUBE_DF['ANAL_1'] = data_ANAL_1
            SCUBE_DF['ANAL_2'] = data_ANAL_2
            SCUBE_DF['EVENT'] = data_EVENT
            SCUBE_DF['TEMP'] = data_TEMP
            SCUBE_DF['HUMI'] = data_HUMI

            import math

            win = int(self.login_widget.lineEdit_AVG_win.text())
            # oving_avg = ts_log.rolling(12).mean()
            SCUBE_DF['Move_AVG_ANAL1'] = SCUBE_DF['ANAL_1'].rolling(win).mean()
            SCUBE_DF['Move_STD_ANAL1'] = SCUBE_DF['ANAL_1'].rolling(win).std() * math.sqrt(win)

            SCUBE_DF['Move_AVG_ANAL2'] = SCUBE_DF['ANAL_2'].rolling(win).mean()
            SCUBE_DF['Move_STD_ANAL2'] = SCUBE_DF['ANAL_2'].rolling(win).std() * math.sqrt(win)

            # reg=np.polyfit(x,SCUBE_DF['ANAL_1'],deg=1)
            # GW_DF['Move_REG']=reg[1]+reg[0]*np.arange(0,len(x))
            self.login_widget.plot1.clear()
            self.login_widget.plot1.plot(SCUBE_DF['date_int'], SCUBE_DF['ANAL_1'], pen=(225, 0, 0), name="Analysis_1")
            self.login_widget.plot1.plot(SCUBE_DF['date_int'], SCUBE_DF['Move_AVG_ANAL1'], pen=(0, 225, 0),
                                         name="Moving AVG")
            self.login_widget.plot1.plot(SCUBE_DF['date_int'], SCUBE_DF['Move_STD_ANAL1'], pen=(0, 0, 255),
                                         name="Moving STD")
            # self.login_widget.plot1.plot(SCUBE_DF.index,SCUBE_DF['Move_AVG_ANAL1'], pen=(0,225,0),name="Moving AVG")
            # self.login_widget.plot1.plot(SCUBE_DF.index,SCUBE_DF['Move_STD_ANAL1'], pen=(0,0,255),name="Moving STD")
            self.login_widget.plot1.setLabel('left', "1st Analysis value'", units='a.u')
            self.login_widget.plot1.setLabel('bottom', "time", units='date')
            self.login_widget.plot1.setLabel('top', ' Analysis-1 Data PLOT ')

            self.login_widget.plot2.clear()
            self.login_widget.plot2.plot(SCUBE_DF['date_int'], SCUBE_DF['ANAL_2'], pen=(225, 0, 0), name="Analysis_2")
            self.login_widget.plot2.plot(SCUBE_DF['date_int'], SCUBE_DF['Move_AVG_ANAL2'], pen=(0, 255, 0),
                                         name="Moving AVG")
            self.login_widget.plot2.plot(SCUBE_DF['date_int'], SCUBE_DF['Move_STD_ANAL2'], pen=(0, 0, 255),
                                         name="Moving STD")
            # self.login_widget.plot2.plot(SCUBE_DF.index,SCUBE_DF['Move_AVG_ANAL2'], pen=(0,255,0),name="Moving AVG")
            # self.login_widget.plot2.plot(SCUBE_DF.index,SCUBE_DF['Move_STD_ANAL2'], pen=(0,0,255),name="Moving STD")
            self.login_widget.plot2.setLabel('left', "2st Analysis value'", units='a.u')
            self.login_widget.plot2.setLabel('bottom', "time", units='date')
            self.login_widget.plot2.setLabel('top', ' Analysis-2 Data PLOT ')

            self.login_widget.plot3.clear()
            self.login_widget.plot3.plot(SCUBE_DF['date_int'], SCUBE_DF['TEMP'], pen=(225, 0, 0), name="TEMP")
            self.login_widget.plot3.plot(SCUBE_DF['date_int'], SCUBE_DF['HUMI'], pen=(0, 0, 255), name="HUMI")
            self.login_widget.plot3.setLabel('left', "Deg/%", units='a.u')
            self.login_widget.plot3.setLabel('bottom', "time", units='a.u')
            self.login_widget.plot3.setLabel('top', ' Temperature / humidity Data PLOT ')

            self.login_widget.plot4.clear()
            self.login_widget.plot4.plot(SCUBE_DF['date_int'], SCUBE_DF['EVENT'], pen=(225, 0, 0), name="EVENT")
            self.login_widget.plot4.setLabel('bottom', "time", units='a.u')
            self.login_widget.plot4.setLabel('top', ' Trigger envent history PLOT ')

            SCUBE_DF.to_csv('data' + '.csv')

        if int((
               self.login_widget.ComboBox_Device_type.currentIndex())) == 0 and self.login_widget.ComboBox_CT_name.currentText() == 'rawe':
            RAWE_DATA_TEMP = pd.read_csv('rawe' + '.csv')
            RAWE_DATA_TEMP = RAWE_DATA_TEMP - RAWE_DATA_TEMP.mean()
            colums_index = RAWE_DATA_TEMP.columns

            Data_set_num = len(RAWE_DATA_TEMP.columns) - 1

            import math
            total_amplitude_Hz = [0]
            mode_frequency = 0
            mode_Amplitude = 0

            NFFT = len(RAWE_DATA_TEMP.index)  # 주파수 분석에 필요한 변수들
            k = np.arange(NFFT)
            f0 = k * Fs / NFFT
            f0 = f0[range(math.trunc(NFFT / 2))]

            FFT_AVG_DF = pd.DataFrame()
            FFT_AVG_DF = pd.DataFrame(index=f0)

            FFT_AVG_num = int(self.login_widget.lineEdit_FFT_AVG_NUM.text())

            self.login_widget.plot1.clear()
            self.login_widget.plot1.setLabel('left', "Sensor Value'", units='a.u')
            self.login_widget.plot1.setLabel('bottom', "Num of data", units='EA')
            self.login_widget.plot1.setLabel('top', ' Trigger-event time history Data PLOT ')

            self.login_widget.plot2.clear()
            self.login_widget.plot2.setLabel('bottom', "'Frequency'", units='Hz')
            self.login_widget.plot2.setLabel('left', "Amplitude", units='a.u')
            self.login_widget.plot2.setLabel('top', ' Averaged frequency analysis Data PLOT ')

            self.login_widget.plot3.clear()
            self.login_widget.plot3.setLabel('bottom', "'Frequency'", units='Hz')
            self.login_widget.plot3.setLabel('left', "Amplitude", units='a.u')
            self.login_widget.plot3.setLabel('top', ' Main frequency component Cluster Data PLOT ')

            self.login_widget.plot4.clear()
            self.login_widget.plot4.setLabel('bottom', "'Frequency'", units='Hz')
            self.login_widget.plot4.setLabel('left', "Amplitude", units='a.u')
            self.login_widget.plot4.setLabel('top', ' Change of cluster center PLOT ')
            x_value = []
            y_value = []

            kmeans_df = pd.DataFrame()
            for i in range(0, Data_set_num):
                ##############################################################################
                # Displacment_data=ACC_TO_DIS.Acc_To_DiS(RAWE_DATA_TEMP[str(i)],f_data)  #변위
                # print(acc_data)
                # print('Displacment_data',max(Displacment_data))
                #################################################################################
                self.login_widget.C_data_Label.setText('- ' + str(i))
                Y = np.fft.fft(RAWE_DATA_TEMP[colums_index[i + 1]]) / NFFT  # 데이터 별로 FFT분석
                Y = Y[range(math.trunc(NFFT / 2))]
                amplitude_Hz = 2 * abs(Y)
                total_amplitude_Hz = total_amplitude_Hz + amplitude_Hz

                if i != 0 and i % FFT_AVG_num == 0:

                    self.login_widget.plot2.plot(f0, total_amplitude_Hz / FFT_AVG_num, pen=(i, 3),
                                                 name="FFT Analysis PLOT")

                    FFT_AVG_DF[str(int(i / FFT_AVG_num))] = total_amplitude_Hz  # 데이터 셋 별로 FFT 평균 FILTER 데이터

                    print('total_amplitude_Hz===', int(i / FFT_AVG_num))

                    for ii in range(0, len(total_amplitude_Hz)):
                        if total_amplitude_Hz[ii] == max(total_amplitude_Hz):
                            mode_frequency = f0[ii]
                            mode_Amplitude = max(total_amplitude_Hz)  # 최대 주파수 분석

                    total_amplitude_Hz = [0]

                    print(
                        '\n>>> mode1_frequency={} Hz,   mode1_Amplitude = {} kN'.format(mode_frequency, mode_Amplitude))
                    if np.isnan(mode_frequency):
                        print(mode_frequency)
                    else:
                        x_value.append(mode_frequency)
                        y_value.append(mode_Amplitude)
                        kmeans_df = kmeans_df.append({'x': mode_frequency, 'y': mode_Amplitude}, ignore_index=True)
                        data_points = kmeans_df.values
                    self.login_widget.plot3.clear()

                    if i > FFT_AVG_num * 5:
                        kmeans = KMeans(n_clusters=2).fit(data_points)

                        for k in range(len(kmeans.labels_)):
                            if kmeans.labels_[k] == 0:
                                # self.login_widget.plot3.plot([mode_frequency],[mode_Amplitude],  pen=(200,200,0), symbolBrush=(0,255,255), symbolPen='w')
                                self.login_widget.plot3.plot([kmeans_df['x'][k]], [kmeans_df['y'][k]],
                                                             pen=(200, 200, 0), symbolBrush=(0, 255, 255),
                                                             symbolPen='w')
                            else:
                                self.login_widget.plot3.plot([kmeans_df['x'][k]], [kmeans_df['y'][k]],
                                                             pen=(200, 0, 200), symbolBrush=(255, 255, 0),
                                                             symbolPen='w')
                                # predict = pd.DataFrame(kmeans.predict(data_points))  예측
                        # print(predict)
                        # predict.columns=['predict']

                        centers = pd.DataFrame(kmeans.cluster_centers_, columns=['feature_0', 'feature_1'])

                        center_x = centers['feature_0']
                        print(center_x)
                        center_y = centers['feature_1']
                        print(center_y)
                        # self.login_widget.plot4.clear()
                        self.login_widget.plot4.plot(pen='y')

                        self.login_widget.plot4.plot([center_x[0]], [center_y[0]], pen=None, symbol='t', symbolPen=None,
                                                     symbolSize=10, symbolBrush=(10, 100, 255, 50))
                        self.login_widget.plot4.plot([center_x[1]], [center_y[1]], pen=None, symbol='t', symbolPen=None,
                                                     symbolSize=10, symbolBrush=(255, 100, 10, 50))

                self.login_widget.plot1.clear()
                self.login_widget.plot1.setLabel('left', "Sensor Value'", units='a.u')
                self.login_widget.plot1.setLabel('bottom', "Num of data", units='EA')
                self.login_widget.plot1.plot(RAWE_DATA_TEMP.index, RAWE_DATA_TEMP[colums_index[i + 1]], pen=(i, 3),
                                             name="TRIGGER EVENT RAW DATA")

                QtCore.QCoreApplication.processEvents()
                # time.sleep(0.5)
            FFT_AVG_DF.to_csv('rawe_fft_avg.csv')
            # self.canvas.draw()

    def pushButton_Save_Clicked(self):

        fname = QFileDialog.getSaveFileName(self)

        if int(
                self.login_widget.ComboBox_Device_type.currentIndex()) == 0 and self.login_widget.ComboBox_CT_name.currentText() == 'rawe':
            DATA_SAVE = pd.read_csv('rawe_fft_avg' + '.csv')
            DATA_SAVE.to_csv(fname[0] + 'rawe_fft_avg' + '.csv')
            DATA_SAVE = pd.read_csv('rawe' + '.csv')
            DATA_SAVE.to_csv(fname[0] + 'rawe_data' + '.csv')
        else:
            DATA_SAVE = pd.read_csv('data' + '.csv')
            DATA_SAVE.to_csv(fname[0] + '.csv')


class LoginWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LoginWidget, self).__init__(parent)

        layoutV1 = QtGui.QVBoxLayout()

        self.setGeometry(600, 200, 1200, 600)
        self.setWindowTitle("ITS DATA Aqusistion S/W v0.1...smartcs.co.kr")
        self.setWindowIcon(QIcon('icon.png'))

        self.lineEdit_IP = QLineEdit('210.105.85.7')
        self.lineEdit_ID = QLineEdit('root')
        self.lineEdit_PW = QLineEdit('smart2016')

        self.label_Device_type = QtGui.QLabel('Device type : ')
        self.ComboBox_Device_type = QtGui.QComboBox()
        self.ComboBox_Device_type.addItems(["S_Cube", "GW(Beacon)"])
        self.ComboBox_Device_type.setCurrentIndex(0)
        # self.lineEdit_Device_type = QLineEdit('2')

        self.label_AE_list = QtGui.QLabel('GateWay List :')
        self.ComboBox_AE_list = QtGui.QComboBox()

        self.label_AE_name = QtGui.QLabel('Device name : ')
        self.lineEdit_AE_name = QLineEdit('cs510')

        self.label_CT_name = QtGui.QLabel('Container : ')
        self.ComboBox_CT_name = QtGui.QComboBox()
        self.ComboBox_CT_name.addItems(["anal", "rawe"])
        self.ComboBox_CT_name.setCurrentIndex(0)
        # self.lineEdit_CT_name = QLineEdit('s-v')

        self.label_CH_num = QtGui.QLabel('CH num(Only GW): ')
        self.ComboBox_CH_num = QtGui.QComboBox()
        self.ComboBox_CH_num.addItems(["1", "2", "3"])
        self.ComboBox_CH_num.setCurrentIndex(0)
        # self.lineEdit_CH_num = QLineEdit('2')

        self.label_Start_date = QtGui.QLabel('Start Date: ')
        self.DateEdit_Start_date = QDateEdit(self)
        self.DateEdit_Start_date.setDate(QDate(2020, 5, 9))
        # self.lineEdit_Start_date = QLineEdit('2018-10-26')

        self.label_End_date = QtGui.QLabel('End Date: ')
        self.DateEdit_End_date = QDateEdit(self)
        self.DateEdit_End_date.setDate(QDate.currentDate())
        # self.lineEdit_End_date = QLineEdit('2018-11-14')

        self.pushButton_call = QPushButton("데이터 불러오기")
        self.C_data_Label = QLabel("-  ", self)
        self.data_num_Label = QLabel("DATA NUM : ", self)

        self.label_AVG_win = QtGui.QLabel('AVG_win NUM: ')
        self.lineEdit_AVG_win = QLineEdit('500')

        self.label_FFT_AVG_NUM = QtGui.QLabel('AVG_win NUM: ')
        self.lineEdit_FFT_AVG_NUM = QLineEdit('10')

        self.pushButton_Plot = QPushButton("그래프 그리기")

        self.pushButton_Save = QPushButton("저장하기")

        self.label_image = QtGui.QLabel()

        layoutV1.addSpacing(20)
        layoutV1.addWidget(self.lineEdit_IP)
        layoutV1.addWidget(self.lineEdit_ID)
        layoutV1.addWidget(self.lineEdit_PW)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_Device_type)
        layoutV1.addWidget(self.ComboBox_Device_type)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_AE_list)
        layoutV1.addWidget(self.ComboBox_AE_list)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_AE_name)
        layoutV1.addWidget(self.lineEdit_AE_name)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_CT_name)
        layoutV1.addWidget(self.ComboBox_CT_name)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_CH_num)
        layoutV1.addWidget(self.ComboBox_CH_num)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_Start_date)
        layoutV1.addWidget(self.DateEdit_Start_date)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_End_date)
        layoutV1.addWidget(self.DateEdit_End_date)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.pushButton_call)

        layoutV1.addWidget(self.data_num_Label)
        layoutV1.addWidget(self.C_data_Label)
        layoutV1.addSpacing(30)

        layoutV1.addWidget(self.label_AVG_win)
        layoutV1.addWidget(self.lineEdit_AVG_win)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.label_FFT_AVG_NUM)
        layoutV1.addWidget(self.lineEdit_FFT_AVG_NUM)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.pushButton_Plot)
        layoutV1.addSpacing(20)

        layoutV1.addWidget(self.pushButton_Save)

        layoutV1.addSpacing(50)
        layoutV1.addWidget(self.label_image)
        layoutV1.addStretch(10)

        layoutH2 = QtGui.QHBoxLayout()
        self.plot1 = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot2 = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        layoutH2.addWidget(self.plot1)
        layoutH2.addWidget(self.plot2)

        layoutH3 = QtGui.QHBoxLayout()
        self.plot3 = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plot4 = pg.PlotWidget(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        layoutH3.addWidget(self.plot3)
        layoutH3.addWidget(self.plot4)

        layoutV2 = QtGui.QVBoxLayout()
        layoutV2.addLayout(layoutH2)
        layoutV2.addLayout(layoutH3)

        layout = QtGui.QHBoxLayout()
        layout.addLayout(layoutV1)
        layout.addLayout(layoutV2)

        layout.setStretchFactor(layoutV1, 0)
        layout.setStretchFactor(layoutV2, 1)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()