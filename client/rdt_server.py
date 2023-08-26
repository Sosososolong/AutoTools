import struct
import socket
from PIL import ImageGrab
import cv2
import numpy as np
import threading
import pyautogui
import mouse
from rdt_keyboard import getKeycodeMapping 

BUFFERSIZE = 1024 * 1024 #4096
HOST = ('0.0.0.0', 8578)
FREQUENCY = 20

# 鼠标每次滚动多少(鼠标滚轮灵敏度)
SCROLL_NUM = 5

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(HOST)
    # 等待处理的连接队列的最大长度为1
    soc.listen(1)
    img = None
    while True:
        conn, addr = soc.accept()
        view_thread = threading.Thread(target=handle, args=(conn,))
        view_thread.start()

        ctrl_thread = threading.Thread(target=ctrl, args=(conn,))
        ctrl_thread.start()




def handle(conn):
    global img
    # 截图获取Image对象
    screenshot = ImageGrab.grab()
    # 转换为数组 NDArray 再 转换为png(二进制); 可做减法计算
    img = np.asarray(screenshot)
    _, imb = cv2.imencode(".png", img)

    # 打包(编码)准备发送(BI传两个数, B: 读取1字节数, I: 读取4字节数), 1表示传原图, 0表示传差异图像
    lenb = struct.pack(">BI", 0, len(imb))
    conn.sendall(lenb)
    conn.sendall(imb)
    while True:
        # 每隔100毫秒(每秒10次)截图, 只计算发送和上次图片比有差异的部分
        cv2.waitKey(FREQUENCY)
        gb = ImageGrab.grab()
        imgnpn = np.asarray(gb)
        subn = imgnpn - img
        if (subn == 0).all():
            continue

        img = imgnpn
        _, imb = cv2.imencode(".png", subn)
        dlen = len(imb)
        lenb = struct.pack(">BI", 0, dlen)
        try:
            conn.sendall(lenb)
            conn.sendall(imb)
        except:
            print("连接中断...")
            return


def ctrl(conn):
    '''
    读取控制命令并按命令操作
    '''
    print('ctrl start')
    keycodeMapping = {}
    def execute(key, op, ox, oy):
        if key == 4:
            # 鼠标移动
            mouse.move(ox, oy)
        elif key == 1:
            if op == 100:
                # 左键按下 down(d: 100)
                pyautogui.mouseDown(button=pyautogui.LEFT)
            elif op == 117:
                # 左键弹起 up(u:117)
                pyautogui.mouseUp(button=pyautogui.LEFT)
        elif key == 2:
            # 滚轮事件
            if op == 0:
                # 向上
                pyautogui.scroll(-SCROLL_NUM)
            else:
                pyautogui.scroll(SCROLL_NUM)
        elif key == 3:
            # 鼠标右键
            if op == 100:
                # 按下
                pyautogui.mouseDown(button=pyautogui.RIGHT)
            elif op == 117:
                # 弹起
                pyautogui.mouseUp(button=pyautogui.RIGHT)
        else:
            # 键盘按键
            k = keycodeMapping.get(key)
            if k is not None:
                if op == 100:
                    pyautogui.keyDown(k)
                elif op == 117:
                    pyautogui.keyUp(k)

    try:
        plat = b''
        while True:
            plat += conn.recv(3 - len(plat))
            if len(plat) == 3:
                break
        print('ctrl plat: ', plat.decode())
        keycodeMapping = getKeycodeMapping(plat)
        base_len = 6
        while True:
            cmd = b''
            rest = base_len - 0
            while rest > 0:
                cmd += conn.recv(rest)
                rest -= len(cmd)
            key = cmd[0]
            op = cmd[1]
            x = struct.unpack('>H', cmd[2:4])[0]
            y = struct.unpack('>H', cmd[4:6])[0]
            execute(key, op, x, y)
    except:
        return

if __name__ == '__main__':
    main()