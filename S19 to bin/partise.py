import tkinter
from tkinter import *
import tkinter.filedialog
import os
import numpy as np
from itertools import groupby
import struct
from binascii import *
from crcmod import *
from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import pyautogui
from pathlib import Path

def readbinfile(binfile_path):  # 将bin文件中的数据，按字节大小存入数组
    # global now
    # now = now + 1
    # t7.set('总进度 ' + str(now) + '/8')
    arr = []
    if (os.path.exists(binfile_path)):

        A = open(binfile_path, 'rb')
        size = os.path.getsize(binfile_path)  # 获得文件大小
        num = struct.unpack('B' * size, A.read(size))  # num为元组，不可修改 num = (data,)
        arr = list(num)  # 将元组转换成数组
        A.close()
        return arr
    else:
        return arr

def getFilepath(type):
    global config_path,app_s19_path,boot_s19_path,bootmanager_s19_path

    base_path = config_path.split(config_path.split('/')[-1])[0]
    if type == 'MCU':
        app_s19_path = base_path + 'MCU/'
        app_s19_path = app_s19_path + str(os.listdir(app_s19_path)[0])
        return app_s19_path
    if type == 'Boot':
        boot_s19_path = base_path + 'Boot/'
        boot_s19_path = boot_s19_path + str(os.listdir(boot_s19_path)[0])
        return boot_s19_path
    if type == 'Bootmanager':
        bootmanager_s19_path = base_path + 'Bootmanager/'
        bootmanager_s19_path = bootmanager_s19_path + str(os.listdir(bootmanager_s19_path)[0])
        return bootmanager_s19_path
    if type == 'OSD':
        osd_path = base_path + 'OSD/'
        osd_path = osd_path + str(os.listdir(osd_path)[0])
        return osd_path
    if type == 'FPGA':
        fpga_path = base_path + 'FPGA/'
        fpga_path = fpga_path + str(os.listdir(fpga_path)[0])
        return fpga_path
    if type == 'TCON':
        tcon_path = base_path + 'TCON/'
        tcon_path = tcon_path + str(os.listdir(tcon_path)[0])
        return tcon_path
    if type == 'ICON':
        icon_path = base_path + 'ICON/'
        icon_path = icon_path + str(os.listdir(icon_path)[0])
        return icon_path
    if type == 'TK':
        tk_path = base_path + 'TK/'
        tk_path = tk_path + str(os.listdir(tk_path)[0])
        return tk_path
    if type == 'TP1':
        tp_path = base_path + 'TP/'
        if len(os.listdir(tp_path)) == 2:
            tp1_path = tp_path + str(os.listdir(tp_path)[0])
            tp2_path = tp_path + str(os.listdir(tp_path)[1])
            tp1_data = readbinfile(tp1_path)
            tp2_data = readbinfile(tp2_path)
            if len(tp1_data) > len(tp2_data):
                tp1_path = tp_path + str(os.listdir(tp_path)[1])
                return tp1_path
            else:
                return tp1_path
        elif len(os.listdir(tp_path)) == 1:
            tp1_path = tp_path + str(os.listdir(tp_path)[0])
            return tp1_path
        elif len(os.listdir(tp_path)) > 2:
            tkinter.messagebox.showinfo(title='信息提示', message='TP文件放置错误')
    if type == 'TP2':
        tp_path = base_path + 'TP/'
        if len(os.listdir(tp_path)) == 2:
            tp1_path = tp_path + str(os.listdir(tp_path)[0])
            tp2_path = tp_path + str(os.listdir(tp_path)[1])
            tp1_data = readbinfile(tp1_path)
            tp2_data = readbinfile(tp2_path)
            if len(tp1_data) > len(tp2_data):
                tp2_path = tp_path + str(os.listdir(tp_path)[0])
                return tp2_path
            else:
                return tp2_path
        elif len(os.listdir(tp_path)) > 2:
            tkinter.messagebox.showinfo(title='信息提示', message='TP文件放置错误')
    if type == 'Bluetooth':
        bluetooth_path = base_path + 'Bluetooth/'
        bluetooth_path = bluetooth_path + str(os.listdir(bluetooth_path)[0])
        return bluetooth_path
    if type == 'Speaker':
        speaker_path = base_path + 'Speaker/'
        speaker_path = speaker_path + str(os.listdir(speaker_path)[0])
        return speaker_path



if __name__ == '__main__':
   block5_addr = 'NA'
   print(block5_addr.zfill(8))