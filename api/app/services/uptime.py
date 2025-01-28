def format_uptime(seconds):
    """Formats the given number of seconds into a human-readable string.

    Args:
        seconds (int): The number of seconds to format.

    Returns:
        str: A human-readable string representation of the given number of seconds.
    """
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")

    return " ".join(parts)
