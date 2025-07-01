# PixelTrainer

Generate a retro 32 x 32 px "trainer sprite" from a picture.

This Minimum Viable Product (MVP) combines a vision model (BLIP-2) that extracts coarse appearance features with a static pixel-art library layered together on the server-side.

The REST API lets you:
1. **/predict** – upload an image → get JSON attributes  
2. **/sprite**  – upload an image → get a composed PNG sprite


## Project Structure
```

├── api.py                    # FastAPI service (predict + sprite endpoints)
├── feature_extractor.py     # BLIP-2 → JSON mapping
├── sprite_composer_fixed.py # PNG layering logic (updated from mapping.py)
├── assets/                   # Static pixel art (see below)
│   ├── base_body/
│   ├── hair/
│   ├── cap/
│   └── top/
└── README.md
```

### Asset Layout
Each subfolder contains transparent 32 x 32 PNGs named after the *categorical value* they represent:

```
assets/
├── base_body/
│   └── trainer_base.png     # base body with transparent BG
├── hair/
│   ├── black.png
│   ├── brown.png
│   ├── blonde.png
│   ├── red.png
│   ├── gray.png
│   ├── white.png
│   └── none.png
├── cap/
│   ├── red.png
│   ├── blue.png
│   ├── black.png
│   ├── white.png
│   ├── green.png
│   ├── yellow.png
│   └── none.png
└── top/
    ├── t-shirt.png
    ├── hoodie.png
    ├── jacket.png
    ├── sweater.png
    ├── shirt.png
    └── none.png
```

All files share the **same canvas size and anchor (0, 0)** so the compositor can simply alpha-blend them in order: `base to hair to cap to top`.

---

## API Endpoints

| Method | Route      | Payload       | Returns                                    |
|--------|------------|---------------|--------------------------------------------|
| GET    | `/`        | -             | Welcome message                            |
| GET    | `/health`  | -             | Health check status                        |
| POST   | `/predict` | file (image)  | JSON `{ hair_color, cap_color, top_style }` |
| POST   | `/sprite`  | file (image)  | image/png trainer sprite                   |

### Example Use

```bash
# Get feature predictions
curl -X POST -F "file=@selfie.jpg" http://127.0.0.1:8000/predict

# Generate sprite
curl -X POST -F "file=@selfie.jpg" http://127.0.0.1:8000/sprite --output trainer.png
```

---

## How It Works

1. **BLIP-2** (`feature_extractor.py`) answers structured prompts such as "What is the hair color? (one word)" -> `brown`.

2. **Feature Mapping**: The answers are snapped to a fixed vocabulary:
   - **Hair colors**: black, brown, blonde, red, gray, white
   - **Cap colors**: black, white, red, blue, green, yellow, none  
   - **Top styles**: t-shirt, hoodie, jacket, sweater, shirt, none

3. **Sprite Composition** (`sprite_composer_fixed.py`) finds the matching PNG layer in `assets/` and alpha-composites them with Pillow.

4. **FastAPI** (`api.py`) exposes the pipeline via REST endpoints with proper error handling.

---

## Roadmap

| Stage | Goal |
|-------|------|
| v0 (this repo) | MVP demo with hard-coded BLIP-2 prompts and 3-layer sprite |
| v1 | More attributes (skin tone, accessories), 8-frame walk cycle |
| v2 | Client-side canvas editor + Palette swap tool |
| v3 | Diffusion-based asset generation for unlimited variety |

---

## Contributing

Fork to feature branch to PR.

- Run `black`, `isort`, and `ruff` before pushing
- Keep assets under 1 MB; sprites should remain 32 × 32
- Add tests for new feature extraction prompts
- Update asset vocabulary when adding new categories
