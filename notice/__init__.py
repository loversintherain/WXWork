import json
import multiprocessing
import random
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
        else:
            time.sleep(10)


def send_hook(msg: str):
    picture = get_rand_picture()
    data = {"msgtype": "markdown",
            "markdown": {
                "title": "WX异常消息通知:",
                "text": "#### {}\n![]({})**请登录企业微信服务器查看并修正错误后重试！**".format(msg, picture)
            },
            "at": {
                "isAtAll": True
            }
            }
    req = requests.post(hook_url, headers=headers, data=json.dumps(data))
    if req.status_code == 200:
        print("send hook ok")


def get_rand_picture() -> str:
    pictures = [
        "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpicnew6.photophoto.cn%2F20111126%2Fjinmaogouchongwutupia"
        "n-09761083_1.jpg&refer=http%3A%2F%2Fpicnew6.photophoto.cn&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?se"
        "c=1663139452&t=518625387046536de25ecee19b326399"
    ]
    for _ in range(10):
        rand_pic = random.choice(pictures)
        result = requests.get(rand_pic)
        if result.status_code == 200:
            return rand_pic
    return "hello world"


if __name__ == '__main__':
    for i in range(16):
        send_hook("55555")
    pass
