import struct
import tkinter
from tkinter import messagebox
import socket
import numpy as np
import cv2
import threading
from PIL import Image, ImageTk
import sys
import platform
import time

BUFFERSIZE = 1024 * 1024 #4096
HOST = "192.168.1.40"
PORT = 8578
host_input = ''

ROOT = tkinter.Tk()
# 缩放大小
scale = 1
# 原传输画面尺寸
fixw, fixh = 0, 0
# 缩放标志
wscale = False
# 屏幕显示画布
showcan = None

img = None
sock = None
cv2.namedWindow("main")

last_send = time.time()

# 平台
PLAT = b'win'
if sys.platform == "win32":
    PLAT = b'win'
elif sys.platform == "darwin":
    PLAT = b'osx'
elif platform.system() == "Linux":
    PLAT = b'x11'

def main():
    global server_addr, host_input
    server_addr = tkinter.StringVar()
    # 输入框控件(服务器地址)
    host_input_label = tkinter.Label(ROOT, text="Host:")
    host_input = tkinter.Entry(ROOT, show=None, font=('Arial', 14), textvariable=server_addr)
    # 缩放控件
    scale_label = tkinter.Label(ROOT, text="Scale:")
    # from_:最小值; to:最大值; orient:方向; length:长度; showvalue:初始显示长度; resolution:最小单位0.1; tickinterval:刻度间隔;
    scale = tkinter.Scale(
        ROOT,
        from_=10,
        to=100,
        orient=tkinter.HORIZONTAL,
        length=100,
        showvalue=100,
        resolution=0.1,
        tickinterval=50,
        command=SetScale)
    # 按钮
    show_btn = tkinter.Button(ROOT, text="Show", command=ShowScreen)

    # 显示输入框控件
    host_input_label.grid(row=0, column=0, padx=10, pady=10, ipadx=0, ipady=0)
    host_input.grid(row=0, column=1, padx=0, pady=0, ipadx=40, ipady=0)
    # 显示缩放控件
    scale_label.grid(row=1, column=0, padx=10, pady=10, ipadx=0, ipady=0)
    scale.grid(row=1, column=1, padx=0, pady=0, ipadx=100, ipady=0)
    # 显示按钮
    show_btn.grid(row=2, column=1, padx=0, pady=10, ipadx=30, ipady=0)
    
    # 设置缩放控件和输入框初始值
    scale.set(100)
    server_addr.set(HOST + ':' + str(PORT))
    
    ROOT.mainloop()

def SetScale(x):
    global scale, wscale
    scale = float(x) / 100
    wscale = True

def ShowScreen():
    global showcan, ROOT, sock, th, wscale
    if showcan is None:
        wscale = True
        showcan = tkinter.Toplevel(ROOT)
        th = threading.Thread(target=run)
        th.start()
    else:
        sock.close()
        showcan.destroy()

