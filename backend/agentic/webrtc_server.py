
import asyncio
import json
import logging
import os
import tempfile
import uuid
from typing import Dict, List, Optional
import time

import numpy as np
import redis.asyncio as redis
import scipy.io.wavfile as wav
import scipy.signal
import soundfile as sf
from fractions import Fraction
from aiortc import (
    MediaStreamTrack,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from langchain_openai import ChatOpenAI
from openai import OpenAI
from prompt import system_prompt

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebRTC-Agent")

# Load Env
load_dotenv()

# --- Configurations ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAID_KEY = os.getenv("paid")

if not OPENAI_API_KEY or not PAID_KEY:
    raise ValueError("Missing API Keys in .env")

# --- Clients ---
openai_client = OpenAI(api_key=OPENAI_API_KEY)
redis_client = redis.from_url(REDIS_URL)

llm = ChatOpenAI(
    api_key=PAID_KEY,
    base_url="https://openrouter.ai/api/v1",
    model="openai/gpt-oss-20b",
)

# --- FastAPI App ---
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("WebRTC Server starting")
    yield
    # Shutdown
    logger.info("WebRTC Server shutting down")
    coros = [pc.close() for pc in pcs]
    if coros:
        await asyncio.gather(*coros)
    if redis_client:
        await redis_client.close()

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="Talk2Book WebRTC Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static dir exists
os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(os.path.dirname(__file__), "static/index.html")) as f:
        return f.read()

# --- Global State ---
pcs = set()

# --- Audio Constants ---
SAMPLE_RATE = 24000  # OpenAI TTS / Opus usually 24k or 48k. Standardizing.
CHANNELS = 1
FRAME_SIZE = 960  # 20ms at 48kHz, or adjusted for 24kHz. 
# aiortc usually expects 48kHz for Opus. Let's stick to 48000 for transport.
TRANSPORT_SAMPLE_RATE = 48000
PTIME = 0.02 # 20ms

class AudioQueueTrack(MediaStreamTrack):
    """
    A MediaStreamTrack that yields audio frames from a queue.
    If queue is empty, yields silence.
    """
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.q = asyncio.Queue()
        self.time = 0
        self.samplerate = TRANSPORT_SAMPLE_RATE
        self.samples_per_frame = int(self.samplerate * PTIME) # 960

    async def recv(self):
        # Handle timestamp
        pts, time_base = self.time, Fraction(1, self.samplerate)
        self.time += self.samples_per_frame

        
        try:
            # Try to get data from queue (non-blocking or short timeout if you wanted)
            # But here we want a continuous stream, so if empty we send silence
            if self.q.empty():
                data = np.zeros(self.samples_per_frame, dtype=np.int16)
            else:
                data = await self.q.get()
                # Ensure data length matches frame size
                if len(data) < self.samples_per_frame:
                    padding = np.zeros(self.samples_per_frame - len(data), dtype=np.int16)
                    data = np.concatenate((data, padding))
                elif len(data) > self.samples_per_frame:
                    # If this happens, we might lose audio, ideally we should chunk before putting to queue
                    data = data[:self.samples_per_frame]
        except Exception as e:
            logger.error(f"Error in AudioQueueTrack: {e}")
            data = np.zeros(self.samples_per_frame, dtype=np.int16)

        # Convert to aiortc Frame (av.AudioFrame)
        # We construct it manually since aiortc expects it
        from av import AudioFrame
        
        # Create AudioFrame from numpy array
        # Provide the data as bytes
        frame = AudioFrame(format='s16', layout='mono', samples=self.samples_per_frame)
        frame.planes[0].update(data.tobytes())
        frame.sample_rate = self.samplerate
        frame.pts = pts
        frame.time_base = time_base
        
        return frame

    def add_audio_data(self, data: np.ndarray):
        """
        Add raw audio data (numpy array) to the queue. 
        Data should be 48kHz s16 mono.
        Splits larger arrays into proper frame sizes.
        """
        offset = 0
        while offset < len(data):
            chunk = data[offset : offset + self.samples_per_frame]
            self.q.put_nowait(chunk)
            offset += self.samples_per_frame

