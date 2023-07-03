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
from pathlib import Path


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
                if int(str(i)[2:4], 16) - 4 == int(str(all_line[j + 1])[4:10], 16) - int(str(all_line[j])[4:10], 16):
                    count = int(str(i)[2:4], 16) * 2
                    S2_data = str(i)
                    S2_data = S2_data[10:count + 2]
                    s_data = s_data + S2_data
                else:
                    S2_data = str(i)
                    count = int(str(i)[2:4], 16) * 2
                    S2_data = S2_data[10:count + 2]

                    drift_len = int(str(all_line[j + 1])[4:10], 16) - int(str(all_line[j])[4:10], 16) - (
                                int(count / 2) - 4)
                    for k in range(drift_len):
                        S2_data = S2_data + 'FF'  # 地址填充
                    s_data = s_data + S2_data
    else:
        s_data = ''
    return s_data


def CRC16_CCITT(read):  # 获取CRC-16 XMODEM校验码时实参必须是字符串,返回也是字符串
    crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)
    data = read.replace(" ", "")
    readcrcout = hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')  # 位数不足补0
    crc_data = "".join(str_list)
    crc_data = int(crc_data[2:], 16)
    crc_data = "%04x" % crc_data
    read = read.strip() + crc_data
    crc_data = crc_data.zfill(8)
    return crc_data

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


def CRC16_XMODEM_MI(read):  # 获取CRC-16 XMODEM校验码时实参必须是字符串,返回也是字符串
    crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)
    data = read.replace(" ", "")
    readcrcout = hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')  # 位数不足补0
    crc_data = "".join(str_list)
    crc_data = int(crc_data[2:], 16)
    crc_data = "%04x" % crc_data
    read = read.strip() + crc_data
    return crc_data.zfill(4)

def getCRC(read):
    global chechang
    if chechang == 'BYD':
        return CRC16_XMODEM(read)
    if chechang == '长城':
        return CRC16_XMODEM(read)
    if chechang == '小米':
        return CRC16_XMODEM_MI(read)
    if chechang == '长安':
        return CRC16_CCITT(read)

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

    binfilepath.close()


def readbinfile(binfile_path):  # 将bin文件中的数据，按字节大小存入数组
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


def element_into_str(arr):  # 将bin文件中的FFFFFFFF后的数据全部转成字符串
    str2 = ''
    if arr == []:
        return ''
    else:
        for i in arr:
            #p1["value"] = p1["value"] +1
            str2 = str2 + hex(int(i)).replace('0x', '').zfill(2)
            # app.update()
        return str2


def ifnull(str):
    if str == '00000000' or str == '' or str == 'FFFF' or str =='ffff':
        return ''
    else:
        return str

def CS(str):
    CS = 0x00
    data = split_into_array(str)
    for i in data:
        CS = CS + int(i, 16)

    CS = 0xFF - int(hex(CS).replace('0x', '')[-2:], 16)    # [-2:0]取后两位字符串
    return CS



def creatApp_flag(app_s19_path):
    global block1_addr,flag_s19_path
    flag = ''
    l = ''
    A = open(app_s19_path, 'r+')
    a = A.readlines()
    A.close()


    flag = 'S30D'+ hex(int(block1_addr,16)-512).replace('0x','').zfill(8) +'A5A5A5A5A5A5A5A5' + hex(CS(hex(int(block1_addr,16)-512).replace('0x','').zfill(8)+'A5A5A5A5A5A5A5A5')).replace('0x','').zfill(2).upper() + '\n'

    a.insert(1, flag)
    A = open(flag_s19_path, 'w+')
    for i in a:
        l = l + i.__str__()
    A.write(l)
    A.close()

def Merge_S19(bootManger_s19_path,boot_s19_path,flag_app_s19_path,):
    global title
    dic_s19 = {}
    a = []
    s_data = ''
    A = open(bootManger_s19_path, 'r+')
    a = a + A.readlines()
    title = a[0]
    A.close()
    A = open(boot_s19_path, 'r+')
    a = a + A.readlines()
    A.close()
    A = open(flag_app_s19_path, 'r+')
    a = a + A.readlines()
    A.close()
    l = ''
    for i in a:
        l = l + i.__str__()  # 将s19所有字符转为字符串
    all_line = l.split('\n')  # 分割每一行

    for i in all_line:
        j = all_line.index(i)
        if i.__contains__('S3'):
            int_k = 0
            count = int(str(i)[2:4], 16)
            int_startAddr = int(str(i)[4:12],16)
            for j in range(int_startAddr,int_startAddr + count - 5):
                dic_s19[j] = str(i)[(int_k*2)+12:(int_k*2)+14]
                int_k = int_k + 1
        elif i.__contains__('S2'):
            int_k = 0
            count = int(str(i)[2:4], 16)
            int_startAddr = int(str(i)[4:10],16)
            for j in range(int_startAddr,int_startAddr + count - 4):
                dic_s19[j] = str(i)[(int_k*2)+10:(int_k*2)+12]
                int_k = int_k + 1
    return dic_s19

