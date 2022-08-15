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
        "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fup.enterdesk.com%2Fedpic_source%2F45%2Ffa%2Fb7%2F45fab71"
        "282dae578be117d2cb4e76eb1.jpg&refer=http%3A%2F%2Fup.enterdesk.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt"
        "=auto?sec=1663065095&t=cdafd16c67d3a32bded7867945f53498",
        "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fup.enterdesk.com%2Fedpic_source%2Fc6%2F04%2F1a%2Fc6041a9"
        "fbccdf051217fb50483cc2a4f.jpg&refer=http%3A%2F%2Fup.enterdesk.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt"
        "=auto?sec=1663065513&t=d90d1cb44db655e12b0fa0184ec40dd9",
        "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic1.win4000.com%2Fpic%2F3%2Fa5%2F5838854cb9.jpg&refer=h"
        "ttp%3A%2F%2Fpic1.win4000.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1663065513&t=56f8c3c2368310"
        "16c3a0016719fc4729",
        "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic1.win4000.com%2Fpic%2F7%2F4d%2F0ec2813734.jpg&refer=h"
        "ttp%3A%2F%2Fpic1.win4000.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1663065619&t=ad5ce07a214d0f"
        "496a8ee9693ca950f0",
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
