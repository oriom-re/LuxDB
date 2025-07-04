import asyncio
import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio)

# Wewnętrzny LuxBus jako kolejka komunikatów
lux_queue = asyncio.Queue()

# Baza wyników (np. na potrzeby późniejszego odebrania danych)
results = {}

# odbieramy komunikat z zewnątrz
@sio.event
async def luxmessage(sid, data):
    print(f"🔵 Odebrano LuxMessage od {sid}: {data}")
    await lux_queue.put(data)  # wrzucamy do LuxBus

# lokalny worker symulujący "długie" zadanie
async def lux_worker():
    while True:
        message = await lux_queue.get()
        print(f"🧠 LuxBus wykonuje: {message['to']}")

        # symulujemy długie działanie
        await asyncio.sleep(3)

        # zapisujemy wynik
        results[message['reply_id']] = {
            "result": f"Przetworzone: {message['payload']['data']}"
        }

        # tylko powiadomienie!
        await sio.emit('luxnotify', {
            "status": "done",
            "reply_id": message['reply_id']
        })

# oddzielny endpoint na odbiór wyniku
@sio.event
async def get_result(sid, data):
    reply_id = data['reply_id']
    result = results.get(reply_id, None)
    await sio.emit('luxresult', {
        "reply_id": reply_id,
        "data": result
    })

# start workerów
async def main():
    asyncio.create_task(lux_worker())

import uvicorn
if __name__ == '__main__':
    asyncio.run(main())
    uvicorn.run(app, host="0.0.0.0", port=3000)
