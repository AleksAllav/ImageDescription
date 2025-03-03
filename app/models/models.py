from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
)
import torch


class Model:
    def __init__(self, name: str):
        self.name = name
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    async def generate_description(self, image_bytes: bytes, length: int):
        inputs = self.processor(images=image_bytes, return_tensors="pt")
        with torch.no_grad():
            output = self.model.generate(**inputs, max_length=length)
        return self.processor.decode(output[0], skip_special_tokens=True)


available_models = {
    "blip": Model("blip"),
    # Можно добавить другие модели
}
