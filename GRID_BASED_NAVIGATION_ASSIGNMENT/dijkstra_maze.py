import sys
import heapq
from PIL import Image, ImageDraw

# Define cost constants
HIGH_COST = 5
MEDIUM_COST = 3
LOW_COST = 1

class Node():
    def __init__(self, state, parent, action, cost, total_cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.total_cost = total_cost

    def __lt__(self, other):
        return self.total_cost < other.total_cost



    
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

    def __init__(self, filename):

        # Read file and set the height and width of the maze
        with open(filename) as f:
            contents = f.read()

        # Validate start and goal
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Determine height and width of maze
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Keep track of walls
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
        self.costs = [[0 for _ in range(len(self.walls[0]))] for _ in range(len(self.walls))]

        for row in range(len(self.walls)):
            for col in range(len(self.walls[0])):
                # Assign high cost if it's a wall, otherwise low cost
                self.costs[row][col] = HIGH_COST if self.walls[row][col] else LOW_COST

    def output_cost_image(self, filename):
        cell_size = 50
        cell_border = 2

        # Create a blank canvas for the cost grid
        img = Image.new(
            "RGBA",
            (len(self.costs[0]) * cell_size, len(self.costs) * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        for i, row in enumerate(self.costs):
            for j, cost in enumerate(row):
                # Map cost values to colors
                if cost == HIGH_COST:
                    fill = (255, 0, 0)  # Red for high cost
                else:
                    fill = (0, 255, 0)  # Green for low cost

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                      ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)


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
                result.append((action, (r, c), 1))  # Assuming uniform cost for all actions

        return result

    def solve(self):
        """Finds a solution to the maze if one exists."""

        # Keep track of the number of states explored
        self.num_explored = 0

        # Initialize the frontier to just the starting position
        start = Node(state=self.start, parent=None, action=None, cost=0, total_cost=0)
        frontier = PriorityQueue()
        frontier.add(start, priority=0)

        # Initialize an empty explored set
        self.explored = set()

        # Keep looping until a solution is found
        while True:

            # If nothing is left in the frontier, then there is no path
            if frontier.empty():
                raise Exception("no solution")

            # Choose a node from the frontier
            node = frontier.remove()
            self.num_explored += 1

            # If the node is the goal, then a solution has been found
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

            # Mark the node as explored
            self.explored.add(node.state)

            # Add neighbors to the frontier
            for action, state, cost in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child_cost = self.costs[state[0]][state[1]]
                    child = Node(state=state, parent=node, action=action, cost=child_cost, total_cost=node.total_cost + child_cost)
                    frontier.add(child, priority=child.total_cost)

    def output_image(self, filename, show_explored=True):
        cell_size = 50
        cell_border = 2

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                # Walls
                if col:
                    fill = (40, 40, 40)

                # Start
                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                # Goal
                elif (i, j) == self.goal:
                    fill = (0, 171, 28)

                # Solution
                elif solution is not None and show_explored and (i, j) in solution:
                    fill = (220, 235, 113)

                # Explored
                elif solution is not None and show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                # Empty cell
                else:
                    fill = (237, 240, 252)

                # Draw cell
                draw.rectangle(
                    ([(j * cell_size + cell_border, i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)]),
                    fill=fill
                )

        img.save(filename)
    def print_cost_grid(self):
        for row in self.costs:
            print(row)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python dijkstra_maze.py maze.txt")

    maze = Maze(sys.argv[1])
    print("Maze:")
    maze.print_maze()

    print("Assigning Costs...")
    maze.assign_costs()
    print("Cost Grid:")
    maze.print_cost_grid()
    print("Cost Grid:")
    for row in maze.costs:
        print(row)  # Print the cost grid values

    print("Solving...")
    maze.solve()

    print("States Explored by using Dijkstra algorithm:", maze.num_explored)
    print("Solution:")
    maze.print_maze()

    print("Outputting Cost Grid Image...")
    maze.output_cost_image("cost_grid.png")
