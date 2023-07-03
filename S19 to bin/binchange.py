import os
import numpy as np
from itertools import groupby
import struct
from binascii import *
from crcmod import *
from tkinter import *
from PyQt5.Qt import *


def getS19Data(s19file_path):
    A = open(s19file_path,'r+')
    a = A.readlines()
    s_data = ''
    l = ''
    for i in a:
        l = l + i.__str__()  # 将s19所有字符转为字符串
    all_line = l.split('\n')  # 分割每一行
    j = len(all_line)
    t_all_line = []
    for i in all_line:
        if i[5:10] == '14200':      # 14200是刷写APP的首地址，往前的地址都属于bootloader，请注意
            t_all_line = all_line[all_line.index(i):]
        else:
            continue
    for i in t_all_line:
        if i.__contains__('S0'):
            count = int(str(i)[2:4],16)
            count = count*2
            S0_data = str(i)
            S0_data = S0_data[8:count+2]
            s_data = s_data+S0_data
        elif i.__contains__('S3'):
            count = int(str(i)[2:4], 16)*2
            S3_data = str(i)
            S3_data = S3_data[12:count + 2]
            s_data = s_data + S3_data
        elif i.__contains__('S2'):
            count = int(str(i)[2:4],16)*2
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

def CRC16_XMODEM(read):       # 获取CRC-16 XMODEM校验码时实参必须是字符串,返回也是字符串
    crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)
    data = read.replace(" ", "")
    readcrcout = hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')  # 位数不足补0
    crc_data = "".join(str_list)
    crc_data = int(crc_data[2:],16)
    crc_data = "%04x" % crc_data
    read = read.strip() + crc_data
    return crc_data.zfill(8)


def strToasscii(A):         # 将零件号和版本号从字符串转换为以16进制字符串表示的ASCII码
    x = ''
    if len(A)< 20:
        for i in range(20-len(A)):
            A = A + ' '
    for i in A:
        x = x + hex(ord(i)).replace('0x','')
    return x

def reversal(A):         # 将字符串按两位进行反转,返回的是反转后的字符串
    if A == '':
        return ''
    else:
        a = A.replace(' ','')
        stack = []
        str = ''
        for i in range(len(a)):
            if i%2 == 0:
                stack.append(a[i:i+2])
        stack.reverse()
        for i in stack:
            str = str + hex(int(i,16)).replace('0x','').zfill(2)
        return str

def split_into_array(s_data):       # 将字符串按两位分割存入数组，形参为字符串
    s_data_arr = []
    for i in range(len(s_data)):
        if i%2 == 0:
            s_data_arr.append(s_data[i:i+2])
    return s_data_arr

def intTobin(arr,binfilepath):    # 形参arr为字符串数组，binfilepath为要写入的bin文件路径
    binfilepath = open(binfilepath, 'wb')
    for i in arr:                   # 遍历数组
        x = bin(int(i,16)).replace('0b','').zfill(8)     # 将数组元素转换为字符串形式的二进制
        b = 0b00000000
        for j in x:         # 获取8位01字符，
            if j == '0':
                b = b << 1
            else:
                b = b << 1
                b = b | 0b00000001
        a = struct.pack('B', b)
        binfilepath.write(a)         # 写入bin文件，每次写入8位，也就是一个字节的数据
    binfilepath.close()

    # 此处往下的函数为bin文件合并使用到的函数

def readbinfile(binfile_path):        # 将bin文件中的数据，按字节大小存入数组
    if binfile_path =='':
        return ''
    else:
        arr = []
        A = open(binfile_path,'rb')
        size = os.path.getsize(binfile_path)  # 获得文件大小
        for i in range(size):
            data = A.read(1)
            num = struct.unpack('B', data)      # num为元组，不可修改 num = (data,)

            arr = arr + list(num)    # 将元组转换成数组
        A.close()
        return arr

def element_into_str(arr):  # 将bin文件中的FFFFFFFF后的数据全部转成字符串
    data_arr = []
    str = ''
    if arr ==[]:
        return ''
    else:
        for i in range(len(arr)):
            data_arr.append(arr[i])
        for i in data_arr:
            str = str + hex(int(i)).replace('0x','').zfill(2)
        return str
    


if __name__ == '__main__':
    head_data = ''     # 头文件数据部分，序列4-15的内容
    all_data = ''
    d = []

    final_binfilepath = 'final.bin'   # bin文件路径
    mcu_path = ''
    app_data = element_into_str(readbinfile(mcu_path)) # 获取app.bin文件的数据
    tp_path = ''
    tp_data = element_into_str(readbinfile(tp_path))  # 获取TP.bin文件的数据
    update_data = app_data + tp_data
    component_num = '7901200XKL01A'             # 字符串类型的零件号 无需反转
    t_component_num = strToasscii(component_num)     # 得到零件号字符串(16进制的ASCII码值)
    version_num = 'SW01.00'        # 版本号以字符串输入无需反转
    t_version_num = strToasscii(version_num)        # 得到版本号字符串(16进制的ASCII码值)
    block_num = '00000002'          # 未进行反转的block数量
    t_block_num = reversal(block_num).zfill(8)
    block1_addr = '00018200'        # 未进行反转的block1地址
    t_block1_addr = reversal(block1_addr).zfill(8)
    block1_len = hex(int(len(app_data)/2)).replace('0x','').zfill(8)        # 未进行反转的block1长度
    t_block1_len = reversal(block1_len).zfill(8)
    block2_addr = '00060000'  # 未进行反转的block2地址
    t_block2_addr = reversal(block2_addr).zfill(8)
    block2_len = hex(len(tp_data)).replace('0x','').zfill(8)  # 未进行反转的block2长度
    t_block2_len = reversal(block2_len).zfill(8)
    headfile_flag = 'FFFFFFFF'
    t_block = t_block_num + t_block1_addr + t_block1_len + t_block2_addr + t_block2_len       # 拼接反转后的block数据
    headfile_len = '00000050'  # 头文件长度,序列1-15的长度
    headfile_len.replace(' ', '').zfill(8)
    t_headfile_len = reversal(headfile_len)
    head_data = t_headfile_len + t_component_num + t_version_num + t_block + headfile_flag      # 反转后的序列4-15内容
    CRC16_head = reversal(CRC16_XMODEM(head_data))  # 序列1的内容
    CRC16_update_data = reversal(CRC16_XMODEM(update_data))     # 序列2的内容
    headandupdate_data = head_data + update_data    # 序列4-N的内容
    CRC16_bin = reversal(CRC16_XMODEM(headandupdate_data))      # 序列3的内容
    all_data = CRC16_head + CRC16_update_data + CRC16_bin + headandupdate_data
    all_data = all_data.replace(' ','')
    bin_data = intTobin(split_into_array(all_data),final_binfilepath)       # 字符串每两位入数组然后转至二进制写入bin文件