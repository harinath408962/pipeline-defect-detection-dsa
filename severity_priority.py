priority_queue = []

def add_to_priority(pipe_id, defect, severity):
    priority_queue.append((severity, pipe_id, defect))
    priority_queue.sort(reverse=True)
