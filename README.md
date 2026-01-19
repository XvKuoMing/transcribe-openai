# T-one Transcription API

An OpenAI-compatible transcription API service built with FastAPI and the T-one speech recognition model. This service automatically processes audio files to ensure they meet the required specifications (8000 Hz sample rate) and returns transcriptions in OpenAI's standard format.

## Features

- **OpenAI-compatible API**: Uses the `/v1/audio/transcriptions` endpoint format
- **Automatic audio processing**: Automatically resamples audio to 8000 Hz sample rate
- **Format conversion**: Handles various audio formats and converts them to the required format
- **T-one model**: Powered by the T-one speech recognition pipeline

## Requirements

- Python >= 3.11
- See `pyproject.toml` for full dependency list

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tone
```

2. Install dependencies:
```bash
pip install -e .
```

## Configuration

The service can be configured via environment variables or a `.env` file:

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)

Example `.env` file:
```
HOST=0.0.0.0
PORT=8000
```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://0.0.0.0:8000` by default.

### API Endpoints

#### POST `/v1/audio/transcriptions`

Transcribe an audio file. This endpoint is compatible with OpenAI's transcription API format.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Parameters:
  - `file` (required): Audio file to transcribe
  - `model` (optional): Model name (default: `whisper-1`)
  - `language` (optional): Language code
  - `response_format` (optional): Response format (default: `json`)

**Response:**
```json
{
  "text": "Transcribed text here"
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/v1/audio/transcriptions" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav" \
  -F "model=whisper-1"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/v1/audio/transcriptions"
files = {"file": open("audio.wav", "rb")}
data = {"model": "whisper-1"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

#### GET `/health` or `/`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Audio Processing

The service automatically processes audio files to meet the T-one model requirements:

1. **Sample Rate**: Audio is automatically resampled to exactly 8000 Hz
2. **Channels**: Stereo audio is converted to mono
3. **Format**: Audio is converted to `np.int32` dtype with values in the int16 range [-32768, 32767]

Supported audio formats include WAV, MP3, FLAC, and other formats supported by `soundfile`.

## Development

The service uses:
- **FastAPI**: Web framework
- **T-one**: Speech recognition model from [voicekit-team/T-one](https://github.com/voicekit-team/T-one)
- **librosa**: Audio resampling
- **soundfile**: Audio file I/O

## License

[Add your license information here]

