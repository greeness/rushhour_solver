from collections import deque
from board import BoardFactory

def BFS(board):
    """ Breadth-first search on a given board to find the optimal solution with the 
    minimum number of moves; after it finds the best solution, the algorithm continues
    to iterate all possible states to report the total state space (optinally).
    """
    queue = deque()
    # -1 indicates the starting state
    queue.append((-1, board, 0))
    seen = set()
    seen.add(hash(board))
    met_dups = 0
    visited = 0
    found = False
    
    while queue:
        blockId, board, depth = queue.popleft()
        # check if b is the ending state
        visited += 1
        if board.IsEndingState():
            # let's trace back
            if not found:
                print "Food Delivered in %d steps after explored %d states" \
                    % (depth, visited)
                found = True 
        for (blockId, new_board) in board.Move():
            if hash(new_board) not in seen:
                queue.append((blockId, new_board, depth+1))
                seen.add(hash(new_board))
            else:
                met_dups += 1
        if (visited % 100 == 0):
            print "visited %6d, depth %3d, queue size %6d, met dups %12d times"  \
                % (visited, depth, len(queue), met_dups)
    if not found:
        print "no solution was found after visited %d states" % visited
    else:
        print "Total states %d" % (visited)

if __name__ == "__main__":
    board = BoardFactory.CreateEasyBoard()
    BFS(board)
    print "DONE"
    
    
    
    
    