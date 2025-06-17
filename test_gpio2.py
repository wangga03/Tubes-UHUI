import RPi.GPIO2 as GPIO
import time

# Menggunakan penomoran pin BCM
GPIO.setmode(GPIO.BCM)

# Mendefinisikan pin GPIO yang akan digunakan
gpio_pins = {
    '1': 17,
    '2': 22,
    '3': 27
}

# Mengonfigurasi pin GPIO sebagai output
for pin in gpio_pins.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Mulai dengan mematikan semua LED

def activate_gpio(pin):
    """Mengaktifkan GPIO berdasarkan input"""
    GPIO.output(pin, GPIO.HIGH)  # Nyalakan LED
    print(f"GPIO {pin} diaktifkan.")
    time.sleep(2)  # LED tetap menyala selama 2 detik
    GPIO.output(pin, GPIO.LOW)  # Matikan LED setelah 2 detik
    print(f"GPIO {pin} dimatikan.")

try:
    while True:
        # Meminta input pengguna
        user_input = input("Masukkan angka (1, 2, 3) untuk mengaktifkan LED: ")

        if user_input in gpio_pins:
            # Mengaktifkan GPIO sesuai input
            activate_gpio(gpio_pins[user_input])
        else:
            print("Input tidak valid. Silakan masukkan 1, 2, atau 3.")
except KeyboardInterrupt:
    print("\nProgram dihentikan.")
finally:
    # Membersihkan konfigurasi GPIO
    GPIO.cleanup()
