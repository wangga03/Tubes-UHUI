import gpiod
import time

gpio_pin = 17  # Ganti jika kamu pakai pin lain

chip = gpiod.Chip("gpiochip4")
line = chip.get_line(gpio_pin)

# Request pin sebagai OUTPUT
line.request(consumer="force_on", type=gpiod.LINE_REQ_DIR_OUT)

line.set_value(1)
print(f"GPIO{gpio_pin} SET HIGH (3.3V)")
input("Tekan Enter untuk matikan...")

line.set_value(0)
line.release()