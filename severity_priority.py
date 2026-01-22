# IMPLEMENTATION: MAX-HEAP (Simulated with List + Sort for simplicity strictly DSA)
# Or Actual Heap. Let's do a simple sort update since N is small.
# Actually, strict DSA implies we should use a Heap structure if we say "Priority Queue".
# Python's `heapq` is standard library DSA.

import heapq

# Stores tuples: (-priority_score, pipe_id, defect_type)
# We use negative score for Max-Heap behavior involved with Min-Heap heapq
priority_queue = [] 

def clear_priority_queue():
    global priority_queue
    priority_queue = [] 

def add_to_priority(pipe_id, defect, severity_score):
    # Store as negative to make it a Max-Heap (Highest severity first)
    heapq.heappush(priority_queue, (-severity_score, pipe_id, defect))

def get_priority_list():
    # Return sorted list without popping, or pop all?
    # For UI display, we usually want to see the list.
    # Let's return a sorted copy
    sorted_list = sorted(priority_queue)
    # Convert back to positive score
    return [(pid, def_type, -score) for (score, pid, def_type) in sorted_list]
