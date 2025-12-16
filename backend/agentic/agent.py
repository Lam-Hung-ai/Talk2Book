
import asyncio
import os
import queue
import re
import sys
import tempfile
import threading
from os import getenv

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import StreamableHttpConnection
from langchain_openai import ChatOpenAI
from openai import OpenAI

load_dotenv()

key: str | None = getenv("paid")
openai_key: str | None = getenv("OPENAI_API_KEY")

if not key or not openai_key:
    raise Exception("Thiếu API Key. Vui lòng kiểm tra file .env")

llm = ChatOpenAI(
    api_key=key, # type: ignore
    base_url="https://openrouter.ai/api/v1",
    model="google/gemini-2.5-flash"
)

openai_client = OpenAI(api_key=openai_key)

class TextToSpeechStreamer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.sentence_buffer = ""
        self.stop_signal = False
        self.play_thread = threading.Thread(target=self._playback_worker)
        self.play_thread.daemon = True
        self.play_thread.start()

    def add_text(self, text):
        if text:
            text = text.replace("*", "").replace("#", "")

        self.sentence_buffer += text
        if re.search(r'[.!?\n]', text):
            sentence = self.sentence_buffer.strip()
            if sentence:
                self._process_sentence(sentence)
            self.sentence_buffer = ""

    def flush(self):
        if self.sentence_buffer.strip():
            self._process_sentence(self.sentence_buffer.strip())
            self.sentence_buffer = ""

    def _process_sentence(self, text):
        clean_text = re.sub(r'\*.*?\*', '', text).strip()
        if not clean_text: return

        try:
            response = openai_client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=clean_text,
                response_format="opus"
            )
            with tempfile.NamedTemporaryFile(delete=False, suffix=".opus") as tmp:
                for chunk in response.iter_bytes():
                    tmp.write(chunk)
                tmp_path = tmp.name
            self.audio_queue.put(tmp_path)
        except Exception as e:
            print(f"\n[Lỗi TTS]: {e}")

    def _playback_worker(self):
        while not self.stop_signal:
            try:
                audio_path = self.audio_queue.get(timeout=1)
                data, fs = sf.read(audio_path)
                sd.play(data, fs)
                sd.wait()
                os.remove(audio_path)
                self.audio_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Lỗi Playback]: {e}")

def record_until_enter(fs=44100):
    print("🎙️  Đang khởi tạo microphone...")
    audio_frames = []

    def callback(indata, frames, time, status):
        if status:
            print(f"Status Audio: {status}", file=sys.stderr)
        audio_frames.append(indata.copy())

    try:
        device_info = sd.query_devices(kind='input')
        print(f"   [Debug] Đang dùng thiết bị: {device_info['name']}")
    except:
        pass

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        print("\n" + "="*40)
        print("   🔴 ĐANG GHI ÂM... (Nhấn Enter để GỬI)   ")
        print("="*40 + "\n")
        input()
        print("⏹️  Đã dừng ghi âm.")

    if not audio_frames:
        print("❌ [Lỗi] Không thu được dữ liệu âm thanh nào (Frame rỗng).")
        return None

    recording = np.concatenate(audio_frames, axis=0)

    max_vol = np.max(np.abs(recording))
    print(f"   [Debug] Âm lượng tối đa thu được: {max_vol:.5f}")
    if max_vol < 0.001:
        print("⚠️ [Cảnh báo] Âm thanh quá nhỏ hoặc Mic đang bị Mute (Toàn số 0).")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(temp_file.name, fs, (recording * 32767).astype(np.int16))
    return temp_file.name

def transcribe_audio(file_path):
    if not file_path or not os.path.exists(file_path):
        return None

    file_size = os.path.getsize(file_path)
    print(f"   [Debug] Kích thước file ghi âm: {file_size} bytes")

    if file_size < 1000:
        print("❌ [Lỗi] File ghi âm quá ngắn hoặc bị lỗi header.")
        return None

    try:
        print("⏳ Đang gửi lên OpenAI Whisper...")
        with open(file_path, "rb") as audio_file:
            res = openai_client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe", file=audio_file, language="vi"
            )
        os.remove(file_path)
        return res.text
    except Exception as e:
        print(f"\n❌ LỖI API WHISPER: {e}")
        return None

async def main():
    connect = StreamableHttpConnection(transport="streamable_http", url="http://localhost:8000/mcp")
    client = MultiServerMCPClient(connections={"Talk2Book backend": connect})
    try:
        tools = await client.get_tools(server_name="Talk2Book backend")
    except:
        tools = []

    agent = create_agent(model=llm, tools=tools,
                         system_prompt="Bạn hãy đóng vai làm nhân viên chăm sóc khách hàng tận tình, nói ngắn gọn đúng trọng tâm, chú ý khi gọi công cụ gì thì bạn hãy thông báo công cụ mình dùng ví dụ:  gọi api xem thông tin người dùng thì bạn hãy thông báo cho người dùng theo phong cách tư vấn là 'Để tôi giúp bạn kiểm tra thông tin của bạn trên hệ thống'")

    system_instruction = """
Bạn hãy đóng vai làm nhân viên chăm sóc khách hàng tận tình, nói ngắn gọn đúng trọng tâm, 
chú ý khi gọi công cụ gì thì bạn hãy thông báo công cụ mình dùng ví dụ:  
Gọi api xem thông tin người dùng thì bạn hãy thông báo cho người dùng theo phong cách tư vấn là 'Để tôi giúp bạn kiểm tra thông tin của bạn trên hệ thống'
Đặc biệt chú ý: Khi bạn không biết id của thành phố (city) hay airport bạn hãy gọi tool_call get_cities hoặc get_airports để lấy id chính xác nhất tránh sai sót
Đặc biệt chú ý trước khi gọi tool_call, bạn hãy đọc kĩ yêu cầu đầu vào của tool_call là kiểu dữ liệu gì và nếu thiếu trường dữ liệu gì thì có thể hỏi tiếp user và có thể gọi các tool_call khác để lấy thông tin
Đặc biệt chú ý khi tool_call yêu cầu UUID bạn phải tìm đúng thì mới được gọi, nếu thiếu thông tin về UUID thì cố gắng gọi các công cụ khác rồi mới hỏi user
"""
    chat_history = [
        SystemMessage(system_instruction)
    ]

    print("=== VOICE AGENT (WITH MEMORY) SẴN SÀNG ===")

    while True:
        audio_path = record_until_enter()
        user_query = transcribe_audio(audio_path)

        if not user_query or user_query.strip() == "":
            print("⚠️ Không nghe rõ.")
            continue

        print(f"\n🗣️  User: {user_query}")

        chat_history.append(HumanMessage(user_query))

        tts_streamer = TextToSpeechStreamer()
        full_response_text = ""

        print("🤖 AI: ", end="", flush=True)
        try:
            async for token, _ in agent.astream({"messages": chat_history}, stream_mode="messages"):
                content = token.content

                if content:
                    if isinstance(content, str):
                        print(content, end="", flush=True)
                        tts_streamer.add_text(content)
                        full_response_text += content
                    elif isinstance(content, list):
                        pass

            tts_streamer.flush()
            print("\n" + "-"*40)

            chat_history.append(AIMessage(full_response_text))

        except Exception as e:
            print(f"\n❌ Lỗi Agent: {e}")

        if len(chat_history) > 11:
            chat_history = [chat_history[0]] + chat_history[-10:]

        if input("Enter để tiếp tục (gõ 'exit' để thoát): ").strip().lower() == 'exit':
            break

if __name__ == "__main__":
    asyncio.run(main())
