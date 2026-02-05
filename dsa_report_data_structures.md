# Data Structures and Their Purposes for Project Report

This section outlines the core Data Structures selected for the Pipe Defect Detection system and the rationale behind each choice.

| Data Structure | Implementation in Code | Purpose & Rationale |
| :--- | :--- | :--- |
| **1. 2D Array (Matrix)** | `pixels` (NumPy), `binary_map` (List of Lists) | **Image Representation:** Used to store the raw image data (RGB) and the processed defect map (0s and 1s). <br> **Why:** Enables O(1) random access to any pixel `[r][c]` which is critical for spatial validity checks and neighbor analysis. |
| **2. Stack (LIFO)** | `stack = []` in `region_analysis.py` | **Graph Traversal (DFS):** Used to implement Iterative Depth First Search for connected components. <br> **Why:** Replaces recursion to prevent "RecursionError" on high-resolution images. It manages the active path of pixels being explored in a defect region. |
| **3. Priority Queue (Max-Heap)** | `heapq` in `severity_priority.py` | **Defect Scheduling:** Used to rank detected defects by severity. <br> **Why:** Ensures that the most critical defects (e.g., "Cracks") are always processed or displayed first. Insertion and maximum extraction are efficient at **O(log N)**. |
| **4. Hash Map (Dictionary)** | `defect_counts` in `image_logic.py` | **Aggregation:** Used to count occurrences of difference defect types (Crack, Corrosion, Damp) in O(1) time. <br> **Why:** rapid lookups and updates during the main analysis loop. |
| **5. Tuple** | `(r, c)` and `(score, id, type)` | **Immutable Records:** Used to represent coordinate pairs and priority queue entries. <br> **Why:** Lightweight and memory-efficient for storing fixed sets of related data needed for graph links and sorting. |

## Algorithmic Workflow Summary
1. **Input:** Image loaded as a **2D Array**.
2. **Process:** **Stack**-based DFS traverses the 2D Array to extract regions.
3. **Analyze:** **Geometric properties** (Area, Aspect Ratio) are calculated for each region.
4. **Output:** Severe defects are pushed into a **Priority Queue** for final reporting.
