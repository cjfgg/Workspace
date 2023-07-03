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


def getS19Data(s19file_path):
    A = open(s19file_path, 'r+')
    a = A.readlines()
    s_data = ''
    l = ''
    for i in a:
        l = l + i.__str__()  # 将s19所有字符转为字符串
    all_line = l.split('\n')  # 分割每一行
    j = len(all_line)
    t_all_line = []
    for i in all_line:
        if i[5:10] == '14200':  # 14200是刷写APP的首地址，往前的地址都属于bootloader，请注意
            t_all_line = all_line[all_line.index(i):]
        else:
            continue
    for i in t_all_line:
        if i.__contains__('S0'):
            count = int(str(i)[2:4], 16)
            count = count * 2
            S0_data = str(i)
            S0_data = S0_data[8:count + 2]
            s_data = s_data + S0_data
        elif i.__contains__('S3'):
            count = int(str(i)[2:4], 16) * 2
            S3_data = str(i)
            S3_data = S3_data[12:count + 2]
            s_data = s_data + S3_data
        elif i.__contains__('S2'):
            count = int(str(i)[2:4], 16) * 2
            S2_data = str(i)
            S2_data = S2_data[10:count + 2]
            s_data = s_data + S2_data
    A.close()
    return s_data


# def CRC16_Modbus(read):    #CRC-16/MODBUS
#     crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
#     data = read.replace(" ", "")
#     read_crcout = hex(crc16(unhexlify(data))).upper()
#     str_list = list(read_crcout)
#     if len(str_list) < 6:
#         str_list.insert(2, '0' * (6 - len(str_list)))  # 位数不足补0
#     crc_data = "".join(str_list)
#
#     read = read.strip() + ' ' + crc_data[4:] + ' ' + crc_data[2:4]
#     crc = crc_data[4:] + crc_data[2:4]
#     return crc

def CRC16_XMODEM(read):  # 获取CRC-16 XMODEM校验码时实参必须是字符串,返回也是字符串
    crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    data = read.replace(" ", "")
    readcrcout = hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')  # 位数不足补0
    crc_data = "".join(str_list)
    crc_data = int(crc_data[2:], 16)
    crc_data = "%04x" % crc_data
    read = read.strip() + crc_data
    return crc_data.zfill(8)


def strToasscii(A):  # 将零件号和版本号从字符串转换为以16进制字符串表示的ASCII码
    x = ''
    if len(A) < 20:
        for i in range(20 - len(A)):
            A = A + ' '
    for i in A:
        x = x + hex(ord(i)).replace('0x', '')
    return x


def reversal(A):  # 将字符串按两位进行反转,返回的是反转后的字符串
    if A == '':
        return ''
    else:
        a = A.replace(' ', '')
        stack = []
        str = ''
        for i in range(len(a)):
            if i % 2 == 0:
                stack.append(a[i:i + 2])
        stack.reverse()
        for i in stack:
            str = str + hex(int(i, 16)).replace('0x', '').zfill(2)
        return str


def split_into_array(s_data):  # 将字符串按两位分割存入数组，形参为字符串
    s_data_arr = []
    # p1["maximum"] = len(s_data)
    # p1["value"] = 0
    # global now
    # now = now + 1
    # t7.set('总进度 '+ str(now)+ '/8')
    if s_data == '':
        return s_data_arr
    else:
        for i in range(len(s_data)):
            # p1["value"] = i + 1
            if i % 2 == 0:
                s_data_arr.append(s_data[i:i + 2])
            app.update()
        return s_data_arr


def intTobin(arr, binfilepath):  # 形参arr为字符串数组，binfilepath为要写入的bin文件路径
    # global p1
    # p1["maximum"] = len(arr)
    # p1["value"] = 0
    # global now
    # now = now + 1
    # t7.set('总进度 '+str(now)+'/8')
    binfilepath = open(binfilepath, 'wb')
    for i in arr:  # 遍历数组
        x = bin(int(i, 16)).replace('0b', '').zfill(8)  # 将数组元素转换为字符串形式的二进制
        b = 0b00000000
        for j in x:  # 获取8位01字符，
            if j == '0':
                b = b << 1
            else:
                b = b << 1
                b = b | 0b00000001
        a = struct.pack('B', b)
        binfilepath.write(a)  # 写入bin文件，每次写入8位，也就是一个字节的数据
        # p1["value"] = p1["value"] +1
        # app.update()
    binfilepath.close()


