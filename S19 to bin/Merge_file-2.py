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
    s_data = ''
    l = ''
    if s19file_path != '':
        A = open(s19file_path, 'r+')
        a = A.readlines()
        A.close()
        for i in a:
            l = l + i.__str__()  # 将s19所有字符转为字符串
        all_line = l.split('\n')  # 分割每一行
        j = len(all_line)
        # t_all_line = []
        # for i in all_line:
        #     if i[5:10] == '14200':  # 14200是刷写APP的首地址，往前的地址都属于bootloader，请注意
        #         t_all_line = all_line[all_line.index(i):]
        #     else:
        #         continue
        for i in all_line:

            j = all_line.index(i)
            if i.__contains__('S3'):
                if int(str(i)[2:4], 16) - 5 == int(str(all_line[j + 1])[4:12], 16) -int(str(all_line[j])[4:12], 16):
                    count = int(str(i)[2:4], 16) * 2
                    S3_data = str(i)
                    S3_data = S3_data[12:count + 2]
                    s_data = s_data + S3_data
                else:
                    S3_data = str(i)
                    count = int(str(i)[2:4], 16) * 2
                    S3_data = S3_data[12:count + 2]

                    drift_len = int(str(all_line[j + 1])[4:12], 16) - int(str(all_line[j])[4:12], 16) - (int(count/2)-5)
                    for k in range(drift_len):
                        S3_data = S3_data + 'FF'       #地址填充
                    s_data = s_data + S3_data
            elif i.__contains__('S2'):
                if int(str(all_line[j + 1])[4:12]) - int(str(all_line[j])[4:12]) == 28:
                    count = int(str(i)[2:4], 16) * 2
                    S2_data = str(i)
                    S2_data = S2_data[10:count + 2]
                    s_data = s_data + S2_data
    else:
        s_data = ''
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
    if A == '00000000':
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
            # app.update()
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
        num = struct.unpack('B'*size, A.read(size))  # num为元组，不可修改 num = (data,)
        arr = list(num)  # 将元组转换成数组
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
            # app.update()
        return str2


def ifnull(str):
    if str == '00000000' or str == '':
        return ''
    else:
        return str



###########################      以下为控件方法   #################################

def get_binC():
    global filename
    filename = tkinter.filedialog.askopenfilename()
    if filename != '':
        binC_path.set(filename)


def drift_4k(str):
    fill_FF = ''
    for i in range(4084):
        fill_FF = fill_FF +'FF'
    return fill_FF+str

