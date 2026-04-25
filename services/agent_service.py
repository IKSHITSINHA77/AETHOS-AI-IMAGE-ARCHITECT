"""
agent_service.py
----------------
Core orchestration engine for the Agentic Image Architect.
Implements Phase 1 (Intent Decomposition), Phase 2 (Model Selection),
and Phase 3 (Critic Loop) as described in the system prompt.
"""

from services.prompt_service import parse_command, assess_quality


# ─── Model Registry ────────────────────────────────────────────────────────────

MODEL_REGISTRY = {
    "diffusion":     {"name": "Stable Diffusion XL",  "role": "Base image synthesis",           "icon": "🎨"},
    "controlnet":    {"name": "ControlNet Canny",      "role": "Structural / pose integrity",    "icon": "🏗️"},
    "yolo":          {"name": "YOLOv8 (Local)",        "role": "Object detection & localization", "icon": "🎯"},
    "blip":          {"name": "BLIP-2 (Salesforce)",   "role": "Visual captioning & VQA",        "icon": "💬"},
    "tesseract":     {"name": "Tesseract OCR",          "role": "Text extraction from imagery",   "icon": "📝"},
    "upscaler":      {"name": "Real-ESRGAN 4×",        "role": "Detail injection & upscaling",   "icon": "✨"},
    "vae":           {"name": "SDXL-VAE",              "role": "Latent space decoding",          "icon": "🔬"},
    "clip":          {"name": "OpenAI CLIP",           "role": "Text-image alignment scoring",   "icon": "🔗"},
    "wikipedia":     {"name": "Wikipedia API",         "role": "Knowledge enrichment",           "icon": "📚"},
    "style_adapter": {"name": "IP-Adapter (Style)",    "role": "Brand / style transfer",         "icon": "🎭"},
}


# ─── Phase 1: Intent Decomposition ────────────────────────────────────────────

def decompose_intent(mode: str, payload: str, constraints: dict) -> dict:
    """
    Identifies the creative goal, breaks it into sub-tasks, and extracts constraints.
    """
    sub_tasks = []
    goal_type = "unknown"

    if mode == "orchestrate":
        goal_type = "new_creation"
        sub_tasks = [
            {"step": 1, "task": "Scene Composition",  "desc": f"Parse visual elements from: \"{payload[:80]}\""},
            {"step": 2, "task": "Subject Rendering",  "desc": "Generate primary subject with texture & lighting"},
            {"step": 3, "task": "Background Synthesis","desc": "Synthesize environment / background layer"},
            {"step": 4, "task": "Lighting Pass",       "desc": "Apply cinematic lighting model and shadows"},
            {"step": 5, "task": "Post-Processing",     "desc": "Upscale, sharpen, and inject fine details"},
        ]
        if constraints.get("style"):
            sub_tasks.insert(1, {
                "step": 1.5, "task": "Style Application",
                "desc": f"Apply \"{constraints['style']}\" aesthetic via style adapter"
            })

    elif mode == "audit":
        goal_type = "quality_audit"
        sub_tasks = [
            {"step": 1, "task": "Object Detection",   "desc": "Run YOLOv8 to identify all elements"},
            {"step": 2, "task": "Caption Generation", "desc": "BLIP-2 describes the scene semantically"},
            {"step": 3, "task": "Text Extraction",    "desc": "Tesseract scans for embedded text or labels"},
            {"step": 4, "task": "Knowledge Enrichment","desc":"Wikipedia API enriches each detected object"},
            {"step": 5, "task": "Critic Evaluation",  "desc": "Score output against quality threshold (8/10)"},
        ]

    elif mode == "brand":
        goal_type = "brand_adaptation"
        sub_tasks = [
            {"step": 1, "task": "Style Extraction",   "desc": "Extract dominant palette and typography DNA"},
            {"step": 2, "task": "Brand Mapping",      "desc": "Map asset colors to provided hex palette"},
            {"step": 3, "task": "Style Transfer",     "desc": "Apply IP-Adapter for brand-consistent output"},
            {"step": 4, "task": "Consistency Check",  "desc": "Verify subject DNA is preserved post-transfer"},
        ]
        if constraints.get("hex_colors"):
            sub_tasks[1]["desc"] += f" → {', '.join(constraints['hex_colors'])}"

    else:  # analyze / default
        goal_type = "image_analysis"
        sub_tasks = [
            {"step": 1, "task": "Object Detection",   "desc": "YOLOv8 identifies objects above 50% confidence"},
            {"step": 2, "task": "Caption Generation", "desc": "BLIP generates a natural-language scene description"},
            {"step": 3, "task": "Text Extraction",    "desc": "Tesseract extracts any embedded text"},
            {"step": 4, "task": "Knowledge Enrichment","desc": "Wikipedia enriches detected labels"},
        ]

    return {
        "goal_type":   goal_type,
        "sub_tasks":   sub_tasks,
        "constraints": constraints,
        "payload":     payload,
    }