class AgentOrchestrator:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.chat_history_key = f"chat:{session_id}"
        self.track = AudioQueueTrack()
        
        # Processing state
        self.buffer = [] # Audio buffer for VAD
        self.is_processing = False
        self.mcp_client = None
        self.agent = None

        # VAD settings
        self.vad_threshold = 500  # Adjust based on mic sensitivity
        self.silence_frames_threshold = 50 # ~1 second of silence (20ms * 50)
        self.silence_counter = 0

    async def initialize(self):
        # Initialize MCP and Agent
        connect = StreamableHttpConnection(transport="streamable_http", url="http://localhost:8000/mcp")
        self.mcp_client = MultiServerMCPClient(connections={"Talk2Book backend": connect})
        try:
            tools = await self.mcp_client.get_tools(server_name="Talk2Book backend")
        except Exception:
            logger.warn("Could not connect to MCP server, using empty tools")
            tools = []

        self.agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
        
        # Load history from Redis
        history_json = await redis_client.get(self.chat_history_key)
        if history_json:
            data = json.loads(history_json)
            # Reconstruct Message objects (simplified)
            self.chat_history = []
            for msg in data:
                if msg["type"] == "human":
                    self.chat_history.append(HumanMessage(msg["content"]))
                else:
                    self.chat_history.append(AIMessage(msg["content"]))
        else:
            self.chat_history = []
            
        logger.info(f"Agent initialized for session {self.session_id}")

    async def process_audio_frame(self, frame):
        """
        Receive audio frame from user, perform VAD, and trigger pipeline.
        """
        # Convert frame to numpy
        data = frame.to_ndarray().flatten() # s16
        
        # Check energy
        # frame.to_ndarray returns int16
        amplitude = np.max(np.abs(data))
        
        if amplitude > self.vad_threshold:
            self.silence_counter = 0
            self.buffer.append(data)
        else:
            if len(self.buffer) > 0:
                self.silence_counter += 1
            
        # Trigger processing if silence persisted and we have data
        if self.silence_counter > self.silence_frames_threshold and len(self.buffer) > 0:
            if not self.is_processing:
                await self.trigger_agent_pipeline()
            
            # Reset
            self.buffer = []
            self.silence_counter = 0

    async def trigger_agent_pipeline(self):
        self.is_processing = True
        logger.info("Processing User Audio...")
        
        try:
            # 1. Save buffer to wav
            full_audio = np.concatenate(self.buffer)
            # Standardize to 48kHz since that's what we received
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav.write(tmp.name, TRANSPORT_SAMPLE_RATE, full_audio)
                tmp_path = tmp.name

            # 2. Whisper
            with open(tmp_path, "rb") as f:
                transcription = await asyncio.to_thread(
                    openai_client.audio.transcriptions.create,
                    model="gpt-4o-transcribe",
                    file=f,
                    language="vi"
                )
            
            os.remove(tmp_path)
            text = transcription.text.strip()
            
            if not text:
                logger.info("Empty transcription.")
                self.is_processing = False
                return

            logger.info(f"User: {text}")
            
            # 3. Update History & Redis
            self.chat_history.append(HumanMessage(text))
            await self._save_history()

            # 4. Agent Stream
            full_response = ""
            current_sentence = ""
            
            # Streaming + TTS
            async for token, _ in self.agent.astream({"messages": self.chat_history}, stream_mode="messages"):
                content = token.content
                if isinstance(content, str) and content:
                    full_response += content
                    current_sentence += content
                    
                    # Heuristic for sentence break
                    if any(c in current_sentence for c in ".!?\n"):
                        logger.info(f"Speaking: {current_sentence}")
                        await self._speak_text(current_sentence)
                        current_sentence = ""
            
            # Flush remaining
            if current_sentence.strip():
                await self._speak_text(current_sentence)

            logger.info(f"AI: {full_response}")
            self.chat_history.append(AIMessage(full_response))
            await self._save_history()
            
        except Exception as e:
            logger.error(f"Pipeline Error: {e}")
        finally:
            self.is_processing = False

    async def _speak_text(self, text):
        """Convert text to speech and push to track queue."""
        clean_text = text.replace("*", "").strip()
        if not clean_text: return
        
        try:
            response = await asyncio.to_thread(
                openai_client.audio.speech.create,
                model="tts-1",
                voice="alloy",
                input=clean_text,
                response_format="pcm" # Request Raw PCM
            )
            
            # Raw PCM from OpenAI is 24kHz s16le usually? Or we need to check documentation.
            # "pcm" format gives 24kHz signed 16-bit PCM.
            audio_data = b""
            for chunk in response.iter_bytes():
                audio_data += chunk
                
            # Convert bytes to numpy
            # 24k -> 48k resampling might be needed for aiortc if the transport requires 48k.
            # aiortc usually negotiates. But let's check.
            # If we just push 24k data to 48k stream, it will sound fast/high pitched or slow.
            
            # Let's read it properly
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            # Resample 24000 to 48000
            # Simple way: Repeat samples (Poor quality) or linear interp. 
            # Better: use scipy.signal.resample
            audio_48k = scipy.signal.resample(audio_np, len(audio_np) * 2).astype(np.int16)
            
            # Push to track
            self.track.add_audio_data(audio_48k)
            
        except Exception as e:
            logger.error(f"TTS Error: {e}")

    async def _save_history(self):
        # Serialize history
        serializable = []
        for msg in self.chat_history:
            if isinstance(msg, HumanMessage):
                serializable.append({"type": "human", "content": msg.content})
            else:
                serializable.append({"type": "ai", "content": msg.content})
        
        # Keep last 20
        if len(serializable) > 20:
            serializable = serializable[-20:]
            
        await redis_client.set(self.chat_history_key, json.dumps(serializable))

@app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    session_id = params.get("session_id", str(uuid.uuid4()))

    pc = RTCPeerConnection()
    pcs.add(pc)

    logger.info(f"Created PC for session: {session_id}")

    # Create Agent Orchestrator
    orchestrator = AgentOrchestrator(session_id)
    await orchestrator.initialize()
    
    # Add the AudioQueueTrack (AI Voice) to PC
    pc.addTrack(orchestrator.track)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            pass

    @pc.on("track")
    def on_track(track):
        logger.info(f"Track received: {track.kind}")
        if track.kind == "audio":
            # Consuming audio in background
            async def consume():
                while True:
                    try:
                        frame = await track.recv()
                        await orchestrator.process_audio_frame(frame)
                    except Exception:
                        break
            asyncio.ensure_future(consume())
        
        @track.on("ended")
        async def on_ended():
            logger.info("Track ended")

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info(f"Connection state: {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            await pc.close()
            pcs.discard(pc)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
        "session_id": session_id
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
