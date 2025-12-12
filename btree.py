import bisect
import random

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


    def removeLargest(self, mindeg):
        if self.leaf():
            return self.keys.pop()
        else:
            removed = self.children[-1].removeLargest(mindeg)
            self.fixViolation(len(self.children) - 1, mindeg)
            return removed


    def fixViolation(self, i, mindeg):
        child = self.children[i]
        if len(child.keys) < mindeg:
            left = self.children[i - 1] if i > 0 else None
            right = self.children[i+1] if i + 1 < len(self.children) else None

            if left and len(left.keys) > mindeg:
                k = left.keys.pop() # largest element from the left becomes the new separator
                child.keys.insert(0,self.keys[i - 1]) # separator is smaller than all the keys in the child
                self.keys[i - 1] = k

                # also take the right child  of the left sibling if present
                if len(left.children) > 0:
                    child.children.insert(0, left.children.pop())

            elif right and len(right.keys) > mindeg:
                k = right.keys.pop(0)
                child.keys.append(self.keys[i])

                # also take the left child of right sibling if present
                if len(right.children) > 0:
                    child.children.append(right.children.pop(0))
                self.keys[i] = k

            else:
                # No siblings have enough keys, we merge two nodes together
                new_node = BTreeNode()

                # find the separator to be moved down, use i to determine
                sep = i - 1 if i > 0 else 0

                middle = self.keys[sep]

                if left:
                    new_node.children = left.children + child.children
                    new_node.keys = left.keys + [middle] + child.keys

                    self.keys.remove(middle)

                    # remove the old nodes
                    self.children.remove(left)
                    self.children.remove(child)

                    # add the new node as a child
                    self.children.insert(i - 1, new_node)

                else:
                    new_node.children = child.children + right.children
                    new_node.keys = child.keys + [middle] + right.keys

                    self.keys.pop(sep)

                    # remove the old nodes
                    self.children.remove(right)
                    self.children.remove(child)

                    # add the new node as a child
                    # i is the index of the separator we are less than, which is now removed
                    # for a given i, i is the left child of the separator, i + 1 is the right child of the separator
                    self.children.insert(i , new_node)


    def delete(self,key, mindeg, root=False):
        # Case I: The node is in the leaf node
        if self.leaf():
            if key in self.keys:
                self.keys.remove(key)
                return True
            else:
                return False

        # Case II: The node is an internal node
        else:
            i = 0
            while (i < (len(self.keys)+1)):
                # If key matches, then found
                if len(self.keys) > i and key == self.keys[i]:
                    left = self.children[i]
                    right = self.children[i+1] if i < len(self.children) else None

                    if left:
                        self.keys[i] = left.removeLargest(mindeg)
                    elif right :
                        self.keys[i] = right.removeLargest(mindeg)

                    break

                # If key is not found, and there is enough children, 
                # then search the child between keys[i] and keys[i-1] (implied by the loop)
                # i == len(self.keys), that means that the search key must be greater than all the keys
                if len(self.keys) == i or key < self.keys[i]:
                    self.children[i].delete(key, mindeg)
                    break
                i+=1

            # Ensure that there is no violation in the children
            self.fixViolation(i, mindeg)

        # Case III: The height of the tree changes
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

    def isEmpty(self):
        return len(self.root.keys) == 0 and len(self.root.children) == 0

def testbtrees():
    print("Create BTree of minimum degree=2")
    btree = BTree(2)

    keys = []
    for _ in range(500):
        keys.append(_)
    random.shuffle(keys)
    print ("The list:", keys)

    for key in keys:
        btree.insert(key)
        print("Insert key:", key)
        btree.printtree()
        print("-----------")

    print("\n\nExpected true: ")
    for key in keys:
        result = btree.search(key)
        print("Search key:", key, "Found:", result)
        assert(result)

    print("\nExpected false: ")
    for key in [507,513,5000,-1,1000,3100,2900]:
        result = btree.search(key)
        print("Search key:", key, "Found:", result)
        assert(not result)

    delete = keys
    for key in delete:
        btree.delete(key)
        print("Delete key:", key)
        btree.printtree()
        print("-----------")

    assert(btree.isEmpty())

    for key in keys:
        btree.insert(key)

    delete.reverse()
    for key in delete:
        btree.delete(key)
        print("Delete key:", key)
        btree.printtree()
        print("-----------")

    assert(btree.isEmpty())

testbtrees()

