"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def var(r,c,v):
    # 9*9 Sudoku Encoding (maps every possible combination to value from 1 to 81 )
    return 81*(r-1)+9*(c-1)+v

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""
    cnf =CNF()

    # Cell constraint
    # r->row, c->column, v->value
    for r in range(1,10):
        for c in range (1,10):
            cnf.append([var(r,c,v) for v in range(1,10)]) #Assures atleat one value in each cell
            for v1 in range(1,10):
                for v2 in range (v1+1,10):
                    cnf.append([-var(r,c,v1),-var(r,c,v2)]) #Assures atmost one value in each cell

    # Row constraint
    for r in range(1,10):
        for v in range(1,10):
            for c1 in range(1,10):
                for c2 in range(c1+1,10):
                    cnf.append([-var(r,c1,v),-var(r,c2,v)])

    # Column constraint
    for c in range(1,10):
        for v in range(1,10):
            for r1 in range(1,10):
                for r2 in range(r1+1,10):
                    cnf.append([-var(r1,c,v),-var(r2,c,v)])   

    # 3*3 Subgrid constraint
    #sgr->row of subgrid top left cell, sgc->column of subgrid top left cell
    for sgr in [1,4,7]:
        for sgc in [1,4,7]:
            for v in range(1,10):
                cells = [(sgr+i,sgc+j) for i in range(3) for j in range(3)]
                for i in range(len(cells)):
                    for j in range(i+1,len(cells)):
                        r1,c1=cells[i]
                        r2,c2=cells[j]
                        cnf.append([-var(r1,c1,v),-var(r2,c2,v)])

    # Given numbers constraint
    for r in range(9):
        for c in range(9):
            if grid[r][c]!=0:
                cnf.append([var(r+1,c+1,grid[r][c])])
    
    # All constraints are covered till here 
    # Now we need to return solved sudoku
          
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model=solver.get_model()
            ans = [[0]*9 for _ in range(9)]

            for r in range(1,10):
                for c in range(1,10):
                    for v in range(1,10):
                        if var(r,c,v) in model :
                            ans[r-1][c-1] = v
            
            return ans
        # Returns original grid if soltion does not exist
        else:
            return grid