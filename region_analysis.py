def dfs(binary_map, pixels, visited, i, j, height, width):
    stack = [(i, j)]
    visited[i][j] = True

    area = 0
    length = 0
    r_sum = int(0)
    g_sum = int(0)
    b_sum = int(0)


    min_i = max_i = i
    min_j = max_j = j

    while stack:
        x, y = stack.pop()
        area += 1

        r, g, b = pixels[x][y]

        r_sum += int(r)
        g_sum += int(g)
        b_sum += int(b)


        min_i = min(min_i, x)
        max_i = max(max_i, x)
        min_j = min(min_j, y)
        max_j = max(max_j, y)

        neighbors = [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
        local_links = 0

        for nx, ny in neighbors:
            if 0 <= nx < height and 0 <= ny < width:
                if binary_map[nx][ny] == 1:
                    local_links += 1
                    if not visited[nx][ny]:
                        visited[nx][ny] = True
                        stack.append((nx, ny))

        if local_links >= 2:
            length += 1

    avg_color = (
        r_sum // area,
        g_sum // area,
        b_sum // area
    )
    
    # Calculate Bounding Box Area
    bbox_width = (max_j - min_j) + 1
    bbox_height = (max_i - min_i) + 1
    bbox_area = bbox_width * bbox_height
    
    # Rectangularity / Solidity: How much of the bounding box is filled?
    # Solid shapes (corrosion) ~ high solidity
    # Thin/diagonal shapes (cracks) ~ low solidity relative to bbox (unless perfectly vertical/horizontal)
    rectangularity = area / bbox_area if bbox_area > 0 else 0

    return area, length, avg_color, min_i, min_j, max_i, max_j, rectangularity