def run():
    global sock, img, wscale, showcan, scale, fixh, fixw, host_input
    host = host_input.get()
    print('host: '  + host)
    if host is None:
        messagebox.showerror('提示', 'Host不能为空')
        return
    hostInfo = host.split(":")
    if len(hostInfo) != 2:
        messagebox.showerror('提示', "Host需要的格式为'IP:域名'")
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostInfo[0], int(hostInfo[1])))

    # 发送平台信息
    sock.sendall(PLAT)

    # unpack的B(1字节) + I(4字节) = 5字节
    lenb = sock.recv(5)
    # 图片(二进制)还有多长没有接收
    imtype, imgLength = struct.unpack(">BI", lenb)
    # 用于接收服务端传过来的图片(二进制)
    imb = b''
    # 接收所有图片数据(二进制)
    while imgLength > BUFFERSIZE:
        t = sock.recv(BUFFERSIZE)
        
        # 接收图片(二进制)
        imb += t

        # 还有多长没有接收
        imgLength -= len(t)
    
    # 接收所有图片数据(二进制) 剩下的部分
    while imgLength > 0:
        # 实际接收到的t有可能不是全部
        t = sock.recv(imgLength)
        imb += t
        imgLength -= len(t)
    
    data = np.frombuffer(imb, dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    h, w, _ = img.shape
    fixh, fixw = h, w
    imsh = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    imi = Image.fromarray(imsh)
    imgTK = ImageTk.PhotoImage(image=imi)
    cv = tkinter.Canvas(showcan, width=w, height=h, bg="white")
    cv.focus_set()
    bindEvent(cv)
    cv.pack()
    cv.create_image(0, 0, anchor=tkinter.NW, image=imgTK)
    h = int(h * scale)
    w = int(w * scale)
    

    # 不断接收差异的部分图片做加法
    while True:
        # cv2.imshow("main", cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if wscale:
            h = int(fixh * scale)
            w = int(fixw * scale)
            cv.config(width=w, height=h)
            wscale = False

        # unpack的B(1字节) + I(4字节) = 5字节
        lenb = sock.recv(5)
        imtype, imgLength = struct.unpack(">BI", lenb)
        imb = b''
        while imgLength > BUFFERSIZE:
            t = sock.recv(BUFFERSIZE)
            imb += t
            imgLength -= len(t)
        while imgLength > 0:
            t = sock.recv(imgLength)
            imb += t
            imgLength -= len(t)
        data = np.frombuffer(imb, dtype=np.uint8)
        ims = cv2.imdecode(data, cv2.IMREAD_COLOR)
        img = img + ims
        
        imt = cv2.resize(img, (w, h))
        imsh = cv2.cvtColor(imt, cv2.COLOR_RGB2RGBA)
        imi = Image.fromarray(imsh)
        imgTK.paste(imi)


def bindEvent(canvas):
    global sock, scale
    '''处理事件'''
    def eventDo(data):
        sock.sendall(data)
    
    # 鼠标左键
    def leftDown(e):
        return eventDo(struct.pack('>BBHH', 1, 100, int(e.x/scale), int(e.y/scale)))
    
    def leftUp(e):
        return eventDo(struct.pack('>BBHH', 1, 117, int(e.x/scale), int(e.y/scale)))

    canvas.bind(sequence="<1>", func=leftDown)
    canvas.bind(sequence="<ButtonRelease-1>", func=leftUp)

    # 鼠标右键
    def RightDown(e):
        return eventDo(struct.pack('>BBHH', 3, 100, int(e.x/scale), int(e.y/scale)))

    def RightUp(e):
        return eventDo(struct.pack('>BBHH', 3, 117, int(e.x/scale), int(e.y/scale)))
    canvas.bind(sequence="<3>", func=RightDown)
    canvas.bind(sequence="<ButtonRelease-3>", func=RightUp)

    # 鼠标滚轮
    if PLAT == b'win' or PLAT == 'osx':
        # windows/mac
        def Wheel(e):
            if e.delta < 0:
                return eventDo(struct.pack('>BBHH', 2, 0, int(e.x/scale), int(e.y/scale)))
            else:
                return eventDo(struct.pack('>BBHH', 2, 1, int(e.x/scale), int(e.y/scale)))
        canvas.bind(sequence="<MouseWheel>", func=Wheel)
    elif PLAT == b'x11':
        def WheelDown(e):
            return eventDo(struct.pack('>BBHH', 2, 0, int(e.x/scale), int(e.y/scale)))
        def WheelUp(e):
            return eventDo(struct.pack('>BBHH', 2, 1, int(e.x/scale), int(e.y/scale)))
        canvas.bind(sequence="<Button-4>", func=WheelUp)
        canvas.bind(sequence="<Button-5>", func=WheelDown)
    
    # 鼠标滑动
    # 100ms发送一次
    def Move(e):
        global last_send
        cu = time.time()
        if cu - last_send > 0.02:
            last_send = cu
            sx, sy = int(e.x/scale), int(e.y/scale)
            return eventDo(struct.pack('>BBHH', 4, 0, sx, sy))
    canvas.bind(sequence="<Motion>", func=Move)

    # 键盘
    def KeyDown(e):
        return eventDo(struct.pack('>BBHH', e.keycode, 100, int(e.x/scale), int(e.y/scale)))

    def KeyUp(e):
        keycode = e.keycode
        if keycode < 256:
            return eventDo(struct.pack('>BBHH', keycode, 117, int(e.x/scale), int(e.y/scale)))

    canvas.bind(sequence="<KeyPress>", func=KeyDown)
    canvas.bind(sequence="<KeyRelease>", func=KeyUp)

if __name__ == "__main__":
    main()
