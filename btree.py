import bisect

# Result pattern class so that we can return a result and a location (if it is false it is still useful to see where it should be)
class searchResult:
    def __init__(self, found:bool, loc):
        self.found = found
        self.loc = loc

class BTreeNode:
    def __init__(self):
        self.keys = [] # list of keys (actual values)
        self.children = [] # list of children (ranges of values between each key)

    def display(self, level=0):
        print(f"Level {level}: {self.keys}")
        for child in self.children:
            child.display(level + 1)


    def leaf(self):
        return len(self.children) == 0

    def search(self, key):
        # iterate through keys
        for i in range(len(self.keys)+1):
            # If key matches, then found
            if len(self.keys) > i and key == self.keys[i]:
                return searchResult(True,self)

            # If key is not found, and there is enough children, 
            # then search the child between keys[i] and keys[i-1] (implied by the loop)
            # i == len(self.keys), that means that the search key must be greater than all the keys
            if not self.leaf() and (len(self.keys) == i or key < self.keys[i]):
                return self.children[i].search(key)
        return searchResult(False,self)
            

    def insert(self, key, maxdeg, root=True):
        """ Insert an element into the btree
            Inputs:
                Key - the element to be inserted
                Maxdeg - the maximum degree of the tree
                root - used internally, should be true if not a recursive call
            Returns: The (potentially new) root of the BTree, with the key inserted
        """
        if self.leaf():
            bisect.insort(self.keys,key) # insert into sorted list and keep sorted

        else:
            i = 0
            # iterate through keys
            while (i < (len(self.keys)+1)):
                # If key matches, then found
                if len(self.keys) > i and key == self.keys[i]:
                    return self # this implies we have no duplicates

                # If key is not found, and there is enough children, 
                # then search the child between keys[i] and keys[i-1] (implied by the loop)
                # i == len(self.keys), that means that the search key must be greater than all the keys
                if len(self.keys) == i or key < self.keys[i]:
                    self.children[i].insert(key, maxdeg, root=False)
                    break
                
                i+=1
        
            child = self.children[i]
            if len(child.keys) > maxdeg:
                left,mid,right = child.split()

                # delete the child first
                self.children.pop(i)

                self.children.insert(i, left) 
                self.children.insert(i+1, right) 
                bisect.insort(self.keys,mid)

        # This isn't the prettiest but it makes sense to me anyways,
        # If this is the root, and we need to split, then do so and return a new root
        if root and len(self.keys) > maxdeg:
            newroot = BTreeNode()
            left,mid,right = self.split()

            # left and right roots should still contain the old children
            newroot.children = [left,right]
            newroot.keys = [mid]
            return newroot
        else: 
            return self
            
        

    def split(self):
        """Splits a node into two, returning a left node, a middle key, and a right node"""
        left,right = BTreeNode(),BTreeNode()
        i_mid = len(self.keys) // 2

        left.keys = self.keys[:i_mid]
        right.keys = self.keys[i_mid+1:]

        # children with keys less than the mid key should go to the left
        left.children = self.children[:i_mid+1]

        # children with keys greater than the mid key shoud go to the right
        right.children = self.children[i_mid+1:]

        return (left,self.keys[i_mid],right)

    def delete(self,key, mindeg, root=False):
        # NTS: every pop, remove, delete action should be followed by a verification of b tree ness
        # NTS: root node can violate the rule, so it can have just one element
        if self.leaf():
            if key in self.keys:
                self.keys.remove(key)
                return True
            else:
                return False
        else:
            i = 0
            while (i < (len(self.keys)+1)):
                # If key matches, then found
                if len(self.keys) > i and key == self.keys[i]:
                    left = self.children[i]
                    right = self.children[i+1] if i < len(self.children) else None

                    if left:
                        self.keys[i] = left.keys[-1]
                        left.delete(self.keys[i], mindeg)
                    elif right :
                        self.keys[i] = right.keys[0]
                        right.delete(self.keys[i], mindeg)

                    break

                # If key is not found, and there is enough children, 
                # then search the child between keys[i] and keys[i-1] (implied by the loop)
                # i == len(self.keys), that means that the search key must be greater than all the keys
                if len(self.keys) == i or key < self.keys[i]:
                    self.children[i].delete(key, mindeg)
                    break
                i+=1

            child = self.children[i]
            if len(child.keys) < mindeg:
                left = self.children[i - 1] if i > 0 else None
                right = self.children[i+1] if i + 1 < len(self.children) else None

                # NTS: self.keys[i] is NOT the separator
                if left and len(left.keys) > mindeg:
                    # find separator between the left sibling and child
                    # it has a left sibling so this is at least 0
                    sep = 0
                    if len(child.keys) > 0:
                        sep = bisect.bisect_left(self.keys, child.keys[0]) - 1


                    k = left.keys.pop() # largest element from the left
                    child.keys.insert(0,self.keys[i]) # separator is smaller than all the keys in the child

                    # also take the right child  of the left sibling if present
                    if len(left.children) > 0:
                        child.children.insert(0, left.children.pop())

                    self.keys[sep] = k # move largest element from the left to the parent
                elif right and len(right.keys) > mindeg:
                    k = right.keys.pop(0)
                    child.keys.append(self.keys[i])

                    # also take the left child of right sibling if present
                    if len(right.children) > 0:
                        child.children.insert(0, right.children.pop(0))
                    self.keys[i] = k
                else:
                    # No siblings have enough keys, we merge two nodes together
                    new_node = BTreeNode()

                    # find the separator to be moved down, use smallest element from child
                    sep = 0
                    if len(child.keys) > 0:
                        sep = bisect.bisect_left(self.keys, child.keys[0]) - 1
                    
                    middle = self.keys[sep]

                    # cases: had a left sibling, had a right sibling, had no siblings
                    if left:
                        new_node.children = left.children + child.children
                        new_node.keys = left.keys + [middle] + child.keys

                        self.keys.pop(sep)

                        # remove the old nodes
                        self.children.remove(left)
                        self.children.remove(child)

                        # add the new node as a child
                        # TODO: fix where it is being added, it's not always at the end
                        self.children.insert(i, new_node)

                    else:
                        new_node.children = child.children + right.children
                        new_node.keys = child.keys + [middle] + right.keys
                        
                        self.keys.pop(sep)

                        # remove the old nodes
                        self.children.remove(right)
                        self.children.remove(child)

                        # add the new node as a child
                        # TODO: fix where it is being added, it's not always at the end
                        # i is the index of the separator we are less than, which is now removed
                        # for a given i, i is the left child of the separator, i + 1 is the right child of the separator
                        self.children.insert(i , new_node)
        if root and len(self.keys) == 0:
            # if the root is empty, then the tree has reconfigured such that the new root is at level 1
            # remove empty root and assign level 1 as the new root
            self.keys = self.children[0].keys
            self.children = self.children[0].children


