

import torch
import whisper
import time

print("CUDA available:", torch.cuda.is_available())

model = whisper.load_model("base", device="cuda")
print("Model loaded on:", next(model.parameters()).device)

start = time.time()
result = model.transcribe("data/processed_audio.wav")
print(f"Transcription took {time.time() - start:.2f}s")
print(result["text"])




















