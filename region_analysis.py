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

    return area, length, avg_color, min_i, min_j, max_i, max_j
