def classify_region(area, bbox_width, bbox_height, avg_color, rectangularity, avg_gradient=20):
    r, g, b = avg_color
    
    # ============================
    # 0. CALCULATE GEOMETRY
    # ============================
    aspect_ratio = max(bbox_width, bbox_height) / max(1, min(bbox_width, bbox_height))

    # ============================
    # 0. BIO/ALGAE CHECK (Green Dominance)
    # ============================
    # Green is dominant and significantly brighter than Red/Blue
    # This overrides everything as Algae = DAMP/BIO
    if g > r + 15 and g > b + 15 and g > 60:
         return "DAMP" 

    # ============================
    # 1. GLOBAL SOFTNESS CHECK (Priority)
    # ============================
    # Soft edges (Low Gradient) indicate Shadows, Dampness, or Out-of-focus background.
    
    is_soft = avg_gradient < 15
    
    if is_soft:
        # EXCEPTION 1: If it is RED/RUSTY/ORANGE
        # Relaxed for Internal Corrosion (Orange/Yellow)
        # Old: (r > g + 10 and r > b + 10)
        # New: Warm colors (R likely max, or R~G for yellow)
        is_warm = (r > b + 20) and (r > 50)
        
        if is_warm:
             # If it is LINEAR (Aspect Ratio > 3.0), it's likely a Rusty Crack even if softish.
             # Only call it "Corrosion Stain" if it is VERY soft (< 10) OR Not Linear.
             if aspect_ratio > 3.0:
                 if avg_gradient < 8: return "CORROSION" # Very soft streak
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
         
    # CORROSION check
    r, g, b = avg_color
    is_red_dominant = (r > g + 15) and (r > b + 15)
    
    # Internal Corrosion: Bright Orange/Yellow (R~G > B)
    # e.g. R=200, G=180, B=50
    is_yellow_corrosion = (r > 100) and (g > 80) and (b < 100) and (abs(int(r)-int(g)) < 40)
    
    c_max = max(r, g, b)
    c_min = min(r, g, b)
    s = (c_max - c_min) / c_max if c_max != 0 else 0
    avg_brightness = (r + g + b) / 3

    if area > 20 and avg_brightness > 40:
        # Strict Color Check for Rust
        if is_red_dominant or is_yellow_corrosion:
            return "CORROSION"
        if s > 0.35 and r > 90: # High Saturation Orange/Yellow/Red
            return "CORROSION"
            
    # DAMP: Default
    # Dark blobs, soft streaks, or low saturation.
    return "DAMP"
            
    return "NORMAL"
