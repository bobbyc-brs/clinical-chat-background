import { useState, useEffect, useCallback, useRef } from "react"
import type { Session, FieldResult } from "./types"

const LIVE_API = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8080"
const MOCK_API = "http://localhost:2222"
export const POLL_INTERVAL_MS = 3000

const HEADERS = { "ngrok-skip-browser-warning": "true" }

function normalizeSession(data: Record<string, unknown>): Session {
  const rawFields = (data.fields ?? {}) as Record<string, FieldResult>
  const fields: Record<string, FieldResult> = Object.fromEntries(
    Object.entries(rawFields).map(([k, v]) => [
      k,
      { ...v, status: v.status === ("complete" as string) ? "filled" : v.status },
    ])
  )

  const followups = (data.followups ?? []) as Session["followups"]
  const fieldValues = Object.values(fields)

  const metrics = (data.metrics as Session["metrics"]) ?? {
    nbFieldsFilled:  fieldValues.filter(f => f.status === "filled").length,
    nbNeedsReview:   fieldValues.filter(f => f.status === "review").length,
    nbActivePrompts: followups.length,
  }

  return {
    updated_at: data.updated_at as number,
    metrics,
    timeline: (data.timeline ?? []) as Session["timeline"],
    fields,
    followups,
  }
}

async function fetchSessionData(base: string): Promise<Session> {
  const r = await fetch(`${base}/api/session`, { headers: HEADERS })
  if (!r.ok) throw new Error()
  return normalizeSession(await r.json())
}

export function useSession() {
  const [isMock, setIsMock]   = useState(false)
  const apiBase                = isMock ? MOCK_API : LIVE_API
  const [session, setSession] = useState<Session | null>(null)
  const [error, setError]     = useState<string | null>(null)
  const activeRef              = useRef(true)

  useEffect(() => {
    activeRef.current = true

    async function poll() {
      try {
        const data = await fetchSessionData(apiBase)
        if (activeRef.current) {
          setSession(data)
          setError(null)
        }
      } catch {
        if (activeRef.current) setError("Server unreachable — retrying")
      }
    }

    poll()
    const id = setInterval(poll, POLL_INTERVAL_MS)
    return () => {
      activeRef.current = false
      clearInterval(id)
    }
  }, [apiBase])

  const refetch = useCallback(async () => {
    try {
      setSession(await fetchSessionData(apiBase))
      setError(null)
    } catch {
      setError("Server unreachable — retrying")
    }
  }, [apiBase])

  const loadDemo = useCallback(async () => {
    await fetch(`${apiBase}/api/demo/load`, { method: "POST", headers: HEADERS })
    void refetch()
  }, [apiBase, refetch])

  const toggleMock = useCallback(() => setIsMock(m => !m), [])

  return { session, error, refetch, loadDemo, isMock, toggleMock }
}
