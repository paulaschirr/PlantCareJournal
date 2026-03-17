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

## Data model & AI direction

The data model deliberately separates **context**, **intent**, and **observed behaviour**.

- **Species** store shared, stable context (e.g. native climate, care tendencies)
- **Plants** represent individual instances of a species, each with its own environment
- **Care profiles** capture seasonal care intent (watering / feeding intervals)
- **Care logs** record what actually happened, as an append‑only history

This structure allows the app to handle multiple plants of the same species behaving differently in different locations, and to reason about how real‑world care aligns (or diverges) from expectations.

The model is designed to support future AI‑assisted insights — such as pattern detection or anomaly highlighting — while keeping all decision logic explainable and human‑controlled. Any AI layer is intended to assist judgement, not replace it.

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
