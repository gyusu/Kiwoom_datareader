# coding=utf-8

import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *

import decorators

TR_REQ_TIME_INTERVAL = 0.2


class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        # Login 요청 후 서버가 발생시키는 이벤트의 핸들러 등록
        self.OnEventConnect.connect(self._on_event_connect)

        # 조회 요청 후 서버가 발생시키는 이벤트의 핸들러 등록
        self.OnReceiveTrData.connect(self._on_receive_tr_data)

    def _on_event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next,
                            unused1, unused2, unused3, unused4):
        import tr_receive_handler as tr

        self.latest_tr_data = None

        if next == '2':
            self.is_tr_data_remained = True
        else:
            self.is_tr_data_remained = False

        if rqname == "opt10081_req":
            self.latest_tr_data = tr.on_receive_opt10081(self, rqname, trcode)
        elif rqname == "opt10080_req":
            self.latest_tr_data = tr.on_receive_opt10080(self, rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def comm_connect(self):
        """Login 요청 후 서버가 이벤트 발생시킬 때까지 대기하는 메소드"""
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    @decorators.call_printer
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        """
        서버에 조회 요청을 하는 메소드
        이 메소드 호출 이전에 set_input_value 메소드를 수차례 호출하여 INPUT을 설정해야 함
        """
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

        # 키움 Open API는 시간당 request 제한이 있기 때문에 딜레이를 줌
        time.sleep(TR_REQ_TIME_INTERVAL)

    def comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def get_code_list_by_market(self, market):
        """market의 모든 종목코드를 서버로부터 가져와 반환하는 메소드"""
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        """종목코드를 받아 종목이름을 반환하는 메소드"""
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_connect_state(self):
        """서버와의 연결 상태를 반환하는 메소드"""
        ret = self.dynamicCall("GetConnectState()")
        return ret

    def set_input_value(self, input_dict):
        """
        CommRqData 함수를 통해 서버에 조회 요청 시,
        요청 이전에 SetInputValue 함수를 수차례 호출하여 해당 요청에 필요한
        INPUT 을 넘겨줘야 한다.
        """
        for key, val in input_dict.items():
            self.dynamicCall("SetInputValue(QString, QString)", key, val)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def get_server_gubun(self):
        """
        실투자 환경인지 모의투자 환경인지 구분하는 메소드
        실투자, 모의투자에 따라 데이터 형식이 달라지는 경우가 있다. 대표적으로 opw00018 데이터의 소수점
        """
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    def get_login_info(self, tag):
        """
        계좌 정보 및 로그인 사용자 정보를 얻어오는 메소드
        """
        ret = self.dynamicCall("GetLoginInfo(QString)", tag)
        return ret


# C++과 python destructors 간의 충돌 방지를 위해 전역 설정
# garbage collect 순서를 맨 마지막으로 강제함
# 사실, 이 파일을 __main__으로 하지 않는경우에는 고려 안해도 무방
app = None


def main():
    global app
    app = QApplication(sys.argv)
    kiwoom = KiwoomAPI()
    kiwoom.comm_connect()


if __name__ == "__main__":
    main()
