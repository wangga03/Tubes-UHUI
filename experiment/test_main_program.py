import gpiod
import subprocess
import time

# Setup GPIO via libgpiod
chip = gpiod.Chip('gpiochip4')  # Pastikan gpiochip sesuai dengan chip Raspberry Pi
pins = {
    'ir_sensor': 26,  # Pin untuk sensor IR, bisa disesuaikan
    'relay' : 24,
    'LEDHijau' : 22,
    'LEDUngu' : 27,
    'LEDMerah' : 17,
}
lines = {k: chip.get_line(v) for k, v in pins.items()}

# Request GPIO line untuk input dan output
for name, line in lines.items():
    if name == 'ir_sensor':  # Sensor IR sebagai input
        line.request(consumer="IR-Sensor", type=gpiod.LINE_REQ_DIR_IN)
    else:  # Semua pin lainnya sebagai output
        line.request(consumer="GPIO-Control", type=gpiod.LINE_REQ_DIR_OUT)

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

        if ir_status == 0:  # Sensor IR mendeteksi objek (status HIGH)
            print("[INFO] Objek terdeteksi oleh IR sensor.")
            run_face_test_script()  # Menjalankan FACE_Test2.py
            time.sleep(2)  # Delay untuk menghindari pemanggilan script terus-menerus
        else:  # Tidak ada objek terdeteksi
            # Reset semua output GPIO ke nilai default
            # lines['LEDHijau'].set_value(0)
            # lines['LEDUngu'].set_value(0)
            lines['relay'].set_value(0)
            print("[INFO] Tidak ada objek terdeteksi.")
            time.sleep(0.5)  # Cek setiap 500ms

except KeyboardInterrupt:
    print("[INFO] Program dihentikan.")
finally:
    # Cleanup GPIO
    for line in lines.values():
        line.release()
