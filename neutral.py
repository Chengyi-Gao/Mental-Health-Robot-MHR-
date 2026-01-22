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
    voice: str = "Matthew"

    # Timing control (seconds)
    pause_after_statement: float = 1.5
    pause_after_answer: float = 1.5

    # Listening robustness
    listen_retries: int = 2               # number of retries after the first attempt
    retry_prompt: str = "I didn't catch that. Please repeat."
    empty_fallback: str = "No response"

    # Logging
    log_dir: str = "data"
    save_log: bool = True


# Interview content
QUESTIONS: List[Tuple[str, Optional[str]]] = [
    (
        "Hello, my name is Furhat. Thank you for taking the time to speak with me today. "
        "In order to help you the best I can, I will need to ask you some questions. "
        "A simple “yes” or “no” will suffice for most of my questions, and based on your answers "
        "I can then advise which of our specialists you would most benefit working with. "
        "Are you ready to begin?",
        None,
    ),
    ("Ok. My inquiry will now begin. What is your name?", "name"),
    ("Ok. What is your date of birth?", "dob"),
    ("Ok. What is your school email?", "email"),
    ("Ok. Do you wish to seek counseling with your university health services?", "counseling"),
    ("Ok. How would you describe your current circumstances regarding your mental health?", "mental_health"),
    ("Ok. In general, do you consider yourself a happy person?", "happy_general"),
    ("Ok. Compared to most of your peers or friends, do you consider yourself happy?", "happy_comparison"),
    (
        "Ok. Some people are generally very happy. They enjoy life regardless of what is going on, "
        "getting the most out of everything. Does this characterization describe you?",
        "happy_very",
    ),
    (
        "Ok. Some people are generally not very happy. Although they are not depressed, "
        "they never seem as happy as they might be. Does this characterization describe you?",
        "happy_not",
    ),
    (
        "Ok. Thank you for your participation, my inquiry is complete now. Based on your answer, "
        "I believe that I have a specialist that will fit your needs. Would you like me to schedule a meeting for you?",
        "schedule_meeting",
    ),
    ("Ok. No problem. Goodbye!", None),
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
    """
    Connect to Furhat and set voice.
    If connection fails, raise an exception with a clear message.
    """
    try:
        furhat = FurhatRemoteAPI(cfg.host)
        furhat.set_voice(name=cfg.voice)
        return furhat
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to Furhat at host='{cfg.host}'. "
            f"Check that Furhat is running and reachable."
        ) from e


def should_nod(question_text: str) -> bool:
    """Decide whether to perform a neutral nod gesture."""
    return question_text.strip().startswith("Ok.")


def listen_with_retries(
    furhat: FurhatRemoteAPI,
    cfg: Config,
    key: str,
    logs: List[Dict[str, Any]],
) -> str:
    """
    Listen for user response with retries.
    Logs each attempt for traceability.
    """
    attempts_total = 1 + cfg.listen_retries
    for attempt in range(1, attempts_total + 1):
        response = None
        try:
            response = furhat.listen()
        except Exception as e:
            # Log listen exception and continue retrying
            logs.append(
                {
                    "t": utc_now_iso(),
                    "event": "listen_exception",
                    "key": key,
                    "attempt": attempt,
                    "error": repr(e),
                }
            )

        msg = getattr(response, "message", None) if response else None
        msg = msg.strip() if isinstance(msg, str) else ""

        logs.append(
            {
                "t": utc_now_iso(),
                "event": "listen_result",
                "key": key,
                "attempt": attempt,
                "message": msg if msg else None,
            }
        )

        if msg:
            return msg

        # If not last attempt, prompt user to repeat
        if attempt < attempts_total:
            furhat.say(text=cfg.retry_prompt, blocking=True)

    return cfg.empty_fallback


def save_session_log(cfg: Config, session: Dict[str, Any]) -> Optional[str]:
    """Save session data to a JSON file and return the filepath."""
    if not cfg.save_log:
        return None

    ensure_dir(cfg.log_dir)
    filename = safe_filename(prefix="neutral_session", ext=".json")
    filepath = os.path.join(cfg.log_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)

    return filepath


# Main interview flow
def run_interview(cfg: Config) -> Dict[str, Any]:
    """
    Run the neutral interview:
    - Ask questions in order
    - Perform a neutral nod gesture for "Ok." questions
    - Listen and store answers for keyed questions
    - Produce a structured session log
    """
    furhat = connect_robot(cfg)

    answers: Dict[str, str] = {}
    event_logs: List[Dict[str, Any]] = []

    session_meta = {
        "t_start": utc_now_iso(),
        "host": cfg.host,
        "voice": cfg.voice,
        "mode": "neutral",
        "questions_count": len(QUESTIONS),
        "timing": {
            "pause_after_statement": cfg.pause_after_statement,
            "pause_after_answer": cfg.pause_after_answer,
        },
        "listen": {
            "retries": cfg.listen_retries,
            "retry_prompt": cfg.retry_prompt,
            "empty_fallback": cfg.empty_fallback,
        },
    }

    for idx, (question_text, key) in enumerate(QUESTIONS, start=1):
        event_logs.append(
            {
                "t": utc_now_iso(),
                "event": "question_start",
                "index": idx,
                "key": key,
                "text": question_text,
            }
        )

        # Optional neutral gesture
        if should_nod(question_text):
            try:
                furhat.gesture(name="Nod")
                event_logs.append(
                    {"t": utc_now_iso(), "event": "gesture", "name": "Nod", "index": idx}
                )
            except Exception as e:
                event_logs.append(
                    {
                        "t": utc_now_iso(),
                        "event": "gesture_exception",
                        "name": "Nod",
                        "index": idx,
                        "error": repr(e),
                    }
                )

        # Speak question
        furhat.say(text=question_text, blocking=True)

        if key is None:
            # Statement-only: short pause for natural pacing
            time.sleep(cfg.pause_after_statement)
            event_logs.append(
                {"t": utc_now_iso(), "event": "pause", "type": "statement", "sec": cfg.pause_after_statement}
            )
            continue

        # Listen (with retries) and store response
        answer = listen_with_retries(furhat, cfg, key=key, logs=event_logs)
        answers[key] = answer

        # Print for visibility
        print(f"{key.capitalize()} (User's answer): {answer}")

        time.sleep(cfg.pause_after_answer)
        event_logs.append(
            {"t": utc_now_iso(), "event": "pause", "type": "answer", "sec": cfg.pause_after_answer}
        )

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
