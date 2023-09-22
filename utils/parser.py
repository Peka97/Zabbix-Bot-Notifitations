def parse_data(data: dict) -> (dict | None, dict | None):
    errors = []
    root = data.get("root")

    try:
        settings = root.get("settings")
    except Exception:
        settings = None
        errors.append("settings")

    try:
        text = root.get("body").get("messages")
    except Exception:
        text = None
        errors.append("messages")

    return settings, text, errors
