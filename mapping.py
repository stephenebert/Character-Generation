# Mapping of feature names to their descriptions
"""
For example, the mapping could look like this:
# features["hair_color"] = hair_color
feature_descriptions = {
    "hair_color": "The color of the person's hair.",
    "cap_color": "The color of the person's cap or hat.",
    "top_style": "The style of the person's top clothing.",
}
"""
from pathlib import Path
from PIL import Image
from typing import Dict, Union
# Import the BLIP-2 model and processor (though not used in this function)
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from feature_extractor import ask

asset_root = Path('assets')
"""
assets/
├── base_body/
│   └── trainer_base.png
├── hair/
│   ├── brown.png
│   ├── black.png
│   └── none.png
├── cap/
│   ├── red.png
│   ├── blue.png
│   └── none.png
└── top/
    ├── t-shirt.png
    ├── hoodie.png
    └── none.png
"""
# Load the BLIP-2 processor and model
print("Loading BLIP-2 model...")

layer_map = {
    "base": asset_root / "base_body" / "trainer_base.png",
    "hair": asset_root / "hair" / "{hair_color}.png",      # e.g. brown.png
    "cap":  asset_root / "cap"  / "{cap_color}.png",       # red.png / none.png
    "top":  asset_root / "top"  / "{top_style}.png",       # t-shirt.png
}

def compose_sprite(features: dict, out_path: Union[str, Path]) -> Path:
    """
    Function to compose a sprite image based on the provided features.
    """
    # Initialize the base image
    base_path = layer_map["base"]
    if not base_path.exists():
        raise FileNotFoundError(f"Base image not found at {base_path}")
    
    base = Image.open(base_path).convert("RGBA")
    
    # Apply layers in order
    for layer_key in ('hair', 'cap', 'top'):
        template = layer_map[layer_key]
        # Check if the template is a directory
        layer_path = Path(str(template).format(**features))
        
        # Skip if it's 'none.png' or if the file doesn't exist
        if layer_path.name == 'none.png' or not layer_path.exists():
            print(f"Skipping layer {layer_key}: {layer_path} not found or is 'none'")
            continue
        
        try:
            # Open the layer image and apply it to the base
            layer = Image.open(layer_path).convert("RGBA")
            base.alpha_composite(layer)
            print(f"Applied layer {layer_key}: {layer_path}")
        except Exception as e:
            print(f"Error applying layer {layer_key} from {layer_path}: {e}")
            continue
    
    # Ensure output directory exists
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the composed image
    base.save(out_path)
    print(f"Sprite saved to: {out_path}")
    return out_path

if __name__ == "__main__":
    # Test the sprite composition
    test_features = {
        "hair_color": "brown",
        "cap_color": "none",
        "top_style": "t-shirt"
    }
    
    try:
        output_path = compose_sprite(test_features, "output_sprite.png")
        print(f"Sprite composed successfully: {output_path}")
    except Exception as e:
        print(f"Error composing sprite: {e}")
