import RPi.GPIO as GPIO
import time

# Menggunakan penomoran pin BCM
GPIO.setmode(GPIO.BCM)

# Mengonfigurasi pin GPIO 17, 22, dan 27 sebagai output
GPIO.setup(17, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

# Menyalakan ketiga pin GPIO
GPIO.output(17, GPIO.HIGH)
GPIO.output(22, GPIO.HIGH)
GPIO.output(27, GPIO.HIGH)

# Menunggu selama 5 detik agar pin tetap menyala
time.sleep(5)

# Mematikan ketiga pin GPIO
GPIO.output(17, GPIO.LOW)
GPIO.output(22, GPIO.LOW)
GPIO.output(27, GPIO.LOW)

# Bersihkan pengaturan GPIO
GPIO.cleanup()
