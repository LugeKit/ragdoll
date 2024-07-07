import enum
import threading
from typing import Callable

import win32con
import ctypes
import ctypes.wintypes

import logs

user32 = ctypes.windll.user32


class HotkeyFsModifiers(enum.IntEnum):
    MOD_NONE = 0x0
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_NOREPEAT = 0x4000
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008


class Hotkey:
    def __init__(
            self,
            callback: Callable,
            fs_modifiers: HotkeyFsModifiers,
            vk: int,  # from win32con.VK
    ):
        self.callback = callback
        self.fs_modifiers = fs_modifiers
        self.vk = vk


# TODO: support gracefully exit
class HotkeyManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self.id = 100
        self.hotkeys: list[tuple[int, Hotkey]] = []
        self.daemon = True

    def register(self, hk: Hotkey):
        if self.is_alive():
            logs.info("failed to register hotkey, please register hotkey before thread is running")

        logs.info(f"register {hk.vk} successfully, id is {self.id}")
        self.hotkeys.append((self.id, hk))
        self.id += 1

    def unregister(self, hk_id: int):
        for (_hk_id, _) in self.hotkeys:
            if _hk_id == hk_id:
                user32.UnregisterHotKey(None, hk_id)
                return

    def unregister_all(self):
        for (hk_id, _) in self.hotkeys:
            self.unregister(hk_id)

    def run(self):
        for (hk_id, hk) in self.hotkeys:
            if not user32.RegisterHotKey(None, hk_id, hk.fs_modifiers, hk.vk):
                logs.info(f"failed to register hotkey: {hk_id}")

        try:
            msg = ctypes.wintypes.MSG()
            while True:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        consumed = False
                        key_id = msg.wParam
                        for (hk_id, hk) in self.hotkeys:
                            if hk_id != key_id:
                                continue

                            consumed = True
                            hk.callback()

                        if consumed:
                            continue

                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            self.unregister_all()
