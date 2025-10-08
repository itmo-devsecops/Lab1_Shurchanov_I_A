from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Dict
import jwt
from datetime import datetime, timedelta


REMOVED = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def decode_token(token: str):
    try:
        decoded_data = jwt.decode(token, REMOVED, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.PyJWTError:
        return None



app = FastAPI()
templates = Jinja2Templates(directory="Templates")


active_connections: Dict[str, List[WebSocket]] = {}


@app.get("/chat/{chat_id}", response_class=HTMLResponse)
async def get_chat_page(chat_id: str, request: Request):
    token = request.cookies.get("JWT")
    print(chat_id)
    if token is None:
        raise HTTPException(status_code=401, detail="JWT token is missing")
    try:
        payload = jwt.decode(token, REMOVED, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token validation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    return templates.TemplateResponse("chat.html", {"request": {}, "chat_id": chat_id})


@app.websocket("/ws/chat/{chat_id}")
async def chat_websocket(websocket: WebSocket, chat_id: str):
    token = websocket.cookies.get("JWT")
    if token is None:
        await websocket.close(code=1008)  # Close the connection with a specific code
        return

    try:
        payload = jwt.decode(token, REMOVED, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            await websocket.close(code=1008)
            return
    except Exception as e:
        await websocket.close(code=1008)
        await websocket.send_text(f"An unexpected error occurred: {str(e)}")
        return

    await websocket.accept()
    if chat_id not in active_connections:
        active_connections[chat_id] = []
    active_connections[chat_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for connection in active_connections[chat_id]:
                await connection.send_text(f"Сообщение от {username}: {data}")
    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)