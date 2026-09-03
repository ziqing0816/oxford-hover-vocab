#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""一键安装：创建隔离环境 → 安装依赖 → 建字典 → 放桌面快捷方式。"""
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(BASE, ".venv")
VENV_PYTHON = os.path.join(VENV, "Scripts", "python.exe")


def say(*a):
    # 一定要 flush：子行程（pip / build_dict）會直接寫主控台，
    # 我們的輸出若還留在緩衝區，訊息順序會前後顛倒。
    print(*a, flush=True)


def rule(t=""):
    say("\n" + "─" * 52 + (f"\n  {t}" if t else ""))


def main():
    os.chdir(BASE)
    rule()
    say("  Oxford 划词助手 － 安装程序")
    say("  屏幕取词、英英释义、简体中文解释、生词保存与复习")
    rule()

    say(f"\n[1/5] Python {sys.version.split()[0]}  OK")
    say(f"      安装位置：{BASE}")

    if not os.path.exists(VENV_PYTHON):
        say("\n[2/5] 创建项目专用 Python 环境…")
        r = subprocess.run([sys.executable, "-m", "venv", VENV])
        if r.returncode != 0:
            say("      创建 .venv 失败，请确认 Python 安装完整。")
            return 1
    else:
        say("\n[2/5] 项目专用 Python 环境已存在")

    say("\n[3/5] 安装锁定版本的依赖…")
    r = subprocess.run([VENV_PYTHON, "-m", "pip", "install", "--quiet",
                        "--disable-pip-version-check", "-r", "requirements.txt"])
    if r.returncode != 0:
        say("      依赖安装失败，请检查网络后重试。")
        return 1
    say("      完成")

    if os.path.exists(os.path.join(BASE, "dict.db")):
        say("\n[4/5] 离线字典已存在，跳过建立")
    else:
        say("\n[4/5] 下载并建立本地简体中文词典…")
        say("      需要下载约 65 MB，通常需要 2–3 分钟。\n")
        r = subprocess.run([VENV_PYTHON, "build_dict.py"])
        if r.returncode != 0:
            say("      字典建立失败，请检查网络后重试。")
            return 1

    say("\n[5/5] 建立桌面快捷方式…")
    subprocess.run([VENV_PYTHON, "make_shortcut.py"])

    rule("安装完成")
    say("\n  双击桌面上的“Oxford 划词助手”开始使用")
    say("  双击“生词复习”复习到期单词\n")
    say("  用法：按住 Ctrl，鼠标停在英文单词上约半秒")
    say("  停止：连续按两次 Esc")
    rule()
    return 0


if __name__ == "__main__":
    code = main()
    try:
        input("\n按 Enter 关闭…")
    except Exception:
        pass
    sys.exit(code)
