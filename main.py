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
wx = WXWork(test)
db_sess = DBSession(test)


def get_tasks(hook_q: Queue, success_q: Queue, exit_q: Queue):
    while True:
        # 任务获取的时间段。不在时间段内则不获取任务。
        if time.time():
            pass
        db_sess.get_send_infos()
        for info in db_sess.infos:
            # 消息发送成功，将flag置为2， 失败flag置为9.
            if wx_start(hook_q, exit_q, [True, info.phone, info.message_detail]):
                info.flag = 2
            else:
                info.flag = 9
            success_q.put(info)
            print("-" * 80)
        time.sleep(10)


def transfer_status(success_q: Queue):
    while True:
        if not success_q.empty():
            info = success_q.get()
            db_sess.transfer2success(info)
            continue
        time.sleep(10)


def wx_start(hook_q: Queue, exit_q: Queue, msg: list) -> bool:
    b = wx.move2search_input()
    if not b:
        hook_q.put("{}\n 'input_img.png' is not found".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        exit_after_failed(exit_q)
        return False
    b = wx.move2trans2global()
    if not b:
        hook_q.put("{}\n 'global_img.png' is not found".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        exit_after_failed(exit_q)
        return False
    if msg[0]:
        b = wx.move2user()
    else:
        b = wx.move2group()
    if not b:
        hook_q.put("{}\n 'user_img.png' is not found".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        exit_after_failed(exit_q)
        return False
    # 复制粘贴接收人或群组信息。
    wx.cv_msg(msg[1])
    if not wx.is_found():
        hook_q.put("user or group is not found => {}".format(msg[1]))
        return False
    wx.enter()
    wx.cv_msg(msg[2])
    first_check = wx.need_add_user()
    if wx.send_ok:
        wx.enter()
        time.sleep(2)
        # 消息发送后是否被正常接收。
        second_check = wx.need_add_user()
        if first_check == 0 and second_check == 0:
            return True
        elif first_check > second_check:
            return True
        elif first_check == 0 and second_check != 0:
            return False
        elif first_check <= second_check:
            return False
    return False


# 当没有找到必须的图像时，程序会推送钉钉报警，并在15秒后退出执行。
def exit_after_failed(exit_q: Queue, exit_time: int = 15):
    time.sleep(exit_time)
    exit_q.put(4004)


# 判断各个关键图像是否存在。不存在则不再往下执行。
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
    exit_q = Queue(1)
    proc_pool: [Process] = list()
    # 此进程在数据库查询信息任务
    proc_pool.append(Process(target=get_tasks, args=(hook_q, success_q, exit_q)))
    # 此进程异常情况发送的钉钉报警
    proc_pool.append(Process(target=send_hook_q, args=(hook_q,)))
    # 此进程信息发送成功后更新数据库状态
    proc_pool.append(Process(target=transfer_status, args=(success_q,)))
    # 此进程用于处理数据库的话术拼接，资产的信息查询

    for proc in proc_pool:
        proc.start()
    exit_code = 0
    while True:
        if exit_q.empty():
            time.sleep(1)
            continue
        exit_code = exit_q.get()
        for proc_s in proc_pool:
            proc_s.terminate()
        break
    exit(exit_code)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(argv) > 1:
        test: bool = False
    else:
        test: bool = True
    print("TEST_env: {}".format(test))
    init_check()
    try:
        main()
    except Exception as e:
        print(e)
