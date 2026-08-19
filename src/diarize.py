import torch
import os

# Compatibility shim: pyannote.audio 3.4.0 internally calls
# hf_hub_download(use_auth_token=...) in multiple places (pipeline.py, model.py, etc),
# but huggingface_hub 1.x removed that kwarg in favor of token=. Patch the function at
# its source, BEFORE importing pyannote.audio, so every submodule that does
# "from huggingface_hub import hf_hub_download" during its own import picks up the
# patched version. We don't downgrade huggingface_hub since the fine-tuning stack
# (transformers/peft/trl) needs the modern API.
import huggingface_hub

_orig_hf_hub_download = huggingface_hub.hf_hub_download

def _patched_hf_hub_download(*args, **kwargs):
    if "use_auth_token" in kwargs:
        kwargs["token"] = kwargs.pop("use_auth_token")
    return _orig_hf_hub_download(*args, **kwargs)

huggingface_hub.hf_hub_download = _patched_hf_hub_download
huggingface_hub.file_download.hf_hub_download = _patched_hf_hub_download

from pyannote.audio import Pipeline  # import AFTER the patch, order matters


def diarize_audio(audio_path: str) -> list:
    """
    Step 5: Speaker Diarization
    Identifies "who spoke when" in an audio file using pyannote.audio.
    Returns a list of (start_sec, end_sec, speaker_label) tuples.
    """
    hf_token = os.environ["HF_TOKEN"]
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    pipeline.to(torch.device("cuda"))
    diarization = pipeline(audio_path, min_speakers=1, max_speakers=8)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append((turn.start, turn.end, speaker))
    return segments


if __name__ == "__main__":
    results = diarize_audio("data/processed_audio.wav")
    for start, end, speaker in results:
        print(f"start={start:.1f}s stop={end:.1f}s speaker={speaker}")
