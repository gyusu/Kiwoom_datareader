# coding=utf-8

"""
이 모듈은 Kiwoom.py의 Kiwoom 클래스 내의 _on_receive_tr_data 메소드에서만 사용하도록 구현됨.
TR마다 각각의 메소드를 일일이 작성해야하기 때문에 기존 클래스에서 분리하였음
"""

# cyclic import 를 피하며 type annotation 을 하기 위해 TYPE_CHECKING 을 이용함
# (https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kiwoomAPI import KiwoomAPI


def on_receive_opt10080(kw: 'KiwoomAPI', rqname, trcode):
    """주식분봉차트조회요청 완료 후 서버에서 보내준 데이터를 받는 메소드"""

    data_cnt = kw.get_repeat_cnt(trcode, rqname)
    ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

    for i in range(data_cnt):
        date = kw.comm_get_data(trcode, "", rqname, i, "체결시간")
        open = kw.comm_get_data(trcode, "", rqname, i, "시가")
        high = kw.comm_get_data(trcode, "", rqname, i, "고가")
        low = kw.comm_get_data(trcode, "", rqname, i, "저가")
        close = kw.comm_get_data(trcode, "", rqname, i, "현재가")
        volume = kw.comm_get_data(trcode, "", rqname, i, "거래량")

        ohlcv['date'].append(date)
        ohlcv['open'].append(abs(int(open)))
        ohlcv['high'].append(abs(int(high)))
        ohlcv['low'].append(abs(int(low)))
        ohlcv['close'].append(abs(int(close)))
        ohlcv['volume'].append(int(volume))

    return ohlcv


def on_receive_opt10081(kw: 'KiwoomAPI', rqname, trcode):
    """주식일봉차트조회요청 완료 후 서버에서 보내준 데이터를 받는 메소드"""

    data_cnt = kw.get_repeat_cnt(trcode, rqname)
    ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

    for i in range(data_cnt):
        date = kw.comm_get_data(trcode, "", rqname, i, "일자")
        open = kw.comm_get_data(trcode, "", rqname, i, "시가")
        high = kw.comm_get_data(trcode, "", rqname, i, "고가")
        low = kw.comm_get_data(trcode, "", rqname, i, "저가")
        close = kw.comm_get_data(trcode, "", rqname, i, "현재가")
        volume = kw.comm_get_data(trcode, "", rqname, i, "거래량")

        ohlcv['date'].append(date)
        ohlcv['open'].append(int(open))
        ohlcv['high'].append(int(high))
        ohlcv['low'].append(int(low))
        ohlcv['close'].append(int(close))
        ohlcv['volume'].append(int(volume))

    return ohlcv
