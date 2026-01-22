from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from furhat_remote_api import FurhatRemoteAPI



# Configuration
@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    voice: str = "Brain"

    # Timing (seconds)
    pause_after_say: float = 0.8
    pause_after_answer: float = 1.2
    pause_after_feedback: float = 1.2

    # Listening robustness
    listen_retries: int = 2
    retry_prompt: str = "I didn't catch that. Could you please repeat?"
    empty_fallback: str = "No response"

    # Logging
    log_dir: str = "data"
    save_log: bool = True

    # Keyword classification
    positive_phrases: Tuple[str, ...] = (
        "yes", "yeah", "yep", "of course", "sure", "absolutely", "definitely",
        "i do", "i am", "good", "nice", "great", "fine", "ok", "okay"
    )
    negative_phrases: Tuple[str, ...] = (
        "no", "nope", "not really", "i don't", "i dont", "i am not",
        "nah", "never", "not good", "bad", "sad", "unhappy"
    )



# Interview content
QUESTIONS: List[Tuple[str, Optional[str]]] = [
    (
        "Hello, my name is Furhat. Thank you for taking the time to speak with me today. "
        "In order to help you the best I can, I will need to ask you some questions. "
        "A simple 'yes' or 'no' will suffice for most of my questions, and based on your answers "
        "I can then advise which of our specialists you would most benefit working with.",
        None,
    ),
    ("Are you ready to begin?", "ready"),

    ("Great! My inquiry will now begin. What is your name?", "name"),
    ("What is your date of birth?", "dob"),
    ("Could you tell me your school email?", "email"),

    ("Wonderful. Do you wish to seek counseling with your university health services?", "counseling"),
    ("Would you describe your current circumstances regarding your mental health as good?", "mental_health"),

    ("In general, do you consider yourself a happy person?", "happy_general"),
    ("Compared to most of your peers or friends, do you consider yourself happy?", "happy_comparison"),

    (
        "Some people are generally very happy. They enjoy life regardless of what is going on, "
        "getting the most out of everything. Does this characterization describe you?",
        "happy_very",
    ),
    (
        "Some people are generally not very happy. Although they are not depressed, "
        "they never seem as happy as they might be. Does this characterization describe you?",
        "happy_not",
    ),

    (
        "Thank you for your participation, my inquiry is complete now. Based on your answer, "
        "I believe that I have a specialist that will fit your needs. Would you like me to schedule a meeting for you?",
        "schedule_meeting",
    ),

    ("Goodbye!", None),
]



