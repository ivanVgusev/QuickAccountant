from faster_whisper import WhisperModel
import warnings
import librosa
import io
from huggingface_hub import login
from configuration import ASR_MODEL, CPU_THREADS, \
    HUGGING_FACE_TOKEN


login(token=HUGGING_FACE_TOKEN)
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
model = WhisperModel(
    ASR_MODEL, 
    device="cpu",
    compute_type="int8",
    cpu_threads=int(CPU_THREADS))


async def transcript(audio_bytes, user_language):
    audio_bytes.seek(0)
    audio, _ = librosa.load(io.BytesIO(audio_bytes.read()), sr=16000, mono=True)
    segments, info = model.transcribe(audio, language=user_language)
    result = " ".join([segment.text for segment in segments])
    return result
