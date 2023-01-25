__all__ = [
    "flag_url",
]

def flag_url(flag_code, size):
    return f"https://www.transformice.com/images/drapeaux/{size}/{flag_code.upper()}.png"
