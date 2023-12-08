from ctypes import *
from ctypes import wintypes

# Define constants and types
LPCTSTR = c_char_p
SIZE_T = c_size_t

kernel32 = windll.kernel32

# Function prototypes
OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
OpenProcess.restype = wintypes.HANDLE

VirtualAllocEx = kernel32.VirtualAllocEx
VirtualAllocEx.argtypes = (wintypes.HANDLE, wintypes.LPVOID, SIZE_T, wintypes.DWORD, wintypes.DWORD)
VirtualAllocEx.restype = wintypes.LPVOID

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = (wintypes.HANDLE, wintypes.LPVOID, wintypes.LPCVOID, SIZE_T, POINTER(SIZE_T))
WriteProcessMemory.restype = wintypes.BOOL

GetModuleHandle = kernel32.GetModuleHandleA
GetModuleHandle.argtypes = (LPCTSTR,)
GetModuleHandle.restype = wintypes.HMODULE

GetProcAddress = kernel32.GetProcAddress
GetProcAddress.argtypes = (wintypes.HMODULE, LPCTSTR)
GetProcAddress.restype = wintypes.LPVOID

class SECURITY_ATTRIBUTES(Structure):
    _fields_ = [
        ('nLength', wintypes.DWORD),
        ('lpSecurityDescriptor', wintypes.LPVOID),
        ('bInheritHandle', wintypes.BOOL),
    ]

LPSECURITY_ATTRIBUTES = POINTER(SECURITY_ATTRIBUTES)
LPTHREAD_START_ROUTINE = CFUNCTYPE(wintypes.DWORD, wintypes.LPVOID)

CreateRemoteThread = kernel32.CreateRemoteThread
CreateRemoteThread.argtypes = (
    wintypes.HANDLE,
    LPSECURITY_ATTRIBUTES,
    SIZE_T,
    LPTHREAD_START_ROUTINE,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.LPWORD,
)
CreateRemoteThread.restype = wintypes.HANDLE

# Constants
MEM_COMMIT = 0x00001000
MEM_RESERVE = 0x00002000
PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = (0x1F0FFF)

# Path to the DLL to be injected
dll_path = b"C:\\Users\\Ionic\\Desktop\\Hello_word.dll"

# Target process ID
pid = 2780

# Open the target process
handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

if not handle:
    raise WinError()

print("Handle obtained: {0:X}".format(handle))

# Allocate memory for the DLL path
dll_path_size = len(dll_path) + 1  # include null terminator
remote_memory = VirtualAllocEx(handle, None, dll_path_size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)

if not remote_memory:
    raise WinError()

print("Memory Allocated =>", hex(remote_memory))

# Correct variable name from ddl to dll_path
write = WriteProcessMemory(handle, remote_memory, dll_path, dll_path_size, None)

if not write:
    raise WinError()

print("Bytes written => {}".format(write))

load_lib = GetProcAddress(GetModuleHandle(b"kernel32.dll"), b"LoadLibraryA")

print("LoadLibrary Address =>", hex(load_lib))

rthread = CreateRemoteThread(handle, None, 0, LPTHREAD_START_ROUTINE(load_lib), remote_memory, 0, None)