def creat_S19(dic_s19,tag):
    global title
    hang = ''
    S3_counter = 0
    intArr_tagAddress = []
    for key in dic_s19.keys():    # 遍历字典的key
        if tag ==0:
            if key+1 in dic_s19.keys():
                pass
            else:
                intArr_tagAddress.append(key)
                tag = 1
        else:
            intArr_tagAddress.append(key)
            tag = 0
    for i in range(0,len(intArr_tagAddress),2):
        startAddress = intArr_tagAddress[i]
        endAddress = intArr_tagAddress[i+1]
        datastr = ''

        for j in range(startAddress,endAddress+1):
            datastr = datastr + dic_s19[j]

        for j in range(0,int(len(datastr)/2),28):
            hangStartAddress = j + startAddress
            S3_hanglen = hex(int(len(datastr[j*2:j*2+56])/2)+5).replace('0x','').zfill(2).upper()
            hang = hang + 'S3' + S3_hanglen + hex(hangStartAddress).replace('0x','').zfill(8).upper() + datastr[j*2:j*2+56] + hex(CS(S3_hanglen + hex(hangStartAddress).replace('0x','').zfill(8) + datastr[j*2:j*2+56])).replace('0x','').zfill(2).upper() + '\n'
            S3_counter = S3_counter + 1
    str_S3_counter = hex(S3_counter).replace('0x','').zfill(4)
    S5 = 'S5050000' + str_S3_counter.upper() + hex(CS('050000' + str_S3_counter)).replace('0x','').zfill(2).upper() + '\n'
    S7 = 'S705FFFFFFFFFE'
    hang = title + hang + S5 + S7
    s19file_path = open(final_s19_path,'w+')
    s19file_path.write(hang)
    s19file_path.close()

def deleteS19flag(app_srec_path):
    l = ''
    A = open(app_srec_path, 'r+')
    a = A.readlines()
    A.close()
    if a[1].__contains__('28000'):
        a.__delitem__(1)
    A = open(app_srec_path, 'w+')
    for i in a:
        l = l + i.__str__()
    A.write(l)
    A.close()

def get_binC():
    global config_path
    config_path = tkinter.filedialog.askopenfilename()
    if config_path != '':
        binC_path.set(config_path)


def drift_4k(str):
    fill_FF = ''
    for i in range(4084):
        fill_FF = fill_FF +'FF'
    return fill_FF+str

def getFilepath(type):
    global config_path,app_s19_path,boot_s19_path,bootmanager_s19_path

    base_path = config_path.split(config_path.split('/')[-1])[0]
    if type == 'MCU':
        app_s19_path = base_path + 'MCU/'
        app_s19_path = app_s19_path + str(os.listdir(app_s19_path)[0])
        return app_s19_path
    if type == 'Boot':
        boot_s19_path = base_path + 'Boot/'
        if len(os.listdir(boot_s19_path)) != 0:
            boot_s19_path = boot_s19_path + str(os.listdir(boot_s19_path)[0])
        return boot_s19_path
    if type == 'Bootmanager':
        bootmanager_s19_path = base_path + 'Bootmanager/'
        if len(os.listdir(bootmanager_s19_path)) != 0:
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


