def classify_local(avg_color):
    r, g, b = avg_color

    if r > 140 and g < 100:
        return "CORROSION"
    elif r < 100 and g < 100:
        return "CRACK"
    else:
        return "DAMP"
