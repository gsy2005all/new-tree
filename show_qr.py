"""
显示「手机访问地址」并生成二维码。

用法:
    python show_qr.py            # 默认端口 8000
    python show_qr.py 8080       # 指定端口

会做三件事:
  1) 自动检测本机在局域网(WiFi)中的 IP
  2) 在终端打印出手机要访问的网址
  3) 在终端画出一个二维码(手机扫一扫即可打开)，同时把二维码图片存到 static/qr.png
"""
import socket
import sys

import qrcode

# Windows 终端默认是 GBK，这里切到 UTF-8，避免打印中文/二维码时报错
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def get_lan_ip() -> str:
    """获取本机在局域网中的 IP（连一下外网拿到出口网卡地址，不会真的发数据）。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"
    ip = get_lan_ip()
    base = f"http://{ip}:{port}"
    home = f"{base}/"

    print("=" * 48)
    print("  手机请确保和电脑连同一个 WiFi，然后访问：")
    print(f"  入口选择首页 : {home}")
    print(f"  用户入口     : {base}/static/user.html")
    print(f"  管理员入口   : {base}/static/admin.html")
    print("=" * 48)
    print("  用手机相机/浏览器扫描下面的二维码直接打开首页：\n")

    qr = qrcode.QRCode(border=2)
    qr.add_data(home)
    qr.make(fit=True)
    try:
        qr.print_ascii(invert=True)  # 在终端画出二维码（部分终端可能不支持）
    except Exception:
        print("（当前终端无法绘制二维码，请打开下面保存的图片扫描）")

    # 同时存一张图片，方便放大查看/扫描
    img = qrcode.make(home)
    img.save("static/qr.png")
    print("\n二维码图片已保存到 static/qr.png（可直接打开扫描）")
    print("启动后端请用: python main.py   (会监听 0.0.0.0，手机才能访问)")


if __name__ == "__main__":
    main()
