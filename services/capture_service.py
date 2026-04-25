from functools import lru_cache

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


@lru_cache(maxsize=1)
def _get_blip():
    # Lazy-load to avoid heavy imports/allocations at Flask startup.
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model


def generate_caption(image_path):
    processor, model = _get_blip()

    image = Image.open(image_path)
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)
