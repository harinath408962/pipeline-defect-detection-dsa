from collections import deque

# ================================
# PIPELINE GRAPH MODULE
# ================================

# Adjacency list representation of pipeline network
pipeline_graph = {
    "PIPE_001": ["PIPE_002", "PIPE_003"],
    "PIPE_002": ["PIPE_001", "PIPE_004"],
    "PIPE_003": ["PIPE_001"],
    "PIPE_004": ["PIPE_002", "PIPE_005"],
    "PIPE_005": ["PIPE_004"]
}

def find_affected_pipes(start_pipe):
    """
    Uses BFS to find all pipeline sections
    affected by the damaged pipe.
    """
    visited = set()
    queue = deque([start_pipe])
    visited.add(start_pipe)

    while queue:
        current = queue.popleft()
        for neighbor in pipeline_graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return visited
