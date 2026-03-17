# My Plant Journal

**My Plant Journal** is a personal plant care tracking app built to demonstrate thoughtful data modelling, decision‑focused UX, and an architecture designed to support future AI‑assisted insights.

The app helps answer a simple daily question: *what needs attention today, and why?*, by combining structured event logging, seasonal logic, and clear status signals across all plants.

This is a deliberately non‑automated first version: the emphasis is on explainable logic, trustworthy data, and foundations that can support more advanced insights later.

---

## What the app does

- Track plant care events such as watering, feeding, and ad‑hoc notes  
- Apply seasonal context to care intervals and status calculations  
- Surface clear, aggregated signals (e.g. plants due vs total) rather than opaque alerts  
- Support multiple plants of the same species in different locations  
- Provide a calm, readable UI optimised for daily decision‑making  

---

## Design principles

- **Decision‑first**: the app focuses on helping users decide *what to do next*, not just logging data  
- **Explainable logic**: all status signals are derived from transparent rules, not black‑box automation  
- **Data before AI**: the underlying schema is normalised and context‑rich to support future pattern detection and recommendations  
- **Human‑in‑the‑loop**: care decisions remain user‑controlled, even as insight complexity increases  

---

## AI‑assisted direction (not yet implemented)

The app is intentionally designed to evolve toward AI‑assisted insights, for example:

- Detecting care patterns across seasons or environments  
- Highlighting anomalous plant behaviour relative to historical trends  
- Supporting recommendation logic grounded in observed data, not fixed schedules  

Crucially, these capabilities are treated as *extensions* of a solid data model, not substitutes for it.

---

## Tech stack

- Python  
- Streamlit (UI)  
- SQLite (local persistence)  

---

## Why this project exists

This project was built as a **portfolio piece** to demonstrate:
- Structured data modelling and schema design  
- Translating messy real‑world behaviour into clear metrics  
- Designing systems that balance usability, explainability, and future extensibility  

It is intentionally small in scope but opinionated in design.

---

## Status

Active personal project. The UI and logic are stable; future work focuses on insight generation rather than feature expansion.
