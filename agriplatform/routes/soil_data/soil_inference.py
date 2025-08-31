import cv2
import numpy as np
import joblib
from skimage.feature import local_binary_pattern
import os

MODEL_PATH = os.environ.get("SOIL_MODEL_PATH", "soil_model.joblib")

# constants must match training
R = 3
N_POINTS = 8 * R
METHOD = "uniform"
IMG_SIZE = (300, 300)

def load_model():
    data = joblib.load(MODEL_PATH)
    return data["model"], data.get("classes", None)

_model = None
_classes = None

def ensure_model_loaded():
    global _model, _classes
    if _model is None:
        _model, _classes = load_model()

def color_histogram(image, bins=(8,8,8)):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0,1,2], None, bins, [0,180,0,256,0,256])
    cv2.normalize(hist, hist)
    return hist.flatten()

def lbp_histogram(image, P=N_POINTS, R=R, method=METHOD):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(gray, P, R, method)
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, P+3), range=(0, P+2))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-7)
    return hist

def extract_features_from_path(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError("Unable to read image at " + path)
    img = cv2.resize(img, IMG_SIZE)
    ch = color_histogram(img)
    lbp = lbp_histogram(img)
    feat = np.hstack([ch, lbp])
    return feat.reshape(1, -1)

def analyze_soil(image_path):
    """
    Returns: (pred_label, {label: probability, ...})
    """
    ensure_model_loaded()
    feat = extract_features_from_path(image_path)
    probs = _model.predict_proba(feat)[0]
    labels = _model.classes_
    # map label->prob
    prob_map = {label: float(probs[i]) for i, label in enumerate(labels)}
    top_idx = int(probs.argmax())
    pred = labels[top_idx]
    return pred, prob_map

