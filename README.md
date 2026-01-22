# Mental-Health-Robot (MHR)

This project implements a socially assistive mental health interview robot using the Furhat SDK. 
The system conducts a structured voice-based interview and supports two interaction modes: a neutral mode and an emotional mode.
The goal is to study user experience and engagement under different robot interaction strategies, while keeping the interview structure consistent.

---

## Features

- Voice-based interview using the Furhat robot
- Two interaction modes:
  - **Neutral mode**: minimal gestures, no affective feedback
  - **Emotional mode**: expressive gestures and supportive verbal feedback
- Structured interview flow with configurable pacing
- Keyword-based response classification
- Session-level logging of user responses and robot behaviors (JSON)

---

## Project Structure
- neutral.py  # Neutral interaction condition
- emotional.py # Emotional interaction condition
- data/ # Local session logs
- README.md

---

## Interaction Modes

### Neutral Mode
- Delivers questions with minimal non-verbal behavior
- Does not adapt robot responses based on user emotion
- Designed to provide a baseline interaction condition

### Emotional Mode
- Uses facial expressions and gestures (e.g., smile, nod, frown)
- Provides supportive feedback based on user responses
- Uses transparent keyword-based rules

---

## How to Run

1. Start the Furhat robot and ensure it is reachable at `localhost`
2. Run one of the scripts:
neutral.py or emotional.py

---

## Data and Privacy
Session logs may contain participant-provided information. All logs are stored locally in the data/ directory and should not be uploaded to public repositories.