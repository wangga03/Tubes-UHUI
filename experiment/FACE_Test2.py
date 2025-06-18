import os
import pickle
import cv2
import sys
import contextlib
import time
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

# Initialize FaceNet + model
embedder = FaceNet()
model_pkl = '/home/pi/Tubes-UHUI/HASIL_FACENET/knn_facenet_aug4.pkl'
if not os.path.exists(model_pkl):
    print("Model .pkl tidak ditemukan! Latih dulu.")
    sys.exit(1)
with open(model_pkl, 'rb') as f:
    knn = pickle.load(f)
print("Model KNN siap digunakan!")

# Setup GPIO via libgpiod
chip = gpiod.Chip('gpiochip4')
pins = {
    'tidak_terdeteksi': 22,
    'lain': 17,
    'jak_wgg': 27,
    'jak_wgg_mirror': 24,  # Tambahan GPIO24 mirror dari GPIO27
    'buzzer': 23
}
lines = {k: chip.get_line(v) for k, v in pins.items()}

# Melepaskan GPIO yang sudah digunakan sebelumnya (jika ada)
for line in lines.values():
    line.release()

# Request GPIO lines untuk input dan output
for name, line in lines.items():
    if name == 'jak_wgg_mirror':  # Pastikan GPIO mirror diatur sebagai output
        line.request(consumer="face-led", type=gpiod.LINE_REQ_DIR_OUT)
    else:
        line.request(consumer="face-led", type=gpiod.LINE_REQ_DIR_OUT)

# Fungsi untuk mengupdate status GPIO
def update_gpio(status):
    # Reset semua LED dan buzzer
    for name, line in lines.items():
        line.set_value(0)
    # Aktifkan sesuai status
    if status in lines:
        lines[status].set_value(1)
    # Mirror GPIO24 jika jak_wgg aktif
    if status == 'jak_wgg':
        lines['jak_wgg_mirror'].set_value(1)
    # Khusus: aktifkan buzzer jika 'lain'
    if status == 'lain':
        lines['buzzer'].set_value(1)

# Setup kamera & face cascade
face_cascade = cv2.CascadeClassifier('/home/pi/Tubes-UHUI/haarcascade_frontalface_alt2.xml')
cap = cv2.VideoCapture(0)
print("[INFO] Kamera aktif—tekan 'q' atau ESC untuk berhenti")

while True:
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
            conf = knn.predict_proba([emb]).max()
            clr = (0, 255, 0) if pred in ['wgg', 'jak'] else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), clr, 2)
            cv2.putText(frame, f"{pred} ({conf:.2f})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, clr, 2)

    print("\033c", end="")

    if pred in ['wgg', 'jak']:
        print(f"[OK] {pred} terdeteksi → GPIO27 & GPIO24 ON", end="\r")
        update_gpio('jak_wgg')
        # Tambahkan delay 10 detik
        print(f"[INFO] Menunggu 10 detik sebelum mematikan kamera...")
        time.sleep(10)  # Delay selama 10 detik sebelum mematikan kamera
        print("[INFO] Kamera dimatikan.")
        cap.release()  # Matikan kamera setelah 10 detik
        break
    elif pred is None:
        print("[INFO] Tidak ada wajah → GPIO22 ON", end="\r")
        update_gpio('tidak_terdeteksi')
    else:
        print(f"[WARN] {pred} wajah lain → GPIO17 & BUZZER ON", end="\r")
        update_gpio('lain')

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:  # 'q' atau ESC
        break

# Cleanup
lines['jak_wgg_mirror'].set_value(0)  # Memastikan GPIO mirror dimatikan sebelum keluar
cap.release()
cv2.destroyAllWindows()
for ln in lines.values():
    ln.release()