def readbinfile(binfile_path):  # 将bin文件中的数据，按字节大小存入数组
    # global now
    # now = now + 1
    # t7.set('总进度 ' + str(now) + '/8')
    arr = []
    if (binfile_path == ''):
        return arr
    else:
        A = open(binfile_path, 'rb')
        size = os.path.getsize(binfile_path)  # 获得文件大小
        for i in range(size):
            data = A.read(1)
            num = struct.unpack('B', data)  # num为元组，不可修改 num = (data,)
            arr = arr + list(num)  # 将元组转换成数组
        A.close()
        return arr


def element_into_str(arr):  # 将bin文件中的FFFFFFFF后的数据全部转成字符串
    str2 = ''
    # global now
    # now = now + 1
    # t7.set('总进度 '+ str(now)+ '/8')
    # p1["maximum"] = len(arr)
    # p1["value"] = 0
    if arr == []:
        return ''
    else:
        for i in arr:
            #p1["value"] = p1["value"] +1
            str2 = str2 + hex(int(i)).replace('0x', '').zfill(2)
            app.update()
        return str2


def ifnull(str):
    if str == '00000000':
        return ''
    else:
        return str


###########################      以下为控件方法   #################################


def get_mcu():
    filename = tkinter.filedialog.askopenfilename()
    if filename != '':
        global mcu_bin_path
        mcu_bin_path = filename  # 将MCU.bin的路径传回全局变量
        mcu_path.set(filename)
    else:
        mcu_path.set('未选择文件')


def get_tp():
    filename = tkinter.filedialog.askopenfilename()
    if filename != '':
        global tp_bin_path
        tp_bin_path = filename  # 将tp.bin路径传回全局变量
        tp_path.set(filename)
    else:
        tp_path.set('未选择文件')


def get_slider():
    filename = tkinter.filedialog.askopenfilename()
    if filename != '':
        global slider_bin_path
        slider_bin_path = filename
        slider_path.set(filename)
    else:
        slider_path.set('未选择文件')


