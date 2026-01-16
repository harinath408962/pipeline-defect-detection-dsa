import heapq

priority_queue = []

SEVERITY_BASE = {
    "CRACK": 1000,
    "CORROSION": 300,
    "DAMP": 100,
    "NORMAL": 0
}

def add_to_priority(pipe_id, defect, score):
    severity = SEVERITY_BASE[defect] + score
    heapq.heappush(priority_queue, (-severity, pipe_id, defect, severity))
