import cv2
import os

# Load Haar Cascade untuk deteksi wajah
face_cascade = cv2.CascadeClassifier('/home/wgg/Tubes_AI/haarcascade_frontalface_alt2.xml')

# Membuka kamera
cap = cv2.VideoCapture(2)
foto_ke = 1  # Untuk penamaan file hasil crop

while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak dapat membuka kamera.")
        break

    # Ubah ke grayscale (lebih akurat untuk deteksi wajah)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Deteksi wajah
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Gambar kotak di wajah yang terdeteksi
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    cv2.imshow("Tekan 's' untuk foto wajah | ESC untuk keluar", frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        if len(faces) == 0:
            print("Tidak ada wajah terdeteksi, foto tidak disimpan.")
        else:
            for (x, y, w, h) in faces:
                crop_wajah = frame[y:y+h, x:x+w]
                filename = f'/home/wgg/Tubes_AI/dataset3/mig/wajah_{foto_ke}.jpg'
                cv2.imwrite(filename, crop_wajah)
                print(f"Wajah disimpan sebagai {filename}")
                foto_ke += 1
    elif key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
