import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

const mockTimeline = [
  { speaker_role: "doctor", start: 0.0, confidence: 0.94, text: "What brings you in today?" },
  { speaker_role: "patient", start: 2.1, confidence: 0.88, text: "I have chest tightness and a cough." },
  { speaker_role: "doctor", start: 3.0, confidence: 0.92, text: "How long have you had the symptoms?" },
  { speaker_role: "patient", start: 5.1, confidence: 0.68, text: "For about three days, I think." },
  { speaker_role: "doctor", start: 6.0, confidence: 0.93, text: "Do you have any allergies?" },
  { speaker_role: "patient", start: 8.1, confidence: 0.84, text: "Not that I know of." },
]

const mockFields = [
  { key: "chief_complaint", label: "Chief Complaint", span: 2, value: "chest tightness and a cough", confidence: 0.88, status: "filled", evidence: "I have chest tightness and a cough." },
  { key: "duration", label: "Duration", span: 1, value: "about three days", confidence: 0.68, status: "review", evidence: "For about three days, I think." },
  { key: "allergies", label: "Allergies", span: 1, value: "no known allergies", confidence: 0.84, status: "filled", evidence: "Not that I know of." },
  { key: "symptoms", label: "Symptoms", span: 2, value: "chest tightness and a cough", confidence: 0.88, status: "filled", evidence: "I have chest tightness and a cough." },
  { key: "medications", label: "Medications", span: 1, value: null, confidence: 0, status: "missing", evidence: null },
  { key: "history", label: "Relevant History", span: 1, value: null, confidence: 0, status: "missing", evidence: null },
]

const mockFollowups = [
  { field_key: "medications", severity: "high", prompt: "Are you taking any medications right now?", reason: "No medication information provided in transcript." },
  { field_key: "history", severity: "medium", prompt: "Is there any relevant medical history?", reason: "Relevant medical history not mentioned." },
]

function confBadgeVariant(confidence: number): "default" | "secondary" | "destructive" {
  if (confidence >= 0.85) return "default"
  if (confidence >= 0.7) return "secondary"
  return "destructive"
}

function statusBadgeVariant(status: string): "default" | "secondary" | "outline" {
  if (status === "filled") return "default"
  if (status === "review") return "secondary"
  return "outline"
}

export default function App() {
  const [dark, setDark] = useState(() => window.matchMedia("(prefers-color-scheme: dark)").matches)

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark)
  }, [dark])

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
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Sessions</p>
          {["visit-001", "visit-002", "visit-003"].map((id) => (
            <Button key={id} variant={id === "visit-001" ? "secondary" : "ghost"} className="justify-start" size="sm">
              {id}
            </Button>
          ))}
        </div>

        <Separator />

        <div className="flex flex-col gap-2 mt-auto">
          <Button className="w-full">Load demo data</Button>
          <Button variant="outline" className="w-full">Refresh</Button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="border-b px-6 py-4 flex items-center justify-between shrink-0">
          <div>
            <h1 className="text-xl font-bold">General Intake — Visit 001</h1>
            <p className="text-sm text-muted-foreground">Doctor and patient transcripts merged into a single encounter timeline.</p>
          </div>
          <Button variant="outline" onClick={() => setDark(d => !d)}>
            {dark ? "Light mode" : "Dark mode"}
          </Button>
        </header>

        <ScrollArea className="flex-1">
          <div className="p-6 flex flex-col gap-6">
            {/* Metrics */}
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: "Active prompts", value: mockFollowups.length, note: "Questions to ask next" },
                { label: "Fields filled", value: `${mockFields.filter(f => f.status !== "missing").length} / ${mockFields.length}`, note: "Chart coverage" },
                { label: "Needs review", value: mockFields.filter(f => f.status === "review").length, note: "Low confidence" },
                { label: "RPC state", value: "Live", note: "Ready for transcripts" },
              ].map((m) => (
                <Card key={m.label}>
                  <CardContent className="pt-4">
                    <p className="text-xs text-muted-foreground uppercase tracking-wider">{m.label}</p>
                    <p className="text-3xl font-bold mt-1">{m.value}</p>
                    <p className="text-xs text-muted-foreground mt-1">{m.note}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* 3-col content */}
            <div className="grid grid-cols-[1.2fr_1fr_0.85fr] gap-4">

              {/* Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle>Conversation timeline</CardTitle>
                  <p className="text-sm text-muted-foreground">Doctor and patient turns merged by timestamp.</p>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  {mockTimeline.map((item, i) => (
                    <div key={i} className="rounded-lg border bg-muted/40 p-3">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <Badge variant={item.speaker_role === "doctor" ? "secondary" : "default"}>
                          {item.speaker_role}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{item.start.toFixed(1)}s</span>
                        <Badge variant={confBadgeVariant(item.confidence)}>
                          conf {item.confidence.toFixed(2)}
                        </Badge>
                      </div>
                      <p className="text-sm">{item.text}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Medical form */}
              <Card>
                <CardHeader>
                  <CardTitle>Medical form</CardTitle>
                  <p className="text-sm text-muted-foreground">Fields populated by LLM extraction.</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {mockFields.map((field) => (
                      <div
                        key={field.key}
                        className={`rounded-lg border bg-muted/40 p-3 ${field.span === 2 ? "col-span-2" : ""}`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-semibold">{field.label}</p>
                          <Badge variant={statusBadgeVariant(field.status)}>{field.status}</Badge>
                        </div>
                        <p className="text-sm">
                          {field.value ?? <span className="text-muted-foreground">Awaiting answer</span>}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">conf {field.confidence.toFixed(2)}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Follow-up prompts */}
              <Card>
                <CardHeader>
                  <CardTitle>Follow-up prompts</CardTitle>
                  <p className="text-sm text-muted-foreground">Questions to ask for missing or unclear fields.</p>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  {mockFollowups.map((fp, i) => (
                    <div key={i} className="rounded-lg border bg-muted/40 p-3">
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-semibold">{fp.field_key}</p>
                        <Badge variant={fp.severity === "high" ? "destructive" : "secondary"}>{fp.severity}</Badge>
                      </div>
                      <p className="text-sm">{fp.prompt}</p>
                      <p className="text-xs text-muted-foreground mt-1">{fp.reason}</p>
                      <div className="flex gap-2 mt-3">
                        <Button size="sm">Mark asked</Button>
                        <Button size="sm" variant="outline">Dismiss</Button>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}
