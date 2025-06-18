import os, pickle, cv2, sys, contextlib, time
from keras_facenet import FaceNet
from sklearn.neighbors import KNeighborsClassifier
import gpiod

@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old

# === Load KNN model ===
embedder = FaceNet()
model_pkl = '/home/pi/Tubes-UHUI/HASIL_FACENET/knn_facenet_aug4.pkl'
if not os.path.exists(model_pkl):
    print("Model .pkl tidak ditemukan! Latih dulu.")
    sys.exit(1)
with open(model_pkl, 'rb') as f:
    knn = pickle.load(f)
print("Model KNN siap digunakan!")

# === Setup GPIO ===
chip = gpiod.Chip('gpiochip4')
pins = {
    'tidak_terdeteksi': 22,
    'lain': 17,
    'jak_wgg': 27,
    'jak_wgg_mirror': 24,
    'buzzer': 23,
    'sensor_ir': 26
}
lines = {}

for name, pin in pins.items():
    try:
        line = chip.get_line(pin)
        if name == 'sensor_ir':
            line.request(consumer="face-led", type=gpiod.LINE_REQ_DIR_IN)
        else:
            line.request(consumer="face-led", type=gpiod.LINE_REQ_DIR_OUT)
            line.set_value(0)
        lines[name] = line
        print(f"[INIT] GPIO{pin} untuk '{name}' siap")
    except Exception as e:
        print(f"[ERROR] Gagal setup GPIO{pin} ({name}): {e}")
        sys.exit(1)

def reset_gpio():
    for name, ln in lines.items():
        if name != 'sensor_ir':
            ln.set_value(0)
    print("[RESET] Semua GPIO dimatikan.")

def wait_for_ir(value):
    while True:
        ir = lines['sensor_ir'].get_value()
        if ir == value:
            break
        time.sleep(0.1)

def face_detection_mode():
    face_cascade = cv2.CascadeClassifier('/home/pi/Tubes-UHUI/haarcascade_frontalface_alt2.xml')
    cap = cv2.VideoCapture(0)
    print("[INFO] Kamera aktif—deteksi wajah dimulai")

    recognized = False

    try:
        while True:
            if recognized:
                # Sudah deteksi jak/wgg, tahan GPIO ON selama 5 detik
                print("\n[TIMER] Menahan GPIO24 & 27 selama 5 detik...")
                time.sleep(5)
                break  # keluar dari loop deteksi wajah

            ret, frame = cap.read()
            if not ret:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
            pred = None

            if len(faces) > 0:
                x, y, w, h = faces[0]
                face = frame[y:y+h, x:x+w]
                if face.size > 0:
                    img = cv2.cvtColor(cv2.resize(face, (160, 160)), cv2.COLOR_BGR2RGB)
                    with suppress_stdout():
                        emb = embedder.embeddings([img])[0]
                    pred = knn.predict([emb])[0]

            print("\033c", end="")
            if pred in ['jak', 'wgg']:
                print(f"[OK] {pred} terdeteksi → GPIO27 & GPIO24 ON", end="\r")

                # Aktifkan pin sekali
                lines['jak_wgg'].set_value(1)
                lines['jak_wgg_mirror'].set_value(1)
                lines['tidak_terdeteksi'].set_value(0)
                lines['lain'].set_value(0)
                lines['buzzer'].set_value(0)

                recognized = True  # tandai sudah dikenali
                continue  # jangan deteksi lagi

            elif pred is None:
                print("[INFO] Tidak ada wajah → GPIO22 ON", end="\r")
                lines['tidak_terdeteksi'].set_value(1)
                lines['jak_wgg'].set_value(0)
                lines['jak_wgg_mirror'].set_value(0)
                lines['lain'].set_value(0)
                lines['buzzer'].set_value(0)

            else:
                print(f"[WARN] {pred} wajah lain → GPIO17 & BUZZER ON", end="\r")
                lines['lain'].set_value(1)
                lines['buzzer'].set_value(1)
                lines['tidak_terdeteksi'].set_value(0)
                lines['jak_wgg'].set_value(0)
                lines['jak_wgg_mirror'].set_value(0)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

def main():
    try:
        while True:
            print("\n[WAIT] Menunggu IR LOW (ada objek)...")
            wait_for_ir(0)

            print("[START] IR aktif → kamera mulai")
            face_detection_mode()

            reset_gpio()

            print("[WAIT] Menunggu IR HIGH (objek keluar)...")
            wait_for_ir(1)

    finally:
        reset_gpio()
        for ln in lines.values():
            ln.release()
        print("\n[INFO] Program selesai. Semua GPIO dilepas.")

if __name__ == '__main__':
    main()
