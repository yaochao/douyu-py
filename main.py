#!/usr/bin/env python
# -*- coding: utf-8 -*-
# created by yaochao at 2023/4/20


import random
import json
import requests
import execjs
import datetime
import urllib.request


def get_douyu_did():
    random_num = random.randint(0, 1000000)
    callback = f"jsonp_{random_num}"
    did_url = f"https://passport.douyu.com/lapi/did/api/get?client_id=1&callback={callback}"
    headers = {"Referer": "https://www.douyu.com"}
    resp = requests.get(did_url, headers=headers, timeout=5.0)
    resp_text = resp.text.strip()[len(callback) + 1:-1]
    resp_dict = json.loads(resp_text)
    if not isinstance(resp_dict, dict) or resp_dict.get("error", 1) != 0:
        return False
    did = resp_dict.get("data", {}).get("did")
    return did


def get_room_js(room_id):
    room_js_uRL = "https://www.douyu.com/swf_api/homeH5Enc?rids={}".format(room_id)
    response = requests.get(room_js_uRL, timeout=5.0)
    if response.status_code == requests.codes.ok:
        resp_dic = json.loads(response.content)
        if resp_dic and isinstance(resp_dic, dict) and resp_dic.get("error") == 0:
            room_js = resp_dic.get("data", {}).get("room{}".format(room_id))
            return room_js
    return ""


def get_room_info(room_id, rate):
    """
    获取流媒体的直播地址
    :param room_id: 房间号
    :param rate: 码率：0，1，2，3
    :return: url
    """
    room_js = get_room_js(room_id)
    did = get_douyu_did()
    ts = int(datetime.datetime.now().timestamp())

    # 创建执行环境
    full_js = "var CryptoJS = require('./crypto-js');" + room_js
    js_ctx = execjs.compile(full_js)
    result = js_ctx.call("ub98484234", room_id, did, ts)
    post_string = f"{result}&cdn=&rate={rate}&ver=Douyu_219021902&iar=1&ive=0".encode('utf-8')

    url = f"https://www.douyu.com/lapi/live/getH5Play/{room_id}"
    request = urllib.request.Request(url)
    request.method = 'POST'
    request.data = post_string
    with urllib.request.urlopen(request, timeout=5.0) as response:
        room_data = response.read()
    response = json.loads(room_data.decode('utf-8'))
    data = response["data"]
    rtmp_prefix = data["rtmp_url"]
    rtmp_suffix = data["rtmp_live"]
    video_url = f"{rtmp_prefix}/{rtmp_suffix}"
    return video_url


if __name__ == '__main__':
    video_url = get_room_info(7996620, 0)
    print(video_url)
