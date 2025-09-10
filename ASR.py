import whisper
import warnings
import librosa
import io


async def transcript(audio_bytes):
    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
    model = whisper.load_model("small", device="cpu")

    audio_bytes.seek(0)
    audio, sr = librosa.load(io.BytesIO(audio_bytes.read()), sr=16000, mono=True)
    result = model.transcribe(audio)
    if result['text'] == '':
        result['text'] = None
    return result['text']
