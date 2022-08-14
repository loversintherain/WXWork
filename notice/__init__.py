import json
import multiprocessing
import time
import requests

hook_url = "https://oapi.dingtalk.com/robot/send?access_token="
hook_token = "1880b53719bc89c21dd0ce58fc18ba01a80fe52b65cacb4fdb8ba3b74051cf67"
hook_url += hook_token
headers = {"Content-Type": "application/json;charset=utf-8"}


def send_hook_q(hook_q: multiprocessing.Queue):
    while True:
        if not hook_q.empty():
            msg = hook_q.get()
            send_hook(msg)
        time.sleep(10)


def send_hook(msg: str):
    data = {"msgtype": "text",
            "text":
                {"content": "WX异常消息通知:\n   {}\n  请登录企业微信服务器查看并修正错误后重试！".format(msg)}
            }
    req = requests.post(hook_url, headers=headers, data=json.dumps(data))
    if req.status_code == 200:
        print("send hook ok")


if __name__ == '__main__':
    pass