def start():
    # global now
    # now = 0
    btn4.config(state = 'disabled')
    app.update()
    final_binfilepath = 'final.bin'  # bin文件路径
    app_data = element_into_str(readbinfile(mcu_path.get()))  # 获取app.bin文件的数据
    tp_data = element_into_str(readbinfile(tp_path.get()))  # 获取TP.bin文件的数据
    slider_data = element_into_str(readbinfile(slider_path.get()))  # 获取Slider.bin文件的数据
    update_data = app_data + tp_data + slider_data
    component_num = t1.get()  # 字符串类型的零件号 无需反转
    t_component_num = strToasscii(component_num)  # 得到零件号字符串(16进制的ASCII码值)
    version_num = t2.get()  # 版本号以字符串输入无需反转
    t_version_num = strToasscii(version_num)  # 得到版本号字符串(16进制的ASCII码值)
    block_num = t3.get()  # 未进行反转的block数量
    t_block_num = reversal(block_num.zfill(8))
    block1_addr = t4.get()  # 未进行反转的block1地址
    t_block1_addr = ifnull(reversal(block1_addr.zfill(8)))
    block1_len = ifnull(hex(int(len(app_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block1长度
    t_block1_len = ifnull(reversal(block1_len))
    block2_addr = t5.get()  # 未进行反转的block2地址
    t_block2_addr = ifnull(reversal(block2_addr.zfill(8)))
    block2_len = ifnull(hex(int(len(tp_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block2长度
    t_block2_len = ifnull(reversal(block2_len))
    block3_addr = t6.get()  # 未进行反转的block3地址
    t_block3_addr = ifnull(reversal(block3_addr.zfill(8)))
    block3_len = ifnull(hex(int(len(slider_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block3长度
    t_block3_len = ifnull(reversal(block3_len))
    headfile_flag = 'FFFFFFFF'
    t_block = t_block_num + t_block1_addr + t_block1_len + t_block2_addr + t_block2_len + t_block3_addr + t_block3_len  # 拼接反转后的block数据
    headfile_len = hex(64 + int(block_num) * 8).replace('0x', '').zfill(8)  # 头文件长度,序列1-15的长度
    headfile_len.replace(' ', '').zfill(8)
    t_headfile_len = reversal(headfile_len)
    head_data = t_headfile_len + t_component_num + t_version_num + t_block + headfile_flag  # 反转后的序列4-15内容
    CRC16_head = reversal(CRC16_XMODEM(head_data))  # 序列1的内容
    CRC16_update_data = reversal(CRC16_XMODEM(update_data))  # 序列2的内容
    headandupdate_data = head_data + update_data  # 序列4-N的内容
    CRC16_bin = reversal(CRC16_XMODEM(headandupdate_data))  # 序列3的内容
    all_data = CRC16_head + CRC16_update_data + CRC16_bin + headandupdate_data
    all_data = all_data.replace(' ', '')
    bin_data = intTobin(split_into_array(all_data), final_binfilepath)  # 字符串每两位入
    btn4.config(state='normal')
    result = tkinter.messagebox.showinfo(title='信息提示', message='合并完成！文件名为final.bin')


if __name__ == '__main__':
    head_data = ''  # 头文件数据部分，序列4-15的内容
    all_data = ''
    d = []
    mcu_bin_path = ''
    tp_bin_path = ''
    slider_bin_path = ''
    app = tkinter.Tk()
    app.geometry('500x500')
    app.title('bin工具')
    mcu_path = tkinter.StringVar()
    tp_path = tkinter.StringVar()
    slider_path = tkinter.StringVar()
    entry1 = tkinter.Entry(app, textvariable=mcu_path, width=22, ).place(x=120, y=20)
    entry2 = tkinter.Entry(app, textvariable=tp_path, width=22, ).place(x=120, y=60)
    entry3 = tkinter.Entry(app, textvariable=slider_path, width=22, ).place(x=120, y=100)
    btn1 = Button(app, text='选择文件', command=get_mcu, width=6, height=1).place(x=300, y=17)
    btn2 = Button(app, text='选择文件', command=get_tp, width=6, height=1).place(x=300, y=56)
    btn3 = Button(app, text='选择文件', command=get_slider, width=6, height=1).place(x=300, y=94)
    label1 = Label(text='MCU bin').place(x=50, y=20)
    label2 = Label(text='TP bin').place(x=50, y=60)
    label3 = Label(text='slider bin').place(x=50, y=100)
    label4 = Label(text='零件号').place(x=50, y=170)
    label5 = Label(text='版本号').place(x=50, y=200)
    label6 = Label(text='block数量').place(x=50, y=230)
    label7 = Label(text='block1地址').place(x=50, y=260)
    label8 = Label(text='block2地址').place(x=50, y=290)
    label9 = Label(text='block3地址').place(x=50, y=320)
    t1 = StringVar()
    t2 = StringVar()
    t3 = StringVar()
    t4 = StringVar()
    t5 = StringVar()
    t6 = StringVar()
    text1 = Entry(app, textvariable=t1).place(x=120, y=170)
    text2 = Entry(app, textvariable=t2).place(x=120, y=200)
    text3 = Entry(app, textvariable=t3).place(x=120, y=230)
    text4 = Entry(app, textvariable=t4).place(x=120, y=260)
    text5 = Entry(app, textvariable=t5).place(x=120, y=290)
    text6 = Entry(app, textvariable=t6).place(x=120, y=320)
    btn4 = Button(app, text='开始合并', command=start)
    btn4.place(x=300, y=230)
    # t7 = StringVar()
    # now = 0
    # t7.set('总进度 '+str(now)+'/8')
    # label10 = Label(app,textvariable=t7).place(x=50, y=370)
    # p1 = ttk.Progressbar(app,length =200, mode = "determinate", orient = HORIZONTAL)
    # p1.place(x = 120 , y = 370 )

    app.mainloop()
