import numpy as np

def is_valid_pipe(pixels, width, height, binary_map, trust_roi=False):
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
    
    # CALCULATE EDGE DENSITY (Manual Loop)
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
             
    total_edges = horizontal_edges + vertical_edges
    sampled_pixels = (width // 4) * (height // 4)
    edge_density = total_edges / (2 * sampled_pixels) if sampled_pixels > 0 else 0
    ratio = 0.0
    
    if total_edges > 50: 
        ratio = (horizontal_edges + 1) / (vertical_edges + 1)

    # TRUST ROI CHECK
    # If a Pipe ROI was found (via DFS), we trust it and skip strict texture checks.
    # BUT: We still reject Excessive Structure (Text/Code ~ 0.5)
    if trust_roi:
         if edge_density < 0.45:
             return True, f"Valid Pipe Structure (ROI Confirmed, Density {edge_density:.2f})"
         # Else fall through to specific rejection logic
         
    # RULE 1: NOISE / TEXTURE REJECTION
    
    # ----------------------------------------------------
    # NEW: DIGITAL ARTIFACT CHECK (Screenshots/Dashboards)
    # ----------------------------------------------------
    # Digital images have "Flat" colors (exact duplicates).
    # Natural photos have noise (Gaussian distribution).
    # Check Histogram: If > 15% of pixels are EXACTLY one value (e.g. White).
    
    gray_int = (np.mean(pixels, axis=2)).astype(np.uint8)
    hist, _ = np.histogram(gray_int, bins=256, range=(0,256))
    max_freq = np.max(hist)
    
    if max_freq > total_pixels * 0.15:
         # Found a massive spike (flat background)
         return False, f"INVALID: Digital Artifact Detected (Flat Color Spike coverage {max_freq/total_pixels:.2f}). Likely screenshot/dashboard."

    # ----------------------------------------------------
    # NEW: DIGITAL WALLPAPER CHECK (High Saturation)
    # ----------------------------------------------------
    # Check for Neon colors (High Saturation > 0.9)
    # Vectorized Saturation Calculation
    px_float = pixels.astype(np.float32)
    c_max = np.max(px_float, axis=2)
    c_min = np.min(px_float, axis=2)
    
    # Avoid divide by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        s_map = (c_max - c_min) / c_max
        s_map[c_max == 0] = 0
        
    s_map = np.nan_to_num(s_map)
    
    # Count high saturation pixels
    high_sat_pixels = np.sum(s_map > 0.85)
    if high_sat_pixels > total_pixels * 0.40: # 40% neon/vibrant
         return False, f"INVALID: Digital Wallpaper/Neon Art (High Saturation Coverage {high_sat_pixels/total_pixels:.2f})."

    # ----------------------------------------------------
    # NEW: LOW INFORMATION CHECK (For Flat/Black/White Images)
    # ----------------------------------------------------
    # Compute edge density on the whole image (simplified)
    # If the image is extremely flat (no edges), it's invalid.
    
    gray_full = np.mean(pixels, axis=2)
    gy, gx = np.gradient(gray_full)
    grad_mag_full = np.sqrt(gx**2 + gy**2)
    # Threshold for "Edge"
    edge_mask = grad_mag_full > 10
    global_edge_density = np.sum(edge_mask) / total_pixels
    
    if global_edge_density < 0.01:
        return False, f"INVALID: Low Information (Edge Density {global_edge_density:.4f}). Image is too flat/empty."

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
            pass
            
    # MOVED UP: Manual Gradient Check was here.


        # Stricter Noise Check ONLY if NOT rusty
        # If High Edge Density AND No dominant direction
        # Lowered threshold to 0.10 for non-rusty (smooth pipes should be < 0.05)
        threshold = 0.65 if is_rusty else 0.10
        
        # Isotropic Noise has ratio ~ 1.0. 
        # Narrowed range to allow weak directionality (e.g. 0.7 or 1.3) to pass.
        if edge_density > threshold and 0.8 < ratio < 1.2:
              return False, f"INVALID: High Texture (Density {edge_density:.2f} > {threshold}) & No Direction (Ratio {ratio:.2f}). Rusty={is_rusty}"

        # Previous Check (Defect Coverage) - Relaxed
        # If is_rusty, use narrower rejection zone
        ratio_min = 0.9 if is_rusty else 0.6
        ratio_max = 1.1 if is_rusty else 1.7
        
        # New: If we have moderate texture but purely isotropic, reject it unless it has strong gradient
        if not is_rusty and 0.2 < edge_density <= threshold and 0.9 < ratio < 1.1:
             # Check if we failed cylindrical gradient already
             return False, f"INVALID: Isotropic Texture (Density {edge_density:.2f}), no dominant direction."

        # ----------------------------------------------------
        # NEW: MAN-MADE STRUCTURE CHECK (High Frequency)
        # ----------------------------------------------------
        # Screenshots of text/code have extremely high edge density (> 0.8) in both directions.
        # Pipe surfaces are rarely that busy.
        # Adjusted to 0.4 based on simulation (Text=0.5)
        if edge_density > 0.4:
             # Even if it has direction, it's too noisy to be a clean pipe.
             # Unless it's EXTREMELY rusty? But heavy rust is usually blobbier, not sharp edges everywhere.
             return False, f"INVALID: Excessive Structure (Density {edge_density:.2f}). Likely text, mesh, or non-pipe object."

        if ratio_min < ratio < ratio_max and defect_pixels > total_pixels * 0.55:
             return False, f"INVALID: High entropy (Defects {defect_pixels/total_pixels:.2f}), no dominant direction."

    return True, f"Valid Pipe Structure (Ratio: {ratio:.2f}, Density: {edge_density:.2f})"
