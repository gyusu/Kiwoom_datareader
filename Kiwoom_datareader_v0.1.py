# coding=utf-8

import sys
import datetime
import pandas as pd
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

from kiwoomAPI import KiwoomAPI
import decorators

form_class = uic.loadUiType("Kiwoom_datareader_v0.1.ui")[0]


class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.kw = KiwoomAPI()

        # login
        self.kw.comm_connect()

        # status bar 에 출력할 메세지를 저장하는 변수
        # 어떤 모듈의 실행 완료를 나타낼 때 쓰인다.
        self.return_status_msg = ''

        # timer 등록. tick per 1s
        self.timer_1s = QTimer(self)
        self.timer_1s.start(1000)
        self.timer_1s.timeout.connect(self.timeout_1s)

        # label '종목코드' 오른쪽 lineEdit 값이 변경 될 시 실행될 함수 연결
        self.lineEdit.textChanged.connect(self.code_changed)

        # pushButton '실행'이 클릭될 시 실행될 함수 연결
        self.pushButton.clicked.connect(self.fetch_chart_data)

    def timeout_1s(self):
        current_time = QTime.currentTime()

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kw.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        if self.return_status_msg == '':
            statusbar_msg = state_msg + " | " + time_msg
        else:
            statusbar_msg = state_msg + " | " + time_msg + " | " + self.return_status_msg

        self.statusbar.showMessage(statusbar_msg)

    # label '종목' 우측의 lineEdit의 이벤트 핸들러
    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kw.get_master_code_name(code)
        self.lineEdit_2.setText(name)

    @decorators.return_status_msg_setter
    def fetch_chart_data(self):

        code = self.lineEdit.text()
        tick_unit = self.comboBox.currentText()
        # 일단 tick range = 1 인 경우만 구현함.
        # tick_range = self.comboBox_2.currentText()
        tick_range = 1

        input_dict = {}
        ohlcv = None

        if tick_unit == '일봉':
            # 일봉 조회의 경우 현재 날짜부터 과거의 데이터를 조회함
            base_date = datetime.datetime.today().strftime('%Y%m%d')
            input_dict['종목코드'] = code
            input_dict['기준일자'] = base_date
            input_dict['수정주가구분'] = 1

            self.kw.set_input_value(input_dict)
            self.kw.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
            ohlcv = self.kw.latest_tr_data

            while self.kw.is_tr_data_remained == True:
                self.kw.set_input_value(input_dict)
                self.kw.comm_rq_data("opt10081_req", "opt10081", 2, "0101")
                for key, val in self.kw.latest_tr_data.items():
                    ohlcv[key][-1:] = val

        elif tick_unit == '분봉':
            # 일봉 조회의 경우 현재 날짜부터 과거의 데이터를 조회함
            # 현 시점부터 과거로 약 160일(약 60000개)의 데이터까지만 제공된다. (2018-02-20)
            base_date = datetime.datetime.today().strftime('%Y%m%d')
            input_dict['종목코드'] = code
            input_dict['틱범위'] = tick_range
            input_dict['수정주가구분'] = 1

            self.kw.set_input_value(input_dict)
            self.kw.comm_rq_data("opt10080_req", "opt10080", 0, "0101")
            ohlcv = self.kw.latest_tr_data

            while self.kw.is_tr_data_remained == True:
                self.kw.set_input_value(input_dict)
                self.kw.comm_rq_data("opt10080_req", "opt10080", 2, "0101")
                for key, val in self.kw.latest_tr_data.items():
                    ohlcv[key][-1:] = val

        df = pd.DataFrame(ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                          index=ohlcv['date'])

        con = sqlite3.connect("./stock_price.db")
        df.to_sql(code, con, if_exists='replace')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
