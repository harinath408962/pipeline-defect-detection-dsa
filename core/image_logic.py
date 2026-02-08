from defect_detection import rgb_to_binary_map, detect_linear_crack
from region_analysis import dfs
from classification import classify_region
from severity_priority import add_to_priority
from core.validity_check import is_valid_pipe
from core.roi_extraction import extract_pipe_roi
# from classification import classify_defect # Removed invalid import
import heapq
import numpy as np

def process_image_logic(pixels, width, height, pipe_id):
    """
    Orchestrates the entire Image Processing Pipeline (DSA Style).
    Steps:
    1. ROI Extraction (DFS) - Find the Pipe Object.
    2. Validity Check - Is it a pipe surface?
    3. Defect Detection - Global Thresholding / Morphology.
    4. Region Analysis - DFS for Connected Components.
    5. Priority Queue - Rank defects.
    """
    
    # 1. ROI EXTRACTION (NEW: Look for Pipe First)
    roi_mask, is_valid_roi, roi_reason = extract_pipe_roi(pixels, width, height)
    
    if not is_valid_roi:
         return {
            "final_defect": "INVALID",
            "explanation": roi_reason,
            "binary_sample": np.zeros((20, 40), dtype=np.uint8), # Empty
            "total_pixels": width * height,
            "suspicious_pixels": 0,
            "affected_percentage": 0.0
        }
        
    # 2. VALIDITY CHECK (Structure/Texture)
    # We pass the original pixels, but ideally we should only check inside ROI.
    # For now, since ROI validation passed, we assume the image IS the pipe.
    # We need a preliminary binary map for validity
    binary_map = rgb_to_binary_map(pixels, width, height)
    binary_map_np = np.array(binary_map) # For slicing
    
    is_valid, reason = is_valid_pipe(pixels, width, height, binary_map, trust_roi=is_valid_roi)
    
    if not is_valid:
         return {
            "final_defect": "INVALID",
            "explanation": reason,
            "binary_sample": [[0]*20 for _ in range(10)], # Empty placeholder
            "total_pixels": width * height,
            "suspicious_pixels": 0,
            "affected_percentage": 0.0
        }

    # ======================================================
    # 1️⃣ REGION ANALYSIS & CLASSIFICATION (MULTI-STAGE)
    # ======================================================
    visited = [[False]*width for _ in range(height)]

    total_length = 0
    regions_count = 0
    suspicious_pixels = 0
    
    defect_counts = {"CRACK": 0, "CORROSION": 0, "DAMP": 0, "NORMAL": 0}
    max_defect_area = 0
    
    # Tracking for UI Sample
    best_defect_score = -1 # Normal=0, Damp=1, Corr=2, Crack=3
    best_sample_coords = (height//2, width//2) # Default center

    for r in range(height):
        for c in range(width):
            if binary_map[r][c] == 1 and not visited[r][c]:
                # DSA: Extract Region (Connected Components)
                area, length, avg_color, mi, mj, Ma, Mb, rectangularity = dfs(
                    binary_map, pixels, visited, r, c, height, width
                )

                suspicious_pixels += area
                regions_count += 1
                total_length += length
                
                # DSA: Classify Region (Geometry > Color)
                bbox_w = (Mb - mj) + 1
                bbox_h = (Ma - mi) + 1
                
                # NEW: Calculate Edge Softness / Gradient Magnitude for this region
                # helps distinguish Sharp Crack vs Soft Damp
                
                # 1. Extract ROI with Context (Margin=2)
                # We need context to see the edge contrast!
                margin = 2
                mi_p = max(0, mi - margin)
                Ma_p = min(height, Ma + margin + 1) # +1 for slice exclusive
                mj_p = max(0, mj - margin)
                Mb_p = min(width, Mb + margin + 1)
                
                roi_pixels = pixels[mi_p:Ma_p, mj_p:Mb_p]
                
                avg_gradient = 0
                if roi_pixels.shape[0] > 1 and roi_pixels.shape[1] > 1:
                     try:
                        roi_gray = np.mean(roi_pixels, axis=2)
                        gy, gx = np.gradient(roi_gray)
                        grad_mag = np.sqrt(gx**2 + gy**2)
                        
                        # We want the gradient ON THE DEFECT pixels.
                        # We need the mask aligned with this expanded ROI.
                        roi_mask_full = binary_map_np[mi_p:Ma_p, mj_p:Mb_p]
                        
                        defect_grads = grad_mag[roi_mask_full == 1]
                        
                        if defect_grads.size > 0:
                            avg_gradient = np.max(defect_grads)
                            
                     except ValueError:
                        pass # Dimensions too small

                # 3. Check for PIPE JOINT (Full span straight line)
                # If Rectangularity > 0.75 AND it spans > 80% of width or height
                is_full_span = (bbox_w > width * 0.8) or (bbox_h > height * 0.8)
                if rectangularity > 0.75 and is_full_span:
                     # Skip classification, count as Normal/Structure
                     # Do not increment defect_counts
                     continue
                
                local_defect = classify_region(area, bbox_w, bbox_h, avg_color, rectangularity, avg_gradient)
                if area > 50: # Ignore noise specs (was 10, now 50 for Normal Pipe robustness)
                    defect_counts[local_defect] += 1
                    max_defect_area = max(max_defect_area, area)
                    
                    # Update Best Sample Coords
                    current_score = 0
                    if local_defect == "CRACK": current_score = 3
                    elif local_defect == "CORROSION": current_score = 2
                    elif local_defect == "DAMP": current_score = 1
                    
                    # Center of Bounding Box
                    center_r = mi + bbox_h // 2
                    center_c = mj + bbox_w // 2

                    if current_score > best_defect_score:
                        best_defect_score = current_score
                        best_sample_coords = (center_r, center_c)
                        
                    elif current_score == best_defect_score and area > max_defect_area:
                         best_sample_coords = (center_r, center_c)


    # ======================================================
    # 2️⃣ GLOBAL CONSISTENCY CHECK
    # ======================================================
    
    final_defect = "HEALTHY"
    explanation = "Healthy Pipe. No significant defects found."
    total_pixels = width * height
    
    # FILTER: NORMAL PIPE CHECK
    # If total defect area is very small (< 1%) AND max defect blob is small (< 100 px),
    # treat as Noise/Normal even if individual regions were classified.
    # treat as Noise/Normal even if individual regions were classified.
    if suspicious_pixels < total_pixels * 0.005 and max_defect_area < 50:
         explanation = "Healthy Pipe. Minor anomalies (<0.5%) ignored as noise."
         final_defect = "HEALTHY"
    
    # Priority Logic (Only if passed Normal Filter)
    elif defect_counts["CRACK"] > 0:
        final_defect = "CRACK"
        explanation = f"CRACK Detected! Found {defect_counts['CRACK']} linear region(s). Geometry: High Aspect Ratio."
        
    elif defect_counts["CORROSION"] > 0:
        final_defect = "CORROSION"
        explanation = f"CORROSION Detected. Found {defect_counts['CORROSION']} irregular region(s). Geometry: High Solidity + Red/Brown Color."
        
    elif defect_counts["DAMP"] > 0:
        final_defect = "DAMP"
        explanation = f"DAMP Detected. Found {defect_counts['DAMP']} spread region(s). Geometry: Low Continuity + Dark/Desaturated."
    
    elif suspicious_pixels > 0:
         explanation = "Minor anomalies detected but classified as Normal/Noise."

    total_pixels = width * height
    affected_percentage = round((suspicious_pixels / total_pixels) * 100, 2)

    # Priority Logic (Only if passed Normal Filter)
    # Severity Score: Crack=3, Corrosion=2, Damp=1. 
    severity_score = 0
    if final_defect == "CRACK": severity_score = 3
    elif final_defect == "CORROSION": severity_score = 2
    elif final_defect == "DAMP": severity_score = 1
    
    # We augment score with affected % for tie-breaking
    # Format: 300XX (Score 3, XX%)
    full_priority_score = (severity_score * 1000) + int(affected_percentage * 10)
    
    # Return directly, no external side effect
    pass

    # ======================================================
    # 3️⃣ DYNAMIC BINARY SAMPLE (Focus on Defect)
    # ======================================================
    
    def optimize_sample_window(bin_map, start_coords, h, w):
        """
        If the default window is all 1s (solid defect) or all 0s, 
        search nearby for a window with useful information (edges).
        Target: Window with sum/area closest to 0.5 (max entropy).
        """
        initial_r, initial_c = start_coords
        best_r, best_c = initial_r, initial_c
        best_score = 0
        
        # Search radius and stride
        search_radius = 60
        stride = 20
        
        # Define window size
        win_h, win_w = 20, 50
        
        # Candidates: Center + Spiral
        candidates = [(0,0)]
        for d in range(stride, search_radius + 1, stride):
            candidates.extend([(d, 0), (-d, 0), (0, d), (0, -d), (d, d), (d, -d), (-d, d), (-d, -d)])
            
        for dr, dc in candidates:
            r = initial_r + dr
            c = initial_c + dc
            
            # Bounds check
            if r < 0 or r >= h or c < 0 or c >= w:
                continue
                
            # Window check
            sr_i = max(0, r - win_h // 2)
            er_i = min(h, sr_i + win_h)
            sc_i = max(0, c - win_w // 2)
            ec_i = min(w, sc_i + win_w)
            
            if (er_i - sr_i) < 5 or (ec_i - sc_i) < 5: 
                continue
                
            window = bin_map[sr_i:er_i, sc_i:ec_i]
            if window.size == 0: continue
            
            fill_ratio = np.sum(window) / window.size
            
            # Score: We want closest to 0.5 (Edge)
            # 1.0 = Bad (Solid), 0.0 = Bad (Empty)
            # Distance from 0.5: abs(0.5 - fill_ratio)
            # Score = 0.5 - abs(0.5 - fill_ratio) => Max 0.5
            
            # Bonus: Prefer closer to original center
            dist_penalty = (abs(dr) + abs(dc)) * 0.0001
            
            score = (0.5 - abs(0.5 - fill_ratio)) - dist_penalty
            
            if score > best_score:
                best_score = score
                best_r, best_c = r, c
                
        # If we failed to find anything better than solid block, return original
        # But best_score initialized to 0 handles "All 0 or All 1" case having score 0.
        # If initial is solid (score 0), almost any edge (score > 0) will win.
        return best_r, best_c

    sr, sc = optimize_sample_window(binary_map_np, best_sample_coords, height, width)
    
    # Ensure bounds
    # We want a 20x50 sample window approx
    # Center it on (sr, sc)
    
    start_r = max(0, sr - 10)
    end_r = min(height, start_r + 20)
    
    start_c = max(0, sc - 25)
    end_c = min(width, start_c + 50)
    
    # Adjust if window is too small (e.g. near bottom/right edge)
    if end_r - start_r < 20 and start_r > 0:
        start_r = max(0, end_r - 20)
    if end_c - start_c < 50 and start_c > 0:
        start_c = max(0, end_c - 50)
        
    binary_sample = []
    for r_idx in range(start_r, end_r):
         binary_sample.append(binary_map_np[r_idx, start_c:end_c].tolist())
         
    # Pad if necessary (rare, but for safety)
    while len(binary_sample) < 20:
        binary_sample.append([0]*50)

    return {
        "final_defect": final_defect,
        "explanation": explanation,
        "binary_sample": binary_sample,
        "total_pixels": total_pixels,
        "suspicious_pixels": suspicious_pixels,
        "affected_percentage": affected_percentage,
        "priority_score": full_priority_score
    }
