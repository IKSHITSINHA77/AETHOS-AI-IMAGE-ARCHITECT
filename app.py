from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

from services.object_detection  import detect_objects, detect_with_confidence
from services.capture_service   import generate_caption
from services.ocr_service       import extract_text
from services.wiki_service      import enrich_objects_with_wiki
from services.agent_service     import orchestrate

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB


# ─── Home ──────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


# ─── /analyze  (legacy — plain image analysis) ────────────────────────────────

@app.route("/analyze", methods=["POST"])
def analyze():
    file     = request.files["image"]
    filename = secure_filename(file.filename)
    path     = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    raw_cmd = request.form.get("command", "/analyze")

    # Run full ML pipeline
    objects, confidences = detect_with_confidence(path)
    caption  = generate_caption(path)
    text     = extract_text(path)
    wiki_data = enrich_objects_with_wiki(objects)

    # Orchestrate agent response
    agent = orchestrate(
        raw_input   = raw_cmd,
        caption     = caption,
        objects     = objects,
        text        = text,
        confidences = confidences,
        wiki_data   = wiki_data,
    )

    return render_template(
        "result.html",
        filename  = filename,
        agent     = agent,
        # Legacy template vars (kept for result.html backward-compat)
        objects   = objects,
        caption   = caption,
        text      = text,
        wiki_data = wiki_data,
    )


# ─── /orchestrate  (text-only creative planning mode) ────────────────────────

@app.route("/orchestrate", methods=["POST"])
def orchestrate_route():
    data    = request.get_json(silent=True) or request.form
    prompt  = data.get("prompt", "")
    raw_cmd = f"/orchestrate {prompt}"

    # No image — orchestrate produces a planning response only
    agent = orchestrate(raw_input=raw_cmd)

    return jsonify({
        "mode":        agent["mode"],
        "plan":        agent["plan"],
        "models_used": agent["models_used"],
        "critic":      agent["critic"],
        "next_step":   agent["next_step"],
    })


# ─── /audit  (image quality audit) ──────────────────────────────────────────

@app.route("/audit", methods=["POST"])
def audit_route():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file     = request.files["image"]
    filename = secure_filename(file.filename)
    path     = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    objects, confidences = detect_with_confidence(path)
    caption  = generate_caption(path)
    text     = extract_text(path)
    wiki_data = enrich_objects_with_wiki(objects)

    agent = orchestrate(
        raw_input   = "/audit",
        caption     = caption,
        objects     = objects,
        text        = text,
        confidences = confidences,
        wiki_data   = wiki_data,
    )

    return render_template(
        "result.html",
        filename  = filename,
        agent     = agent,
        objects   = objects,
        caption   = caption,
        text      = text,
        wiki_data = wiki_data,
    )


# ─── /brand  (brand-style adaptation) ────────────────────────────────────────

@app.route("/brand", methods=["POST"])
def brand_route():
    data    = request.get_json(silent=True) or request.form
    prompt  = data.get("prompt", "")
    raw_cmd = f"/brand {prompt}"

    agent = orchestrate(raw_input=raw_cmd)

    return jsonify({
        "mode":        agent["mode"],
        "plan":        agent["plan"],
        "models_used": agent["models_used"],
        "critic":      agent["critic"],
        "next_step":   agent["next_step"],
    })


if __name__ == "__main__":
    app.run(debug=True)