import { useEffect, useRef, useState } from 'react'

interface UseWebSocketOptions<T> {
  url: string | null
  onMessage?: (data: T) => void
  onClose?: () => void
}

export function useWebSocket<T>({ url, onMessage, onClose }: UseWebSocketOptions<T>) {
  const [lastMessage, setLastMessage] = useState<T | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!url) return

    const ws = new WebSocket(url.startsWith('ws') ? url : `ws://localhost:8000${url}`)
    wsRef.current = ws

    ws.onopen = () => setIsConnected(true)
    ws.onmessage = (evt) => {
      try {
        const data: T = JSON.parse(evt.data as string)
        setLastMessage(data)
        onMessage?.(data)
      } catch {
        // ignore parse errors
      }
    }
    ws.onclose = () => {
      setIsConnected(false)
      onClose?.()
    }
    ws.onerror = () => ws.close()

    return () => ws.close()
  }, [url]) // eslint-disable-line react-hooks/exhaustive-deps

  return { lastMessage, isConnected }
}
