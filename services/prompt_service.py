"""
prompt_service.py
-----------------
Parses slash commands and computes critic quality scores.
"""

import re


# ─── Command Parser ────────────────────────────────────────────────────────────

COMMANDS = {
    "/orchestrate": "orchestrate",
    "/audit":       "audit",
    "/brand":       "brand",
}

def parse_command(raw_input: str) -> dict:
    """
    Detects the slash command and extracts the payload.

    Returns:
        {
          "mode":    "orchestrate" | "audit" | "brand" | "analyze",
          "payload": <string after command>,
          "constraints": { ... extracted constraints ... }
        }
    """
    raw = raw_input.strip()

    mode    = "analyze"
    payload = raw

    for cmd, name in COMMANDS.items():
        if raw.lower().startswith(cmd.lower()):
            mode    = name
            payload = raw[len(cmd):].strip()
            break

    constraints = _extract_constraints(payload)

    return {
        "mode":        mode,
        "payload":     payload,
        "constraints": constraints,
    }


def _extract_constraints(text: str) -> dict:
    """
    Heuristically extracts known constraints from the prompt/payload.
    """
    constraints = {
        "dimensions": None,
        "hex_colors":  [],
        "style":       None,
        "subject_dna": None,
    }

    # Dimensions: e.g. 1920x1080, 16:9, 4:3
    dim_match = re.search(r"\b(\d{3,4})[x×:](\d{3,4})\b", text, re.IGNORECASE)
    if dim_match:
        constraints["dimensions"] = f"{dim_match.group(1)}×{dim_match.group(2)}"

    # Hex colors
    constraints["hex_colors"] = re.findall(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", text)

    # Style keywords
    style_keywords = [
        "cyberpunk", "watercolor", "oil painting", "photorealistic",
        "anime", "sketch", "cinematic", "noir", "vaporwave", "3d render",
        "minimalist", "baroque", "impressionist", "pixel art"
    ]
    for kw in style_keywords:
        if kw.lower() in text.lower():
            constraints["style"] = kw
            break

    # Subject DNA — quoted text or capitalized nouns heuristic
    quoted = re.findall(r'"([^"]+)"', text)
    if quoted:
        constraints["subject_dna"] = quoted[0]

    return constraints


# ─── Critic Quality Scoring ────────────────────────────────────────────────────

def assess_quality(
    caption: str,
    objects: list,
    text: str,
    confidences: list = None
) -> dict:
    """
    Computes a deterministic critic score (1–10) from available ML outputs.

    Scoring breakdown (max 10 pts):
      - Caption quality     : 0–4 pts  (length, vocabulary richness)
      - Object confidence   : 0–3 pts  (mean confidence of detections)
      - Text extraction     : 0–2 pts  (presence and length of OCR)
      - Object count        : 0–1 pt   (diversity of detections)

    Returns:
        {
          "score": float,
          "breakdown": { ... },
          "verdict": "pass" | "refine",
          "notes": [...]
        }
    """
    notes = []
    breakdown = {}

    # 1. Caption quality (0–4)
    cap_score = 0
    if caption:
        words = caption.split()
        length_score = min(len(words) / 10, 1.0)   # saturates at 10 words → 1.0
        unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
        cap_score = round((length_score * 2 + unique_ratio * 2), 2)
        if cap_score < 1.5:
            notes.append("Caption is too brief or repetitive — consider re-captioning.")
    else:
        notes.append("No caption generated — BLIP model may have failed.")

    breakdown["caption_quality"] = round(cap_score, 2)

    # 2. Object confidence (0–3)
    obj_score = 0
    if confidences and len(confidences) > 0:
        mean_conf = sum(confidences) / len(confidences)
        obj_score = round(mean_conf * 3, 2)
        if mean_conf < 0.65:
            notes.append("Average detection confidence is low — consider a larger YOLO model.")
    elif objects:
        obj_score = 1.5  # fallback: detections exist but no confidence data
        notes.append("Confidence data unavailable — scores estimated.")
    else:
        notes.append("No objects detected — image may be abstract or low-contrast.")

    breakdown["object_confidence"] = round(obj_score, 2)

    # 3. OCR / text extraction (0–2)
    ocr_score = 0
    if text and text.strip():
        ocr_score = min(len(text.strip()) / 50, 1.0) * 2  # saturates at 50 chars → 2.0
    breakdown["text_extraction"] = round(ocr_score, 2)

    # 4. Object diversity (0–1)
    diversity_score = min(len(set(objects)) / 5, 1.0) if objects else 0
    if len(set(objects)) >= 3:
        notes.append("Good object diversity detected.")
    breakdown["object_diversity"] = round(diversity_score, 2)

    total = cap_score + obj_score + ocr_score + diversity_score
    total = round(min(total, 10.0), 2)

    verdict = "pass" if total >= 8.0 else "refine"
    if verdict == "refine":
        notes.append(f"Score {total}/10 is below threshold (8.0) — Refine step triggered.")

    return {
        "score":     total,
        "breakdown": breakdown,
        "verdict":   verdict,
        "notes":     notes,
    }
