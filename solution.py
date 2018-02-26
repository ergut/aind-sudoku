
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
rows = 'ABCDEFGHI'
diag_units = [[r+c for r,c in zip(rows,'123456789')],
              [r+c for r,c in zip(rows[::-1],'123456789')]]
unitlist = row_units + column_units + square_units + diag_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    for unit in unitlist:
        # Find boxes of length 2
        len2boxes = [box for box in unit if len(values[box])==2]
        # Identify twins
        for i in range(0,len(len2boxes)-1):
            for j in range(i+1,len(len2boxes)):
                if values[len2boxes[i]] == values[len2boxes[j]]:
                    twin = values[len2boxes[i]]
                    # Delete twins from other boxes in this unit
                    for box in unit:
                        if values[box] != twin:
                            #values[box] = values[box].replace(twin[0],'').replace(twin[1],'')
                            if twin[0] in values[box] or twin[1] in values[box]:
                                assign_value(values,box,values[box].replace(twin[0], '').replace(twin[1], ''))

    return values

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for box, value in values.items():
        if len(value) == 1:
            # Eliminate peers
            for p in peers[box]:
                # We don't need to check if len(p) > 1
                #values[p] = values[p].replace(value,'')
                if value in values[p]:
                    assign_value(values,p,values[p].replace(value,''))
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #values[dplaces[0]] = digit
                if len(values[dplaces[0]]) > 1:
                    assign_value(values, dplaces[0], digit)

    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the Naked Twins Strategy
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        # This happens for a failed branch
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False

    # Choose one of the unfilled squares with the fewest possibilities
    num_solved_boxes = len([box for box in values.keys() if len(values[box]) == 1])
    if num_solved_boxes == len(values.keys()):
        # Sudoku solved!
        return values

    # choose min length box
    min_len = 9
    min_len_box = ''
    for box in values.keys():
        if 1 < len(values[box]) < min_len:
            min_len = len(values[box])
            min_len_box = box

    assert(min_len_box != '')

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    # Iterate over all possible values for this min length box
    for k in values[min_len_box]:
        values_tmp = values.copy()
        # Replace this box with current value
        values_tmp[min_len_box] = k
        # Search a solution over this branch
        values_tmp = search(values_tmp)
        if values_tmp is not False:
            # Found a solution
            return values_tmp

    # No solution exists! -- Weird
    return False


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid1 = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid_solution = \
                        '374596812'\
                        '962138475'\
                        '629385741'\
                        '157864328'\
                        '843271569'\
                        '418752936'\
                        '295643187'\
                        '736819254'

    diag_sudoku_grid = \
        '5...4...3'\
        '....87...'\
        '...653...'\
        '.71.3.4..'\
        '4825.6391'\
        '..6.9.27.'\
        '...324...'\
        '...81....'\
        '1...6...9'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    assert(result is not False)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
