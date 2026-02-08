from fpdf import FPDF
import os
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Pipeline Defect Detection Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(results_list):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # 1. Title & Metadata
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'L')
    pdf.ln(5)
    
    # 2. Executive Summary
    total_pipes = len(results_list)
    defects = {"CRACK": 0, "CORROSION": 0, "DAMP": 0, "NORMAL": 0, "INVALID": 0}
    
    for res in results_list:
        defect = res.get("final_defect", "NORMAL")
        defects[defect] = defects.get(defect, 0) + 1
        
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Executive Summary", 0, 1, 'L')
    pdf.set_font("Arial", size=11)
    
    pdf.cell(0, 8, f"Total Pipes Analyzed: {total_pipes}", 0, 1, 'L')
    pdf.cell(0, 8, f"Cracks Detected: {defects['CRACK']}", 0, 1, 'L')
    pdf.cell(0, 8, f"Corrosion Detected: {defects['CORROSION']}", 0, 1, 'L')
    pdf.cell(0, 8, f"Dampness/Algae Detected: {defects['DAMP']}", 0, 1, 'L')
    pdf.cell(0, 8, f"Invalid Images: {defects['INVALID']}", 0, 1, 'L')
    pdf.ln(10)
    
    # 3. Detailed Analysis with Images
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Detailed Analysis", 0, 1, 'L')
    pdf.ln(5)
    
    for i, res in enumerate(results_list):
        pipe_id = res.get("pipe_id", "N/A")
        status = res.get("final_defect", "UNKNOWN")
        explanation = res.get("explanation", "")
        affected = f"{res.get('affected_percentage', 0)}%"
        
        # Header for this Pipe
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{i+1}. {pipe_id} - {status}", 0, 1, 'L')
        
        # Image Handling
        if 'image_obj' in res:
            try:
                # Save temp image
                img_path = f"temp_img_{i}.jpg"
                res['image_obj'].save(img_path)
                
                # Add Image to PDF (Width ~100mm)
                # Get current Y
                start_y = pdf.get_y()
                pdf.image(img_path, x=10, y=start_y, w=80)
                
                # Move cursor to right of image for text
                pdf.set_xy(100, start_y)
                
                # Clean up immediately? Or later. 
                # Better to keep simple: overwrite next time or ignore.
                # removing is good practice.
            except Exception as e:
                pdf.cell(0, 10, f"Error adding image: {e}", 0, 1)

        # Details Text (Right side or Below)
        # We are at X=100.
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, f"Status: {status}\nAffected Area: {affected}\n\nExplanation:\n{explanation}")
        
        # Reset Cursor below image
        pdf.set_y(start_y + 65) # Approx image height + margin
        pdf.ln(5)
        
        # Cleanup temp file
        if 'image_obj' in res and os.path.exists(f"temp_img_{i}.jpg"):
            os.remove(f"temp_img_{i}.jpg")
            
    # Save to file
    output_path = "Pipeline_Report.pdf"
    pdf.output(output_path)
    return output_path