def creat_backup_binfile(backup_path,backup_block1_addr,backup_block2_addr,backup_block3_addr,backup_block4_addr,backup_block5_addr):
    global app_s19_path,bin_path_1,bin_path_2,bin_path_3,bin_path_4,bin_path_5
    global backup_rank,error
    global app_bin_path

    block1 = ''
    block2 = ''
    block3 = ''
    block4 = ''
    block5 = ''

    block1_path = ''
    block2_path = ''
    block3_path = ''
    block4_path = ''
    block5_path = ''
    backup_rank_arr = backup_rank.split('、')

    for i in range(len(backup_rank_arr)):
        # 先判断备份顺序和备份地址是否有误
        if backup_rank_arr[i] == '':
            error = True
            tkinter.messagebox.showinfo(title='信息提示', message='block顺序处有误')
        if backup_rank_arr[i] == 'NA' and backup_rank_arr[i+1] != 'NA':
            error = True
            tkinter.messagebox.showinfo(title='信息提示', message='block顺序处有误')
        # 然后分配备份文件顺序
        if i <= len(backup_rank_arr) - 1:
            if i == 0:
                if backup_rank_arr[0] == 'app':
                    block1_path = app_bin_path
                elif backup_rank_arr[0] == 'tp1':
                    block1_path = getFilepath('TP1')
                elif backup_rank_arr[0] == 'tp2':
                    block1_path = getFilepath('TP2')
                elif backup_rank_arr[0] == 'osd':
                    block1_path = getFilepath('OSD')
                elif backup_rank_arr[0] == 'fpga':
                    block1_path = getFilepath('FPGA')
                elif backup_rank_arr[0] == 'tcon':
                    block1_path = getFilepath('TCON')
                elif backup_rank_arr[0] == 'icon':
                    block1_path = getFilepath('ICON')
                elif backup_rank_arr[0] == 'bluetooth':
                    block1_path = getFilepath('Bluetooth')
                elif backup_rank_arr[0] == 'tk':
                    block1_path = getFilepath('TK')
                elif backup_rank_arr[0] == 'speaker':
                    block1_path = getFilepath('Speaker')
            if i == 1:
                if backup_rank_arr[1] == 'app':
                    block2_path = app_bin_path
                elif backup_rank_arr[1] == 'tp1':
                    block2_path = getFilepath('TP1')
                elif backup_rank_arr[1] == 'tp2':
                    block2_path = getFilepath('TP2')
                elif backup_rank_arr[1] == 'osd':
                    block2_path = getFilepath('OSD')
                elif backup_rank_arr[1] == 'fpga':
                    block2_path = getFilepath('FPGA')
                elif backup_rank_arr[1] == 'tcon':
                    block2_path = getFilepath('TCON')
                elif backup_rank_arr[1] == 'icon':
                    block2_path = getFilepath('ICON')
                elif backup_rank_arr[1] == 'bluetooth':
                    block2_path = getFilepath('Bluetooth')
                elif backup_rank_arr[1] == 'tk':
                    block2_path = getFilepath('TK')
                elif backup_rank_arr[1] == 'speaker':
                    block2_path = getFilepath('Speaker')
            if i == 2:
                if backup_rank_arr[2] == 'app':
                    block3_path = app_bin_path
                elif backup_rank_arr[2] == 'tp1':
                    block3_path = getFilepath('TP1')
                elif backup_rank_arr[2] == 'tp2':
                    block3_path = getFilepath('TP2')
                elif backup_rank_arr[2] == 'osd':
                    block3_path = getFilepath('OSD')
                elif backup_rank_arr[2] == 'fpga':
                    block3_path = getFilepath('FPGA')
                elif backup_rank_arr[2] == 'tcon':
                    block3_path = getFilepath('TCON')
                elif backup_rank_arr[2] == 'icon':
                    block3_path = getFilepath('ICON')
                elif backup_rank_arr[2] == 'bluetooth':
                    block3_path = getFilepath('Bluetooth')
                elif backup_rank_arr[2] == 'tk':
                    block3_path = getFilepath('TK')
                elif backup_rank_arr[2] == 'speaker':
                    block3_path = getFilepath('Speaker')
            if i == 3:
                if backup_rank_arr[3] == 'app':
                    block4_path = app_bin_path
                elif backup_rank_arr[3] == 'tp1':
                    block4_path = getFilepath('TP1')
                elif backup_rank_arr[3] == 'tp2':
                    block4_path = getFilepath('TP2')
                elif backup_rank_arr[3] == 'osd':
                    block4_path = getFilepath('OSD')
                elif backup_rank_arr[3] == 'fpga':
                    block4_path = getFilepath('FPGA')
                elif backup_rank_arr[3] == 'tcon':
                    block4_path = getFilepath('TCON')
                elif backup_rank_arr[3] == 'icon':
                    block4_path = getFilepath('ICON')
                elif backup_rank_arr[3] == 'bluetooth':
                    block4_path = getFilepath('Bluetooth')
                elif backup_rank_arr[3] == 'tk':
                    block4_path = getFilepath('TK')
                elif backup_rank_arr[3] == 'speaker':
                    block4_path = getFilepath('Speaker')
            if i == 4:
                if backup_rank_arr[4] == 'app':
                    block5_path = app_bin_path
                elif backup_rank_arr[4] == 'tp1':
                    block5_path = getFilepath('TP1')
                elif backup_rank_arr[4] == 'tp2':
                    block5_path = getFilepath('TP2')
                elif backup_rank_arr[4] == 'osd':
                    block5_path = getFilepath('OSD')
                elif backup_rank_arr[4] == 'fpga':
                    block5_path = getFilepath('FPGA')
                elif backup_rank_arr[4] == 'tcon':
                    block5_path = getFilepath('TCON')
                elif backup_rank_arr[4] == 'icon':
                    block5_path = getFilepath('ICON')
                elif backup_rank_arr[4] == 'bluetooth':
                    block5_path = getFilepath('Bluetooth')
                elif backup_rank_arr[4] == 'tk':
                    block5_path = getFilepath('TK')
                elif backup_rank_arr[4] == 'speaker':
                    block5_path = getFilepath('Speaker')
        else:
            pass

    block1_data = element_into_str(readbinfile(block1_path))
    block2_data = element_into_str(readbinfile(block2_path))
    block3_data = element_into_str(readbinfile(block3_path))
    block4_data = element_into_str(readbinfile(block4_path))
    block5_data = element_into_str(readbinfile(block5_path))

    block1_len = reversal(hex(int(len(block1_data)/2)).replace('0x','').zfill(8))
    block1_crc = reversal(getCRC(block1_data))  # 备份文件的block1数据部分的校验码
    block1 = 'A5A5A5A5' + block1_len + block1_crc + drift_4k(block1_data)
    # 不为空则填充block1至block2的空间
    if backup_block2_addr != 'NA':
        if (len(block1) / 2 ) < int(backup_block2_addr,16):
            looptimes = int(int(backup_block2_addr,16) - int(backup_block1_addr,16) - (len(block1) / 2))
            for i in range(looptimes):
                block1 = block1 + 'FF'
    else:
        block2 = ''
        block3 = ''
        block4 = ''
        block5 = ''
    if backup_block1_addr != 'NA' and backup_block2_addr != 'NA':
        block2_len = reversal(hex(int(len(block2_data) / 2)).replace('0x', '').zfill(8))
        block2_crc = reversal(getCRC(block2_data))  # 备份文件的block2数据部分的校验码
        block2 = 'A5A5A5A5' + block2_len + block2_crc + drift_4k(block2_data)
        if backup_block3_addr != 'NA':
            if (len(block2) / 2) < int(backup_block3_addr,16):
                looptimes = int(int(backup_block3_addr,16) - int(backup_block2_addr,16) - (len(block2) / 2))
                for i in range(looptimes):
                    block2 = block2 + 'FF'

    if backup_block1_addr != 'NA' and backup_block2_addr != 'NA' and backup_block3_addr != 'NA':
        block3_len = reversal(hex(int(len(block3_data) / 2)).replace('0x', '').zfill(8))
        block3_crc = reversal(getCRC(block3_data))  # 备份文件的block3数据部分的校验码
        block3 = 'A5A5A5A5' + block3_len + block3_crc + drift_4k(block3_data)
        if backup_block4_addr != 'NA':
            if (len(block3) / 2) < int(backup_block4_addr,16):
                looptimes = int(int(backup_block4_addr,16) - int(backup_block3_addr,16) - (len(block3) / 2))
                for i in range(looptimes):
                    block3 = block3 + 'FF'
    if backup_block1_addr != 'NA' and backup_block2_addr != 'NA' and backup_block3_addr != 'NA' and backup_block4_addr != 'NA':
        block4_len = reversal(hex(int(len(block4_data) / 2)).replace('0x', '').zfill(8))
        block4_crc = reversal(getCRC(block4_data))  # 备份文件的block4数据部分的校验码
        block4 = 'A5A5A5A5' + block4_len + block4_crc + drift_4k(block4_data)
        if backup_block5_addr != 'NA':
            if (len(block4) / 2) < int(backup_block5_addr,16):
                looptimes = int(int(backup_block5_addr,16) - int(backup_block4_addr,16) - (len(block4) / 2))
                for i in range(looptimes):
                    block3 = block3 + 'FF'

    if backup_block1_addr != 'NA' and backup_block2_addr != 'NA' and backup_block3_addr != 'NA' and backup_block4_addr != 'NA' and backup_block5_addr != 'NA':
        block5_len = reversal(hex(int(len(block5_data) / 2)).replace('0x', '').zfill(8))
        block5_crc = reversal(getCRC(block5_data))  # 备份文件的block5数据部分的校验码
        block5 = 'A5A5A5A5' + block5_len + block5_crc + drift_4k(block5_data)


    all_backup = block1 + block2 + block3 + block4 + block5


    intTobin(split_into_array(all_backup),backup_path)


