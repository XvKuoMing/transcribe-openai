import asyncio
import io
import soundfile as sf
import numpy as np
import librosa
from tone import StreamingCTCPipeline, TextPhrase
from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    host: str = Field(default="0.0.0.0", description="Host to run the server on")
    port: int = Field(default=8000, description="Port to run the server on")

class TranscriptionResponse(BaseModel):
    text: str

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.tone_pipeline = StreamingCTCPipeline.from_hugging_face()
    yield

app = FastAPI(lifespan=lifespan)

TonePipelineDep = Annotated[StreamingCTCPipeline, Depends(lambda: app.state.tone_pipeline)]

def resample_to_8000hz(audio_bytes: bytes) -> np.ndarray:
    """Resample audio to exactly 8000 Hz sample rate and return as numpy array."""
    # Read audio from bytes
    audio_io = io.BytesIO(audio_bytes)
    data, sample_rate = sf.read(audio_io)
    
    # Convert to mono if stereo
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
    
    # Convert to float32 for resampling (librosa requires float)
    if data.dtype != np.float32:
        # If already normalized [-1.0, 1.0], keep as is
        # If integer format, normalize to [-1.0, 1.0]
        if np.issubdtype(data.dtype, np.integer):
            # Normalize integer audio to [-1.0, 1.0]
            max_val = np.iinfo(data.dtype).max
            data = data.astype(np.float32) / max_val
        else:
            data = data.astype(np.float32)
    
    # Resample to 8000 Hz if needed
    if sample_rate != 8000:
        data = librosa.resample(data, orig_sr=sample_rate, target_sr=8000)
    
    # Convert to int32 dtype with values in int16 range as expected by the pipeline
    # Scale from normalized [-1.0, 1.0] to int16 range [-32768, 32767], then convert to int32
    data = (data * 32767).astype(np.int32)
    
    return data

@app.post("/v1/audio/transcriptions")
async def transcribe(
    tone_pipeline: TonePipelineDep,
    file: UploadFile = File(...),
    model: str = Form("whisper-1"),
    language: Optional[str] = Form(None),
    response_format: Optional[str] = Form("json"),
):
    # Read audio file
    audio_bytes = await file.read()
    
    # Resample to 8000 Hz
    try:
        audio_8000hz = await asyncio.to_thread(resample_to_8000hz, audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Audio processing error: {str(e)}")
    
    # Transcribe
    try:
        transcriptions: list[TextPhrase] = await asyncio.to_thread(tone_pipeline.forward_offline, audio_8000hz)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    return TranscriptionResponse(text=". ".join([phrase.text for phrase in transcriptions]))

@app.get("/health")
@app.get("/")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)