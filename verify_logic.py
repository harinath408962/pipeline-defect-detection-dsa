import numpy as np
from core.image_logic import process_image_logic

def create_synthetic_image(type="normal"):
    # 100x100 image
    pixels = np.zeros((100, 100, 3), dtype=np.uint8)
    # Background gray
    pixels[:] = (128, 128, 128)
    
    if type == "crack":
        # Draw a vertical dark line
        # Crack color: dark gray (50, 50, 50)
        # Length 60, Width 2
        for y in range(20, 80):
            pixels[y, 50] = (50, 50, 50)
            pixels[y, 51] = (50, 50, 50)
            pixels[y, 52] = (50, 50, 50) # Width 3 -> 180 px
            
    elif type == "corrosion":
        # Draw a blob
        # Reddish (150, 80, 80)
        # 10x10 square
        for y in range(40, 50):
            for x in range(40, 50):
                pixels[y, x] = (150, 80, 80)
                
    elif type == "invalid":
        # Random high contrast noise
        pixels = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
    return pixels

def run_test():
    print("Running Verification Tests...\n")
    
    # Test 1: Crack
    print("Test 1: Synthetic Crack Image")
    img_crack = create_synthetic_image("crack")
    res1 = process_image_logic(img_crack, 100, 100, "TEST_CRACK")
    print(f"Result: {res1['final_defect']}")
    if res1['final_defect'] == "CRACK": print("[PASS]")
    else: print(f"[FAIL] - Reason: {res1.get('explanation')}")
    print("-" * 30)
    
    # Test 2: Corrosion
    print("Test 2: Synthetic Corrosion Image")
    img_corr = create_synthetic_image("corrosion")
    res2 = process_image_logic(img_corr, 100, 100, "TEST_CORR")
    print(f"Result: {res2['final_defect']}")
    if res2['final_defect'] == "CORROSION": print("[PASS]")
    else: print(f"[FAIL] - Reason: {res2.get('explanation')}")
    print("-" * 30)
    
    # Test 3: Invalid Random Noise
    print("Test 3: Invalid Noise Image")
    img_inv = create_synthetic_image("invalid")
    res3 = process_image_logic(img_inv, 100, 100, "TEST_INV")
    print(f"Result: {res3['final_defect']}")
    if res3['final_defect'] == "INVALID": print("[PASS]")
    else: print(f"[FAIL] - Reason: {res3.get('explanation')}")
    print("-" * 30)
    
    # Test 4: Rusty Wall (High Texture, Valid Color, NO Structure) -> Should Fail Validity
    print("Test 4: Rusty Wall (High Texture, No Direction)")
    img_rust = np.random.randint(50, 150, (100, 100, 3), dtype=np.uint8)
    img_rust[:, :, 0] += 100 
    img_rust = np.clip(img_rust, 0, 255)
    
    res4 = process_image_logic(img_rust, 100, 100, "TEST_RUSTY_WALL")
    print(f"Result: {res4['final_defect']}")
    if res4['final_defect'] == "INVALID": print("[PASS] (Correctly rejected as Wall)")
    else: print(f"[FAIL] - Should be INVALID. Reason: {res4.get('explanation')}")
    print("-" * 30)

    # Test 5: Rusty Pipe (Structured)
    print("Test 5: Rusty Pipe (Structured)")
    img_rust_pipe = np.random.randint(50, 150, (100, 100, 3), dtype=np.uint8)
    img_rust_pipe[:, :, 0] += 100 
    img_rust_pipe = np.clip(img_rust_pipe, 0, 255)
    
    # Add strong horizontal edges (Pipe shape)
    for r in range(0, 100, 10):
        img_rust_pipe[r, :] = (50, 20, 20) # Dark lines
        
    res5 = process_image_logic(img_rust_pipe, 100, 100, "TEST_RUSTY_PIPE")
    print(f"Result: {res5['final_defect']}")
    if res5['final_defect'] != "INVALID": print("[PASS] (Correctly accepted as Pipe)")
    else: print(f"[FAIL] - Reason: {res5.get('explanation')}")
    print("-" * 30)

    # Test 6: Linear Corrosion (Streak) vs Crack
    # A red vertical line should be CORROSION now, not crack.
    print("Test 6: Linear Corrosion (Red Streak)")
    img_streak = np.zeros((100, 100, 3), dtype=np.uint8)
    img_streak[:] = (128, 128, 128)
    # Draw Red Vertical Line
    for y in range(20, 80):
        img_streak[y, 50] = (180, 50, 50)
        img_streak[y, 51] = (180, 50, 50)
        
    # BLUR IT to make it a "Stain" not a Crack
    copy_st = img_streak.astype(float)
    for i in range(2): # Double blur
        for y in range(21, 79):
            for x in range(48, 54):
                 patch = copy_st[max(0, y-1):y+2, max(0, x-1):x+2]
                 copy_st[y, x] = np.mean(patch, axis=(0,1))
    img_streak = copy_st.astype(np.uint8)
        
    res6 = process_image_logic(img_streak, 100, 100, "TEST_STREAK")
    print(f"Result: {res6['final_defect']}")
    if res6['final_defect'] == "CORROSION": print("[PASS] (Correctly identified as Linear Corrosion)")
    else: print(f"[FAIL] - Got {res6['final_defect']}, expected CORROSION")
    print("-" * 30)


    # Test 7: Damp Blob (Dark, Low Saturation)
    print("Test 7: Damp Blob (Dark, Low Saturation)")
    img_damp = np.zeros((100, 100, 3), dtype=np.uint8)
    img_damp[:] = (128, 128, 128)
    # Draw Dark Blob
    for y in range(40, 60):
        for x in range(40, 60):
            img_damp[y, x] = (60, 65, 60) # Dark Greenish/Gray
            
    res7 = process_image_logic(img_damp, 100, 100, "TEST_DAMP")
    print(f"Result: {res7['final_defect']}")
    if res7['final_defect'] == "DAMP": print("[PASS] (Correctly identified as Damp)")
    else: print(f"[FAIL] - Got {res7['final_defect']}, expected DAMP")
    print("-" * 30)

    # Test 8: Damp Linear Streak (Dark, Irregular) vs Crack
    print("Test 8: Damp Linear Streak (Low Rectangularity)")
    img_damp_streak = np.zeros((100, 100, 3), dtype=np.uint8)
    img_damp_streak[:] = (128, 128, 128)
    # Draw Irregular Dark Streak
    for y in range(20, 80):
        img_damp_streak[y, 50] = (90, 90, 90) # Lighter shadow (Damp)
        img_damp_streak[y, 51] = (90, 90, 90)
        if y % 2 == 0: 
            img_damp_streak[y, 52] = (90, 90, 90) 
            img_damp_streak[y, 53] = (90, 90, 90) # Zigzag/Wider
        
    res8 = process_image_logic(img_damp_streak, 100, 100, "TEST_DAMP_STREAK")
    print(f"Result: {res8['final_defect']}")
    # Should be Damp because irregular, or Crack if too linear? 
    # Logic: if rectangularity < 0.4. A zigzag line has low rectangularity compared to bbox.
    if res8['final_defect'] == "DAMP": print("[PASS] (Correctly identified as Damp Streak)")
    else: print(f"[FAIL] - Got {res8['final_defect']}, Reason: {res8.get('explanation')}")
    print("-" * 30)
    
    # Test 9: Normal Pipe (Minor Noise < 1%)
    print("Test 9: Normal Pipe (Minor Noise)")
    img_norm = np.zeros((100, 100, 3), dtype=np.uint8)
    img_norm[:] = (128, 128, 128)
    # Add 5 pixels of noise
    for i in range(5):
        img_norm[i, i] = (0, 0, 0)
        
    res9 = process_image_logic(img_norm, 100, 100, "TEST_NORMAL")
    print(f"Result: {res9['final_defect']}")
    if res9['final_defect'] == "NORMAL": print("[PASS] (Correctly ignored minor noise)")
    else: print(f"[FAIL] - Got {res9['final_defect']}, Reason: {res9.get('explanation')}")
    print("-" * 30)
 
    # Test 10: Shadowy Pipe (Valid but High Defect Coverage ~45%)
    print("Test 10: Shadowy Pipe (High Coverage, Valid)")
    img_shadow = np.zeros((100, 100, 3), dtype=np.uint8)
    img_shadow[:] = (180, 180, 180) # Bright Pipe
    # Huge shadow covering 50%
    img_shadow[50:, :] = (100, 100, 100) # Darker but not "Defect black"
    
    # NOTE: This relies on global threshold. 
    # Avg ~ 140. Shadow (100) is 0.71 of Avg.
    # Current threshold 0.75 WILL mark this as defect.
    # Coverage = 50%.
    # Should be VALID (NORMAL) because it's just a shadow, but Validity Check rejects > 40%.
    
    res10 = process_image_logic(img_shadow, 100, 100, "TEST_SHADOW_PIPE")
    print(f"Result: {res10['final_defect']}")
    if res10['final_defect'] != "INVALID": print("[PASS] (Accepted as Valid Pipe)")
    else: print(f"[FAIL] - Rejected as INVALID. Reason: {res10.get('explanation')}")
    print("-" * 30)

    # Test 11: Dark Sticky Damp vs Crack (Needs Soft Edges)
    print("Test 11: Dark Sticky Damp vs Crack (Soft Edges)")
    img_dark_damp = np.zeros((100, 100, 3), dtype=np.uint8)
    img_dark_damp[:] = (150, 150, 150)
    
    # Draw linear-ish dark blobs then BLUR them manually
    for y in range(20, 80):
         img_dark_damp[y, 50] = (65, 65, 65)
         img_dark_damp[y, 51] = (65, 65, 65)
         img_dark_damp[y, 52] = (65, 65, 65) 
         img_dark_damp[y, 53] = (65, 65, 65) # Width 4
    
    # Simple manual blur to simulate softness
    # Box filter 3x3 approx
    copy_img = img_dark_damp.astype(float)
    for i in range(1): # Repeat for softness
        for y in range(21, 79):
            for x in range(48, 54):
                # blur kernel
                patch = copy_img[y-1:y+2, x-1:x+2]
                copy_img[y, x] = np.mean(patch, axis=(0,1))
    
    img_dark_damp = copy_img.astype(np.uint8)
         
    res11 = process_image_logic(img_dark_damp, 100, 100, "TEST_DARK_DAMP")
    print(f"Result: {res11['final_defect']}")
    if res11['final_defect'] == "DAMP": print("[PASS] (Correctly identified as Damp)")
    else: print(f"[FAIL] - Got {res11['final_defect']} (Likely CRACK)")
    print("-" * 30)

    # Test 12: Brownish Damp vs Corrosion (Soft Edges)
    print("Test 12: Brown Damp vs Corrosion")
    img_brown_damp = np.zeros((100, 100, 3), dtype=np.uint8)
    img_brown_damp[:] = (150, 150, 150)
    # Draw Brownish Blob
    for y in range(40, 60):
        for x in range(40, 60):
            img_brown_damp[y, x] = (100, 90, 80)
            
    # Apply Blur
    copy_img2 = img_brown_damp.astype(float)
    for y in range(39, 61):
        for x in range(39, 61):
             patch = copy_img2[max(0, y-1):y+2, max(0, x-1):x+2]
             copy_img2[y, x] = np.mean(patch, axis=(0,1))
    img_brown_damp = copy_img2.astype(np.uint8)

    res12 = process_image_logic(img_brown_damp, 100, 100, "TEST_BROWN_DAMP")
    print(f"Result: {res12['final_defect']}")
    if res12['final_defect'] == "DAMP": print("[PASS] (Correctly identified as Damp)")
    else: print(f"[FAIL] - Got {res12['final_defect']} (Likely CORROSION)")
    print("-" * 30)
    
    # Test 13: Red "Interior" Pipe (Isotropic Noise but Cylindrical Gradient)
    print("Test 13: Red Interior Pipe (Cylindrical Gradient)")
    img_red_int = np.random.randint(100, 120, (100, 100, 3), dtype=np.uint8) # Noisy Red
    img_red_int[:, :, 0] += 50 # Make it Red
    
    # ADD CYLINDRICAL GRADIENT (Bright Center, Dark Edges)
    # y-axis brightness
    for c in range(100):
        # Parabolic factor: 1.0 at center, 0.5 at edges
        factor = 1.0 - 0.5 * ((c - 50)/50)**2
        img_red_int[:, c, :] = (img_red_int[:, c, :] * factor).astype(np.uint8)
        
    # This image has High Texture (random noise) but a structured gradient.
    # Should PASS Validity despite noise.
    
    res13 = process_image_logic(img_red_int, 100, 100, "TEST_RED_CYLINDER")
    print(f"Result: {res13['final_defect']}")
    # Test 14: Pipe Joint (Perfectly Straight, Dark, Vertical)
    # This should be NORMAL (Joint), not Crack.
    print("Test 14: Pipe Joint (Visible Joint)")
    img_joint = np.zeros((100, 100, 3), dtype=np.uint8)
    img_joint[:] = (180, 180, 180)
    # Draw perfect vertical line (Joint)
    # High rectangularity (Solidity)
    for y in range(0, 100):
        img_joint[y, 50] = (20, 20, 20)
        img_joint[y, 51] = (20, 20, 20)
        
    res14 = process_image_logic(img_joint, 100, 100, "TEST_JOINT")
    print(f"Result: {res14['final_defect']}")
    if res14['final_defect'] == "NORMAL": print("[PASS] (Correctly identified as Joint/Normal)")
    else: print(f"[FAIL] - Got {res14['final_defect']} (Likely CRACK)")
    print("-" * 30)

    # Test 15: Dark Damp Streak (No Blur, just dark)
    # Testing logic without blur to ensure brightness check works
    print("Test 15: Dark Damp (Hard Edge but Light Shadow)")
    img_damp_hard = np.zeros((100, 100, 3), dtype=np.uint8)
    img_damp_hard[:] = (180, 180, 180)
    # Draw streak with brightness 60 (Lighter than crack < 40)
    for y in range(20, 80):
        img_damp_hard[y, 50] = (60, 60, 60)
        img_damp_hard[y, 51] = (60, 60, 60)
        img_damp_hard[y, 52] = (60, 60, 60) # Width 3 -> Area 60 * 3 = 180 > 50
        
    res15 = process_image_logic(img_damp_hard, 100, 100, "TEST_DAMP_HARD")
    print(f"Result: {res15['final_defect']}")
    if res15['final_defect'] == "DAMP": print("[PASS] (Correctly identified as Damp)")
    else: print(f"[FAIL] - Got {res15['final_defect']} (Likely CRACK)")
    print("-" * 30)

    # Test 16: Rusty Crack (Red but Sharp)
    print("Test 16: Rusty Crack (Sharp Red Line)")
    img_rusty_crack = np.zeros((100, 100, 3), dtype=np.uint8)
    img_rusty_crack[:] = (180, 180, 180) # Light background
    # Draw Red Sharp Line (High Contrast)
    for y in range(20, 80):
        img_rusty_crack[y, 50] = (150, 50, 50) # Red
        img_rusty_crack[y, 51] = (150, 50, 50)
        # Background is 180. Crack is 150. Contrast 30.
        # But Red channel diff 30. Blue channel diff 130.
        # Gradients will be huge (130).
        
    res16 = process_image_logic(img_rusty_crack, 100, 100, "TEST_RUSTY_CRACK")
    print(f"Result: {res16['final_defect']}")
    if res16['final_defect'] == "CRACK": print("[PASS] (Correctly identified as Rusty CRACK)")
    else: print(f"[FAIL] - Got {res16['final_defect']} (Likely CORROSION)")
    print("-" * 30)
 
if __name__ == "__main__":
    run_test()
