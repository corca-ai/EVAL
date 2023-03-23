import torch
from PIL import Image
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
)

from core.prompts.file import IMAGE_PROMPT

from .base import BaseHandler


class ImageCaptioning(BaseHandler):
    def __init__(self, device):
        print("Initializing ImageCaptioning to %s" % device)
        self.device = device
        self.torch_dtype = torch.float16 if "cuda" in device else torch.float32
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base", torch_dtype=self.torch_dtype
        ).to(self.device)

    def handle(self, filename: str):
        img = Image.open(filename)
        width, height = img.size
        ratio = min(512 / width, 512 / height)
        width_new, height_new = (round(width * ratio), round(height * ratio))
        img = img.resize((width_new, height_new))
        img = img.convert("RGB")
        img.save(filename, "PNG")
        print(f"Resize image form {width}x{height} to {width_new}x{height_new}")

        inputs = self.processor(Image.open(filename), return_tensors="pt").to(
            self.device, self.torch_dtype
        )
        out = self.model.generate(**inputs)
        description = self.processor.decode(out[0], skip_special_tokens=True)
        print(
            f"\nProcessed ImageCaptioning, Input Image: {filename}, Output Text: {description}"
        )

        return IMAGE_PROMPT.format(filename=filename, description=description)