class BTree:
    def __init__(self, mindeg):
        self.root = BTreeNode()
        self.mindeg = mindeg # min degree of children a node can have (maxdegree = 2(mindeg) - 1)
        self.maxdeg = mindeg*2

    def search(self, key):
        return self.root.search(key).found
        
    def insert(self, key):
        self.root = self.root.insert(key,self.maxdeg)

    def delete(self, key):
        self.root.delete(key, self.mindeg, True)

    def printtree(self):
        self.root.display()

def testbtrees():
    print("Create BTree of minimum degree=2")
    btree = BTree(1)
    # example from: https://www.youtube.com/watch?v=K1a2Bk8NrYQ
    keys = [20, 40, 10, 30, 32, 50, 60, 5, 15, 25, 28, 31, 32, 35, 45, 55, 65]

    for key in keys:
        btree.insert(key)
        print("Insert key:", key)
        btree.printtree()
        print("-----------")

    print("\n\nExpected true: ")
    for key in keys:
        print("Search key:", key, "Found:",btree.search(key))
    print("\nExpected false: ")
    for key in [11,13,0,-1,100,31,29]:
        print("Search key:", key, "Found:",btree.search(key))

    delete = [31, 28, 45, 32]
    for key in delete:
        btree.delete(key)
        print("Delete key:", key)
        btree.printtree()
        print("-----------")

    btree = BTree(2)
    keys = [59, 23, 7, 97, 73, 67, 19, 79, 61, 41]

    for key in keys:
        btree.insert(key)

    keys.reverse()
    for key in keys:
        btree.delete(key)
        print("Delete key:", key)
        btree.printtree()
        print("-----------")

testbtrees()

