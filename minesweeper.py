import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # if count = len(self.cells), all neightbours are mines
        if len(self.cells) == self.count and self.count > 0:
            return set(self.cells)
        return set()  
        
        #raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If count = 0, all neighbours are safe
        if self.count == 0:
            return set(self.cells)
        return set()


        # raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If a cell is a mine, we can remove it from the cells and reduce the count by 1
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

        # raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If a cell is safe, it can be removed from all the sentences.
        if cell in self.cells:
            self.cells.discard(cell)

    
        #raise NotImplementedError

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8, game=None):

        # Set initial height and width
        self.height = height
        self.width = width
        self.game = game
        self.cell_counts = {}

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        Verify the neighbours of a new mines to find new safes
        """
        # 1. If new mines known, nothing to do
        if cell in self.mines:
            return

        # 2. Add to mines found list
        self.mines.add(cell)

        # 3. Remove the new mine from the safes list
        if cell in self.safes:
            self.safes.remove(cell)

        # 4. Update all sentences
        for sentence in list(self.knowledge):
            sentence.mark_mine(cell)

        # 5. Clean empty sentences
        self.knowledge = [
            s for s in self.knowledge
            if not (len(s.cells) == 0 and s.count == 0)
        ]

        # 6. Verify if new safes have been found around the new mine
        self.update_safes_around_new_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """

        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def update_safes_around_new_mine(self, mine_cell):

        """
        si known_mines == count → toutes les autres cases autour sont safe.
        When a new mine is found, inspect cells around to identified new safes: 
            if known_mines around a cell == its count, then its neighbours are safe.
        """
        
        i0, j0 = mine_cell

        # Examine the 8 neighbours of the mine
        for i in range(i0 - 1, i0 + 2):
            for j in range(j0 - 1, j0 + 2):

                if (i, j) == mine_cell:
                    continue

                # Check board limits
                if not (0 <= i < self.height and 0 <= j < self.width):
                    continue

                cell = (i, j)

                # Look for revealed cells
                if cell not in self.moves_made:
                    continue

                # Recover the count of the cell being examined
                count = self.cell_counts.get(cell)
                if count is None:
                    # In case the cell have been revealed with no score (rare)
                    continue

                known_mines = 0
                unknown_neighbors = []

                # Inspect neigbours of this revealed cell
                for x in range(i - 1, i + 2):
                    for y in range(j - 1, j + 2):

                        if (x, y) == cell:
                            continue

                        if not (0 <= x < self.height and 0 <= y < self.width):
                            continue

                        pos = (x, y)

                        if pos in self.mines:
                            known_mines += 1
                        elif pos not in self.moves_made:
                            unknown_neighbors.append(pos)

                # If all expected mines have been discovered, all the other neighours are safe
                if known_mines == count:
                    for pos in unknown_neighbors:
                        if pos not in self.mines:
                            self.mark_safe(pos)


    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark the cell as a move made
        self.moves_made.add(cell)
         
         # Mark cell as safe
        self.mark_safe(cell)

        # Record the count value of the cell
        self.cell_counts[cell] = count

        # Add new sentence
        # Loop over all cells within one row and column
        new_set = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                new_count = count
                # Add to knowledge if cell in bounds and not played and is not known_safe
                if 0 <= i < self.height and 0 <= j < self.width:
                    if ((i, j) not in self.moves_made) and ((i, j) not in self.safes):
                        new_set.add((i, j))

        # Avoid empty and repeat sentences
        if (len(new_set) > 0):
            new_sentence = Sentence(new_set, new_count)
            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        # Add new knowledge inferred
        new_knowledge = self.inferred_knowledge()
        for s in new_knowledge:
            self.knowledge.append(s)     

        # Mark new safes and mines
        for sentence in list(self.knowledge):
            safe_set = sentence.known_safes()
            for cell_safe in safe_set:
                self.mark_safe(cell_safe)
             
            mine_set = sentence.known_mines()
            for cell_mine in mine_set:
                self.mark_mine(cell_mine)
        
        # Remove empty sentences from knowledge
        self.knowledge = [
            s for s in self.knowledge
            if not (len(s.cells) == 0 and s.count == 0)
        ]

    def inferred_knowledge(self):
        new_sentences = []

        # Work on copy of knowledge
        knowledge_copy = list(self.knowledge)

        for s1 in knowledge_copy:
            for s2 in knowledge_copy:
                if s1 == s2:
                    continue

                # s1 is subset of s2
                if s1.cells.issubset(s2.cells) and len(s1.cells) > 0:
                    diff_cells = s2.cells - s1.cells
                    diff_count = s2.count - s1.count

                    # Remove known mines and known safes
                    diff_cells_mod = diff_cells.difference(self.mines)
                    diff_count_mod = diff_count - ((len(diff_cells)) - len(diff_cells_mod))
                  
                    diff_cells_mod = diff_cells_mod.difference(self.safes)
                 
                    if len(diff_cells) > 0:
                        new_sentence = Sentence(diff_cells, diff_count)

                        if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                            new_sentences.append(new_sentence)


        return new_sentences            

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for element in self.safes:
            if (element not in self.mines) and (element not in self.moves_made):
                return element
        return None # If no safe moves left
        
        
        #raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Check if game is completed: number played + known mines = total number of cells
        cells_remaining = len(self.moves_made) + len(self.mines) - self.height * self.width
        if cells_remaining == 0:
            return None        
        
        # If self.knowledge is empty (beginning of game) return random cell
        if len(self.knowledge) == 0:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            return((i,j))

        # Look for the cell with lowest probability of being a mine
        lower_probability = 100
        best_guess = None
        for sentence in self.knowledge:
            if len(sentence.cells) > 0:
                ratio = sentence.count / len(sentence.cells)
                if ratio < lower_probability:
                    lower_probability = ratio
                    free_cells = sentence.cells.difference(self.moves_made)
                    free_cells_safe = free_cells.difference(self.mines)
                    if len(free_cells_safe) > 0:
                        best_guess = free_cells_safe.pop()
        return best_guess        

        
        #raise NotImplementedError
