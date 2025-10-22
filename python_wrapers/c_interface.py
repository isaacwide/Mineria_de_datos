import  ctypes
import os
from numpy import ctypeslib as npct

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dll_path = os.path.join(base_dir, "c_libs/build", "lid_lda.dll")


if not os.path.exists(dll_path):
    raise FileNotFoundError(f"No se encuentra la DLL en: {dll_path}")

# Cargar la librería
lib = ctypes.CDLL(dll_path)