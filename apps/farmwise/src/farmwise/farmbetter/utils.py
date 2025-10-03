def strip_typename(data):
    if isinstance(data, dict):
        return {k: strip_typename(v) for k, v in data.items() if k != "__typename"}
    elif isinstance(data, list):
        return [strip_typename(v) for v in data]
    return data
