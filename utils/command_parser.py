from typing import Optional
MAX_REQUESTED_MESSAGES = 2000

def parse_analyz_command(text: str) -> Optional[int]:
    """
    Parse /analyz command.

    Returns:
        int: for commands like /analyz 30
        None: for /analyz all
    """
    parts = text.strip().split()

    if len(parts) == 2 and parts[1] == "all":
        return None

    if len(parts) == 2 and parts[1].isdigit():
        count = int(parts[1])

        if count <= 0:
            raise ValueError("Count must be greater than zero.")

        if count > MAX_REQUESTED_MESSAGES:
            raise ValueError(
                f"Maximum allowed count is {MAX_REQUESTED_MESSAGES}."
            )

        return count

    raise ValueError("Invalid command format. Use `/analyz all` or `/analyz 30`")