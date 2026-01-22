from defect_detection import rgb_to_binary_map, detect_linear_crack
from region_analysis import dfs
from classification import classify_region
from severity_priority import add_to_priority
from core.validity_check import is_valid_pipe
import numpy as np

def process_image_logic(pixels, width, height, pipe_id):
    
    # ======================================================
    # 0️⃣ PIPE VALIDITY CHECK (MANDATORY)
    # ======================================================
    # We need a preliminary binary map for validity
    binary_map = rgb_to_binary_map(pixels, width, height)
    binary_map_np = np.array(binary_map) # For slicing
    
    is_valid, reason = is_valid_pipe(pixels, width, height, binary_map)
    
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


    # ======================================================
    # 2️⃣ GLOBAL CONSISTENCY CHECK
    # ======================================================
    
    final_defect = "NORMAL"
    explanation = "No significant defects found."
    total_pixels = width * height
    
    # FILTER: NORMAL PIPE CHECK
    # If total defect area is very small (< 1%) AND max defect blob is small (< 100 px),
    # treat as Noise/Normal even if individual regions were classified.
    # treat as Noise/Normal even if individual regions were classified.
    if suspicious_pixels < total_pixels * 0.005 and max_defect_area < 50:
         explanation = "Valid Pipe. Minor anomalies (<0.5%) ignored as noise."
         final_defect = "NORMAL"
    
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

    # Add to Priority Queue
    # Severity Score: Crack=3, Corrosion=2, Damp=1. 
    # Use negative for Min-Heap simulation if needed, or structured object.
    severity_score = 0
    if final_defect == "CRACK": severity_score = 3
    elif final_defect == "CORROSION": severity_score = 2
    elif final_defect == "DAMP": severity_score = 1
    
    # We augment score with affected % for tie-breaking
    full_priority_score = severity_score * 100 + int(affected_percentage)
    
    add_to_priority(pipe_id, final_defect, full_priority_score)

    # ======================================================
    # 3️⃣ SAFE BINARY SAMPLE FOR UI
    # ======================================================
    center = height // 2
    binary_sample = [
        row[:50] for row in binary_map[max(0, center-10):center+10] # Wider sample
    ]

    return {
        "final_defect": final_defect,
        "explanation": explanation,
        "binary_sample": binary_sample,
        "total_pixels": total_pixels,
        "suspicious_pixels": suspicious_pixels,
        "affected_percentage": affected_percentage
    }
