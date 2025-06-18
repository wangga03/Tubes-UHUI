import gpiod
import subprocess
import time

# Setup GPIO via libgpiod
chip = gpiod.Chip('gpiochip4')  # Pastikan gpiochip sesuai dengan chip Raspberry Pi
pins = {
    'ir_sensor': 26,  # Pin untuk sensor IR, bisa disesuaikan
    'tidak_terdeteksi': 22,  # Pin GPIO untuk status tidak terdeteksi
    'lain': 17,  # Pin GPIO untuk status wajah lain
    'jak_wgg': 27,  # Pin GPIO untuk status wgg/jak
    'buzzer': 23  # Pin GPIO untuk buzzer
}
lines = {k: chip.get_line(v) for k, v in pins.items()}

# Request GPIO line untuk input dan output
for line in lines.values():
    line.request(consumer="IR-Sensor", type=gpiod.LINE_REQ_DIR_OUT)

# Fungsi untuk mereset semua state GPIO
def reset_gpio_state():
    print("[INFO] Resetting all GPIO states...")
    for name, line in lines.items():
        line.set_value(0)  # Mematikan semua GPIO (reset state)

# Fungsi untuk menjalankan script FACE_Test2.py menggunakan /bin/python
def run_face_test_script():
    try:
        print("[INFO] Menjalankan script FACE_Test2.py menggunakan /bin/python...")
        subprocess.run(['/bin/python', '/home/pi/Tubes-UHUI/experiment/FACE_Test2.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Terjadi kesalahan saat menjalankan script: {e}")

# Main loop untuk memeriksa sensor IR
try:
    print("[INFO] Program aktif. Menunggu deteksi objek...")
    while True:
        # Membaca status sensor IR (apakah terdeteksi objek atau tidak)
        ir_status = lines['ir_sensor'].get_value()

        if ir_status == 1:
            # Jika sensor IR mendeteksi objek (status HIGH), jalankan script
            print("[INFO] Objek terdeteksi oleh IR sensor.")
            run_face_test_script()  # Menjalankan FACE_Test2.py
            time.sleep(2)  # Delay untuk menghindari pemanggilan script terus-menerus

            # Setelah script selesai, reset semua state GPIO
            reset_gpio_state()

        else:
            print("[INFO] Tidak ada objek terdeteksi.")
            time.sleep(0.5)  # Cek setiap 500ms

except KeyboardInterrupt:
    print("[INFO] Program dihentikan.")
    reset_gpio_state()  # Reset state GPIO sebelum keluar dari program

finally:
    # Cleanup GPIO
    for line in lines.values():
        line.release()
