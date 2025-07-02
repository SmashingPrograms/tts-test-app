from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import io
import subprocess
import tempfile
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Real-time TTS API", version="1.0.0")

print("🔥🔥🔥 FASTAPI APP CREATED")

# Add middleware to handle OPTIONS requests before they hit route validation
@app.middleware("http")
async def cors_handler(request: Request, call_next):
    print(f"🔥🔥🔥 MIDDLEWARE HIT: {request.method} {request.url.path}")
    print(f"🔥🔥🔥 CLIENT IP: {request.client}")
    print(f"🔥🔥🔥 ALL HEADERS: {list(request.headers.items())}")
    
    if request.method == "OPTIONS":
        print("🚨🚨🚨 OPTIONS REQUEST DETECTED IN MIDDLEWARE!")
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        print("✅✅✅ RETURNING OPTIONS RESPONSE FROM MIDDLEWARE")
        return response
    
    print("➡️➡️➡️ NOT OPTIONS, CALLING NEXT")
    response = await call_next(request)
    print(f"⬅️⬅️⬅️ GOT RESPONSE: {response.status_code}")
    
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

print("🔥🔥🔥 CORS MIDDLEWARE ADDED")

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    speed: float = 1.0

print("🔥🔥🔥 MODELS DEFINED")

class SimpleTTSEngine:
    def __init__(self):
        self.engine_type = self._detect_available_engine()
        logger.info(f"Using TTS engine: {self.engine_type}")
    
    def _detect_available_engine(self):
        """Detect which open-source TTS engine is available on this system"""
        
        # Check for espeak-ng (preferred open-source TTS)
        try:
            result = subprocess.run(["espeak-ng", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return "espeak-ng"
        except FileNotFoundError:
            pass
        
        # Check for espeak (older version)
        try:
            result = subprocess.run(["espeak", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return "espeak"
        except FileNotFoundError:
            pass
        
        # Check for Festival (another open-source TTS)
        try:
            result = subprocess.run(["festival", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return "festival"
        except FileNotFoundError:
            pass
        
        return "none"
    
    def generate_speech(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        """Generate speech using system TTS"""
        
        print(f"🔧 TTS ENGINE: generate_speech called")
        print(f"🔧 TTS ENGINE: text='{text[:30]}...', voice={voice}, speed={speed}")
        print(f"🔧 TTS ENGINE: engine_type={self.engine_type}")
        
        if self.engine_type == "none":
            print("💥 TTS ENGINE: No engine available!")
            raise HTTPException(status_code=500, detail="No TTS engine available on this system")
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
        
        print(f"📁 TTS ENGINE: Created temp file: {temp_path}")
        
        try:
            if self.engine_type in ["espeak", "espeak-ng"]:
                print("🔊 TTS ENGINE: Using espeak engine")
                self._generate_espeak(text, temp_path, speed)
            elif self.engine_type == "festival":
                print("🔊 TTS ENGINE: Using festival engine")
                self._generate_festival(text, temp_path, speed)
            else:
                print("💥 TTS ENGINE: Unknown engine type!")
                raise Exception("No open-source TTS engine available")
            
            print("📖 TTS ENGINE: Reading generated audio file...")
            # Read the generated audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            print(f"✅ TTS ENGINE: Successfully read {len(audio_data)} bytes")
            return audio_data
            
        except Exception as e:
            print(f"💥 TTS ENGINE: Exception in generate_speech: {e}")
            logger.error(f"TTS generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                print(f"🗑️ TTS ENGINE: Cleaning up temp file: {temp_path}")
                os.unlink(temp_path)
    
    def _generate_espeak(self, text: str, output_path: str, speed: float):
        """Generate speech using espeak/espeak-ng (open-source)"""
        speed_wpm = int(160 * speed)  # espeak speed in words per minute
        
        print(f"🗣️ ESPEAK: Starting generation")
        print(f"🗣️ ESPEAK: engine={self.engine_type}, speed_wpm={speed_wpm}")
        print(f"🗣️ ESPEAK: output_path={output_path}")
        
        cmd = [
            self.engine_type,
            "-s", str(speed_wpm),
            "-w", output_path,
            text
        ]
        
        print(f"🗣️ ESPEAK: Running command: {' '.join(cmd[:4])} [text...]")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"🗣️ ESPEAK: Command finished with return code: {result.returncode}")
        if result.stdout:
            print(f"🗣️ ESPEAK: stdout: {result.stdout}")
        if result.stderr:
            print(f"🗣️ ESPEAK: stderr: {result.stderr}")
        
        if result.returncode != 0:
            print(f"💥 ESPEAK: Command failed!")
            raise Exception(f"espeak failed: {result.stderr}")
        
        print(f"✅ ESPEAK: Generation completed successfully")
    
    def _generate_festival(self, text: str, output_path: str, speed: float):
        """Generate speech using Festival (open-source)"""
        
        # Create temporary text file for Festival
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as text_file:
            text_file.write(text)
            text_file_path = text_file.name
        
        try:
            # Festival command to generate speech
            cmd = [
                "festival",
                "--tts",
                text_file_path
            ]
            
            # Festival outputs to stdout, so we need to redirect
            with open(output_path, 'wb') as output_file:
                result = subprocess.run(cmd, stdout=output_file, stderr=subprocess.PIPE, text=False)
            
            if result.returncode != 0:
                raise Exception(f"Festival failed: {result.stderr.decode()}")
                
        finally:
            os.unlink(text_file_path)

# Initialize TTS engine
tts_engine = SimpleTTSEngine()

@app.get("/")
async def root():
    return {
        "message": "Simple TTS API is running", 
        "engine": tts_engine.engine_type,
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "engine": tts_engine.engine_type,
        "available": tts_engine.engine_type != "none"
    }

@app.post("/generate-speech")
async def generate_speech(request: TTSRequest):
    """Generate speech from text"""
    
    print(f"🎤 POST ENDPOINT: Received request")
    print(f"🎤 POST ENDPOINT: Text: '{request.text[:50]}...'")
    print(f"🎤 POST ENDPOINT: Voice: {request.voice}")
    print(f"🎤 POST ENDPOINT: Speed: {request.speed}")
    
    if not request.text.strip():
        print("❌ POST ENDPOINT: Text is empty!")
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(request.text) > 1000:
        print("❌ POST ENDPOINT: Text too long!")
        raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
    
    try:
        print(f"🔄 POST ENDPOINT: Starting TTS generation with engine: {tts_engine.engine_type}")
        logger.info(f"Generating speech: '{request.text[:50]}...' using {tts_engine.engine_type}")
        
        # Generate audio
        print("🎵 POST ENDPOINT: Calling tts_engine.generate_speech...")
        audio_data = tts_engine.generate_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )
        print(f"🎵 POST ENDPOINT: Got audio data, size: {len(audio_data)} bytes")
        
        # Return audio as streaming response
        print("📤 POST ENDPOINT: Creating streaming response...")
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Content-Length": str(len(audio_data))
            }
        )
        
    except Exception as e:
        print(f"💥 POST ENDPOINT: ERROR occurred: {e}")
        logger.error(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.options("/generate-speech")
async def options_generate_speech():
    """Handle CORS preflight requests"""
    return {"message": "OK"}

@app.get("/voices")
async def get_available_voices():
    """Get list of available voices"""
    
    if tts_engine.engine_type in ["espeak", "espeak-ng"]:
        voices = [
            {"id": "default", "name": "Default", "language": "en"},
            {"id": "en", "name": "English", "language": "en"},
            {"id": "en-us", "name": "US English", "language": "en"}
        ]
    elif tts_engine.engine_type == "festival":
        voices = [
            {"id": "default", "name": "Festival Default", "language": "en"}
        ]
    else:
        voices = [
            {"id": "none", "name": "No Engine Available", "language": "en"}
        ]
    
    return {"voices": voices, "engine": tts_engine.engine_type}

if __name__ == "__main__":
    import uvicorn
    
    print("🎤 Starting Open-Source TTS API...")
    print(f"Engine detected: {tts_engine.engine_type}")
    
    if tts_engine.engine_type == "none":
        print("\n❌ No open-source TTS engine found!")
        print("Install one of these:")
        print("  • espeak-ng: brew install espeak-ng")
        print("  • espeak: brew install espeak") 
        print("  • festival: brew install festival")
        print("\nServer will start but TTS won't work until you install an engine.")
    else:
        print("✅ Open-source TTS ready!")
    
    print("Server starting at http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)