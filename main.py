import time
from multiprocessing import Process, Queue
from worker import WXWork
from notice import send_hook
from msginfo import get_session, Info


wx = WXWork()


def get_task(q: Queue):
    session = get_session(False)
    while True:
        wx_start(q, [True, 13651495352, time.strftime("%Y%m%d %H:%M:%S")])
        # infos = session.query(Info).filter(Info.flag == 9)
        # for info in infos.all():
        #     wx_start(q, [True, 13651495352, info.message_detail])
        time.sleep(20)


def wx_start(q: Queue, msg: list) -> bool:
    is_success = False
    b = wx.move2search_input()
    if not b:
        q.put("{} not found search input_img".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    b = wx.move2trans2global()
    if not b:
        q.put("{} not found search global_img".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    b = wx.move2user(msg[0])
    if not b:
        q.put("{} not found search user_img".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        return is_success
    wx.cv_msg(msg[1])
    if not wx.is_found():
        q.put("not found user or group => {}".format(msg[1]))
        return is_success
    wx.enter()
    wx.cv_msg(msg[2])
    wx.enter()
    return True


def main():
    hook_q = Queue()
    p1 = Process(target=get_task, args=(hook_q,))
    p2 = Process(target=send_hook, args=(hook_q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
