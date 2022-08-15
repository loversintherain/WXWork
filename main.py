import os
import time
from sys import argv
from multiprocessing import Process, Queue
from worker import WXWork
from notice import send_hook_q, send_hook
from msginfo import DBSession

# 获取企业微信对象,数据库操作对象,如果是测试可以不传或传入True， 传入False则进入正式环境
if len(argv) > 1:
    test: bool = False
else:
    test: bool = True
print("TEST_env: {}".format(test))
wx = WXWork(test)
db_sess = DBSession(test)


def get_tasks(hook_q: Queue, success_q: Queue):
    while True:
        # 任务获取的时间段。不在时间段内则不获取任务。
        if time.time():
            pass
        db_sess.get_send_infos()
        for info in db_sess.infos:
            if wx_start(hook_q, [True, info.phone, info.message_detail]):
                info.flag = 2
                success_q.put(info)
            print("-" * 80)
        time.sleep(10)


def transfer2success(success_q: Queue):
    while True:
        if not success_q.empty():
            info = success_q.get()
            db_sess.transfer2success(info)
        time.sleep(10)


def wx_start(hook_q: Queue, msg: list) -> bool:
    is_success = False
    b = wx.move2search_input()
    if not b:
        hook_q.put("{}\n 'input_img.png' is not found".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    b = wx.move2trans2global()
    if not b:
        hook_q.put("{}\n 'global_img.png' is not found".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    b = wx.move2user(msg[0])
    if not b:
        hook_q.put("{}\n 'user_img.png' is not found".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    wx.cv_msg(msg[1])
    if not wx.is_found():
        hook_q.put("user or group is not found => {}".format(msg[1]))
        return is_success
    wx.enter()
    wx.cv_msg(msg[2])
    if wx.send_ok:
        wx.enter()
        return True
    return False


def init_check():
    pngs_set_exist = set()
    pngs_set_must = {'allsearchitems.png',
                     'key_word.png',
                     'notfound.png',
                     'searchinput.png',
                     'searchinputglobal.png',
                     'searchinputglobal2.png',
                     'send_img.png',
                     'trans2global.png'}
    for _, _, files in os.walk(wx.img_dir, topdown=False):
        pngs_set_exist = set(files)
    pngs = list(pngs_set_must - pngs_set_exist)
    if len(pngs):
        send_hook("{} '{}' not found".
                  format(time.strftime("%Y-%m-%d %H:%M:%S"),
                         ", ".join(pngs),
                         wx.img_dir
                         ))
        exit(-1)


def main():
    hook_q = Queue(10)
    success_q = Queue(10)
    # 在数据库查询信息任务
    p1 = Process(target=get_tasks, args=(hook_q, success_q))
    # 异常情况发送的钉钉报警
    p2 = Process(target=send_hook_q, args=(hook_q,))
    # 信息发送成功后更新数据库状态
    p3 = Process(target=transfer2success, args=(success_q,))
    # p4 用于处理数据库的话术拼接，资产的信息查询
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    init_check()
    try:
        main()
    except Exception as e:
        print(e)
