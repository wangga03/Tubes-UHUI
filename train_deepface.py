from keras_facenet import FaceNet
import cv2, os
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import imgaug.augmenters as iaa
import pickle

embedder = FaceNet()
X, y = [], []

base_dir = "/home/wgg/Tubes_AI/dataset3"

# Augmentasi ringan (flip horizontal, rotasi kecil, brightness, blur kecil)
seq = iaa.Sequential([
    iaa.Fliplr(0.5),
    iaa.Affine(rotate=(-10, 10)),
    iaa.Multiply((0.8, 1.2)),
    iaa.GaussianBlur(sigma=(0, 1.0)),
])

AUG_PER_IMG = 2  # Berapa banyak augmentasi per gambar

for label in os.listdir(base_dir):
    folder = os.path.join(base_dir, label)
    for file in os.listdir(folder):
        img_path = os.path.join(folder, file)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (160, 160))

        # Embedding gambar asli
        emb = embedder.embeddings([img])[0]
        X.append(emb)
        y.append(label)

        # Augmentasi beberapa kali per gambar
        for _ in range(AUG_PER_IMG):
            aug_img = seq(image=img)
            emb_aug = embedder.embeddings([aug_img])[0]
            X.append(emb_aug)
            y.append(label)

X = np.array(X)
y = np.array(y)

# Latih KNN
knn = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
knn.fit(X, y)

# Simpan ke file .pkl
with open('/home/wgg/Tubes_AI/HASIL_FACENET/knn_facenet_aug2.pkl', 'wb') as f:
    pickle.dump(knn, f)

print("Model KNN FaceNet (dengan augmentasi) berhasil disimpan!")

