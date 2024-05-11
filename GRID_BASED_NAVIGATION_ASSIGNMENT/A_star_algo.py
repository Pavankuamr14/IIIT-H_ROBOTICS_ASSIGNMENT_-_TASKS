import sys
import heapq
from PIL import Image, ImageDraw
from enum import Enum

class Node():
    def __init__(self, state, parent, action, cost, heuristic):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.heuristic = heuristic

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

class PriorityQueue():
    def __init__(self):
        self.heap = []

    def add(self, node, priority):
        heapq.heappush(self.heap, (priority, node))

    def contains_state(self, state):
        return any(node.state == state for _, node in self.heap)

    def empty(self):
        return len(self.heap) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            _, node = heapq.heappop(self.heap)
            return node

class Maze():
    class CostLevel(Enum):
        HIGH_COST = 5
        MEDIUM_COST = 3
        LOW_COST = 1

    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

        if contents.count("A") != 1 or contents.count("B") != 1:
            raise Exception("maze must have exactly one start and one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

    def assign_costs(self):
        self.costs = [[float('inf') for _ in range(self.width)] for _ in range(self.height)]
        self.costs[self.start[0]][self.start[1]] = 0

        start_node = Node(state=self.start, parent=None, action=None, cost=0, heuristic=self.heuristic(self.start))

        frontier = PriorityQueue()
        frontier.add(start_node, priority=start_node.cost + start_node.heuristic)

        while not frontier.empty():
            node = frontier.remove()

            for action, state, cost in self.neighbors(node.state):
                total_cost = node.cost + cost
                if total_cost < self.costs[state[0]][state[1]]:
                    self.costs[state[0]][state[1]] = total_cost
                    child = Node(state=state, parent=node, action=action, cost=total_cost, heuristic=self.heuristic(state))
                    frontier.add(child, priority=child.cost + child.heuristic)

    def print_maze(self):
        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("██", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()

    def heuristic(self, state):
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c), 1))

        return result

    def solve(self):
        self.num_explored = 0
        start = Node(state=self.start, parent=None, action=None, cost=0, heuristic=self.heuristic(self.start))

        frontier = PriorityQueue()
        frontier.add(start, priority=0)
        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state, cost in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action, cost=node.cost + cost, heuristic=self.heuristic(state))

                    frontier.add(child, priority=child.cost)

    def output_cost_image(self, filename):
        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (len(self.costs[0]) * cell_size, len(self.costs) * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        for i, row in enumerate(self.costs):
            for j, cost in enumerate(row):
                fill = (255, 0, 0) if cost == self.CostLevel.HIGH_COST.value else (0, 255, 0)

                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)

    def output_image(self, filename, show_explored=True):
        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    fill = (40, 40, 40)
                elif (i, j) == self.start:
                    fill = (255, 0, 0)
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)
                elif solution is not None and show_explored and (i, j) in solution:
                    fill = (220, 235, 113)
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)
                else:
                    fill = (237, 240, 252)

                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python astar_maze.py maze.txt")

    maze = Maze(sys.argv[1])
    print("Maze:")
    maze.print_maze()

    print("Solving...")
    maze.solve()

    print("States Explored By A* algorithm:", maze.num_explored)
    print("Solution:")
    maze.print_maze()

    print("Assigning Costs...")
    maze.assign_costs()

    print("Cost Grid:")
    for row in maze.costs:
        print(row)

    maze.output_image("astar_maze_solution.png", show_explored=True)
    print("Outputting Cost Grid Image...")
    maze.output_cost_image("astar_maze_cost_grid.png")
