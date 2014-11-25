from numpy.ctypeslib import as_ctypes as as_c
import numpy as np
import ctypes as C
lib = C.CDLL("libHampel.so")

def hampel_filter_2d(array2d,
                     threshold,
                     window_size_x=16,
                     window_size_y=16):


    outarray = np.empty(array2d.shape, dtype="float32")

    lib.hampel_filter_2d(as_c(array2d),
                         C.c_int(array2d.shape[1]),
                         as_c(outarray),
                         C.C_float(threshold),
                         C.c_int(window_size_x),
                         C.c_int(window_size_y))
