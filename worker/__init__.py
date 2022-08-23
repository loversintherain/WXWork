import time

import pyautogui as pg
import pyperclip

PAUSE_TIME = 0.5
# 设置每个pg操作间隔
pg.PAUSE = PAUSE_TIME
pg.FAILSAFE = False


class WXWork(object):
    def __init__(self, test: bool = True):
        if test:
            self.img_dir = "./img_test/"
        else:
            self.img_dir = "./img_ser/"
        self.key_word = "{}key_word.png".format(self.img_dir)
        self.notfound = "{}notfound.png".format(self.img_dir)
        self.all_search_items = "{}allsearchitems.png".format(self.img_dir)
        self.search_input = "{}searchinput.png".format(self.img_dir)
        # self.search_input2 = "{}searchinput2.png".format(self.img_dir)
        self.trans2global = "{}trans2global.png".format(self.img_dir)
        self.send_img = "{}send_img.png".format(self.img_dir)
        self.search_input_global = "{}searchinputglobal.png".format(self.img_dir)
        self.search_input_global2 = "{}searchinputglobal2.png".format(self.img_dir)
        self.need_add = "{}need_add.png".format(self.img_dir)
        self.show_log = True

    # 将鼠标移动到搜索框并双击, 第一次寻找搜索框未找到时，会先尝试关闭全部搜索框，再进行第二次寻找搜索框。
    def move2search_input(self, offset: tuple = (50, 15)) -> bool:
        self.show_logs(self.search_input)
        # 第一次
        if not WXWork.move_and_click(self.search_input, offset):
            self.close_key_word()
        else:
            return True
        # 必要时，第二次
        return WXWork.move_and_click(self.search_input, offset)

    # 将鼠标移动到全局搜索并单击
    def move2trans2global(self,  offset: tuple = (50, 10)) -> bool:
        self.show_logs(self.trans2global)
        return WXWork.move_and_click(self.trans2global, offset)

    # 找到全局搜索的图，返回左上角坐标(x, y)
    def get_all_search_items(self) -> tuple:
        ret = pg.locateOnScreen(self.all_search_items)
        if ret is None:
            return -1, -1
        return tuple(ret[0:2])

    # 将鼠标移动到联系人上并点击后再移动到全局搜索并点击,is_user表示搜索的是联系人还是群组。
    def move2user(self, is_user: bool = True) -> bool:
        self.show_logs(self.all_search_items)
        if is_user:
            offset: tuple = (30, 10)
        else:
            offset: tuple = (80, 10)
        x, y = self.get_all_search_items()
        if x < 0 and y < 0:
            return False
        x += offset[0]
        y += offset[1]
        pg.moveTo(x, y, PAUSE_TIME)
        pg.click()
        # 鼠标点击联系人或群组之后再找搜索框。
        # ret = WXWork.move_and_click(self.search_input_global, offset=(80, 15))
        # if not ret:
        #     ret = WXWork.move_and_click(self.search_input_global2, offset=(80, 15))
        #     if not ret:
        #         return False
        return True

    def move2group(self):
        self.move2user(False)

    # 判断是否发现输入的用户或群组
    def is_found(self) -> bool:
        ret = pg.locateOnScreen(self.notfound)
        return False if ret else True

    # 当第一次没有找到输入框，就会寻找是否是进入了全局搜索，如果找到就会关闭。
    def close_key_word(self):
        WXWork.move_and_click(self.key_word, offset=(10, 10))

    # 判断'发送'按钮是否可以点击。
    def send_ok(self) -> bool:
        ret = pg.locateOnScreen(self.send_img)
        if ret is None:
            return False
        return True

    # 在发送的前后判断消息是否被正常接收
    def need_add_user(self) -> int:
        ret = pg.locateAllOnScreen(self.need_add)
        if not ret:
            *_, last_pos = ret
            return int(last_pos.top)
        return 0

    # 将输入框内容全部选中删除，然后将msg复制到clip并粘贴。
    @staticmethod
    def cv_msg(msg):
        pg.hotkey("ctrl", "a")
        pg.press("delete")
        pyperclip.copy(msg)
        pg.hotkey("ctrl", "v")

    @staticmethod
    def enter():
        pg.press("enter")

    # 先屏幕找图img，发现了该图就在x，y上offset后将鼠标移动过去并点击，没有发现返回False
    @staticmethod
    def move_and_click(img: str, offset: tuple) -> bool:
        ret = pg.locateOnScreen(img)
        if ret is None:
            print("'{}': move_and_click not found '{}'".format(time.strftime("%Y-%m-%d %H:%M:%S"), img[2:]))
            return False
        x, y = ret[0:2]
        x += offset[0]
        y += offset[1]
        pg.moveTo(x, y, PAUSE_TIME)
        if img.endswith("searchinput.png") or img.endswith("searchinput2.png"):
            pg.doubleClick()
        else:
            pg.click()
        return True

    # 检查消息是否被接收
    def final_check_success(self):
        pg.locateAllOnScreen(self.final_check)

    def show_logs(self, img: str):
        if self.show_log:
            print("'{}': Start to find out the image: {}".format(time.strftime("%Y-%m-%d %H:%M:%S"), img[2:]))

    def __call__(self, *args, **kwargs):
        print("I can send messages to users and groups automation!!")
