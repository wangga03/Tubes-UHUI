import lgpio
import time

# Menentukan nomor GPIO
GPIO_PIN = 26  # Ganti dengan pin GPIO yang sesuai dengan sensor PIR Anda

# Inisialisasi GPIO
try:
    # Membuka koneksi ke GPIO
    handle = lgpio.gpiochip_open(0)  # 0 untuk chip pertama (biasanya 0 di Raspberry Pi)
    
    # Mengatur pin sebagai input (untuk sensor PIR)
    lgpio.gpio_claim_input(handle, GPIO_PIN)
    
    print(f"Menggunakan GPIO Pin {GPIO_PIN} untuk membaca data dari Sensor PIR...")
    
    while True:
        # Membaca status pin
        status = lgpio.gpio_read(handle, GPIO_PIN)
        
        if status == 0:
            print("Tidak ada gerakan (LOW)")
        else:
            print("Gerakan terdeteksi (HIGH)")
        
        time.sleep(1)  # Menunggu 1 detik sebelum membaca lagi

except lgpio.LgpioError as e:
    print(f"Terjadi kesalahan: {e}")

finally:
    # Menutup koneksi GPIO
    lgpio.gpiochip_close(handle)
