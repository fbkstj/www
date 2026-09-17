"""測試 ESP32 的燈號與蜂鳴器：依序送出 安全 → 注意 → 危險，各 3 秒。

用法：python test_lights.py          自動尋找序列埠
      python test_lights.py COM5
"""
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    raise SystemExit("尚未安裝 pyserial：pip install pyserial")

KEYS = ("cp210", "ch340", "ch910", "silicon labs", "usb serial", "usb-serial", "usb jtag", "uart")


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else next(
        (p.device for p in list_ports.comports()
         if any(k in f"{p.description} {p.manufacturer or ''}".lower() for k in KEYS)), None)
    if not port:
        print("找不到 ESP32。目前的序列埠：")
        for p in list_ports.comports():
            print("  ", p.device, p.description)
        raise SystemExit("請確認 USB 線，或指定序列埠，例如：python test_lights.py COM5")

    with serial.Serial(port, 115200, timeout=0.1) as ser:
        print("已連線", port, "，等待 ESP32 重新開機…")
        time.sleep(2)
        print("ESP32 回應：", ser.read(200).decode("ascii", "ignore").strip() or "（沒有）")
        for level, name in ((0, "安全：綠燈恆亮"), (1, "注意：黃燈閃、每秒嗶一聲"), (2, "危險：紅燈快閃、連續嗶聲")):
            print(name)
            end = time.time() + 3
            while time.time() < end:
                ser.write(f"L{level}\n".encode())
                time.sleep(0.2)
        print("停止傳送：約 1.5 秒後應該變成「離線」（綠燈慢閃）")
        time.sleep(3)
    print("測試完成")


if __name__ == "__main__":
    main()
