def classify_region(area, bbox_width, bbox_height, avg_color, rectangularity, avg_gradient=20):
    r, g, b = avg_color
    
    # ============================
    # 0. CALCULATE GEOMETRY
    # ============================
    aspect_ratio = max(bbox_width, bbox_height) / max(1, min(bbox_width, bbox_height))

    # ============================
    # 1. GLOBAL SOFTNESS CHECK (Priority)
    # ============================
    # Soft edges (Low Gradient) indicate Shadows, Dampness, or Out-of-focus background.
    
    is_soft = avg_gradient < 15
    
    if is_soft:
        # EXCEPTION 1: If it is RED/RUSTY
        if (r > g + 10 and r > b + 10) or (r > 100 and g < 80):
             # If it is LINEAR (Aspect Ratio > 3.0), it's likely a Rusty Crack even if softish.
             # Only call it "Corrosion Stain" if it is VERY soft (< 10) OR Not Linear.
             if aspect_ratio > 3.0:
                 if avg_gradient < 10: return "CORROSION"
                 return "CRACK" # Rusty Linear Crack (Soft but not too soft)
             else:
                 return "CORROSION" # Blobby soft stain
             
        # EXCEPTION 2: Straight Soft Line -> Shadow/Joint -> Normal
        if rectangularity > 0.60:
            return "NORMAL"
        # EXCEPTION 3: Irregular -> Damp
        return "DAMP"

    # ============================
    # 2. GEOMETRY (CRACK vs REST)
    # ============================
    
    # CRACK: Long, thin, high aspect ratio.
    if aspect_ratio > 3.0:
        
        # CHECK EXCEPTION: RUST STREAK (Red/Brown)
        # Corrosion needs Red Dominance
        # BUT: If it is very SHARP, it is a Rusty Crack, not a diffuse stain.
        if (r > g + 10 and r > b + 10) or (r > 100 and g < 80):
             if avg_gradient < 15: # Stricter: Only soft streaks are Corrosion
                 return "CORROSION"
             # If Sharp (>15), treat as Rusty Crack
             return "CRACK"
             
        # CHECK EXCEPTION: DAMP STREAK (Not strictly deep dark)
        # We handle "Light Crack" vs "Dark Crack"
        # True cracks are usually very dark (< 50)
        avg_brightness = (r + g + b) / 3
        if avg_brightness > 55:
             # Too light to be a deep crack, unless super sharp
             if avg_gradient < 30:
                 return "DAMP"
                 
        return "CRACK"
        
    # ============================
    # 2. BLOB ANALYSIS (CORROSION vs DAMP)
    # ============================
    
    # CORROSION needs High Saturation or Strong Red
    is_red_dominant = (r > g + 15) and (r > b + 15)
    
    # Calculate Saturation
    c_max = max(r, g, b)
    c_min = min(r, g, b)
    s = (c_max - c_min) / c_max if c_max != 0 else 0

    if area > 20:
        # Check for Corrosion (Rust)
        # Stricter: Brightness > 60 (Rust is bright oxide) AND (High Sat OR Red Dom)
        avg_brightness = (r + g + b) / 3
        
        if avg_brightness > 60:
            if is_red_dominant or (s > 0.4 and r > 100):
                return "CORROSION"
            
        # DAMP needs Low Saturation (relative to Rust) + Darker/Brownish
        # Or just default to Damp if not Corrosion
        return "DAMP"
            
    return "NORMAL"
