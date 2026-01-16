def dfs(binary_map, pixels, visited, r, c, height, width):
    stack = [(r, c)]
    visited[r][c] = True

    area = 0
    length = 0
    sum_r = sum_g = sum_b = 0

    min_r = max_r = r
    min_c = max_c = c

    while stack:
        x, y = stack.pop()
        area += 1
        length += 1

        pr, pg, pb = pixels[y, x]
        sum_r += pr
        sum_g += pg
        sum_b += pb

        min_r = min(min_r, x)
        max_r = max(max_r, x)
        min_c = min(min_c, y)
        max_c = max(max_c, y)

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < height and 0 <= ny < width:
                if binary_map[nx][ny] == 1 and not visited[nx][ny]:
                    visited[nx][ny] = True
                    stack.append((nx, ny))

    avg_color = (
        sum_r//area,
        sum_g//area,
        sum_b//area
    )

    return area, length, avg_color, min_r, min_c, max_r, max_c


def binary_map_summary(binary_map):
    total = 0
    suspicious = 0

    for row in binary_map:
        for cell in row:
            total += 1
            if cell == 1:
                suspicious += 1

    percent = round((suspicious / total) * 100, 2)
    return total, suspicious, percent
