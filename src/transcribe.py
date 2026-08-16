import whisper


def transcribe_audio(audio_path: str, model_size: str = "base") -> dict:
    """
    Step 4: Speech-to-Text (ASR)
    Returns Whisper's result dict (text + segments with timestamps).
    """
    model = whisper.load_model(model_size, device="cuda")
    result = model.transcribe(audio_path, word_timestamps=True)
    return result


if __name__ == "__main__":
    import torch
    print("CUDA available:", torch.cuda.is_available())
    result = transcribe_audio("data/sample_audio.flac")
    print(result["text"])
















