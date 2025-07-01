import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from feature_extractor import extract_features
from mapping import compose_sprite
# FastAPI application instance
app = FastAPI()


@app.post("/predict")
# Predict endpoint to extract features from an uploaded image file
async def predict(file: UploadFile = File(...)):
    img_bytes = await file.read()
    feats = extract_features(io.BytesIO(img_bytes))
    return JSONResponse(feats)


@app.post("/sprite")
# Sprite endpoint to create a sprite image from extracted features
async def sprite(file: UploadFile = File(...)):
    img_bytes = await file.read()
    feats = extract_features(io.BytesIO(img_bytes))
    sprite_path = compose_sprite(feats, "out.png")
    return StreamingResponse(open(sprite_path, "rb"), media_type="image/png")
