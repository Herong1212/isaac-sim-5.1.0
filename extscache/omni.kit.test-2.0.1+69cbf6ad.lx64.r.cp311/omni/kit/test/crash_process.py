import asyncio


def _warning(stream, msg):
    stream.write(f"[warning] [{__file__}] {msg}\n")


async def _crash_process_win(pid, timeout=30):
    # fmt: off
    import ctypes

    POINTER              = ctypes.POINTER
    LPVOID               = ctypes.c_void_p
    PVOID                = LPVOID
    HANDLE               = LPVOID
    PHANDLE              = POINTER(HANDLE)
    ULONG                = ctypes.c_ulong
    SIZE_T               = ctypes.c_size_t
    LONG                 = ctypes.c_long
    NTSTATUS             = LONG
    DWORD                = ctypes.c_uint32
    ACCESS_MASK          = DWORD
    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    BOOL                 = ctypes.c_int
    byref                = ctypes.byref
    long                 = int
    WAIT_TIMEOUT         = 0x102
    WAIT_FAILED          = 0xFFFFFFFF
    WAIT_OBJECT_0        = 0
    STANDARD_RIGHTS_ALL  = long(0x001F0000)
    SPECIFIC_RIGHTS_ALL  = long(0x0000FFFF)
    SYNCHRONIZE          = long(0x00100000)
    STANDARD_RIGHTS_REQUIRED = long(0x000F0000)
    PROCESS_ALL_ACCESS   = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF)
    THREAD_CREATE_FLAGS_SKIP_THREAD_ATTACH = long(0x00000002)

    def NT_SUCCESS(x): return x >= 0

    windll = ctypes.windll

    # HANDLE WINAPI OpenProcess(
    #   IN  DWORD dwDesiredAccess,
    #   IN  BOOL bInheritHandle,
    #   IN  DWORD dwProcessId
    #   );
    _OpenProcess = windll.kernel32.OpenProcess
    _OpenProcess.argtypes = [DWORD, BOOL, DWORD]
    _OpenProcess.restype  = HANDLE

    # NTSTATUS NtCreateThreadEx(
    #     OUT PHANDLE hThread,
    #     IN ACCESS_MASK DesiredAccess,
    #     IN PVOID ObjectAttributes,
    #     IN HANDLE ProcessHandle,
    #     IN PVOID lpStartAddress,
    #     IN PVOID lpParameter,
    #     IN ULONG Flags,
    #     IN SIZE_T StackZeroBits,
    #     IN SIZE_T SizeOfStackCommit,
    #     IN SIZE_T SizeOfStackReserve,
    #     OUT PVOID lpBytesBuffer
    #     );
    _NtCreateThreadEx = windll.ntdll.NtCreateThreadEx
    _NtCreateThreadEx.argtypes = [PHANDLE, ACCESS_MASK, PVOID, HANDLE, PVOID, PVOID, ULONG, SIZE_T, SIZE_T, SIZE_T, PVOID]
    _NtCreateThreadEx.restype  = NTSTATUS

    #HANDLE CreateRemoteThread(
    #  [in]  HANDLE                 hProcess,
    #  [in]  LPSECURITY_ATTRIBUTES  lpThreadAttributes,
    #  [in]  SIZE_T                 dwStackSize,
    #  [in]  LPTHREAD_START_ROUTINE lpStartAddress,
    #  [in]  LPVOID                 lpParameter,
    #  [in]  DWORD                  dwCreationFlags,
    #  [out] LPDWORD                lpThreadId
    #);
    _CreateRemoteThread = windll.kernel32.CreateRemoteThread
    _CreateRemoteThread.argtypes = [HANDLE, PVOID, SIZE_T, PVOID, PVOID, DWORD, PVOID]
    _CreateRemoteThread.restype = HANDLE

    # DWORD WINAPI WaitForSingleObject(
    #   HANDLE hHandle,
    #   DWORD dwMilliseconds
    #   );
    _WaitForSingleObject = windll.kernel32.WaitForSingleObject
    _WaitForSingleObject.argtypes = [HANDLE, DWORD]
    _WaitForSingleObject.restype  = DWORD

    # BOOL CloseHandle(
    #   [in] HANDLE hObject
    # );
    _CloseHandle = windll.kernel32.CloseHandle
    _CloseHandle.argtypes = [HANDLE]
    _CloseHandle.restype = BOOL

    hProcess = _OpenProcess(
        PROCESS_ALL_ACCESS,
        0,  # bInheritHandle
        pid
    )
    if not hProcess:
        raise OSError(None, f"OpenProcess failed: {ctypes.WinError()}")

    # this injects a new thread into the process running the test code. this thread starts executing at address 0,
    # causing a crash.
    #
    # First we try CreateRemoteThread(), though this approach may not work if the target process has the loader lock
    # locked. We try this first because breakpad often has issues with NtCreateThread where the newly-created thread
    # does not have a TEB, so attempting to EnterCriticalSection or get the thread ID may cause a crash within the
    # crash handler.

    # NOTE: This method is currently disabled, but the NtCreateThreadEx() method below requires that Carbonite and
    # breakpad are fixed under OM-87381.

    hThread = HANDLE(0)
    #hThread = _CreateRemoteThread(
    #    hProcess,
    #    0, # lpThreadAttributes
    #    0, # dwStackSize (default size)
    #    0, # lpStartAddress (null -> triggers a crash)
    #    0, # lpParameter
    #    0, # dwCreationFlags
    #    0, # lpThreadId
    #)
    if hThread:
        # WaitForSingleObject isn't awaitable, so we'll call it in short bursts.
        sleepTimeMs = timeout * 1000
        while sleepTimeMs > 0:
            if _WaitForSingleObject(hThread, 0) == WAIT_OBJECT_0:
                break
            await asyncio.sleep(0.01) # 10 ms
            sleepTimeMs = sleepTimeMs - 10
        else:
            # Timed out, thread is maybe stuck
            _CloseHandle(hThread)
            hThread = None

    # If CreateRemoteThread() did not succeed, fall back to NtCreateThread.
    #
    # Unlike CreateRemoteThread(), NtCreateThreadEx accepts the THREAD_CREATE_FLAGS_SKIP_THREAD_ATTACH flag which skips
    # THREAD_ATTACH in DllMain thereby avoiding the loader lock.
    #
    # alternatives considered:
    #
    # DebugBreakProcess(): in order for DebugBreakProcess() to send the breakpoint, a debugger must be attached.  this
    # can be accomplished with DebugActiveProcess()/WaitForDebugEvent()/ContinueDebugEvent().  unfortunately, when a
    # debugger is attached, UnhandledExceptionFilter() is ignored.  UnhandledExceptionFilter() is where the test process
    # runs the crash dump code.
    #
    if not hThread:
        hThread = HANDLE(0)
        status = _NtCreateThreadEx(
            byref(hThread),
            (STANDARD_RIGHTS_ALL | SPECIFIC_RIGHTS_ALL),
            0,  # ObjectAttributes
            hProcess,
            0,  # lpStartAddress (calls into null causing a crash)
            0,  # lpParameter
            THREAD_CREATE_FLAGS_SKIP_THREAD_ATTACH,
            0,  # StackZeroBits
            0,  # StackZeroBits (must be 0 to crash)
            0,  # SizeOfStackReserve
            0,  # lpBytesBuffer
        )
        if not NT_SUCCESS(status):
            _CloseHandle(hProcess)
            raise OSError(None, "NtCreateThreadEx failed", None, status)

    if hThread:
        _CloseHandle(hThread)
        hThread = None

    # Like above, WaitForSingleObject isn't awaitable, so we'll poll it in short bursts
    sleepTimeMs = timeout * 1000
    while sleepTimeMs > 0:
        status = _WaitForSingleObject(hProcess, 0)
        if status == WAIT_OBJECT_0:
            break
        elif status != WAIT_TIMEOUT:
            raise OSError(None, f"WaitForSingleObject failed: {ctypes.WinError()}")

        await asyncio.sleep(0.01) # 10 ms
        sleepTimeMs = sleepTimeMs - 10
    else:
        raise TimeoutError("timed out while waiting for target process to exit")
    # fmt: on


async def crash_process(process, stream, timeout=60):
    """
    Triggers a crash dump in the test process, terminating the process.

    Returns True if the test process was terminated, False if the process is still running.
    """
    import os

    assert process
    pid = process.pid

    try:
        stream.write(f"Attempting to crash process {pid} ({process.name()})\n")
        if os.name == "nt":
            await _crash_process_win(pid, timeout)

        else:
            import signal

            process.send_signal(signal.SIGABRT)
            process.wait(timeout)  # seconds
    except Exception as e:
        _warning(stream, f"Failed to crash process: {pid}. Error: {e}")
        return False

    return not process.is_running()
