# Headache Protocol Scenario

This document describes the mock clinical conversation used in `mock_visit_api.py`.
It is intended for new developers, testers, and clinical reviewers who want to understand
what the system is doing and why.

---

## Overview

A patient presents with three weeks of worsening daily headaches.
The doctor follows a structured headache intake protocol, systematically
ruling out dangerous secondary causes before arriving at a primary headache assessment.

The scenario runs for 25 segments (13 doctor turns, 12 patient turns).
Each call to `GET /api/session` advances one segment and returns the updated structured state.

---

## Why This Protocol?

Headache is one of the most common presentations in primary care, but a small subset
of headaches are caused by dangerous conditions (brain bleed, meningitis, tumour).
The clinical goal is to ask the right questions in the right order to:

1. Rapidly screen for red flags that require emergency action
2. Characterise the headache to classify it (tension, migraine, cluster, secondary)
3. Identify modifiable contributing factors (medication overuse, lifestyle, stress)
4. Form a safe, appropriate plan

---

## Segment-by-Segment Breakdown

| # | Speaker | What is said | Field extracted | Why it matters |
|---|---|---|---|---|
| 1 | Doctor | "What brings you in today?" | — | Opens the encounter |
| 2 | Patient | "Headaches for three weeks, getting worse" | `chief_complaint` | Establishes the presenting problem |
| 3 | Doctor | "When did it start — sudden or gradual?" | — | Asks onset and thunderclap screen |
| 4 | Patient | "Gradual, three weeks ago — not the worst ever" | `onset_pattern`, `thunderclap_screen` | Gradual onset and denial of "worst ever" reduce urgent secondary risk |
| 5 | Doctor | "Where is it and what does it feel like?" | — | Location and character question |
| 6 | Patient | "Both sides of my forehead, pressure, sometimes throbbing" | `location_character` | Bifrontal pressure with throbbing is consistent with tension or migraine |
| 7 | Doctor | "How often, how long, how severe out of ten?" | — | Asks frequency, duration, severity in one turn |
| 8 | Patient | "Almost every day, several hours, six or seven out of ten" | `frequency_duration_severity` | Near-daily, moderate-severe headache is a significant burden and raises medication-overuse concern |
| 9 | Doctor | "Nausea, vomiting, light or sound sensitivity, visual aura?" | — | Migraine-feature screen |
| 10 | Patient | "Light sensitivity and want quiet — no vomiting, no aura" | `associated_symptoms` | Photophobia and phonophobia without aura is consistent with migraine without aura |
| 11 | Doctor | "Fever, neck stiffness, weakness, numbness, confusion?" | — | Neurologic and infectious red-flag screen |
| 12 | Patient | "No fever, no neck stiffness, no weakness or speech trouble" | `neurologic_red_flags` | Absence of these features reduces concern for meningitis, stroke, or mass lesion |
| 13 | Doctor | "Recent head injury, cancer, immune problems, pregnancy, blood thinners, new meds?" | — | Secondary-risk factor screen |
| 14 | Patient | "None of those — but I started a decongestant recently" | `secondary_risk_factors` | New medication can cause or worsen headache; all other secondary risks denied |
| 15 | Doctor | "What triggers it — what makes it better or worse?" | — | Triggers and relieving factors |
| 16 | Patient | "Worse with screens and dehydration; rest, coffee, and ibuprofen help a bit" | `triggers_relief` | Screen time, dehydration, and caffeine withdrawal are common primary headache drivers |
| 17 | Doctor | "How often are you taking ibuprofen or other pain medicine?" | — | Medication-overuse screen |
| 18 | Patient | "About five or six days a week lately" | `medication_use` | Analgesic use ≥10 days/month meets the threshold for medication-overuse headache (MOH) |
| 19 | Doctor | "How have sleep, stress, hydration, and caffeine been?" | — | Lifestyle context |
| 20 | Patient | "Poor sleep, high stress, not enough water, two large coffees a day" | `lifestyle_context` | Multiple compounding lifestyle factors — all modifiable |
| 21 | Doctor | "Is this similar to past headaches or a new pattern?" | — | Prior headache history |
| 22 | Patient | "Had occasional headaches before, but not like this — this is new" | `prior_headache_history` | A new or changing headache pattern increases concern for secondary causes |
| 23 | Doctor | "Any allergy to aspirin or NSAIDs?" | — | Allergy screen before treatment suggestion |
| 24 | Patient | "No, not allergic to aspirin or NSAIDs" | `allergies` | Clears the way for NSAID-based treatment recommendations |
| 25 | Doctor | "This sounds like a primary headache — reduce ibuprofen, hydrate, improve sleep, keep a diary" | `assessment_plan` | Closes the encounter with a safety-net plan and modifiable-factor counselling |

---

## Fields and Status Transitions

Each field moves through three states as the conversation progresses:

| Status | Meaning |
|---|---|
| `missing` | Not yet discussed |
| `review` | Extracted but low confidence — should be confirmed |
| `filled` | Extracted with high confidence |

Fields transition from `missing` → `review` or `filled` as the relevant segments are spoken.
The `thunderclap_screen` and `neurologic_red_flags` fields are prioritised highest when missing
because unrecognised red flags carry the most clinical risk.

---

## Follow-up Priority Logic

At each tick, the server computes the top 5 prompts to surface to the clinician.
Prompts are ranked in this order:

1. **Low-confidence extractions** — already filled but marked `review`; confirm before proceeding
2. **Asked but unanswered** — doctor has already raised the topic; patient has not responded yet
3. **Thunderclap screen** — highest-risk red flag when still missing
4. **Neurologic / infectious red flags** — second highest risk
5. **Secondary risk factors** — trauma, cancer, pregnancy, anticoagulants, new medications
6. **Frequency / duration / severity** — core diagnostic characterisation
7. **Associated symptoms** — migraine feature classification
8. **Medication use** — medication-overuse headache risk
9. **Lifestyle context, triggers, prior history, allergies** — important but lower urgency
10. **Assessment and plan** — lowest priority (documents the conclusion)
11. **Optional fields** (e.g. air conditioning) — only surfaced if the topic arises in conversation

---

## Clinical Notes for Reviewers

- **Medication-overuse headache (MOH):** Analgesic use on ≥10 days/month for ≥3 months can paradoxically worsen headache frequency. This patient is at significant risk given near-daily ibuprofen use.
- **New or worsening pattern:** This patient's shift from occasional to near-daily headaches over three weeks warrants follow-up even after red flags are cleared.
- **Decongestant:** Some decongestants can elevate blood pressure or cause rebound headache. Worth reviewing the specific agent.
- **Lifestyle cluster:** Poor sleep + high stress + low hydration + high caffeine intake all independently worsen primary headaches and often co-occur.

---

## Extending the Scenario

To add new segments, append to the `SEGMENTS` list in `mock_visit_api.py` and add the
corresponding field extraction logic in `build_fields()`.

To add a new optional field (e.g. air conditioning, work environment, hormonal factors),
add it to `FIELD_SPECS` with `required=False` and give it a low priority in `question_priority()`.
It will only surface in the top-5 once higher-priority fields are resolved.

