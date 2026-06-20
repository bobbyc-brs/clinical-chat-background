import { useEffect, useRef, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { ArrowUpIcon, ArrowDownIcon } from "@phosphor-icons/react"
import { useSession, POLL_INTERVAL_MS } from "@/lib/useSession"

function ScrollSection({ className, children }: { className?: string; children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const [canScrollUp, setCanScrollUp]     = useState(false)
  const [canScrollDown, setCanScrollDown] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const update = () => {
      setCanScrollUp(el.scrollTop > 0)
      setCanScrollDown(el.scrollTop + el.clientHeight < el.scrollHeight - 1)
    }
    update()
    el.addEventListener("scroll", update)
    const ro = new ResizeObserver(update)
    ro.observe(el)
    return () => { el.removeEventListener("scroll", update); ro.disconnect() }
  }, [])

  return (
    <div className="relative h-full flex flex-col">
      {canScrollUp && (
        <div className="absolute top-0 left-0 right-0 z-10 flex justify-center py-0.5 bg-card border-b border-border">
          <ArrowUpIcon size={12} className="text-muted-foreground" />
        </div>
      )}
      <div ref={ref} className={`h-full overflow-y-auto ${className ?? ""}`}>
        {children}
      </div>
      {canScrollDown && (
        <div className="absolute bottom-0 left-0 right-0 z-10 flex justify-center py-0.5 bg-card border-t border-border">
          <ArrowDownIcon size={12} className="text-muted-foreground" />
        </div>
      )}
    </div>
  )
}

function confBadgeProps(confidence: number): { variant: "outline" | "destructive"; className: string } {
  if (confidence >= 0.85) return { variant: "outline", className: "rounded-none text-primary border-primary/40" }
  if (confidence >= 0.7)  return { variant: "outline", className: "rounded-none text-yellow-500 border-yellow-500/40" }
  return { variant: "destructive", className: "rounded-none" }
}

function statusBadgeProps(status: string): { variant: "default" | "outline"; className?: string } {
  if (status === "filled") return { variant: "default" }
  if (status === "review") return { variant: "outline", className: "text-yellow-500 border-yellow-500/40" }
  return { variant: "outline", className: "text-muted-foreground" }
}

