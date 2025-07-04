# Przykład zastosowania callbacków z UID w React + WebSocket (socket.io)

## Cel
Implementacja mechanizmu, w którym komponent React wysyła zapytanie przez WebSocket z unikalnym identyfikatorem (`uid`) i **czeka asynchronicznie** na odpowiedź z tym samym `uid`.

---

## 1. Kontekst WebSocket (`SocketContext.tsx`)

- Inicjalizuje połączenie `socket.io-client`
- Przechowuje mapę callbacków (`callbacks`) do powiązania odpowiedzi z `uid`
- Metoda `sendAndAwait` wysyła wiadomość z `uid` i zwraca `Promise`
- Gdy przychodzi odpowiedź z serwera z tym `uid`, odpowiednia obietnica jest rozwiązywana (`resolve`)

```tsx
import { createContext, useContext, useEffect, useRef } from 'react'
import { io } from 'socket.io-client'
import { v4 as uuidv4 } from 'uuid'

const SocketContext = createContext(null)

export const SocketProvider = ({ children }) => {
  const socket = useRef(io('ws://localhost:3000'))
  const callbacks = useRef(new Map())

  useEffect(() => {
    socket.current.on('luxresult', (msg) => {
      const { reply_id, data } = msg
      if (callbacks.current.has(reply_id)) {
        callbacks.current.get(reply_id)(data)
        callbacks.current.delete(reply_id)
      }
    })
  }, [])

  const sendAndAwait = (event, payload) => {
    return new Promise((resolve) => {
      const uid = uuidv4()
      callbacks.current.set(uid, resolve)

      socket.current.emit(event, {
        ...payload,
        reply_id: uid,
      })
    })
  }

  return (
    <SocketContext.Provider value={{ sendAndAwait }}>
      {children}
    </SocketContext.Provider>
  )
}

export const useSocket = () => useContext(SocketContext)
2. Przykładowy komponent React
tsx
Kopiuj
Edytuj
const MyComponent = () => {
  const { sendAndAwait } = useSocket()

  const handleClick = async () => {
    const result = await sendAndAwait('luxmessage', {
      to: 'soul://lux.test.echo',
      payload: { msg: 'Cześć z Reacta!' }
    })

    console.log("🔁 Otrzymano:", result)
  }

  return <button onClick={handleClick}>Wyślij zapytanie</button>
}
3. Omówienie
uid generowane jest unikalnie dla każdej wiadomości (UUID v4)

callbacks mapuje uid na funkcję resolve obietnicy

Gdy serwer odsyła odpowiedź z reply_id == uid, Promise jest rozwiązywane i wynik przekazywany do wywołującego

Pozwala to na prostą, asynchroniczną komunikację z mechanizmem callbacków bez komplikowania stanu komponentów

4. Możliwe rozszerzenia
Timeout dla sendAndAwait (reject, jeśli brak odpowiedzi po czasie)

Logika retry (ponowne wysłanie po błędzie lub timeout)

Oddzielenie eventów typu notify (bez oczekiwania na odpowiedź) od result

Obsługa błędów w komunikacji

Podsumowanie
Ten prosty, elegancki wzorzec pozwala na asynchroniczną komunikację klient-serwer w React z gwarancją, że odpowiedź zostanie dopasowana do konkretnego zapytania przez uid.
Idealny fundament do rozwoju bardziej skomplikowanych protokołów jak LuxChain czy Astra.

