"""
Feature extraction module for image processing tasks.
How to use this code:
1. from feature_extractor import extract_features
2. features = extract_features(image)
3. print(features) = {'hair_color': 'brown', 'cap_color': 'none', 'top_style': 't-shirt'}
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image
import numpy as np
import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration

# Set the device to GPU if available, otherwise use CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "Salesforce/blip2-flan-t5-xl"

prompts = {
    "hair_color": "What is the hair color? Answer with one word.",
    "cap_color": "If the person wears a hat or cap, what color is it? If none, answer 'none'.",
    "top_style": "Describe the style of the top (e.g., t-shirt, hoodie, jacket) in one word.",
}

# Define valid choices for each feature
hair_choices = {'black', 'brown', 'blonde', 'red', 'gray', 'white'}
cap_choices = {'black', 'white', 'red', 'blue', 'green', 'yellow', 'none'}
top_choices = {'t-shirt', 'hoodie', 'jacket', 'sweater', 'shirt', 'none'}

# Load the BLIP-2 processor and model
print("Loading BLIP-2 model...")
processor = Blip2Processor.from_pretrained(model_name)
model = Blip2ForConditionalGeneration.from_pretrained(model_name)
model = model.to(device)
model.eval()
print("Model loaded successfully!")

def ask(image: Image.Image, prompt: str) -> str:
    """
    Ask a question about the image using the BLIP-2 model.
    """
    inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)
    
    # Generate the answer using the model
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=10, do_sample=False)
    
    # Decode the output to get the answer
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # Clean up the response (remove the original prompt if it's included)
    answer = generated_text.replace(prompt, "").strip().lower()
    
    return answer

def extract_features(image: Image.Image) -> Dict[str, str]:
    """
    Extract features from the image using the BLIP-2 model.
    :param image: PIL Image object
    :return: Dictionary with extracted features
    """
    features = {}
    
    # Hair color
    hair_color = ask(image, prompts["hair_color"])
    # Find best match in hair_choices
    hair_words = hair_color.split()
    found_hair = None
    for word in hair_words:
        if word in hair_choices:
            found_hair = word
            break
    features["hair_color"] = found_hair if found_hair else "unknown"

    # Cap color
    cap_color = ask(image, prompts["cap_color"])
    cap_words = cap_color.split()
    found_cap = None
    for word in cap_words:
        if word in cap_choices:
            found_cap = word
            break
    features["cap_color"] = found_cap if found_cap else "none"

    # Top style
    top_style = ask(image, prompts["top_style"])
    top_words = top_style.split()
    found_top = None
    for word in top_words:
        if word in top_choices:
            found_top = word
            break
    # Handle common variations
    if not found_top:
        if "tshirt" in top_style or "t shirt" in top_style:
            found_top = "t-shirt"
        elif "sweatshirt" in top_style:
            found_top = "sweater"
    
    features["top_style"] = found_top if found_top else "unknown"

    return features

if __name__ == "__main__":
    # Test with a sample image
    try:
        image_path = "test_image.jpg"  # Replace with the actual image path
        if Path(image_path).exists():
            image = Image.open(image_path)
            features = extract_features(image)
            print("Extracted features:", features)
        else:
            print(f"Test image not found at {image_path}")
    except Exception as e:
        print(f"Error during testing: {e}")