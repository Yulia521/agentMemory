import os
import sys
import subprocess
import time

def main():
    print("智能体记忆系统启动器")
    print("正在启动 Web 界面...")

    # 检查是否有其他实例正在运行
    lock_file = os.path.join("mem0_storage", ".lock")
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = f.read().strip()
            if pid:
                print(f"检测到其他实例正在运行 (PID: {pid})")
                print("正在尝试关闭...")
                # 尝试删除锁文件
                os.remove(lock_file)
                print("锁文件已删除")
        except Exception as e:
            print(f"检查锁文件时出错: {e}")

    # 启动 app.py
    print("启动 app.py...")
    subprocess.run([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
