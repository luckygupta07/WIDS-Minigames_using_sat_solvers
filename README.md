# WIDS-Minigames_using_sat_solversz
# Sudoku Solver using SAT (PySAT)

## Overview
This project implements a **Sudoku solver using Boolean Satisfiability (SAT)**.  
The Sudoku puzzle is encoded as a **CNF formula**, and a SAT solver from **PySAT (Glucose3)** is used to find a valid solution.

The solver supports standard **9×9 Sudoku** puzzles with partially filled cells.

---

## Approach

Each Sudoku cell `(row, column)` can take exactly one value from `1` to `9`.
This is encoded using Boolean variables of the form:

    X(r, c, v) = True  ⇔  cell (r, c) contains value v
---

## Constraints Encoded

1. **Cell constraints**
   - Each cell has **at least one value**
   - Each cell has **at most one value**

2. **Row constraints**
   - Each number appears **at most once** in every row

3. **Column constraints**
   - Each number appears **at most once** in every column

4. **Subgrid constraints**
   - Each number appears **at most once** in every 3×3 subgrid

5. **Given clues**
   - Pre-filled cells are fixed using unit clauses

---

## Implementation

- Language: **Python**
- SAT Library: **PySAT**
- Solver used: **Glucose3**

Main implementation is in `q1.py`.

---

## Resources
- CS 228 lecture slides 1-10
- Huth and Ryan chapter 1
- YT videos by IIT B and IIT D professors
- Copilot and Chatgpt for setting up python, github, git, running codes, downloadng extensions, finding error in code, making repo
  
---
## How to Run

1. Install dependencies:
   ```bash
   pip install python-sat tqdm
2. Place files in the same directory:
   ```bash
   tester.py
   q1.py
   testcases
3. Run:
   ```bash
   python tester.py
4. Output:
    ```bash
    500/500 test cases passed

   


