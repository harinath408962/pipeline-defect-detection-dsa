import numpy as np

def is_valid_pipe(pixels, width, height, binary_map):
    """
    Determines if the image is likely a pipe based on structural continuity and noise distribution.
    Returns: (is_valid: bool, reason: str)
    """
    
    total_pixels = width * height
    defect_pixels = 0
    
    for r in range(height):
        for c in range(width):
            if binary_map[r][c] == 1:
                defect_pixels += 1
                
    
    # Check for Rust Color Dominance (Simple Avg)
    # Perform this early to adjust thresholds
    center_region = pixels[height//4 : 3*height//4, width//4 : 3*width//4]
    if center_region.size > 0:
         avg_r = np.mean(center_region[:,:,0])
         avg_g = np.mean(center_region[:,:,1])
         avg_b = np.mean(center_region[:,:,2])
         
         # Red dominant and warm colors
         is_rusty = (avg_r > avg_g + 10) and (avg_r > avg_b + 10)
    else:
         is_rusty = False

    # ----------------------------------------------------
    # NEW: CYLINDRICAL GRADIENT CHECK (For Red/Glossy Pipes)
    # ----------------------------------------------------
    # Valid pipes often have a "highlight" in the center and darker edges (Cylinder).
    # Walls are usually flat or random.
    # If we detect a strong "Cylindrical Profile", we VALIDATE immediately, skipping noise checks.
    
    def check_cylindrical_gradient(px):
        # Convert to grayscale
        gray = np.mean(px, axis=2)
        h, w = gray.shape
        
        # Check Vertical Profile (Average of Columns) - for Horizontal Pipe
        col_profile = np.mean(gray, axis=0)
        # Check Horizontal Profile (Average of Rows) - for Vertical Pipe
        row_profile = np.mean(gray, axis=1)
        
        # Logic: Center should be brighter than edges (Highlight)
        # OR Center should be darker than edges (if inside lit from end? rare)
        # We assume standard external lighting: Convex Cylinder -> Center Bright.
        
        def is_convex(profile):
            if len(profile) < 10: return False
            center_idx = len(profile) // 2
            edge_l = np.mean(profile[:len(profile)//4])
            edge_r = np.mean(profile[3*len(profile)//4:])
            center_val = np.mean(profile[center_idx-5:center_idx+5])
            
            # Significant highlight?
            return center_val > (edge_l + 15) and center_val > (edge_r + 15)

        return is_convex(col_profile) or is_convex(row_profile)

    if check_cylindrical_gradient(pixels):
         return True, "Valid Pipe Structure (Cylindrical Gradient Detected)"
         
    # RULE 1: NOISE / TEXTURE REJECTION

    # RULE 1: NOISE / TEXTURE REJECTION
    # If using purely coverage, we might reject heavy corrosion.
    # If is_rusty is True, we SKIP the coverage check and rely on Structural Direction (Rule 2)
    # because a rusty pipe is basically "100% defect" by color, but should have structure.
    
    if not is_rusty:
        if defect_pixels > total_pixels * 0.8:
            return False, "INVALID: Too much noise/texture (>80% coverage). Likely not a pipe."
    
    # Check Horizontal Runs (sampled)
    for r in range(0, height, 5): # skip every 5 lines for speed
        current_run = 0
        for c in range(width):
            # We look for continuity in the PIXELS, not just binary map.
            # But let's use binary map "edges" or just simple brightness continuity?
            # Requirement: "Spatial continuity... Directional consistency"
            # Let's check for long continuous standard-deviation-low regions?
            # Simpler: Valid pipes often have long edges (shadow/highlight).
            # Let's check the binary map for large connected components (we effectively do this in region analysis).
            # But here we need a quick check.
            pass

    # Better approach for "Pipe Validity":
    # A pipe image usually has dominant gradient direction (the curve of the pipe).
    # Walls have isotropic gradients.
    
    # Let's count "Edge" pixels using a valid manual gradient check.
    edge_pixels = 0
    vertical_edges = 0
    horizontal_edges = 0
    
    for r in range(1, height-1, 4):
        for c in range(1, width-1, 4):
             # Simple Sobel-like manual check
             # Cast to int32 to avoid uint8 overflow
             p_center = np.sum(pixels[r,c], dtype=np.int32)
             p_right = np.sum(pixels[r, c+1], dtype=np.int32)
             p_down = np.sum(pixels[r+1, c], dtype=np.int32)
             
             dx = abs(p_right - p_center)
             dy = abs(p_down - p_center)
             
             if dx > 40: horizontal_edges += 1
             if dy > 40: vertical_edges += 1
             
    # If edges are totally random (ratio close to 1:1) and high count -> texture.
    # If dominant direction -> Pipe/Cylinder.
    
    total_edges = horizontal_edges + vertical_edges
    # Sampled area approx (width/4 * height/4).
    sampled_pixels = (width // 4) * (height // 4)
    edge_density = total_edges / (2 * sampled_pixels) if sampled_pixels > 0 else 0
    ratio = 0.0
    
    if total_edges > 50: # If significant structure exists
        ratio = (horizontal_edges + 1) / (vertical_edges + 1)
        
        # Color Check moved to top


        # Stricter Noise Check ONLY if NOT rusty
        # If High Edge Density (e.g. > 50% of pixels) AND No dominant direction
        threshold = 0.65 if is_rusty else 0.35
        
        # Isotropic Noise has ratio ~ 1.0. 
        # Narrowed range to allow weak directionality (e.g. 0.7 or 1.3) to pass.
        if edge_density > threshold and 0.8 < ratio < 1.2:
              return False, f"INVALID: High Texture (Density {edge_density:.2f} > {threshold}) & No Direction (Ratio {ratio:.2f}). Rusty={is_rusty}"

        # Previous Check (Defect Coverage) - Relaxed
        # If is_rusty, use narrower rejection zone
        ratio_min = 0.9 if is_rusty else 0.6
        ratio_max = 1.1 if is_rusty else 1.7
        
        if ratio_min < ratio < ratio_max and defect_pixels > total_pixels * 0.55:
             return False, f"INVALID: High entropy (Defects {defect_pixels/total_pixels:.2f}), no dominant direction."

    return True, f"Valid Pipe Structure (Ratio: {ratio:.2f}, Density: {edge_density:.2f})"
