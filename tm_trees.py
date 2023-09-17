"""
Assignment 2: Trees for Treemap

=== CSC148 Summer 2023 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Bogdan Simion, David Liu, Diane Horton,
                   Haocheng Hu, Jacqueline Smith, Andrea Mitchell,
                   Bahar Aameri

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


def get_colour() -> Tuple[int, int, int]:
    """
    This function picks a random colour selectively such that it is not on the
    grey scale. The colour is close to the grey scale if the r g b values have a
    small variance. This function checks if all the numbers are close to the
    mean, if so, it shifts the last digit by 150.

    This way you can't confuse the leaf rectangles with folder rectangles,
    because the leaves will always be a colour, never close to black / white.
    """
    rgb = [randint(0, 255), randint(0, 255), randint(0, 255)]
    avg = sum(rgb) // 3
    count = 0
    for item in rgb:
        if abs(item - avg) < 20:
            count += 1
    if count == 3:
        rgb[2] = (rgb[2] + 150) % 255
    return tuple(rgb)


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect: The pygame rectangle representing this node in the visualization.
    data_size: The size of the data represented by this tree.

    === Private Attributes ===
    _colour: The RGB colour value of the root of this tree.
    _name: The root value of this tree, or None if this tree is empty.
    _subtrees: The subtrees of this tree.
    _parent_tree: The parent tree of this tree; i.e., the tree that contains
    this tree as a subtree, or None if this tree is not part of a larger tree.
    _expanded: Whether this tree is considered expanded for visualization.
    _depth: The depth of this tree node in relation to the root.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - _colour's elements are each in the range 0-255.
    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - if _parent_tree is not None, then self is in _parent_tree._subtrees
    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool
    _depth: int

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initializes a new TMTree with a random colour, the provided name
        and sets the subtrees to the list of provided subtrees. Sets this tree
        as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._parent_tree = None
        self._depth = 0

        self._expanded = False

        # 1. Initialize: - self._name
        #                - self._colour (use the get_colour() function)
        #                - self._subtrees
        #                - self.data_size
        # 2. Set this tree as the parent for each of its subtrees.
        #
        # NOTES: - self._expanded will be changed in task 5
        #        - Leaf nodes will have data_size set to the size of the file
        #        - Internal nodes will have the data_size = 0
        #           -> this needs to be updated based on the sizes of subtrees
        #
        self._name = name
        self._colour = get_colour()
        self._subtrees = subtrees
        self.data_size = data_size
        for subtree in self._subtrees:  # data_size = sum of data_size of subtre
            self.data_size += subtree.data_size
        for subtree in self._subtrees:
            subtree._parent_tree = self

    def is_empty(self) -> bool:
        """Returns True iff this tree is empty.
        """
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    # **************************************************************************
    # ************* TASK 2: UPDATE AND GET RECTANGLES **************************
    # **************************************************************************

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Updates the rectangles in this tree and its descendants using the
        treemap algorithm to fill the area defined by the <rect> parameter.
        """
        # Read the Treemap Algorithm description in the handout thoroughly and
        # implement this algorithm to set the <rect> parameter for each
        # tree node.
        #
        # NOTES: - Empty folders should not take up any space
        #        - Both files AND folders need to be assigned a rect attribute
        #        - Don't forget that the last subtree occupies remaining space
        #        - tip: use "tuple unpacking assignment" for easy extraction:
        #           -> x, y, width, height = rect
        #
        x, y, width, height = self.rect
        self.rect = rect
        total = sum(tree.data_size for tree in self._subtrees)

        if width > height:  # horizontal rectangles
            temp_x = x
            for subtree in self._subtrees:
                if subtree == self._subtrees[-1]:
                    new_width = width + x - temp_x
                else:
                    new_width = math.floor(subtree.data_size * width / total)
                subtree.update_rectangles((temp_x, y, new_width, height))
                temp_x += new_width
        else:  # vertical rectangles
            temp_y = y
            for subtree in self._subtrees:
                if subtree == self._subtrees[-1]:
                    new_height = height + y - temp_y
                else:
                    new_height = math.floor(subtree.data_size * height / total)
                subtree.update_rectangles((x, temp_y, width, new_height))

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Returns a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        #
        # NOTES: - This method will be modified in Task 6 to return both leaf
        #          nodes and internal nodes which are not expanded
        #
        if self._name is None:
            return [((0, 0, 0, 0), (0, 0, 0))]
        elif not self._expanded:
            return [(self.rect, self._colour)]
        else:
            list_of_tuples = []
            for subtree in self._subtrees:
                list_of_tuples.extend(subtree.get_rectangles())
            return list_of_tuples

    # **************************************************************************
    # **************** TASK 3: GET_TREE_AT_POSITION ****************************
    # **************************************************************************

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Returns the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two or more rectangles,
        always return the leftmost and topmost rectangle (wherever applicable).
        """
        #
        # NOTES: - This method will be modified in Task 6 to return either a
        #          leaf node or an internal node which is not expanded
        #
        if self.is_empty():
            return None
        elif not self._subtrees:  # self is a leaf
            if self.rect[0] <= pos[0] <= self.rect[2] + self.rect[0] \
                    and self.rect[1] <= pos[1] <= self.rect[3] + self.rect[1]:
                # if <pos> is between x value and x + width and between y value
                # and y + height
                return self
            else:
                return None
        else:
            if self.rect[0] <= pos[0] <= self.rect[2] + self.rect[0] \
                    and self.rect[1] <= pos[1] <= self.rect[3] + self.rect[1]:
                if self._expanded is False:
                    return self

            for subtree in self._subtrees:
                tree = subtree.get_tree_at_position(pos)
                if tree is not None:
                    return tree

    # **************************************************************************
    # ********* TASK 4: MOVE, CHANGE SIZE, DELETE, UPDATE SIZES ****************
    # **************************************************************************

    def update_data_sizes(self) -> int:
        """Updates the data_size attribute for this tree and all its subtrees,
        based on the size of their leaves, and return the new size of the given
        tree node after updating.

        If this tree is a leaf, return its size unchanged.
        """
        #
        # NOTES: - This method is called after some change is made to the tree
        #          so that the change of is reflected in all ancestor
        #          nodes which are affected. (i.e., one leaf node size being
        #          modified results in size changes for its ancestral nodes)
        #
        if self.is_empty():
            return 0
        elif not self._subtrees:  # if TMT object is a leaf
            return self.data_size
        else:
            total_size = 0
            for subtree in self._subtrees:
                total_size += subtree.update_data_sizes()
            if self._parent_tree is not None:
                self._parent_tree.data_size = total_size
            return total_size

    def change_size(self, factor: float) -> None:
        """Changes the value of this tree's data_size attribute by <factor>.
        Always rounds up the amount to change, so that it's an int, and
        some change is made. If the tree is not a leaf, this method does
        nothing.
        """
        #
        # NOTES: - factor is a percentage in the form of a decimal.
        #          (i.e., factor = 0.01 should increase size by 1%)
        #        - factor may be negative
        #        - the lower limit on data_size is 1 (i.e., you can't let the
        #          size decrease below 1)
        #
        if factor < 0:
            amount_change = math.floor(self.data_size * factor)
        else:
            amount_change = math.ceil(self.data_size * factor)

        if not (amount_change + self.data_size) < 1:
            self.data_size += amount_change
        else:
            self.data_size = 1

        # Update data sizes
        self.update_data_sizes()
        # Reapply rect algorithm
        self.update_rectangles(self.rect)

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful. Only do this if this node
        has a parent tree.

        Do not set self._parent_tree to None, because it might be used
        by the visualizer to go back to the parent folder.
        """
        #
        # NOTES: - if this tree node is an "only child", you need to
        #          recursively keep deleting the empty folder above
        #        - the root node should not be deleted, and the size won't be
        #          updated if the root node is attempted to be deleted

        # first delete the self (intended file)
        temp = False
        parent_tree = self._parent_tree
        parent_tree._subtrees.remove(self)
        self._parent_tree = None
        if self not in parent_tree._subtrees:
            temp = True

        # recursively delete parent, if parent has no files
        while parent_tree._parent_tree is not None:  # recurse till root
            if not parent_tree._subtrees:  # if folder had no more files
                deleted = parent_tree.delete_helper()
                if not deleted:
                    return False
            parent_tree = parent_tree._parent_tree
        return temp

    def delete_helper(self):
        self._parent_tree._subtrees.remove(self)
        if self not in self._parent_tree._subtrees:
            return True
        else:
            return False

    # **************************************************************************
    # ************* TASK 5: UPDATE_COLOURS_AND_DEPTHS **************************
    # **************************************************************************

    def update_depths(self) -> None:
        """Updates the depths of the nodes, starting with a depth of 0 at this
        tree node.
        """
        if self.is_empty():
            pass
        elif not self._subtrees:  # self is a leaf
            if self._parent_tree is not None:
                self._depth = self._parent_tree._depth + 1
            else:
                self._depth = 0
        else:
            if self._parent_tree is not None:
                self._depth = self._parent_tree._depth + 1
            else:
                self._depth = 0
            for subtree in self._subtrees:
                subtree.update_depths()

    def max_depth(self) -> int:
        """Returns the maximum depth of the tree, which is the maximum length
        between a leaf node and the root node.
        """
        if self.is_empty():
            return 0
        elif not self._subtrees:
            return self._depth
        else:
            largest_depth = 0
            for subtree in self._subtrees:
                new_depth = subtree.max_depth()
                if new_depth > largest_depth:
                    largest_depth = new_depth
            return largest_depth

    def update_colours(self, step_size: int) -> None:
        """Updates the colours so that the internal tree nodes are
        shades of grey depending on their depth. The root node will be black
        (0, 0, 0) and all internal nodes will be shades of grey depending on
        their depth, where the step size determines the shade of grey.
        Leaf nodes should not be updated.
        """
        if self.is_empty():
            return
        elif not self._subtrees:
            pass
        else:
            self._colour = (step_size * self._depth, step_size * self._depth,
                            step_size * self._depth)
            for subtree in self._subtrees:
                subtree.update_colours(step_size)

    def update_colours_and_depths(self) -> None:
        """This method is called any time the tree is manipulated or right after
        instantiation. Updates the _depth and _colour attributes throughout
        the tree.
        """
        # 1. Call the update depths method you wrote.
        # 2. Find the maximum depth of the tree.
        # 3. Use the maximum depth to determine the step_size.
        # 4. Call the update_colours method and use step_size as the parameter.
        self.update_depths()
        max_depth = self.max_depth()
        step_size = 200 // max_depth
        self.update_colours(step_size)

    # **************************************************************************
    # ********* TASK 6: EXPAND, COLLAPSE, EXPAND ALL, COLLAPSE ALL *************
    # **************************************************************************

    def expand(self) -> None:
        """Sets this tree to be expanded. But not if it is a leaf.
        """
        if self.is_empty():
            pass
        elif not self._subtrees:  # self is a leaf
            pass
        else:
            self._expanded = True
            if self._parent_tree is not None:
                self._parent_tree._expanded = True

        self.update_data_sizes()
        self.update_rectangles(self.rect)

    def expand_all(self) -> None:
        """Sets this tree and all its descendants to be expanded, apart from the
        leaf nodes.
        """
        if self.is_empty():
            pass
        elif not self._subtrees:  # self is a leaf
            pass
        else:
            self._expanded = True
            if self._parent_tree is not None:
                self._parent_tree._expanded = True
            for subtree in self._subtrees:
                subtree.expand_all()

        self.update_data_sizes()
        self.update_rectangles(self.rect)

    def collapse(self) -> None:
        """Collapses the parent tree of the given tree node and also collapse
        all of its descendants.
        """
        #
        # NOTES: - This method could be called with any node on the tree.
        #        - After this method is called, the parent of the given node
        #          should not be expanded, and any node underneath this tree
        #          should not be expanded.
        #
        if self.is_empty():
            pass
        elif not self._subtrees:  # self is a leaf
            pass
        else:
            self._expanded = False
            if self._parent_tree is not None:
                self._parent_tree._expanded = False
            for subtree in self._subtrees:
                subtree.collapse()

        self.update_data_sizes()
        self.update_rectangles(self.rect)

    def collapse_all(self) -> None:
        """ Collapses ALL nodes in the tree.
        """
        #
        # NOTES - This should work if it is called on any node in the tree.
        #       - After this method is called, _expanded should be set to false
        #         for all nodes in the tree.
        if self.is_empty():
            pass
        elif not self._subtrees:  # self is a leaf
            pass
        else:
            temp_self = self
            while temp_self._parent_tree is not None:
                temp_self = temp_self._parent_tree
                temp_self._helper_collapse()

            self.update_data_sizes()
            self.update_rectangles(self.rect)

    def _helper_collapse(self) -> None:
        """
        Helper to <collapse_all>. Collapses <self>'s subtrees including <self>.
        """
        self._expanded = False
        for subtree in self._subtrees:
            subtree._helper_collapse()

    # **************************************************************************
    # ************* TASK 7 : DUPLICATE MOVE COPY_PASTE *************************
    # **************************************************************************

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, moves this
        tree to be the last subtree of <destination>. Otherwise, does nothing.
        """
        if not self._subtrees and destination._subtrees:  # self is a leaf
            self._parent_tree._subtrees.remove(self)
            self.update_data_sizes()

            # Transferring to Destination
            destination._subtrees.append(self)
            destination.expand()
            self._parent_tree = destination

            # change data sizes and rectangle of respective nodes to account
            # for the change
            self.update_data_sizes()
            self.update_rectangles(self.rect)

    def duplicate(self) -> Optional[TMTree]:
        """Duplicates the given tree, if it is a leaf node. It stores
        the new tree with the same parent as the given leaf. Returns the
        new node. If the given tree is not a leaf, does nothing.
        """
        #
        # NOTES: - make good use of the FileSystemTree constructor to
        #          instantiate a new node.
        if not self._subtrees:  # if self is a leaf
            path = self.get_full_path()
            tree_object = FileSystemTree(path)  # duplicate of self
            tree_object._parent_tree = self._parent_tree
            self._parent_tree._subtrees.append(tree_object)
            self.update_data_sizes()
            self.update_rectangles(self.rect)
            return tree_object
        else:
            return None

    def copy_paste(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, this method
        copies the given, and moves the copy to the last subtree of
        <destination>. Otherwise, does nothing.
        """
        if not self._subtrees and destination._subtrees:  # self is a leaf
            # duplicate the file:
            copy_of_self = self.duplicate()

            # move the copy to different location
            copy_of_self.move(destination)

            # change data sizes and rectangle of respective nodes to account
            # for the change
            self.update_data_sizes()
            self.update_rectangles(self.rect)

    # **************************************************************************
    # ************* HELPER FUNCTION FOR TESTING PURPOSES  **********************
    # **************************************************************************
    def tree_traversal(self) -> List[Tuple[str, int, Tuple[int, int, int]]]:
        """For testing purposes to see the depth and colour attributes for each
        internal node in the tree. Used for passing test case 5.
        """
        if len(self._subtrees) > 0:
            output_list = [(self._name, self._depth, self._colour)]
            for tree in self._subtrees:
                output_list += tree.tree_traversal()
            return output_list
        else:
            return []

    # **************************************************************************
    # *********** METHODS DEFINED FOR STRING REPRESENTATION  *******************
    # **************************************************************************
    def get_path_string(self) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                   self.get_separator() + self._name

    def get_separator(self) -> str:
        """Returns the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Returns the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

    # **************************************************************************
    # **************** HELPER FUNCTION FOR TASK 7  *****************************
    # **************************************************************************
    def get_full_path(self) -> str:
        """Returns the path attribute for this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.

    === Private Attributes ===
    _path: the path that was used to instantiate this tree.
    """
    _path: str

    def __init__(self, my_path: str) -> None:
        """Stores the directory given by <my_path> into a tree data structure
        using the TMTree class.

        Precondition: <my_path> is a valid path for this computer.
        """
        # 1. Initialize the single attribute: self._path
        # 2. Implement the algorithm described in the handout.
        #
        # NOTES: - Review OS module documentation summary provided!
        #        - Remember to make good use of the superclass constructor!
        #        - Notice that the size of folders is calculated in the TMTree
        #          initializer. Thus, set data_size = 0 for the folders
        #
        self._path = my_path
        #
        if not os.path.isdir(self._path):  # if path is a file (leaf)
            # this is base case which returns a file or leaf of the
            # FileSystemTree, which is then appended into <lst_subtrees> later.
            super().__init__(os.path.basename(self._path), [],
                             os.path.getsize(self._path))
        else:  # if it is a folder or (Tree node)
            lst = os.listdir(self._path)
            lst_subtrees = []
            for item in lst:
                new_path = os.path.join(self._path, item)
                # my bug was that I wasn't sure how to return the FileSystemTree
                # object I created below and save it somewhere, because the
                # initializer doesn;t return anything. So how do I save what I
                # created in the recursive step? I simply append the
                # instantiation code (FileSystemTree object) into our subtree
                # list.
                lst_subtrees.append(FileSystemTree(new_path))  # recursion
            # now we instantiate the folder
            super().__init__(os.path.basename(self._path), lst_subtrees, 0)

    def get_full_path(self) -> str:
        """Returns the file path for the tree object.
        """
        return self._path

    def get_separator(self) -> str:
        """Returns the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Returns the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
