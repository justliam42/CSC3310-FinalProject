class BTreeNode:
    def __init__(self, leaf):
        self.leaf = leaf # Is true if the node is a leaf
        self.keys = [] # list of keys (actual values)
        self.children = [] # list of children (ranges of values between each key)

class BTree:
    def __init__(self, mindeg):
        self.root = BTreeNode(True)
        self.mindeg = mindeg # min degree of children a node can have (maxdegree = 2(mindeg) - 1)
    def insert(self, key):
        root = self.root
        if len(root.keys) == (2 * self.mindeg) - 1: # root is full
            newnode = BTreeNode(False)
            newnode.children.append(root)
            self.split_child(newnode, 0)
            self.root = newnode
            self.insert_not_full(newnode, key)
        else:
            self.insert_not_full(root, key)

    def insert_not_full(self, node, key):
        idx = len(node.keys) - 1
        if node.leaf:
            # inserting key into correct position of leaf node
            node.keys.append(0)
            while idx >= 0 and key < node.keys[idx]:
                node.keys[idx + 1] = node.keys[idx]
                idx -= 1
            node.keys[idx + 1] = key
        else:
            # finds which child will have the new key
            while idx >= 0 and key < node.keys[idx]:
                idx -= 1
            idx += 1

            # splitting child if its full
            if len(node.children[idx].keys) == (2 * self.mindeg) - 1:
                self.split_child(node, idx)
                if key > node.keys[idx]:
                    idx += 1
            self.insert_not_full(node.children[idx], key)

    def split_child(self, parent, idx):
        mindeg = self.mindeg
        node = parent.children[idx]
        newnode = BTreeNode(node.leaf)
        parent.keys.insert(idx, node.keys[mindeg - 1])
        parent.children.insert(idx+1, newnode)

        # split the keys
        newnode.keys = node.keys[mindeg:]
        node.keys = node.keys[:mindeg - 1]

        # split children if they are not a leaf node
        if not node.leaf:
            newnode.children = node.children[mindeg:]
            node.children = node.children[:mindeg]



    def printtree(self, node=None, lvl=0):
        if node is None:
            node = self.root
        print("Level", lvl, "Keys: ", node.keys)
        for child in node.children:
            self.printtree(child, lvl + 1)

def testbtrees():
    print("Create BTree of minimum degree=2")
    btree = BTree(2)
    for key in [10, 20, 5, 6, 12, 30, 7, 17]:
        btree.insert(key)
        print("Insert key:", key)
        btree.printtree()
        print("-----------")
testbtrees()

