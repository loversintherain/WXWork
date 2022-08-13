import json
import multiprocessing
import time

import requests


def send_hook(hook_q: multiprocessing.Queue):
    while True:
        if not hook_q.empty():
            msg = hook_q.get()
            hook_url = "https://oapi.dingtalk.com/robot/send?access_token="
            hook_token = "1880b53719bc89c21dd0ce58fc18ba01a80fe52b65cacb4fdb8ba3b74051cf67"
            hook_url += hook_token
            headers = {"Content-Type": "application/json;charset=utf-8"}
            data = {"msgtype": "text",
                    "text":
                        {"content": "WX异常消息通知:\n  {},请登录服务器查看修正错误".format(msg)}
                    }
            req = requests.post(hook_url, headers=headers, data=json.dumps(data))
            if req.status_code == 200:
                print("send hook ok， msg: {}".format(msg))
        time.sleep(10)


if __name__ == '__main__':
    pass
