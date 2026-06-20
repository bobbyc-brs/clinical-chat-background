export type SpeakerRole = "doctor" | "patient"

export type TimelineItem = {
  segment_id: number
  start: number
  end: number
  text: string
  confidence: number | null
  speaker_role: SpeakerRole
  device_id: string
}

export type FieldStatus = "filled" | "review" | "missing"

export type FieldResult = {
  key: string
  label?: string
  value: string | null
  confidence: number
  evidence: string[]
  status: FieldStatus
}

export type Followup = {
  field_key: string
  severity: "high" | "medium" | "low"
  prompt: string
  reason: string
}

export type Metrics = {
  nbFieldsFilled: number
  nbNeedsReview: number
  nbActivePrompts: number
}

export type Session = {
  updated_at: number
  metrics: Metrics
  timeline: TimelineItem[]
  fields: Record<string, FieldResult>
  followups: Followup[]
}

export type TemplateField = {
  key: string
  label: string
  section: string
  position: { row: number; col: number; span?: number }
}

export type Template = {
  form_name: string
  fields: TemplateField[]
}
