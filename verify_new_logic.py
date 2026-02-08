import numpy as np
from classification import classify_region
from core.image_logic import process_image_logic
import sys

def verify():
    print("--- START VERIFICATION ---")
    
    # 1. Green Algae
    # Green Dominant: G=150 >> R=50, B=50
    res = classify_region(area=100, bbox_width=20, bbox_height=20, avg_color=(50,150,50), rectangularity=0.8, avg_gradient=10)
    print(f"Green Algae: {res}")
    
    # 2. Internal Corrosion
    # Yellow/Orange: R=200, G=180, B=20
    res = classify_region(area=100, bbox_width=20, bbox_height=20, avg_color=(200,180,20), rectangularity=0.8, avg_gradient=20)
    print(f"Internal Corrosion: {res}")
    
    # 3. Neon Wallpaper
    width, height = 100, 100
    pixels = np.zeros((height, width, 3), dtype=np.uint8)
    pixels[:, :50] = [255, 0, 255] # Magenta
    pixels[:, 50:] = [0, 255, 0]   # Green
    
    try:
        result = process_image_logic(pixels, width, height, "TEST_NEON")
        print(f"Neon Check: {result['final_defect']}")
    except Exception as e:
        print(f"Neon Check Crashed: {e}")

    # 4. Horizontal Crack
    # Sharpness: 30
    res = classify_region(area=100, bbox_width=50, bbox_height=5, avg_color=(30,30,30), rectangularity=0.4, avg_gradient=30)
    print(f"Horizontal Crack: {res}")

    print("--- END VERIFICATION ---")

if __name__ == "__main__":
    verify()