def creat_backup_binfile(backup_path):
    global s19file_path,bin_path_1,bin_path_2,bin_path_3,bin_path_4,bin_path_5,bin_path_6
    backup_app_data = ''
    backup_boot_data = ''
    backup_key_data = ''
    backup_tp1_data = ''
    backup_tp2_data = ''

    backup_app_data = element_into_str(readbinfile(bin_path_1))
    backup_boot_data = element_into_str(readbinfile(bin_path_2))
    backup_key_data = element_into_str(readbinfile(bin_path_3))
    backup_tp1_data = element_into_str(readbinfile(bin_path_4))
    backup_tp2_data = element_into_str(readbinfile(bin_path_5))

    backup_app_len = reversal(hex(int(len(backup_app_data)/2)).replace('0x','').zfill(8))
    backup_app_crc = reversal(CRC16_XMODEM(backup_app_data).zfill(8))  # 备份文件的APP数据部分的校验码
    backup_app = 'A5A5A5A5' + backup_app_len + backup_app_crc + drift_4k(backup_app_data)
    if (len(backup_app)) / 2 < 655360:
        looptime = int(655360 - (len(backup_app) / 2))
        for i in range(looptime):
            backup_app = backup_app + 'FF'

    if backup_boot_data !='':
        backup_boot_len = reversal(hex(int(len(backup_boot_data)/2)).replace('0x','').zfill(8))
        backup_boot_crc = reversal(CRC16_XMODEM(backup_boot_data).zfill(8))
        backup_boot = 'A5A5A5A5' + backup_boot_len + backup_boot_crc + drift_4k(backup_boot_data)
        if (len(backup_boot)/2)<131072:
            looptime = int(131072-(len(backup_boot)/2))
            for i in range(looptime):
                backup_boot = backup_boot + 'FF'
    else:
        backup_boot = ''
        looptime = int(131072)
        for i in range(looptime):
            backup_boot = backup_boot + 'FF'

    if backup_key_data != '':
        backup_key_len = reversal(hex(int(len(backup_key_data)/2)).replace('0x','').zfill(8))
        backup_key_crc = reversal(CRC16_XMODEM(backup_key_data).zfill(8))
        backup_key = 'A5A5A5A5' + backup_key_len + backup_key_crc + drift_4k(backup_key_data)
        if (len(backup_key) / 2) < 65536:
            looptime = int(65536 - (len(backup_key) / 2))
            for i in range(looptime):
                backup_key = backup_key + 'FF'
    else:
        backup_key = ''
        looptime = int(65536)
        for i in range(looptime):
            backup_key = backup_key + 'FF'

    if bin_path_5 == '':
        if backup_tp1_data !='':
            backup_tp1_len = reversal(hex(int(len(backup_tp1_data)/2)).replace('0x','').zfill(8))
            backup_tp1_crc = reversal(CRC16_XMODEM(backup_tp1_data).zfill(8))
            backup_tp1 = 'A5A5A5A5' + backup_tp1_len + backup_tp1_crc + drift_4k(backup_tp1_data)
            backup_tp = backup_tp1
        else:
            backup_tp1 = ''
            looptime = 2048
            for i in range(looptime):
                backup_tp1 = backup_tp1 + 'FF'
            backup_tp = backup_tp1
    else:
        backup_tp1_len = reversal(hex(int(len(backup_tp1_data)/2)).replace('0x','').zfill(8))
        backup_tp1_crc = reversal(CRC16_XMODEM(backup_tp1_data).zfill(8))
        backup_tp1 = 'A5A5A5A5' + backup_tp1_len + backup_tp1_crc + drift_4k(backup_tp1_data)
        if (len(backup_tp1) / 2) < 32768:
            looptime = int(32768 - (len(backup_tp1) / 2))
            for i in range(looptime):
                backup_tp1 = backup_tp1 + 'FF'
        backup_tp2_len = reversal(hex(int(len(backup_tp2_data)/2)).replace('0x','').zfill(8))
        backup_tp2_crc = reversal(CRC16_XMODEM(backup_tp2_data).zfill(8))
        backup_tp2 = 'A5A5A5A5' + backup_tp2_len + backup_tp2_crc + drift_4k(backup_tp2_data)
        backup_tp = backup_tp1 + backup_tp2

    all_backup = backup_app + backup_boot + backup_key + backup_tp
    intTobin(split_into_array(all_backup),backup_path)


