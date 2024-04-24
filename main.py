from typing import List
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
import uvicorn

app = FastAPI()
socketRouter = APIRouter()

count = 0
async def process_request(websocket: WebSocket, decoded_message: str,count:int):
    await websocket.send_text(decoded_message+str(count))

async def websocket_handler(websocket: WebSocket):
    global count 
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            decoded_message = message
            count=count+1
            print(decoded_message+str(count))
            await process_request(websocket, decoded_message,count)
    except asyncio.TimeoutError:
        await websocket.send_text(json.dumps({"status": "error", "message": "Timeout occurred"}))
        await websocket.close(code=1000)
    except WebSocketDisconnect as e:
        await websocket.send_text(json.dumps({"status": "error", "message": "Client disconnected"}))
        await websocket.close(code=1000)
    except Exception as e:
        print(e)
        await websocket.send_text(json.dumps({"status": "error", "message": "Something went wrong"}))
        await websocket.close(code=1011)

socketRouter.websocket("/ws")(websocket_handler)

@app.get("/hello")
def test_connection():
    return "Hello from Socket server!!"

app.include_router(socketRouter)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
