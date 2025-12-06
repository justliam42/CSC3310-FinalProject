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
                left,mid,right = child.split

                self.children.insert(i, left) 
                self.children.insert(i+1, right) 
                bisect.insort(self.keys,mid)

        # This isn't the prettiest but it makes sense to me anyways,
        # If this is the root, and we need to split, then do so and return a new root
        if root and len(self.keys) > maxdeg:
            newroot = BTreeNode()
            left,mid,right = self.split()
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

        return (left,self.keys[i_mid],right)

    def delete(self,key, mindeg):
        if self.leaf():
            bisect.insort(self.keys,key) # insert into sorted list and keep sorted
            i = bisect.bisect_left(self.keys, key)
            if i != len(self.keys) and self.keys[i] == key:
                del self.keys[i]
                return True
            else:
                return False
        else:
            i = 0
            while (i < (len(self.keys)+1)):
                # If key matches, then found
                if len(self.keys) > i and key == self.keys[i]:
                    left = self.children[i-1] if i > 0 else None
                    right = self.children[i+1] if i < len(self.children) else None
                    if left:
                        self.keys[i] = left.keys.pop()
                    else:
                        self.keys[i] = right.keys.pop(0)
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
                left = self.children[i-1] if i > 0 else None
                right = self.children[i+1] if i < len(self.children) else None

                if left and left.keys > mindeg:
                    k = left.keys.pop()
                    child.keys.insert(0,self.keys[i])
                    self.keys[i] = k
                elif right and right.keys > mindeg:
                    k = right.keys.pop(0)
                    child.keys.append(self.keys[i])
                    self.keys[i] = k
                else:
                    # No siblings have enough keys, we merge two nodes together
                    new_node = BTreeNode()
                    i = bisect.bisect_left(self.keys, k)
                    if left:
                        mid_i = i

                        new_node.children = left.children + child.children
                        new_node.keys = left.keys + self.keys[mid_i] + child.keys
                        self.keys.pop(mid_i)
                    else:
                        mid_i = i+1
                        new_node.children = child.children + right.children
                        new_node.keys = child.keys + self.keys[mid_i] + right.keys
                        self.keys.pop(mid_i)


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
        self.root.delete(key, self.mindeg)

    def printtree(self):
        self.root.display()

def testbtrees():
    print("Create BTree of minimum degree=2")
    btree = BTree(2)
    keys = [10, 20, 5, 6, 12, 30, 7, 17]
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

    for key in keys:
        btree.delete(key)
        print("Delete key:", key)
        btree.printtree()
        print("-----------")

testbtrees()

