import time
from multiprocessing import Process, Queue
from worker import WXWork
from notice import send_hook
from msginfo import DBSession


wx = WXWork()
db_sess = DBSession()


def get_tasks(hook_q: Queue, success_q: Queue):
    db_sess.get_send_infos()
    for info in db_sess.infos:
        if wx_start(hook_q, [True, info.phone, info.message_detail]):
            info.flag = 2
            success_q.put(info)


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
        hook_q.put("{}\n 'input_img.png' is not found ".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    b = wx.move2trans2global()
    if not b:
        hook_q.put("{}\n 'global_img.png' is not found 'global_img.png' is".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    b = wx.move2user(msg[0])
    if not b:
        hook_q.put("{}\n 'user_img.png' is not found search ".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    wx.cv_msg(msg[1])
    if not wx.is_found():
        hook_q.put("user or group is not found => {}".format(msg[1]))
        return is_success
    wx.enter()
    wx.cv_msg(msg[2])
    wx.enter()
    return True


def main():
    hook_q = Queue(10)
    success_q = Queue(10)
    # 在数据库查询信息任务
    p1 = Process(target=get_tasks, args=(hook_q, success_q))
    # 异常情况发送的钉钉报警
    p2 = Process(target=send_hook, args=(hook_q,))
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
    try:
        main()
    except Exception as e:
        print(e)
