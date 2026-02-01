from pysat.formula import CNF
from pysat.solvers import Solver

DIRS = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}

class SokobanEncoder:
    def __init__(self, grid, T):
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None

        self._parse_grid()
        self.num_boxes = len(self.boxes)

        self.cnf = CNF()

        self.VP = (T + 1) * self.N * self.M
        self.VB = self.num_boxes * self.VP
        self.VA = T * (4 + 4 * self.num_boxes)

    def _parse_grid(self):
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] == 'P':
                    self.player_start = (i, j)
                elif self.grid[i][j] == 'B':
                    self.boxes.append((i, j))
                elif self.grid[i][j] == 'G':
                    self.goals.append((i, j))

    # ---------- VARIABLES ----------

    def var_player(self, x, y, t):
        return 1 + t * self.N * self.M + x * self.M + y

    def var_box(self, b, x, y, t):
        return 1 + self.VP + b * self.VP + t * self.N * self.M + x * self.M + y

    def var_move(self, d, t):
        return 1 + self.VP + self.VB + t * 4 + list(DIRS).index(d)

    def var_push(self, b, d, t):
        return (
            1 + self.VP + self.VB + self.VA +
            t * self.num_boxes * 4 +
            b * 4 +
            list(DIRS).index(d)
        )

    # ---------- ENCODING ----------

    def encode(self):
        N, M, T = self.N, self.M, self.T

        # Initial player
        px, py = self.player_start
        self.cnf.append([self.var_player(px, py, 0)])
        for x in range(N):
            for y in range(M):
                if (x, y) != (px, py):
                    self.cnf.append([-self.var_player(x, y, 0)])

        # Initial boxes
        for b, (x, y) in enumerate(self.boxes):
            self.cnf.append([self.var_box(b, x, y, 0)])
            for i in range(N):
                for j in range(M):
                    if (i, j) != (x, y):
                        self.cnf.append([-self.var_box(b, i, j, 0)])

        # Uniqueness (player + boxes)
        for t in range(T + 1):
            self._exactly_one_player(t)
            for b in range(self.num_boxes):
                self._exactly_one_box(b, t)
            self._no_box_overlap(t)

        # Exactly one action per timestep
        for t in range(T):
            actions = []
            for d in DIRS:
                actions.append(self.var_move(d, t))
                for b in range(self.num_boxes):
                    actions.append(self.var_push(b, d, t))
            self._exactly_one(actions)

        # Move semantics
        for t in range(T):
            for x in range(N):
                for y in range(M):
                    if self.grid[x][y] == '#':
                        continue
                    for d, (dx, dy) in DIRS.items():
                        nx, ny = x + dx, y + dy
                        if not (0 <= nx < N and 0 <= ny < M):
                            self.cnf.append([-self.var_player(x, y, t),
                                             -self.var_move(d, t)])
                            continue
                        if self.grid[nx][ny] == '#':
                            self.cnf.append([-self.var_player(x, y, t),
                                             -self.var_move(d, t)])
                            continue

                        # can't move into a box
                        for b in range(self.num_boxes):
                            self.cnf.append([
                                -self.var_move(d, t),
                                -self.var_player(x, y, t),
                                -self.var_box(b, nx, ny, t)
                            ])

                        self.cnf.append([
                            -self.var_move(d, t),
                            -self.var_player(x, y, t),
                            self.var_player(nx, ny, t + 1)
                        ])

        # Push semantics
        for t in range(T):
            for b in range(self.num_boxes):
                for x in range(N):
                    for y in range(M):
                        if self.grid[x][y] == '#':
                            continue
                        for d, (dx, dy) in DIRS.items():
                            bx, by = x + dx, y + dy
                            tx, ty = bx + dx, by + dy

                            if not (0 <= bx < N and 0 <= by < M and
                                    0 <= tx < N and 0 <= ty < M):
                                self.cnf.append([-self.var_push(b, d, t)])
                                continue

                            if self.grid[tx][ty] == '#':
                                self.cnf.append([-self.var_push(b, d, t)])
                                continue

                            # Preconditions
                            self.cnf.append([
                                -self.var_push(b, d, t),
                                self.var_player(x, y, t)
                            ])
                            self.cnf.append([
                                -self.var_push(b, d, t),
                                self.var_box(b, bx, by, t)
                            ])

                            # Target cell empty
                            for b2 in range(self.num_boxes):
                                if b2 != b:
                                    self.cnf.append([
                                        -self.var_push(b, d, t),
                                        -self.var_box(b2, tx, ty, t)
                                    ])

                            # Effects
                            self.cnf.append([
                                -self.var_push(b, d, t),
                                self.var_player(bx, by, t + 1)
                            ])
                            self.cnf.append([
                                -self.var_push(b, d, t),
                                self.var_box(b, tx, ty, t + 1)
                            ])

        # Persistence (simple & safe)
        for t in range(T):
            for x in range(N):
                for y in range(M):
                    self.cnf.append([
                        -self.var_player(x, y, t),
                        self.var_player(x, y, t + 1)
                    ])

            for b in range(self.num_boxes):
                for x in range(N):
                    for y in range(M):
                        self.cnf.append([
                            -self.var_box(b, x, y, t),
                            self.var_box(b, x, y, t + 1)
                        ])

        # No player-box overlap
        for t in range(T + 1):
            for b in range(self.num_boxes):
                for x in range(N):
                    for y in range(M):
                        self.cnf.append([
                            -self.var_player(x, y, t),
                            -self.var_box(b, x, y, t)
                        ])

        # Goal condition
        for b in range(self.num_boxes):
            self.cnf.append([
                self.var_box(b, gx, gy, T)
                for gx, gy in self.goals
            ])

        return self.cnf.clauses

    # ---------- HELPERS ----------

    def _exactly_one(self, vars):
        self.cnf.append(vars)
        for i in range(len(vars)):
            for j in range(i + 1, len(vars)):
                self.cnf.append([-vars[i], -vars[j]])

    def _exactly_one_player(self, t):
        cells = [
            self.var_player(x, y, t)
            for x in range(self.N)
            for y in range(self.M)
            if self.grid[x][y] != '#'
        ]
        self._exactly_one(cells)

    def _exactly_one_box(self, b, t):
        cells = [
            self.var_box(b, x, y, t)
            for x in range(self.N)
            for y in range(self.M)
            if self.grid[x][y] != '#'
        ]
        self._exactly_one(cells)

    def _no_box_overlap(self, t):
        for b1 in range(self.num_boxes):
            for b2 in range(b1 + 1, self.num_boxes):
                for x in range(self.N):
                    for y in range(self.M):
                        self.cnf.append([
                            -self.var_box(b1, x, y, t),
                            -self.var_box(b2, x, y, t)
                        ])


def decode(model, encoder):
    model = set(model)
    plan = []
    for t in range(encoder.T):
        for d in DIRS:
            if encoder.var_move(d, t) in model:
                plan.append(('MOVE', d))
        for b in range(encoder.num_boxes):
            for d in DIRS:
                if encoder.var_push(b, d, t) in model:
                    plan.append(('PUSH', b, d))
    return plan


def solve_sokoban(grid, T):
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()
    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1
        return decode(solver.get_model(), encoder)
