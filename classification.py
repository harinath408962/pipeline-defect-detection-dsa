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
    # 2. GEOMETRY & SHARPNESS CHECK
    # ============================
    
    # 1. LINEARITY
    # Standard: High Aspect Ratio (> 3.5)
    # Diagonal: Low Rectangularity/Solidity (< 0.22) because a diagonal line fills little of its square bbox.
    is_linear = (aspect_ratio > 3.5) or (rectangularity < 0.22)
    
    # 2. SHARPNESS
    # Cracks have sharp edges (High Gradient).
    # Damp streaks have soft edges (Low Gradient).
    # Corrosion is rough (High Texture) but often irregular.
    # Raised to 25 to reject soft damp/dust streaks.
    is_sharp = avg_gradient > 25
    
    # ============================
    # 3. CLASSIFICATION LOGIC
    # ============================
    
    # CRACK: Linear AND Sharp.
    # We prioritize this over Color because a "Rusty Crack" is still a Crack.
    if is_linear and is_sharp:
         return "CRACK"
         
    # CORROSION: Red/Saturated AND Not Linear
    r, g, b = avg_color
    is_red_dominant = (r > g + 15) and (r > b + 15)
    
    c_max = max(r, g, b)
    c_min = min(r, g, b)
    s = (c_max - c_min) / c_max if c_max != 0 else 0
    avg_brightness = (r + g + b) / 3

    if area > 20 and avg_brightness > 50:
        # Strict Color Check for Rust
        if is_red_dominant:
            return "CORROSION"
        if s > 0.4 and r > 100: # High Saturation Orange/Yellow
            return "CORROSION"
            
    # DAMP: Default
    # Dark blobs, soft streaks, or low saturation.
    return "DAMP"
            
    return "NORMAL"