export default function App() {
  const [dark, setDark] = useState(false)
  const [localEdits, setLocalEdits] = useState<Record<string, string>>({})
  const { session, error, loadDemo, isMock, toggleMock } = useSession()

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark)
  }, [dark])

  const formFields = Object.values(session?.fields ?? {}).map(f => ({
    key:        f.key,
    label:      f.label ?? f.key,
    value:      f.value,
    confidence: f.confidence,
    status:     f.status,
    evidence:   f.evidence,
  }))

  const metrics = session?.metrics ?? { nbFieldsFilled: 0, nbNeedsReview: 0, nbActivePrompts: 0 }
  const timeline  = session?.timeline  ?? []
  const followups = session?.followups ?? []

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r flex flex-col p-4 gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">+</div>
          <div>
            <p className="font-semibold text-sm">Clinical Server</p>
            <p className="text-xs text-muted-foreground">Conversation-aware charting</p>
          </div>
        </div>

        <Separator />

        <div className="flex flex-col gap-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Status</p>
          <div className="flex items-center gap-2">
            <Badge variant={isMock ? "secondary" : "default"} className="text-xs">
              {isMock ? "Mock" : "Live"}
            </Badge>
            {error
              ? <p className="text-xs text-destructive">{error}</p>
              : <p className="text-xs text-green-500">polling every {POLL_INTERVAL_MS / 1000}s</p>
            }
          </div>
          {session && (
            <p className="text-xs text-muted-foreground">
              {session.updated_at.toFixed(1)}s into session
            </p>
          )}
        </div>

        <Separator />

        <div className="flex flex-col gap-2 mt-auto">
          {isMock && (
            <Button variant="secondary" className="w-full" onClick={loadDemo}>Restart demo</Button>
          )}
          <Button variant={isMock ? "default" : "outline"} className="w-full" onClick={toggleMock}>
            {isMock ? "Switch to live server" : "Switch to mock server"}
          </Button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="border-b px-6 py-4 flex items-center justify-between shrink-0">
          <div>
            <h1 className="text-xl font-bold">General Intake</h1>
            <p className="text-sm text-muted-foreground">Doctor and patient transcripts merged into a single encounter timeline.</p>
          </div>
          <Button variant="outline" onClick={() => setDark(d => !d)}>
            {dark ? "Light mode" : "Dark mode"}
          </Button>
        </header>

        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="p-6 flex flex-col gap-6 flex-1 min-h-0">
            {/* Metrics */}
            <div className="grid grid-cols-4 gap-4 shrink-0">
              {[
                { label: "Active prompts", value: metrics.nbActivePrompts },
                { label: "Fields filled",  value: `${metrics.nbFieldsFilled} / ${formFields.length || "—"}` },
                { label: "Needs review",   value: metrics.nbNeedsReview },
                { label: "Timeline",       value: timeline.length },
              ].map((m) => (
                <Card key={m.label} size="sm" className="py-1">
                  <CardContent className="flex items-center justify-between gap-2 py-0 px-3">
                    <p className="text-xs text-muted-foreground">{m.label}</p>
                    <p className="text-sm font-semibold">{m.value}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 3-col content */}
            <div className="grid grid-cols-[1.2fr_1fr_0.85fr] gap-4 flex-1 min-h-0">

              {/* Timeline */}
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Conversation timeline</CardTitle>
                  <p className="text-sm text-muted-foreground">Doctor and patient turns merged by timestamp.</p>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden">
                  <ScrollSection className="flex flex-col gap-3 pr-1">

                  {timeline.length === 0 && (
                    <p className="text-sm text-muted-foreground">Waiting for transcript...</p>
                  )}
                  {timeline.map((item) => (
                    <div key={item.segment_id} className="rounded-lg border bg-muted/40 p-3">
                      {item.speaker_role === "doctor" ? (
                        <div className="flex items-center justify-end gap-2 mb-1">
                          <span className="text-xs text-muted-foreground">{item.start.toFixed(1)}s</span>
                          <Badge variant="secondary">doctor</Badge>
                        </div>
                      ) : (
                        <div className="flex items-center justify-start gap-2 mb-1">
                          <Badge variant="secondary">patient</Badge>
                          <span className="text-xs text-muted-foreground">{item.start.toFixed(1)}s</span>
                        </div>
                      )}
                      <p className={`text-sm mt-1 ${item.speaker_role === "doctor" ? "text-right" : "text-left"}`}>{item.text}</p>
                      {item.confidence != null && (
                        <div className="flex justify-end mt-1">
                          <Badge {...confBadgeProps(item.confidence)}>
                            conf {item.confidence.toFixed(2)}
                          </Badge>
                        </div>
                      )}
                    </div>
                  ))}
                  </ScrollSection>
                </CardContent>
              </Card>

              {/* Medical form */}
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Medical form</CardTitle>
                  <p className="text-sm text-muted-foreground">Fields populated by LLM extraction.</p>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden">
                  <ScrollSection className="flex flex-col gap-3 pr-1">
                    {formFields.length === 0 && (
                      <p className="text-sm text-muted-foreground col-span-2">Loading template...</p>
                    )}
                    {formFields.map((field) => (
                      <div
                        key={field.key}
                        className="rounded-lg border bg-muted/40 p-3"
                      >
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-semibold">{field.label}</p>
                          <Badge {...statusBadgeProps(field.status)}>{field.status}</Badge>
                        </div>
                        <textarea
                          className="w-full text-sm bg-transparent outline-none placeholder:text-muted-foreground mt-1 resize-none border border-border rounded-sm px-2 py-1 focus:border-primary transition-colors"
                          value={localEdits[field.key] ?? field.value ?? ""}
                          placeholder="Awaiting answer"
                          rows={2}
                          onChange={e => setLocalEdits(prev => ({ ...prev, [field.key]: e.target.value }))}
                        />
                        <p className="text-xs text-muted-foreground mt-1">conf {field.confidence.toFixed(2)}</p>
                      </div>
                    ))}
                  </ScrollSection>
                </CardContent>
              </Card>

              {/* Follow-up prompts */}
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Follow-up prompts</CardTitle>
                  <p className="text-sm text-muted-foreground">Questions to ask for missing or unclear fields.</p>
                </CardHeader>
                <CardContent className="flex-1 overflow-hidden">
                  <ScrollSection className="flex flex-col gap-3 pr-1">

                  {followups.length === 0 && (
                    <p className="text-sm text-muted-foreground">No prompts yet.</p>
                  )}
                  {followups.map((fp, i) => (
                    <div key={i} className="rounded-lg border bg-muted/40 p-3">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-semibold">{fp.field_key}</p>
                        <Badge variant={fp.severity === "high" ? "destructive" : "secondary"}>{fp.severity}</Badge>
                      </div>
                      <p className="text-sm">{fp.prompt}</p>
                      <p className="text-xs text-muted-foreground mt-1">{fp.reason}</p>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm" variant="secondary">Mark asked</Button>
                        <Button size="sm" variant="outline">Dismiss</Button>
                      </div>
                    </div>
                  ))}
                  </ScrollSection>
                </CardContent>
              </Card>

            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
