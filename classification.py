def classify_local(avg_color):
    r, g, b = avg_color
    brightness = (r + g + b) / 3

    # Crack color rule (dark + low variance)
    if (
        brightness <= 80 and
        abs(r - g) <= 15 and
        abs(g - b) <= 15 and
        abs(r - b) <= 15
    ):
        return "CRACK"

    # Corrosion rule
    if r >= 120 and g >= 60 and b <= 100:
        return "CORROSION"

    return "NORMAL"

