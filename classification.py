def classify_local(avg_color):
    r, g, b = avg_color
    if r > g and r > b:
        return "CORROSION"
    return "DAMP"