# ─── Phase 2: Model Selection ─────────────────────────────────────────────────

_MODEL_MAP = {
    "new_creation": [
        "diffusion", "controlnet", "style_adapter", "vae", "clip", "upscaler"
    ],
    "quality_audit": [
        "yolo", "blip", "tesseract", "clip", "wikipedia"
    ],
    "brand_adaptation": [
        "style_adapter", "controlnet", "clip", "upscaler"
    ],
    "image_analysis": [
        "yolo", "blip", "tesseract", "wikipedia"
    ],
}

def select_models(goal_type: str, constraints: dict) -> list:
    """
    Returns the ordered list of models chosen for this workflow.
    """
    model_keys = _MODEL_MAP.get(goal_type, _MODEL_MAP["image_analysis"])

    # If hex colors specified → ensure style_adapter is included
    if constraints.get("hex_colors") and "style_adapter" not in model_keys:
        model_keys = ["style_adapter"] + model_keys

    models_used = [
        {**MODEL_REGISTRY[k], "key": k}
        for k in model_keys
        if k in MODEL_REGISTRY
    ]
    return models_used


# ─── Phase 3: Critic Loop ─────────────────────────────────────────────────────

def run_critic_loop(
    caption: str,
    objects: list,
    text: str,
    confidences: list = None,
    threshold: float = 8.0
) -> dict:
    """
    Simulates the Critic Agent. Scores the output and optionally triggers a
    refinement step if the score falls below the threshold.
    """
    quality = assess_quality(caption, objects, text, confidences)
    score   = quality["score"]
    verdict = quality["verdict"]

    refinements = []
    if verdict == "refine":
        # Trigger synthetic refinement actions
        if not caption or len(caption.split()) < 5:
            refinements.append("🔁 Re-prompted BLIP with higher beam search count (beam=8 → 16)")
        if not objects:
            refinements.append("🔁 Switched from YOLOv8n → YOLOv8l for higher recall")
        if not text or not text.strip():
            refinements.append("🔁 Applied adaptive thresholding before Tesseract re-run")
        if not refinements:
            refinements.append("🔁 Applied CLIP re-alignment pass to boost semantic fidelity")

    return {
        "score":        score,
        "breakdown":    quality["breakdown"],
        "verdict":      verdict,
        "notes":        quality["notes"],
        "refinements":  refinements,
        "threshold":    threshold,
    }


# ─── Next Step Suggestions ────────────────────────────────────────────────────

_NEXT_STEPS = {
    "new_creation":    "Would you like to `/audit` this generated image to score its quality, or `/brand` it with a custom palette?",
    "quality_audit":   "Would you like to `/orchestrate` a new variation of this scene, or `/brand` the image to match a style guide?",
    "brand_adaptation":"Would you like to create a full brand asset series? Try `/orchestrate` with a different angle of the same subject.",
    "image_analysis":  "Try `/orchestrate` to generate a new version of this scene, or `/audit` for a deep quality critique.",
}

def get_next_step(goal_type: str) -> str:
    return _NEXT_STEPS.get(goal_type, "Try `/orchestrate [your creative prompt]` to generate a new agentic workflow.")


# ─── Master Orchestrator ─────────────────────────────────────────────────────

def orchestrate(
    raw_input: str,
    caption: str = "",
    objects: list = None,
    text: str = "",
    confidences: list = None,
    wiki_data: list = None,
) -> dict:
    """
    Full orchestration pipeline. Called by Flask routes.

    Returns:
        {
          "mode":        str,
          "plan":        { goal_type, sub_tasks, constraints, payload },
          "models_used": [ { name, role, icon, key }, ... ],
          "critic":      { score, breakdown, verdict, notes, refinements },
          "next_step":   str,
          "analysis":    { caption, objects, text, wiki_data }
        }
    """
    if objects is None:
        objects = []
    if wiki_data is None:
        wiki_data = []

    # Parse command
    parsed   = parse_command(raw_input)
    mode     = parsed["mode"]
    payload  = parsed["payload"]
    constraints = parsed["constraints"]

    # Phase 1: Intent decomposition
    plan = decompose_intent(mode, payload, constraints)

    # Phase 2: Model selection
    models_used = select_models(plan["goal_type"], constraints)

    # Phase 3: Critic loop
    critic = run_critic_loop(caption, objects, text, confidences)

    # Next step suggestion
    next_step = get_next_step(plan["goal_type"])

    return {
        "mode":        mode,
        "plan":        plan,
        "models_used": models_used,
        "critic":      critic,
        "next_step":   next_step,
        "analysis": {
            "caption":   caption,
            "objects":   objects,
            "text":      text,
            "wiki_data": wiki_data,
        }
    }
