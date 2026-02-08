
import sys
import os
import numpy as np
from core.image_logic import process_image_logic

def test_black_image():
    print("Testing Black Image (100x100)...")
    width, height = 100, 100
    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    try:
        result = process_image_logic(pixels, width, height, "TEST_BLACK")
        print(f"Result: {result['final_defect']}")
        print(f"Explanation: {result['explanation']}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

def test_white_image():
    print("\nTesting White Image (100x100)...")
    width, height = 100, 100
    pixels = np.ones((height, width, 3), dtype=np.uint8) * 255
    try:
        result = process_image_logic(pixels, width, height, "TEST_WHITE")
        print(f"Result: {result['final_defect']}")
        print(f"Explanation: {result['explanation']}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

def test_random_noise():
    print("\nTesting Random Noise (100x100)...")
    width, height = 100, 100
    pixels = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    try:
        result = process_image_logic(pixels, width, height, "TEST_NOISE")
        print(f"Result: {result['final_defect']}")
        print(f"Explanation: {result['explanation']}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

def test_crack_sample():
    print("\nTesting Crack Sample (Visualization Check)...")
    width, height = 200, 200
    # Add noise to pass "Low Information" check (Edge Density > 0.01)
    pixels = np.random.randint(180, 220, (height, width, 3), dtype=np.uint8) 
    # pixels = np.ones((height, width, 3), dtype=np.uint8) * 200 # Light gray background
    
    # Draw a vertical crack at (150, 150) - clearly OUTSIDE the default center (100, 100)
    # Default sample window is rows 90-110.
    # Our crack is at rows 50-150 (Length 100 > 50 threshold).
    for r in range(50, 150):
        pixels[r, 150] = [20, 20, 20] # Dark pixel
        
    try:
        result = process_image_logic(pixels, width, height, "TEST_CRACK")
        print(f"Result: {result['final_defect']}")
        
        # Check binary sample for 1s
        sample = result['binary_sample']
        has_defect = any(1 in row for row in sample)
        print(f"Sample contains defect (1s): {has_defect}")
        if not has_defect:
            print("FAILURE: Sample is all zeros but crack exists!")
            # print sample for debug
            for row in sample:
                print(row)
        else:
             print("SUCCESS: Sample correctly captured the crack.")
             
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

def test_text_screenshot():
    print("\nTesting Text/Code Screenshot (High Freq pattern)...")
    width, height = 200, 200
    pixels = np.zeros((height, width, 3), dtype=np.uint8) 
    
    # Simulate Dense Text / Code: Lines every 4 pixels
    for r in range(0, height, 4):
        # Line of text
        pixels[r:r+2, 0:width] = [255, 255, 255]
        # Simulate characters (vertical gaps)
        for c in range(0, width, 4):
            pixels[r:r+2, c] = [0, 0, 0]
        
    try:
        result = process_image_logic(pixels, width, height, "TEST_TEXT")
        print(f"Result: {result['final_defect']}")
        print(f"Explanation: {result['explanation']}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

def test_roi_failure():
    print("\nTesting ROI Extraction (Scattered Text)...")
    width, height = 200, 200
    pixels = np.zeros((height, width, 3), dtype=np.uint8) 
    
    # Simulate Scattered Text (No large component)
    # Patches at random
    import random
    for i in range(50):
        r = random.randint(0, height-20)
        c = random.randint(0, width-20)
        # Small patch (character)
        pixels[r:r+10, c:c+10] = [200, 200, 200]
        
    try:
        result = process_image_logic(pixels, width, height, "TEST_ROI")
        print(f"Result: {result['final_defect']}")
        print(f"Explanation: {result['explanation']}")
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

def test_classification_logic_sim():
    print("\nTesting Classification Logic Simulation...")
    from classification import classify_region
    
    # CASE 1: DIAGONAL CRACK (Square Box, Low Rectangularity, Sharp)
    # Increased Gradient to 26 to pass > 25 threshold
    res = classify_region(area=15, bbox_width=10, bbox_height=10, avg_color=(50,50,50), rectangularity=0.15, avg_gradient=26)
    print(f"1. Diagonal Crack (Rect=0.15, Grad=26): {res} (Exp: CRACK)", flush=True)
    
    # CASE 2: SOFT LINEAR STREAK (Long Box, Soft Edge)
    res = classify_region(area=100, bbox_width=30, bbox_height=5, avg_color=(60,60,60), rectangularity=0.6, avg_gradient=10)
    print(f"2. Soft Linear Streak (AR=6.0, Grad=10): {res} (Exp: DAMP)", flush=True)
    
    # CASE 3: RUSTY CRACK (Line, Sharp, Red)
    res = classify_region(area=50, bbox_width=50, bbox_height=10, avg_color=(150,50,50), rectangularity=0.5, avg_gradient=30)
    print(f"3. Rusty Crack (AR=5.0, Grad=30, Red): {res} (Exp: CRACK)", flush=True)
    
    # CASE 4: CORROSION BLOB (Square, Blob, Red)
    res = classify_region(area=80, bbox_width=10, bbox_height=10, avg_color=(150,50,50), rectangularity=0.8, avg_gradient=20)
    print(f"4. Corrosion Blob (Rect=0.8, Red): {res} (Exp: CORROSION)", flush=True)

    # CASE 5: DUST STREAK (Linear but Soft)
    # Long Box, High Rect (Streak), but Gradient < 25
    res = classify_region(area=100, bbox_width=40, bbox_height=5, avg_color=(30,30,30), rectangularity=0.4, avg_gradient=18)
    print(f"5. Dust Streak (Grad=18 < 25): {res} (Exp: DAMP)", flush=True)
    
    # CASE 6: REAL CRACK (Linear and Very Sharp)
    # Gradient > 25
    res = classify_region(area=100, bbox_width=40, bbox_height=5, avg_color=(30,30,30), rectangularity=0.4, avg_gradient=30)
    print(f"6. Real Crack (Grad=30 > 25): {res} (Exp: CRACK)", flush=True)
    
def test_histogram_logic():
    print("\nTesting Histogram Logic (Simulation)...", flush=True)
    import numpy as np
    
    # Create Simulated Dashboard (Flat White Background 80%)
    h, w = 100, 100
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = [255, 255, 255] # All White
    
    # Add some "Text" noise
    img[40:60, 40:60] = [0, 0, 0] 
    
    gray_int = (np.mean(img, axis=2)).astype(np.uint8)
    hist, _ = np.histogram(gray_int, bins=256, range=(0,256))
    max_freq = np.max(hist)
    
    ratio = max_freq / (h*w)
    print(f"Dashboard Ratio: {ratio:.2f} (Exp: > 0.15)", flush=True)
    
    if ratio > 0.15:
        print("RESULT: REJECTED (Correct)", flush=True)
    else:
        print("RESULT: ACCEPTED (Incorrect)", flush=True)

def test_neon_wallpaper():
    print("\nTesting Neon Wallpaper (High Saturation)...", flush=True)
    width, height = 100, 100
    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 50% Pink (255, 0, 255)
    pixels[:, :50] = [255, 0, 255] 
    # 50% Green (0, 255, 0)
    pixels[:, 50:] = [0, 255, 0]   
    
    try:
        result = process_image_logic(pixels, width, height, "TEST_NEON")
        print(f"Result: {result['final_defect']}", flush=True)
        print(f"Explanation: {result['explanation']}", flush=True) 
    except Exception as e:
        print(f"CRASHED: {e}", flush=True)
        import traceback
        traceback.print_exc()

def test_green_algae_sim():
    print("\nTesting Green Algae Simulation...", flush=True)
    from classification import classify_region
    res = classify_region(area=100, bbox_width=20, bbox_height=20, avg_color=(50,150,50), rectangularity=0.8, avg_gradient=10)
    print(f"Green Algae (G=150 >> R,B): {res} (Exp: DAMP)", flush=True)

def test_internal_corrosion_sim():
    print("\nTesting Internal Corrosion Simulation...", flush=True)
    from classification import classify_region
    res = classify_region(area=100, bbox_width=20, bbox_height=20, avg_color=(200,180,20), rectangularity=0.8, avg_gradient=20)
    print(f"Internal Corrosion (R=200, G=180, B=20): {res} (Exp: CORROSION)", flush=True)

def test_horizontal_crack_sim():
    print("\nTesting Horizontal Crack Simulation...", flush=True)
    from classification import classify_region
    res = classify_region(area=100, bbox_width=50, bbox_height=5, avg_color=(30,30,30), rectangularity=0.4, avg_gradient=30)
    print(f"Horizontal Crack (AR=10, Grad=30): {res} (Exp: CRACK)", flush=True)

if __name__ == "__main__":
    test_histogram_logic()
    test_classification_logic_sim()
    test_neon_wallpaper()
    test_green_algae_sim()
    test_internal_corrosion_sim()
    test_horizontal_crack_sim()
