from collections import deque
from board import BoardFactory

def BFS(board, visitAll=True):
    """ Breadth-first search on a given board to find the optimal solution with the 
    minimum number of moves; after it finds the best solution, the algorithm continues
    to iterate all possible states to report the total state space (optinally).
    """
    queue = deque()
    # -1 indicates the starting state
    # board: current board state
    # 0: depth

    queue.append((-1, board, 0))
    seen = set()
    seen.add(hash(board))
    met_dups = 0
    visited = 0
    minSteps = -1
    
    
    while queue:
        blockId, board, depth = queue.popleft()
        # check if b is the ending state
        visited += 1
        if board.IsEndingState():
            # let's trace back
            if minSteps == -1:
                print "Food Delivered in %d steps after explored %d states" \
                    % (depth, visited)
                minSteps = depth
                if not visitAll:
                    break
        for (blockId, new_board) in board.Move():
            if hash(new_board) not in seen:
                queue.append((blockId, new_board, depth+1))
                seen.add(hash(new_board))
            else:
                met_dups += 1
        if (visited % 100 == 0):
            print "visited %6d, depth %3d, queue size %6d, met dups %12d times"  \
                % (visited, depth, len(queue), met_dups)
           
    return minSteps

if __name__ == "__main__":
    board = BoardFactory.CreateHardBoard()
    BFS(board)
    print "DONE"
    
    
    
    
    