# thumbnail_utils.py
# Everything related to image/thumbnail analysis

import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple
import os


# ─────────────────────────────────────────────
# FUNCTION 1 — CALCULATE BRIGHTNESS
# ─────────────────────────────────────────────

def calculate_brightness(image_path: str) -> float:
    """
    Calculate average brightness of image.
    
    Returns score 0.0 to 1.0
    0.0 = completely black
    1.0 = completely white
    0.5-0.7 = ideal for thumbnails
    """
    
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Mean pixel value (0-255)
    mean_brightness = np.mean(gray)
    
    # Normalize to 0.0-1.0
    score = mean_brightness / 255.0
    
    return round(float(score), 3)


# ─────────────────────────────────────────────
# FUNCTION 2 — CALCULATE CONTRAST
# ─────────────────────────────────────────────

def calculate_contrast(image_path: str) -> float:
    """
    Calculate contrast using standard deviation of pixel values.
    Higher std deviation = more contrast = better thumbnail visibility.
    
    Returns score 0.0 to 1.0
    """
    
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Standard deviation of pixel values
    std_dev = np.std(gray)
    
    # Max possible std_dev for grayscale is ~128
    # Normalize to 0.0-1.0
    score = min(std_dev / 128.0, 1.0)
    
    return round(float(score), 3)


# ─────────────────────────────────────────────
# FUNCTION 3 — CALCULATE SHARPNESS
# ─────────────────────────────────────────────

def calculate_sharpness(image_path: str) -> float:
    """
    Calculate image sharpness using Laplacian variance.
    High variance = sharp image.
    Low variance = blurry image.
    
    Returns score 0.0 to 1.0
    """
    
    img = cv2.imread(image_path)
    
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Laplacian detects edges/sharpness
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    
    # Cap at 1000 for normalization (adjust based on testing)
    score = min(variance / 1000.0, 1.0)
    
    return round(float(score), 3)


# ─────────────────────────────────────────────
# FUNCTION 4 — DETECT FACE
# ─────────────────────────────────────────────

def detect_face(image_path: str) -> bool:
    """
    Use OpenCV Haar Cascade to detect if face exists in image.
    Returns True if face detected, False otherwise.
    Compatible with OpenCV 4.x and 5.x
    """

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    try:
        # Try standard method first (OpenCV 4.x)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(30, 30)
        )

        return len(faces) > 0

    except AttributeError:
        # OpenCV 5.x fallback — use objdetect module
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            face_cascade = cv2.objdetect.CascadeClassifier(cascade_path)

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(30, 30)
            )

            return len(faces) > 0

        except Exception:
            # If both fail, return False safely
            # Do not crash the entire analysis
            print("   ⚠️  Face detection unavailable — returning False")
            return False


# ─────────────────────────────────────────────
# FUNCTION 5 — GENERATE COMPOSITION FEEDBACK
# ─────────────────────────────────────────────

def generate_composition_feedback(
    brightness: float,
    contrast: float,
    sharpness: float,
    face_detected: bool
) -> Tuple[str, List[str]]:
    """
    Based on scores, generate human-readable feedback and recommendations.
    
    Returns (composition_feedback_string, list_of_recommendations)
    """
    
    recommendations = []
    feedback_parts = []
    
    # Brightness feedback
    if brightness < 0.3:
        feedback_parts.append("Image is too dark")
        recommendations.append("Increase brightness - dark thumbnails get ignored in feeds")
    elif brightness > 0.85:
        feedback_parts.append("Image is overexposed")
        recommendations.append("Reduce brightness - overexposed thumbnails look washed out")
    else:
        feedback_parts.append("Brightness is good")
    
    # Contrast feedback
    if contrast < 0.3:
        feedback_parts.append("Low contrast makes text and subjects hard to see")
        recommendations.append("Increase contrast to make subject stand out more")
    elif contrast > 0.85:
        feedback_parts.append("Very high contrast")
        recommendations.append("High contrast is fine but check for harsh shadows")
    else:
        feedback_parts.append("Contrast is good")
    
    # Sharpness feedback
    if sharpness < 0.2:
        feedback_parts.append("Image appears blurry")
        recommendations.append("Use a sharper image - blurry thumbnails lose clicks immediately")
    elif sharpness > 0.8:
        feedback_parts.append("Image is very sharp and clear")
    else:
        feedback_parts.append("Sharpness is acceptable")
    
    # Face feedback
    if not face_detected:
        recommendations.append("Consider adding a face - thumbnails with faces get 38% more clicks")
    else:
        feedback_parts.append("Face detected - good for click-through rate")
    
    composition_feedback = ". ".join(feedback_parts)
    
    return composition_feedback, recommendations