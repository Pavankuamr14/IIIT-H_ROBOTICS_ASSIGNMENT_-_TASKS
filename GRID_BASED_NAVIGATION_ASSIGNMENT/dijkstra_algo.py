import heapq
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def dijkstra(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    # Priority queue for Dijkstra's algorithm
    pq = [(0, start)]
    distances = {start: 0}

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_node == end:
            break

        for dr, dc in directions:
            new_row, new_col = current_node[0] + dr, current_node[1] + dc

            if 0 <= new_row < rows and 0 <= new_col < cols and maze[new_row][new_col] == 0:
                new_dist = current_dist + 1

                if (new_row, new_col) not in distances or new_dist < distances[(new_row, new_col)]:
                    distances[(new_row, new_col)] = new_dist
                    heapq.heappush(pq, (new_dist, (new_row, new_col)))

    # Reconstruct the path
    path = []
    current = end

    while current != start:
        path.append(current)
        neighbors = [(current[0] + dr, current[1] + dc) for dr, dc in directions]
        current = min(neighbors, key=lambda x: distances.get(x, float('inf')))

    path.append(start)
    path.reverse()
    return path

def visualize_maze(maze, path):
    fig, ax = plt.subplots()

    # Plot maze
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 1:
                rect = patches.Rectangle((col, row), 1, 1, linewidth=1, edgecolor='black', facecolor='black')
                ax.add_patch(rect)

    # Plot path
    for node in path:
        rect = patches.Rectangle((node[1], node[0]), 1, 1, linewidth=1, edgecolor='red', facecolor='red')
        ax.add_patch(rect)

    ax.set_aspect('equal', 'box')
    plt.xlim(0, len(maze[0]))
    plt.ylim(0, len(maze))
    plt.show()

# Example usage for a 5x8 maze:


maze_5x8 = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

start_point_5x8 = (2, 1)
end_point_5x8 = (5, 6)

result_path_5x8 = dijkstra(maze_5x8, start_point_5x8, end_point_5x8)
print("Shortest path:", result_path_5x8)

# Visualize maze and path
visualize_maze(maze_5x8, result_path_5x8)
