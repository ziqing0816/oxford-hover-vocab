#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""在桌面建立划词与复习快捷方式（pythonw，无控制台）。

為什麼不用 .bat 直接做：cmd.exe 是以系統 OEM 編碼逐位元組讀批次檔，
批次檔裡一旦有中文（或用 chcp 65001 硬轉），續行符號與含中文的 %~dp0
都會被打斷。所以 .bat 只留純 ASCII 當薄殼，實際工作交給 Python。
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
def _create(shell, pyw, name, script, description):
    lnk = os.path.join(shell.SpecialFolders("Desktop"), name + ".lnk")
    shortcut = shell.CreateShortCut(lnk)
    shortcut.TargetPath = pyw
    shortcut.Arguments = f'"{script}"'
    shortcut.WorkingDirectory = BASE
    icon = os.path.join(BASE, "icon.ico")
    if os.path.exists(icon):
        shortcut.IconLocation = icon + ",0"
    shortcut.Description = description
    shortcut.WindowStyle = 7
    try:
        shortcut.save()
    except AttributeError:
        shortcut.Save()
    return lnk


def main():
    try:
        import win32com.client
    except ImportError:
        print("  缺少 pywin32，请先运行 setup.bat")
        return 1

    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pyw):
        pyw = sys.executable          # 沒有 pythonw 就退回 python（會有主控台）
        print("  找不到 pythonw.exe，改用 python.exe（启动时会显示控制台）")

    shell = win32com.client.Dispatch("WScript.Shell")
    links = [
        _create(shell, pyw, "Oxford 划词助手", "hover_translate.py",
                "屏幕取词、Oxford 英英释义、简体中文解释与自动生词保存"),
        _create(shell, pyw, "生词复习", "review_app.py",
                "本地英语生词卡片与间隔复习"),
    ]
    if all(os.path.exists(path) for path in links):
        for path in links:
            print(f"  已建立桌面快捷方式：{path}")
        return 0
    print("  快捷方式建立失败，仍可使用 run.bat 和 review-vocab.bat。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