def start():
    global chechang
    global component_num, version_num, block_num, block1_addr, block2_addr, block3_addr, block4_addr, block5_addr, config_path
    global app_s19_path, flag_s19_path, boot_s19_path, bootmanager_s19_path,final_s19_path
    global bin1_path, bin2_path, bin3_path, bin4_path, bin5_path
    global app_bin_path, boot_bin_path
    # global tp1_path,tp2_path,tk_path,osd_path,fpga_path,tcon_path,icon_path,speaker_path,bluetooth_path
    global update_rank,backup_rank
    global title
    global error
    btnC.config(state='disabled')
    btn6.config(state='disabled')
    cbox.config(state='disabled')
    bin1_path = ''
    bin2_path = ''
    bin3_path = ''
    bin4_path = ''
    bin5_path = ''


    chechang = cbox.get()
    A = open(config_path, 'r')
    size = os.path.getsize(config_path)
    data_Config = A.read(size)
    A.close()
    data_config = data_Config.split('=')
    component_num = data_config[1].split('\n', 1)[0]
    version_num = t_Version.get()  # 版本号以字符串输入无需反转
    update_rank = data_config[2].split('\n', 1)[0]
    block_num = data_config[3].split('\n', 1)[0]
    block1_addr = data_config[4].split('\n', 1)[0]
    block2_addr = data_config[5].split('\n', 1)[0]
    block3_addr = data_config[6].split('\n', 1)[0]
    block4_addr = data_config[7].split('\n', 1)[0]
    block5_addr = data_config[8].split('\n', 1)[0]
    backup_rank = data_config[9].split('\n', 1)[0]
    backup_block1_addr = data_config[10].split('\n', 1)[0]
    backup_block2_addr = data_config[11].split('\n', 1)[0]
    backup_block3_addr = data_config[12].split('\n', 1)[0]
    backup_block4_addr = data_config[13].split('\n', 1)[0]
    backup_block5_addr = data_config[14].split('\n', 1)[0]
    update_rank_arr = update_rank.split('、')
    backup_rank_arr = backup_rank.split('、')

    if update_rank_arr[0] == 'NA':
        update_rank_arr = []
    if backup_rank_arr[0] == 'NA':
        backup_rank_arr = []
    if block1_addr =='NA':
        block1_addr = ''
    if block2_addr =='NA':
        block2_addr = ''
    if block3_addr =='NA':
        block3_addr = ''
    if block4_addr =='NA':
        block4_addr = ''
    if block5_addr =='NA':
        block5_addr = ''


    # 基路径为config所在文件夹
    base_path = config_path.split(config_path.split('/')[-1])[0]
    flag_s19_path = base_path + 'Output/' + 'Flag_app.s19'
    app_bin_path = base_path + 'Output/' + 'app.bin'
    boot_bin_path = base_path + 'Output/' + 'Boot.bin'
    final_s19_path = base_path + 'Output/' + 'Final.s19'
    final_bin_path = base_path + 'Output/' + 'Final.bin'
    backup_bin_path = base_path + 'Output/' + 'Backup.bin'

    # 生成带flag的APP.s19
    app_s19_path = getFilepath('MCU')

    # 合并flag.s19 Boot.s19 Bootmanager.s19
    boot_s19_path = getFilepath('Boot')
    bootmanager_s19_path = getFilepath('Bootmanager')
    # 如果有Boot和Bootmanager才合成final.s19
    if Path(boot_s19_path).is_file() and Path(bootmanager_s19_path).is_file():
        if len(update_rank_arr) != 0 :
            creatApp_flag(app_s19_path)
            creat_S19(Merge_S19(bootmanager_s19_path, boot_s19_path, flag_s19_path), 1)
        else:
            pass
    else:
        pass

    # 用MCU.s19创建app.bin
    if app_s19_path == "":
        pass
        tkinter.messagebox.showinfo(title = '信息提示',message = '无MCU软件')
    else:
        intTobin(split_into_array(getS19Data(app_s19_path)), app_bin_path)  # 生成APP.bin


    # 分配升级文件的bin文件的路径
    for i in range(len(update_rank_arr)):
        if update_rank_arr[i] == '':
            tkinter.messagebox.showinfo(title='信息提示', message='block顺序处有误')
        if i <= len(update_rank_arr) - 1:
            if i == 0:
                if update_rank_arr[0] == 'app':
                    bin1_path = app_bin_path
                elif update_rank_arr[0] == 'tp1':
                    bin1_path = getFilepath('TP1')
                elif update_rank_arr[0] == 'tp2':
                    bin1_path = getFilepath('TP2')
                elif update_rank_arr[0] == 'osd':
                    bin1_path = getFilepath('OSD')
                elif update_rank_arr[0] == 'fpga':
                    bin1_path = getFilepath('FPGA')
                elif update_rank_arr[0] == 'tcon':
                    bin1_path = getFilepath('TCON')
                elif update_rank_arr[0] == 'icon':
                    bin1_path = getFilepath('ICON')
                elif update_rank_arr[0] == 'bluetooth':
                    bin1_path = getFilepath('Bluetooth')
                elif update_rank_arr[0] == 'tk':
                    bin1_path = getFilepath('TK')
                elif update_rank_arr[0] == 'speaker':
                    bin1_path = getFilepath('Speaker')
            if i == 1:
                if update_rank_arr[1] == 'app':
                    bin2_path = app_bin_path
                elif update_rank_arr[1] == 'tp1':
                    bin2_path = getFilepath('TP1')
                elif update_rank_arr[1] == 'tp2':
                    bin2_path = getFilepath('TP2')
                elif update_rank_arr[1] == 'osd':
                    bin2_path = getFilepath('OSD')
                elif update_rank_arr[1] == 'fpga':
                    bin2_path = getFilepath('FPGA')
                elif update_rank_arr[1] == 'tcon':
                    bin2_path = getFilepath('TCON')
                elif update_rank_arr[1] == 'icon':
                    bin2_path = getFilepath('ICON')
                elif update_rank_arr[1] == 'bluetooth':
                    bin2_path = getFilepath('Bluetooth')
                elif update_rank_arr[1] == 'tk':
                    bin2_path = getFilepath('TK')
                elif update_rank_arr[1] == 'speaker':
                    bin2_path = getFilepath('Speaker')
            if i == 2:
                if update_rank_arr[2] == 'app':
                    bin3_path = app_bin_path
                elif update_rank_arr[2] == 'tp1':
                    bin3_path = getFilepath('TP1')
                elif update_rank_arr[2] == 'tp2':
                    bin3_path = getFilepath('TP2')
                elif update_rank_arr[2] == 'osd':
                    bin3_path = getFilepath('OSD')
                elif update_rank_arr[2] == 'fpga':
                    bin3_path = getFilepath('FPGA')
                elif update_rank_arr[2] == 'tcon':
                    bin3_path = getFilepath('TCON')
                elif update_rank_arr[2] == 'icon':
                    bin3_path = getFilepath('ICON')
                elif update_rank_arr[2] == 'bluetooth':
                    bin3_path = getFilepath('Bluetooth')
                elif update_rank_arr[2] == 'tk':
                    bin3_path = getFilepath('TK')
                elif update_rank_arr[2] == 'speaker':
                    bin3_path = getFilepath('Speaker')
            if i == 3:
                if update_rank_arr[3] == 'app':
                    bin4_path = app_bin_path
                elif update_rank_arr[3] == 'tp1':
                    bin4_path = getFilepath('TP1')
                elif update_rank_arr[3] == 'tp2':
                    bin4_path = getFilepath('TP2')
                elif update_rank_arr[3] == 'osd':
                    bin4_path = getFilepath('OSD')
                elif update_rank_arr[3] == 'fpga':
                    bin4_path = getFilepath('FPGA')
                elif update_rank_arr[3] == 'tcon':
                    bin4_path = getFilepath('TCON')
                elif update_rank_arr[3] == 'icon':
                    bin4_path = getFilepath('ICON')
                elif update_rank_arr[3] == 'bluetooth':
                    bin4_path = getFilepath('Bluetooth')
                elif update_rank_arr[3] == 'tk':
                    bin4_path = getFilepath('TK')
                elif update_rank_arr[3] == 'speaker':
                    bin4_path = getFilepath('Speaker')
            if i == 4:
                if update_rank_arr[4] == 'app':
                    bin5_path = app_bin_path
                elif update_rank_arr[4] == 'tp1':
                    bin5_path = getFilepath('TP1')
                elif update_rank_arr[4] == 'tp2':
                    bin5_path = getFilepath('TP2')
                elif update_rank_arr[4] == 'osd':
                    bin5_path = getFilepath('OSD')
                elif update_rank_arr[4] == 'fpga':
                    bin5_path = getFilepath('FPGA')
                elif update_rank_arr[4] == 'tcon':
                    bin5_path = getFilepath('TCON')
                elif update_rank_arr[4] == 'icon':
                    bin5_path = getFilepath('ICON')
                elif update_rank_arr[4] == 'bluetooth':
                    bin5_path = getFilepath('Bluetooth')
                elif update_rank_arr[4] == 'tk':
                    bin5_path = getFilepath('TK')
                elif update_rank_arr[4] == 'speaker':
                    bin5_path = getFilepath('Speaker')
        else:
            pass

    # 升级文件顺序不为空则合成升级文件
    if len(update_rank_arr) == 0 :
        pass
    else:
        bin1_data = element_into_str(readbinfile(bin1_path))  # 获取作为block1的文件数据
        bin2_data = element_into_str(readbinfile(bin2_path))  # 获取作为block2的文件数据
        bin3_data = element_into_str(readbinfile(bin3_path))  # 获取作为block3的文件数据
        bin4_data = element_into_str(readbinfile(bin4_path))  # 获取作为block4的文件数据
        bin5_data = element_into_str(readbinfile(bin5_path))  # 获取作为block5的文件数据
        update_data = bin1_data + bin2_data + bin3_data + bin4_data + bin5_data
        if chechang == '小米':
            t_component_num = strToasscii(component_num).replace('20','')  # 得到零件号字符串(16进制的ASCII码值)
            t_version_num = strToasscii(version_num).replace('20','')  # 得到版本号字符串(16进制的ASCII码值)
            t_block_num = block_num.zfill(4)
        else:
            t_component_num = strToasscii(component_num)
            t_version_num = strToasscii(version_num)
            t_block_num = reversal(block_num.zfill(8))
        t_block1_addr = ifnull(reversal(block1_addr.zfill(8)))
        block1_len = ifnull(hex(int(len(bin1_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block1长度
        t_block1_len = ifnull(reversal(block1_len))

        t_block2_addr = ifnull(reversal(block2_addr.zfill(8)))
        block2_len = ifnull(hex(int(len(bin2_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block2长度
        t_block2_len = ifnull(reversal(block2_len))

        t_block3_addr = ifnull(reversal(block3_addr.zfill(8)))
        block3_len = ifnull(hex(int(len(bin3_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block3长度
        t_block3_len = ifnull(reversal(block3_len))

        t_block4_addr = ifnull(reversal(block4_addr.zfill(8)))
        block4_len = ifnull(hex(int(len(bin4_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block4长度
        t_block4_len = ifnull(reversal(block4_len))

        t_block5_addr = ifnull(reversal(block5_addr.zfill(8)))
        block5_len = ifnull(hex(int(len(bin5_data) / 2)).replace('0x', '').zfill(8))  # 未进行反转的block5长度
        t_block5_len = ifnull(reversal(block5_len))
        headfile_flag = 'FFFFFFFF'
        t_block = t_block_num + t_block1_addr + t_block1_len + t_block2_addr + t_block2_len + t_block3_addr + t_block3_len + t_block4_addr + t_block4_len + t_block5_addr + t_block5_len  # 拼接反转后的block数据
        headfile_len = hex(64 + int(block_num) * 8).replace('0x', '').zfill(8)  # 头文件长度,序列1-15的长度
        headfile_len.replace(' ', '').zfill(8)
        t_headfile_len = reversal(headfile_len)
        head_data = t_headfile_len + t_component_num + t_version_num + t_block + headfile_flag  # 反转后的序列4-15内容
        CRC16_head = reversal(getCRC(head_data))  # 序列1的内容
        CRC16_update_data = reversal(getCRC(update_data))  # 序列2的内容
        headandupdate_data = head_data + update_data  # 序列4-N的内容
        CRC16_bin = reversal(getCRC(headandupdate_data))  # 序列3的内容
        all_data = CRC16_head + CRC16_update_data + CRC16_bin + headandupdate_data

        if app_s19_path == "":
            pass
        else:
            intTobin(split_into_array(all_data), final_bin_path)  # 生成升级文件
            if len(backup_rank_arr) == 0 :
                tkinter.messagebox.showinfo(title='信息提示', message='合并完成！文件名为Final.bin')

        boot_data = getS19Data(boot_s19_path)
        boot_len = ifnull(hex(int(len(boot_data) / 2)).replace('0x', '').zfill(8))
        t_boot_len = ifnull(reversal(boot_len))
        t_boot = '01000000' + '00400000' + t_boot_len
        t_headfile_len = '48000000'
        head_data = t_headfile_len + t_component_num + t_version_num + t_boot + headfile_flag
        CRC16_head = reversal(getCRC(head_data))
        CRC16_boot_data = reversal(getCRC(boot_data))  # 序列2的内容
        headandboot_data = head_data + boot_data  # 序列4-N的内容
        CRC16_bin = reversal(getCRC(headandboot_data))  # 序列3的内容
        all_data = CRC16_head + CRC16_boot_data + CRC16_bin + headandboot_data
        all_data = all_data.replace(' ', '')

        if boot_s19_path == "":
            pass
        else:
            intTobin(split_into_array(all_data), boot_bin_path)


    if backup_block1_addr == 'NA' or len(backup_rank_arr) ==0 :
        # block1地址为空或备份顺序为空则不备份
        error = False
    elif backup_block1_addr == 'NA' and (backup_block2_addr != 'NA' or backup_block3_addr != 'NA' or backup_block4_addr != 'NA' or backup_block5_addr != 'NA'):
        error = True
        tkinter.messagebox.showinfo(title='信息提示', message='备份block地址错误')
    if backup_block1_addr != 'NA' and len(backup_rank_arr) != 0 :
        creat_backup_binfile(backup_bin_path,backup_block1_addr,backup_block2_addr,backup_block3_addr,backup_block4_addr,backup_block5_addr)  # 生成备份升级文件
        result = tkinter.messagebox.showinfo(title='信息提示', message='合并完成！文件名为Backup.bin')
    btnC.config(state='normal')
    btn6.config(state='normal')
    cbox.config(state='normal')




if __name__ == '__main__':
    global app_s19_path, flag_s19_path, boot_s19_path, bootmanager_s19_path, title
    global config_path
    global bin1_path
    global bin2_path
    global bin3_path
    global bin4_path
    global bin5_path
    global component_num
    global version_num
    global block_num
    global block1_addr
    global block2_addr
    global block3_addr
    global block4_addr
    global block5_addr
    # global tp1_path,tp2_path,tk_path,osd_path,fpga_path,tcon_path,icon_path,speaker_path,bluetooth_path
    global error

    head_data = ''  # 头文件数据部分，序列4-15的内容
    all_data = ''
    d = []
    app = tkinter.Tk()
    app.geometry('500x200')
    app.title('bin工具')

    binC_path = tkinter.StringVar()
    entryC = tkinter.Entry(app, textvariable=binC_path, width=45, ).place(x=130, y=80)     # 将Entry控件的创建和打包放在同一行，否则会出错
    btnC = Button(app, text='选择Config文件', command=get_binC, width=18, height=1)
    btnC.place(x=130, y=130)

    labelC = Label(text='Config文件 :').place(x=40, y=80)
    label_Version = Label(text='请输入版本号 :').place(x=210, y=30)
    labelBox = Label(text = '项目：').place(x=40,y=30)
    t_Version = StringVar()
    text_Version = Entry(app, textvariable=t_Version,width = 17).place(x=300, y=30)

    btn6 = Button(app, text='开始合并', width=18, command=start)
    btn6.place(x=300, y=130)

    cbox = ttk.Combobox(app,width = 10)
    cbox.grid(row=1, sticky="NW")
    cbox.place(x=90,y=30)
    cbox['value'] = ('长城', 'BYD', '小米','长安')
    cbox.current(0)

    app.mainloop()