def start():
    # global now
    # now = 0
    global s19file_path,bin_path_1,bin_path_2,bin_path_3,bin_path_4,bin_path_5,bin_path_6
    global component_num,version_num,block_num,block1_addr,block2_addr,block3_addr,block4_addr,block5_addr,filename
    btnC.config(state='disabled')
    btn6.config(state = 'disabled')



    bin_path_1 = filename
    A = open(filename, 'r')
    size = os.path.getsize(filename)
    data_Config = A.read(size)
    A.close()
    data_config = data_Config.split('=')
    component_num = data_config[1].split('\n', 1)[0]
    version_num = t_Version.get()  # 版本号以字符串输入无需反转
    block_num = data_config[2].split('\n', 1)[0]
    block1_addr = data_config[3].split('\n', 1)[0]
    block2_addr = data_config[4].split('\n', 1)[0]
    block3_addr = data_config[5].split('\n', 1)[0]
    block4_addr = data_config[6].split('\n', 1)[0]
    block5_addr = data_config[7].split('\n', 1)[0]

    filepath = filename.split(filename.split('/')[-1])[0]
    s19file_path = filepath + "app.s19"
    s19updater_path = filepath + "updater.s19"
    s19boot_path = filepath + "boot.s19"
    bin_path_1 = filepath + "app.bin"
    bin_path_2 = filepath + "boot.bin"
    bin_path_3 = filepath + "tk.bin"
    bin_path_4 = filepath + "tp1.bin"
    bin_path_5 = filepath + "tp2.bin"

    if (os.path.lexists(s19file_path)) == False:
        s19file_path = ""
    if (os.path.lexists(s19updater_path)) == False:
        s19updater_path = ""
    if (os.path.lexists(s19boot_path)) == False:
        s19boot_path = ""

    s19_app_path = s19file_path
    if s19file_path == "":
        pass
    else:
        intTobin(split_into_array(getS19Data(s19_app_path)),bin_path_1)    # 生成APP.bin

    if (os.path.lexists(bin_path_1)) == False:
        bin_path_1 = ""
    if (os.path.lexists(bin_path_2)) == False:
        bin_path_2 = ""
    if (os.path.lexists(bin_path_3)) == False:
        bin_path_3 = ""
    if (os.path.lexists(bin_path_4)) == False:
        bin_path_4 = ""
    if (os.path.lexists(bin_path_5)) == False:
        bin_path_5 = ""

    final_binfilepath = filepath + component_num + '_Final.bin'  # bin文件路径
    backup_path = filepath + component_num + "_Backup.bin"       # 备份升级文件路径
    updater_path = filepath + component_num + "_Updater.bin"
    boot_path = filepath + component_num + "_Boot.bin"
    bin1_data = element_into_str(readbinfile(bin_path_1))  # 获取app.bin文件的数据
    bin2_data = element_into_str(readbinfile(bin_path_2))  # 获取boot.bin文件的数据
    bin3_data = element_into_str(readbinfile(bin_path_3))  # 获取tk.bin文件的数据
    bin4_data = element_into_str(readbinfile(bin_path_4))  # 获取tp1.bin文件的数据
    bin5_data = element_into_str(readbinfile(bin_path_5))  # 获取tp2.bin文件的数据
    update_data = bin1_data + bin4_data + bin5_data + bin3_data

    t_component_num = strToasscii(component_num)  # 得到零件号字符串(16进制的ASCII码值)
    t_version_num = strToasscii(version_num)  # 得到版本号字符串(16进制的ASCII码值)

    t_block_num = reversal(block_num.zfill(8))
    t_block1_addr = ifnull(reversal(block1_addr.zfill(8)))
    block1_len = ifnull(hex(int(len(bin1_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的app长度
    t_block1_len = ifnull(reversal(block1_len))

    t_block2_addr = ifnull(reversal(block2_addr.zfill(8)))
    block2_len = ifnull(hex(int(len(bin4_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的tp1.bin长度
    t_block2_len = ifnull(reversal(block2_len))

    t_block3_addr = ifnull(reversal(block3_addr.zfill(8)))
    block3_len = ifnull(hex(int(len(bin5_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的tp2.bin长度
    t_block3_len = ifnull(reversal(block3_len))

    t_block4_addr = ifnull(reversal(block4_addr.zfill(8)))
    block4_len = ifnull(hex(int(len(bin3_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的touchkey.bin长度
    t_block4_len = ifnull(reversal(block4_len))

    t_block5_addr = ifnull(reversal(block5_addr.zfill(8)))
    block5_len = ifnull(hex(int(len('') / 2)).replace('0x', '').zfill(8))  # 未进行反转的block5长度
    t_block5_len = ifnull(reversal(block5_len))
    headfile_flag = 'FFFFFFFF'
    t_block = t_block_num + t_block1_addr + t_block1_len + t_block2_addr + t_block2_len + t_block3_addr + t_block3_len + t_block4_addr + t_block4_len + t_block5_addr + t_block5_len  # 拼接反转后的block数据
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

    if s19file_path == "":
        pass
    else:
        intTobin(split_into_array(all_data), final_binfilepath)  # 生成升级文件

    s19_updater_path = s19updater_path
    updater_data = getS19Data(s19_updater_path)  # 生成updater.bin
    block1_len = ifnull(hex(int(len(updater_data) / 2)).replace('0x', '').zfill(8))
    t_block1_len = ifnull(reversal(block1_len))
    t_block = '01000000' + t_block1_addr + t_block1_len
    t_headfile_len = '48000000'
    head_data = t_headfile_len + t_component_num + t_version_num + t_block + headfile_flag
    CRC16_head = reversal(CRC16_XMODEM(head_data))
    CRC16_update_data = reversal(CRC16_XMODEM(updater_data))  # 序列2的内容
    headandupdate_data = head_data + updater_data  # 序列4-N的内容
    CRC16_bin = reversal(CRC16_XMODEM(headandupdate_data))  # 序列3的内容
    all_data = CRC16_head + CRC16_update_data + CRC16_bin + headandupdate_data
    all_data = all_data.replace(' ', '')

    if s19updater_path == "":
        pass
    else:
        intTobin(split_into_array(all_data), updater_path)   # creat updater.bin

    s19_boot_path = s19boot_path
    boot_data = getS19Data(s19_boot_path)  #
    block1_len = ifnull(hex(int(len(boot_data) / 2)).replace('0x', '').zfill(8))
    t_block1_len = ifnull(reversal(block1_len))
    t_block = '01000000' + '00400000' + t_block1_len
    t_headfile_len = '48000000'
    head_data = t_headfile_len + t_component_num + t_version_num + t_block + headfile_flag
    CRC16_head = reversal(CRC16_XMODEM(head_data))
    CRC16_update_data = reversal(CRC16_XMODEM(boot_data))  # 序列2的内容
    headandupdate_data = head_data + boot_data  # 序列4-N的内容
    CRC16_bin = reversal(CRC16_XMODEM(headandupdate_data))  # 序列3的内容
    all_data = CRC16_head + CRC16_update_data + CRC16_bin + headandupdate_data
    all_data = all_data.replace(' ', '')

    if s19boot_path == "":
        pass
    else:
        intTobin(split_into_array(all_data), boot_path)    # creat updater.bin


    if s19file_path == "":
        pass
    else:
        creat_backup_binfile(backup_path) #生成备份升级文件

    btnC.config(state='normal')
    btn6.config(state='normal')
    result = tkinter.messagebox.showinfo(title='信息提示', message='合并完成！文件名为final.bin')



if __name__ == '__main__':
    global bin_path_1
    global bin_path_2
    global bin_path_3
    global bin_path_4
    global bin_path_5
    global component_num
    global version_num
    global block_num
    global block1_addr
    global block2_addr
    global block3_addr
    global block4_addr
    global block5_addr
    global filename
    head_data = ''  # 头文件数据部分，序列4-15的内容
    all_data = ''
    d = []
    app = tkinter.Tk()
    app.geometry('500x200')
    app.title('bin工具')

    binC_path = tkinter.StringVar()
    bin1_path = tkinter.StringVar()
    bin2_path = tkinter.StringVar()
    bin3_path = tkinter.StringVar()
    bin4_path = tkinter.StringVar()
    bin5_path = tkinter.StringVar()

    entryC = tkinter.Entry(app, textvariable=binC_path, width=45, ).place(x=130, y=80)     # 将Entry控件的创建和打包放在同一行，否则会出错
    btnC = Button(app, text='选择Config文件', command=get_binC, width=18, height=1)
    btnC.place(x=130, y=130)

    labelC = Label(text='Config文件 :').place(x=40, y=80)
    label_Version = Label(text='请输入版本号 :').place(x=40, y=30)
    t_Version = StringVar()
    text_Version = Entry(app, textvariable=t_Version).place(x=130, y=30)

    btn6 = Button(app, text='开始合并', width=18, command=start)
    btn6.place(x=300, y=130)
    # t7 = StringVar()
    # now = 0
    # t7.set('总进度 '+str(now)+'/8')
    # label10 = Label(app,textvariable=t7).place(x=50, y=370)
    # p1 = ttk.Progressbar(app,length =200, mode = "determinate", orient = HORIZONTAL)
    # p1.place(x = 120 , y = 370 )

    app.mainloop()
