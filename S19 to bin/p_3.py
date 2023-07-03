import os
import numpy as np
from itertools import groupby
import struct
from binascii import *
from crcmod import *
from tkinter import *
from tkinter import ttk
import tkinter.messagebox


x = 483
print(hex(x).replace('0x','')[-2:])