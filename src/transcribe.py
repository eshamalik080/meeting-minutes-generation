import torch
import whisper

_model = None


def transcribe_audio(audio_path: str, model_name: str = "small") -> dict:
    """
    Step 4: Speech-to-Text (ASR)
    Caches the loaded model so it's not reloaded on every call.
    """
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = whisper.load_model(model_name, device=device)
    return _model.transcribe(audio_path, word_timestamps=True)


if __name__ == "__main__":
    print("CUDA available:", torch.cuda.is_available())
    result = transcribe_audio("data/sample_audio.flac")
    print(result["text"])
