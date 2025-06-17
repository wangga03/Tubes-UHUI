import lgpio
import time

# Buka chip GPIO utama
h = lgpio.gpiochip_open(0)

# Daftar pin LED
led_pins = [17, 22, 27]

# Klaim semua pin sebagai output dan set awal ke LOW (mati)
for pin in led_pins:
    lgpio.gpio_claim_output(h, pin, 0)

# Nyalakan semua LED
for pin in led_pins:
    lgpio.gpio_write(h, pin, 1)

print("LED ON")
time.sleep(2)

# Matikan semua LED
for pin in led_pins:
    lgpio.gpio_write(h, pin, 0)

print("LED OFF")

# Tutup chip GPIO
lgpio.gpiochip_close(h)
