def get_score(defect, affected):
    # Severity Map
    severity = 0
    if defect == "CRACK": severity = 10
    elif defect == "CORROSION": severity = 5
    elif defect == "DAMP": severity = 2
    elif defect == "NORMAL": severity = 1
    elif defect == "INVALID": severity = 0
    
    return (severity * 1000) + affected

params = [
    ("CRACK", 50.0),
    ("CORROSION", 80.0),
    ("CRACK", 75.5),
    ("DAMP", 90.0),
    ("NORMAL", 0.0),
    ("HEALTHY", 99.9) # Test unknown case default to NORMAL=1
]

results = []
for defect, affected in params:
    # Simulate app logic default
    status = defect
    if status == "HEALTHY": status = "NORMAL" # Logic in app defaults to NORMAL if not mapped? 
    # Actually app.py maps: .get('final_defect', 'NORMAL'). 
    # And calculate_priority has fallback severity=0 if not matched? 
    # No, I used `severity = 0` init, but `NORMAL` maps to 1.
    
    score = get_score(defect, affected)
    results.append({"defect": defect, "affected": affected, "priority_score": score})

# Sort
sorted_results = sorted(results, key=lambda x: x['priority_score'], reverse=True)

print("Sorted Results:")
for r in sorted_results:
    print(f"{r['defect']} \t {r['affected']}% \t Score: {r['priority_score']}")
