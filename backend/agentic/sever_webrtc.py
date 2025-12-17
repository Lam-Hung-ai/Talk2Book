# server.py
import os

import socketio
from aiohttp import web

# Tạo Socket.IO server (cho phép mọi nguồn gốc để test dễ dàng)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Khi client kết nối
@sio.event
async def connect(sid, environ):
    print(f"Client đã kết nối: {sid}")

# Khi client ngắt kết nối
@sio.event
async def disconnect(sid):
    print(f"Client đã ngắt kết nối: {sid}")

# Hàm quan trọng nhất: Chuyển tiếp tin nhắn
# Khi client A gửi tin nhắn, server sẽ gửi lại cho tất cả client khác (trừ A)
@sio.event
async def message(sid, data):
    # print(f"Tin nhắn từ {sid}: {data}")
    # skip_sid=sid nghĩa là gửi cho mọi người trừ người gửi
    await sio.emit('message', data, skip_sid=sid)

# Phục vụ file index.html
async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

# Định tuyến đường dẫn gốc '/' tới hàm index
app.router.add_get('/', index)

if __name__ == '__main__':
    print("Server đang chạy tại http://localhost:8080")
    web.run_app(app, host='0.0.0.0', port=8080)