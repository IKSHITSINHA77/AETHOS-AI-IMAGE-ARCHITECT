import os
from functools import lru_cache
from ultralytics import YOLO


def _resolve_model_path() -> str:
    """
    Keep model selection flexible for different repo layouts:
    - env override via YOLO_MODEL_PATH
    - prefer ./models/yolov8n.pt if present
    - fallback to ./yolov8n.pt (current repo already has this)
    """
    override = os.getenv("YOLO_MODEL_PATH")
    if override:
        return override

    candidates = [
        os.path.join("models", "yolov8n.pt"),
        "yolov8n.pt",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    # Last resort: let Ultralytics handle whatever it can, but be explicit.
    return "yolov8n.pt"


@lru_cache(maxsize=1)
def _get_model() -> YOLO:
    # Lazy-load so `python app.py` can start even on low-memory machines.
    return YOLO(_resolve_model_path())

def detect_objects(image_path):
    model = _get_model()
    results = model(image_path)
    objects = []
    for r in results:
        for box in r.boxes:
            if box.conf > 0.5:
                label = model.names[int(box.cls)]
                objects.append(label)
    return list(set(objects))


def detect_with_confidence(image_path):
    """
    Extended detection that returns label + confidence score pairs.
    Used by the Critic Loop for quality scoring.

    Returns:
        objects    : list of unique label strings
        confidences: list of float confidence values (one per detection, not unique)
    """
    model = _get_model()
    results = model(image_path)
    objects     = []
    confidences = []

    for r in results:
        for box in r.boxes:
            conf  = float(box.conf)
            label = model.names[int(box.cls)]
            if conf > 0.5:
                objects.append(label)
                confidences.append(conf)

    return list(set(objects)), confidences
