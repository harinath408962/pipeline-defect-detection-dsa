DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

def dfs(defect_map, pixels, visited, si, sj, h, w):
    stack = [(si, sj)]
    visited[si][sj] = True

    area = 0
    min_i = max_i = si
    min_j = max_j = sj
    color_sum = [0,0,0]

    while stack:
        i, j = stack.pop()
        area += 1

        r, g, b = pixels[j, i]
        color_sum[0] += r
        color_sum[1] += g
        color_sum[2] += b

        min_i, max_i = min(min_i, i), max(max_i, i)
        min_j, max_j = min(min_j, j), max(max_j, j)

        for di, dj in DIRECTIONS:
            ni, nj = i+di, j+dj
            if 0 <= ni < h and 0 <= nj < w:
                if defect_map[ni][nj] and not visited[ni][nj]:
                    visited[ni][nj] = True
                    stack.append((ni, nj))

    length = max(max_i - min_i, max_j - min_j)
    avg_color = [c//area for c in color_sum]

    return area, length, avg_color, min_i, min_j, max_i, max_j
