# train_soil_classifier.py
import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from skimage.feature import local_binary_pattern

# ---- Parameters ----
DATA_DIR = "data/train"   # Trains on subfolders per class
MODEL_OUT = "soil_model.joblib"
RANDOM_STATE = 42
IMG_SIZE = (300, 300)     # resize for consistency
# LBP params
R = 3
N_POINTS = 8 * R
METHOD = "uniform"

def load_images_and_labels(data_dir):
    X = []
    y = []
    classes = sorted(os.listdir(data_dir))
    for cls in classes:
        cls_dir = os.path.join(data_dir, cls)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            path = os.path.join(cls_dir, fname)
            try:
                img = cv2.imread(path)
                if img is None:
                    continue
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, IMG_SIZE)
                X.append(img)
                y.append(cls)
            except Exception as e:
                print("Error reading", path, e)
    return X, y

def color_histogram(image, bins=(8, 8, 8)):
    # image in RGB
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], None, bins,
                        [0, 180, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

def lbp_histogram(image, P=N_POINTS, R=R, method=METHOD, bins=24):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    lbp = local_binary_pattern(gray, P, R, method)
    # compute histogram
    (hist, _) = np.histogram(lbp.ravel(),
                             bins=np.arange(0, P + 3),
                             range=(0, P + 2))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-7)
    return hist

def extract_features(images):
    feats = []
    for img in images:
        ch = color_histogram(img)
        lbp = lbp_histogram(img)
        feat = np.hstack([ch, lbp])
        feats.append(feat)
    return np.array(feats)

if __name__ == "__main__":
    print("Loading images...")
    X_imgs, y = load_images_and_labels(DATA_DIR)
    print(f"Loaded {len(X_imgs)} images across {len(set(y))} classes.")

    print("Extracting features...")
    X = extract_features(X_imgs)

    print("Splitting dataset...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    print("Training RandomForest...")
    clf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
    clf.fit(X_train, y_train)

    print("Evaluating...")
    y_pred = clf.predict(X_val)
    print(classification_report(y_val, y_pred))
    print("Confusion matrix:")
    print(confusion_matrix(y_val, y_pred))

    print(f"Saving model to {MODEL_OUT}")
    joblib.dump({
        "model": clf,
        "classes": clf.classes_,
        "img_size": IMG_SIZE
    }, MODEL_OUT)

    print("Done.")

