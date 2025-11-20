# Trip Planner Chatbot 
# --------------------------------------------------------------
# This version fixes the `OSError: [Errno 29] I/O error` that
# occurs in sandboxed/non-interactive environments where
# `input()` is not available. The chatbot now supports three modes:
#  1) Interactive mode (when run in a real terminal)
#  2) Demo (non-interactive) mode — runs a scripted conversation
#  3) Programmatic mode — functions that can be used in unit tests
#
# Usage:
#  - Interactive terminal: `python trip_chatbot.py`
#  - Demo (automated): `python trip_chatbot.py --demo`
#  - Run tests: `python trip_chatbot.py --test`
#
# If you prefer a strictly non-interactive library API (for a web app
# or unit tests), use `get_bot_responses(inputs: List[str]) -> List[str]`.
#
# NOTE FOR THE USER: If the desired behavior for unknown destinations
# or the conversation flow differs from what's implemented below, please
# tell me what you expect (for example: auto-suggest close matches,
# provide booking links, integrate maps, or different exit commands).
# --------------------------------------------------------------

import random
import sys
import argparse
from typing import List

# Sample destinations with data
DESTINATIONS = {
    "goa": {
        "best_time": "November to February",
        "things_to_do": [
            "Visit Baga and Calangute beaches",
            "Water sports",
            "Fort Aguada",
            "Nightlife at Tito's Lane"
        ],
        "budget": "₹15,000 - ₹25,000 for 3-4 days"
    },
    "manali": {
        "best_time": "October to February for snow, March to June for summer trips",
        "things_to_do": [
            "Rohtang Pass",
            "Solang Valley",
            "Mall Road",
            "Hidimba Devi Temple"
        ],
        "budget": "₹12,000 - ₹20,000 for 3-5 days"
    },
    "kerala": {
        "best_time": "September to March",
        "things_to_do": [
            "Backwaters of Alleppey",
            "Munnar tea gardens",
            "Kovalam Beach",
            "Athirappilly Falls"
        ],
        "budget": "₹18,000 - ₹30,000 for 4-6 days"
    }
}

# Greeting messages
GREETINGS = [
    "Hi! I'm your Trip Planner Bot. Where would you like to go?",
    "Hello Traveller! Tell me your dream destination.",
    "Hey! Ready to plan your next adventure? Name a destination."
]

# Unknown response messages
UNKNOWN_RESPONSES = [
    "I don't have information on that destination yet.",
    "Hmm, I'm still learning about that place.",
    "Sorry, I can't find details for that destination. Try another!"
]

EXIT_COMMANDS = {"exit", "quit", "bye", "q"}


def format_trip_for(place_key: str) -> List[str]:
    """Return a list of response lines for a known destination."""
    place = DESTINATIONS[place_key]
    lines = [f"Bot: Here's your trip plan for {place_key.capitalize()}"]
    lines.append(f"Best Time to Visit: {place['best_time']}")
    lines.append("Things to Do:")
    for activity in place["things_to_do"]:
        lines.append(f" - {activity}")
    lines.append(f"Estimated Budget: {place['budget']}")
    return lines


def handle_user_input(user_input: str) -> List[str]:
    """Process a single user_input and return bot response lines.

    This function is programmatic and safe to call from tests.
    """
    if not isinstance(user_input, str):
        return ["Bot: Sorry, I didn't understand that input."]

    user_input = user_input.strip().lower()
    if user_input == "":
        return ["Bot: Please type a destination or 'exit' to quit."]

    if user_input in EXIT_COMMANDS:
        return ["Bot: Safe travels! Have a great day!"]

    if user_input in DESTINATIONS:
        return format_trip_for(user_input)

    # If not found, we return a single helpful message. You can change this
    # behavior to return suggestions or run a fuzzy match.
    return [f"Bot: {random.choice(UNKNOWN_RESPONSES)}"]


def get_bot_responses(inputs: List[str]) -> List[str]:
    """Given a list of user input strings, return a flattened list of bot replies.

    This is convenient for testing and non-interactive runs.
    """
    replies: List[str] = []
    for inp in inputs:
        out_lines = handle_user_input(inp)
        replies.extend(out_lines)
        # If the user asked to exit, stop processing further inputs
        if any(line.startswith("Bot: Safe travels") for line in out_lines):
            break
    return replies


def run_demo():
    """Run a scripted demo conversation (used when input() is not available)."""
    demo_inputs = [
        "Goa",
        "unknowncity",
        "Manali",
        "bye"
    ]
    print("--- Demo mode: simulated conversation (non-interactive) ---")
    print(random.choice(GREETINGS))
    for u in demo_inputs:
        print(f"You: {u}")
        for line in handle_user_input(u):
            print(line)
    print("--- End of demo ---")


def run_interactive():
    """Run the chatbot interactively using input() when available.

    This function gracefully falls back to demo mode if input() is not
    available (for example, in sandboxed execution environments).
    """
    print(random.choice(GREETINGS))

    while True:
        try:
            # In some sandboxed environments input() raises OSError or EOFError.
            user_input = input("You: ")
        except (OSError, EOFError):
            # Fallback to demo mode if interactive input fails.
            print('\nBot: Interactive input is not available in this environment.')
            print("Bot: Switching to demo mode.\n")
            run_demo()
            break

        # Process input and print responses
        responses = handle_user_input(user_input)
        for line in responses:
            print(line)

        # If user requested exit, break
        if any(line.startswith("Bot: Safe travels") for line in responses):
            break


# ------------------ Unit tests / sanity checks ------------------
def _run_tests() -> None:
    """Basic tests to ensure the chatbot logic works."""
    # Test known destination
    res = handle_user_input("goa")
    assert any("Best Time to Visit" in line for line in res), "Goa: missing best time"

    # Test unknown destination
    res2 = handle_user_input("atlantis")
    assert len(res2) == 1 and res2[0].startswith("Bot:"), "Unknown should return a single Bot response"

    # Test exit commands
    for cmd in ["exit", "quit", "bye", "q"]:
        out = handle_user_input(cmd)
        assert out == ["Bot: Safe travels! Have a great day!"], f"Exit command {cmd} failed"

    # Test programmatic flow with multiple inputs
    seq = ["kerala", "unknowncity", "bye", "goa"]  # last "goa" should be ignored after bye
    flat = get_bot_responses(seq)
    assert any("Kerala" in s or "trip plan" in s.lower() for s in flat if isinstance(s, str)), "Kerala response missing"
    assert any(s.startswith("Bot:") for s in flat), "Responses should include Bot lines"

    print("All tests passed.")


# ------------------ CLI entrypoint ------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trip Planner Chatbot")
    parser.add_argument("--demo", action="store_true", help="Run demo (non-interactive) mode")
    parser.add_argument("--test", action="store_true", help="Run basic unit tests and exit")
    parser.add_argument("--no-interactive", action="store_true", help="Never attempt interactive input; use demo instead")
    args = parser.parse_args()

    if args.test:
        _run_tests()
        sys.exit(0)

    # If user explicitly asked for demo, or input isn't a TTY, just demo.
    if args.demo or args.no_interactive or not sys.stdin.isatty():
        run_demo()
    else:
        run_interactive()
