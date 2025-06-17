import gpiod
import time

chip = gpiod.Chip("gpiochip4")  # ✅ GANTI KE gpiochip4
line = chip.get_line(17)        # Gunakan BCM 17

line.request(consumer="blink", type=gpiod.LINE_REQ_DIR_OUT)

for _ in range(5):
    line.set_value(1)
    print("LED ON")
    time.sleep(1)
    line.set_value(0)
    print("LED OFF")
    time.sleep(1)

line.release()
