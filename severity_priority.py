import heapq
from config import SEVERITY_BASE

priority_queue = []

def add_to_priority(pipe_id, defect, pixels):
    severity = SEVERITY_BASE[defect] + pixels
    heapq.heappush(priority_queue, (-severity, pipe_id, defect, severity))