# Utilities
def utc_now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def safe_filename(prefix: str, ext: str = ".json") -> str:
    """Generate a safe filename with UTC timestamp."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}{ext}"


def connect_robot(cfg: Config) -> FurhatRemoteAPI:
    """Connect to Furhat and set the configured voice."""
    try:
        furhat = FurhatRemoteAPI(cfg.host)
        furhat.set_voice(name=cfg.voice)
        return furhat
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to Furhat at host='{cfg.host}'. "
            f"Check that Furhat is running and reachable."
        ) from e


def classify_response(cfg: Config, text: str) -> str:
    """
    Classify response into: POSITIVE / NEGATIVE / UNKNOWN.
    """
    t = (text or "").strip().lower()
    if not t:
        return "UNKNOWN"

    # Handle common negation patterns that flip sentiment
    if "not bad" in t:
        return "POSITIVE"
    if "not good" in t:
        return "NEGATIVE"

    if any(p in t for p in cfg.positive_phrases):
        return "POSITIVE"
    if any(p in t for p in cfg.negative_phrases):
        return "NEGATIVE"
    return "UNKNOWN"


def say_safe(
    furhat: FurhatRemoteAPI,
    logs: List[Dict[str, Any]],
    text: str,
    blocking: bool = True,
) -> None:
    """Speak using Furhat and log the utterance; tolerate transient exceptions."""
    try:
        furhat.say(text=text, blocking=blocking)
        logs.append({"t": utc_now_iso(), "event": "say", "text": text, "blocking": blocking})
    except Exception as e:
        logs.append({"t": utc_now_iso(), "event": "say_exception", "text": text, "error": repr(e)})


def gesture_safe(
    furhat: FurhatRemoteAPI,
    logs: List[Dict[str, Any]],
    name: str,
    blocking: bool = False,
) -> None:
    """Perform a gesture and log it; tolerate transient exceptions."""
    try:
        furhat.gesture(name=name, blocking=blocking)
        logs.append({"t": utc_now_iso(), "event": "gesture", "name": name, "blocking": blocking})
    except Exception as e:
        logs.append({"t": utc_now_iso(), "event": "gesture_exception", "name": name, "error": repr(e)})


def listen_with_retries(
    furhat: FurhatRemoteAPI,
    cfg: Config,
    logs: List[Dict[str, Any]],
    key: str,
) -> str:
    """Listen for user response with retries and structured logging."""
    attempts_total = 1 + cfg.listen_retries

    for attempt in range(1, attempts_total + 1):
        response = None
        try:
            response = furhat.listen()
        except Exception as e:
            logs.append(
                {"t": utc_now_iso(), "event": "listen_exception", "key": key, "attempt": attempt, "error": repr(e)}
            )

        msg = getattr(response, "message", None) if response else None
        msg = msg.strip() if isinstance(msg, str) else ""

        logs.append(
            {"t": utc_now_iso(), "event": "listen_result", "key": key, "attempt": attempt, "message": msg or None}
        )

        if msg:
            return msg

        if attempt < attempts_total:
            say_safe(furhat, logs, cfg.retry_prompt, blocking=True)

    return cfg.empty_fallback


def save_session_log(cfg: Config, session: Dict[str, Any]) -> Optional[str]:
    """Save session data to a JSON file and return the filepath."""
    if not cfg.save_log:
        return None

    ensure_dir(cfg.log_dir)
    filename = safe_filename(prefix="emotional_session", ext=".json")
    filepath = os.path.join(cfg.log_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    return filepath



# Expressive behavior layer
def opening_sequence(furhat: FurhatRemoteAPI, logs: List[Dict[str, Any]]) -> None:
    """Run an expressive but consistent opening (emotive condition)."""
    gesture_safe(furhat, logs, "BigSmile", blocking=False)
    say_safe(furhat, logs, "Hello, my name is Furhat. Thank you for taking the time to speak with me today.", True)

    gesture_safe(furhat, logs, "BrowRaise", blocking=False)
    say_safe(furhat, logs, "In order to help you the best I can, I will need to ask you some questions.", True)

    gesture_safe(furhat, logs, "Nod", blocking=False)
    say_safe(
        furhat,
        logs,
        "A simple 'yes' or 'no' will suffice for most of my questions, and based on your answers I can then advise "
        "which of our specialists you would most benefit working with.",
        True,
    )


def feedback_for_answer(
    furhat: FurhatRemoteAPI,
    cfg: Config,
    logs: List[Dict[str, Any]],
    key: str,
    user_name: str,
    answer: str,
) -> None:
    """
    Provide expressive feedback after certain questions.
    """
    label = classify_response(cfg, answer)

    # Keep feedback limited to selected items
    if key == "mental_health":
        if label == "POSITIVE":
            gesture_safe(furhat, logs, "Smile", blocking=False)
            say_safe(furhat, logs, f"I'm happy to hear that, {user_name}.", True)
        elif label == "NEGATIVE":
            gesture_safe(furhat, logs, "ExpressSad", blocking=False)
            say_safe(furhat, logs, f"I'm sorry to hear that, {user_name}.", True)
        else:
            gesture_safe(furhat, logs, "Thoughtful", blocking=False)
            say_safe(furhat, logs, f"Thank you for sharing, {user_name}.", True)

    elif key in {"happy_general", "happy_comparison", "happy_very"}:
        if label == "POSITIVE":
            gesture_safe(furhat, logs, "Wink", blocking=False)
            say_safe(furhat, logs, "I'm happy to hear that.", True)
        elif label == "NEGATIVE":
            gesture_safe(furhat, logs, "BrowFrown", blocking=False)
            say_safe(furhat, logs, "Sorry to hear that.", True)
        else:
            gesture_safe(furhat, logs, "Thoughtful", blocking=False)
            say_safe(furhat, logs, "Thank you for sharing.", True)

    elif key == "happy_not":
        # If the user says YES, they identify with "not very happy" -> treat as NEGATIVE situation
        # If the user says NO, they do NOT identify with "not very happy" -> treat as POSITIVE situation
        if label == "POSITIVE":
            gesture_safe(furhat, logs, "ExpressSad", blocking=False)
            say_safe(
                furhat,
                logs,
                f"I'm sorry to hear that, {user_name}. I hope this doesn't impact your everyday life significantly.",
                True,
            )
        elif label == "NEGATIVE":
            gesture_safe(furhat, logs, "BigSmile", blocking=False)
            gesture_safe(furhat, logs, "Nod", blocking=False)
            say_safe(furhat, logs, "I'm happy to hear that!", True)
        else:
            gesture_safe(furhat, logs, "BrowFrown", blocking=False)
            say_safe(furhat, logs, "Thank you for telling me.", True)

    elif key == "schedule_meeting":
        if label == "POSITIVE":
            gesture_safe(furhat, logs, "Smile", blocking=False)
            gesture_safe(furhat, logs, "Nod", blocking=False)
            say_safe(
                furhat,
                logs,
                "Great, I will schedule the meeting and send the details to your school email. Goodbye!",
                True,
            )
        elif label == "NEGATIVE":
            gesture_safe(furhat, logs, "Nod", blocking=False)
            say_safe(
                furhat,
                logs,
                "No problem. You can always reach out if you change your mind. Goodbye!",
                True,
            )
        else:
            gesture_safe(furhat, logs, "Thoughtful", blocking=False)
            say_safe(furhat, logs, "Okay, thank you for your response. Goodbye!", True)



# Main interview flow
def run_interview(cfg: Config) -> Dict[str, Any]:
    """Run the emotional interview and return a structured session object."""
    furhat = connect_robot(cfg)

    answers: Dict[str, str] = {}
    event_logs: List[Dict[str, Any]] = []

    session_meta = {
        "t_start": utc_now_iso(),
        "host": cfg.host,
        "voice": cfg.voice,
        "mode": "emotional",
        "questions_count": len(QUESTIONS),
        "timing": {
            "pause_after_say": cfg.pause_after_say,
            "pause_after_answer": cfg.pause_after_answer,
            "pause_after_feedback": cfg.pause_after_feedback,
        },
        "listen": {
            "retries": cfg.listen_retries,
            "retry_prompt": cfg.retry_prompt,
            "empty_fallback": cfg.empty_fallback,
        },
    }

    # Expressive opening
    opening_sequence(furhat, event_logs)
    time.sleep(cfg.pause_after_say)

    user_name = "there"

    for idx, (question_text, key) in enumerate(QUESTIONS, start=1):
        # Skip the duplicated opening statements already handled by opening_sequence
        if idx == 1 and key is None:
            continue

        event_logs.append({"t": utc_now_iso(), "event": "question_start", "index": idx, "key": key, "text": question_text})

        # Light expressive cues before asking key questions
        if key in {"name", "happy_general", "schedule_meeting"}:
            gesture_safe(furhat, event_logs, "Smile", blocking=False)
            gesture_safe(furhat, event_logs, "Nod", blocking=False)

        say_safe(furhat, event_logs, question_text, blocking=True)
        time.sleep(cfg.pause_after_say)

        if key is None:
            continue

        answer = listen_with_retries(furhat, cfg, event_logs, key=key)
        answers[key] = answer

        # Update user name for personalization
        if key == "name":
            cleaned = answer.strip()
            user_name = cleaned if cleaned and cleaned != cfg.empty_fallback else "there"

            # Optional friendly reaction after receiving a name
            gesture_safe(furhat, event_logs, "BigSmile", blocking=False)
            say_safe(furhat, event_logs, "What a lovely name!", blocking=True)
            gesture_safe(furhat, event_logs, "Wink", blocking=False)
            say_safe(furhat, event_logs, f"It's nice to meet you, {user_name}.", blocking=True)
            time.sleep(cfg.pause_after_feedback)

        # Print to visibility
        print(f"{key.capitalize()} (User's answer): {answer}")

        time.sleep(cfg.pause_after_answer)

        # Provide expressive feedback
        feedback_for_answer(
            furhat=furhat,
            cfg=cfg,
            logs=event_logs,
            key=key,
            user_name=user_name,
            answer=answer,
        )
        time.sleep(cfg.pause_after_feedback)

    session = {
        "meta": session_meta,
        "t_end": utc_now_iso(),
        "answers": answers,
        "events": event_logs,
    }
    return session


def main() -> None:
    cfg = Config()

    session = run_interview(cfg)
    filepath = save_session_log(cfg, session)

    print("\nInterview completed. Collected information:")
    for k, v in session["answers"].items():
        print(f"{k.capitalize()}: {v}")

    if filepath:
        print(f"\nSession log saved to: {filepath}")


if __name__ == "__main__":
    main()
