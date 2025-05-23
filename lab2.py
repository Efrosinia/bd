import math

def name_hash(name: str):
    return tuple(ord(c) for c in name.lower())

# Node creation
class Node:
    def __init__(self, order):
        self.order = order
        self.values = []
        self.keys = []
        self.nextKey = None
        self.parent = None
        self.check_leaf = False

    # Insert at the leaf
    def insert_at_leaf(self, leaf, value, key):
        if self.values:
            for i in range(len(self.values)):
                if name_hash(value) == name_hash(self.values[i]):
                    self.keys[i].append(key)
                    break
                elif name_hash(value) < name_hash(self.values[i]):
                    self.values = self.values[:i] + [value] + self.values[i:]
                    self.keys = self.keys[:i] + [[key]] + self.keys[i:]
                    break
                elif i + 1 == len(self.values):
                    self.values.append(value)
                    self.keys.append([key])
                    break
        else:
            self.values = [value]
            self.keys = [[key]]


# B plus tree
class BplusTree:
    def __init__(self, order):
        self.root = Node(order)
        self.root.check_leaf = True

    # Insert operation
    def insert(self, value, key):
        value = str(value)
        old_node = self.search(value)
        old_node.insert_at_leaf(old_node, value, key)

        if (len(old_node.values) == old_node.order):
            node1 = Node(old_node.order)
            node1.check_leaf = True
            node1.parent = old_node.parent
            mid = int(math.ceil(old_node.order / 2)) - 1
            node1.values = old_node.values[mid + 1:]
            node1.keys = old_node.keys[mid + 1:]
            node1.nextKey = old_node.nextKey
            old_node.values = old_node.values[:mid + 1]
            old_node.keys = old_node.keys[:mid + 1]
            old_node.nextKey = node1
            self.insert_in_parent(old_node, node1.values[0], node1)

    # Search operation for different operations
    def search(self, value):
        current_node = self.root
        while not current_node.check_leaf:
            for i in range(len(current_node.values)):
                if name_hash(value) == name_hash(current_node.values[i]):
                    current_node = current_node.keys[i + 1]
                    break
                elif name_hash(value) < name_hash(current_node.values[i]):
                    current_node = current_node.keys[i]
                    break
                elif i + 1 == len(current_node.values):
                    current_node = current_node.keys[i + 1]
                    break
        return current_node

    # Find the node
    def find(self, value, key):
        l = self.search(value)
        for i, item in enumerate(l.values):
            if name_hash(item) == name_hash(value):
                return key in l.keys[i]
        return False

    # Inserting at the parent
    def insert_in_parent(self, n, value, ndash):
        if (self.root == n):
            rootNode = Node(n.order)
            rootNode.values = [value]
            rootNode.keys = [n, ndash]
            self.root = rootNode
            n.parent = rootNode
            ndash.parent = rootNode
            return

        parentNode = n.parent
        temp3 = parentNode.keys
        for i in range(len(temp3)):
            if (temp3[i] == n):
                parentNode.values = parentNode.values[:i] + \
                    [value] + parentNode.values[i:]
                parentNode.keys = parentNode.keys[:i +
                                                  1] + [ndash] + parentNode.keys[i + 1:]
                if (len(parentNode.keys) > parentNode.order):
                    parentdash = Node(parentNode.order)
                    parentdash.parent = parentNode.parent
                    mid = int(math.ceil(parentNode.order / 2)) - 1
                    parentdash.values = parentNode.values[mid + 1:]
                    parentdash.keys = parentNode.keys[mid + 1:]
                    value_ = parentNode.values[mid]
                    if (mid == 0):
                        parentNode.values = parentNode.values[:mid + 1]
                    else:
                        parentNode.values = parentNode.values[:mid]
                    parentNode.keys = parentNode.keys[:mid + 1]
                    for j in parentNode.keys:
                        j.parent = parentNode
                    for j in parentdash.keys:
                        j.parent = parentdash
                    self.insert_in_parent(parentNode, value_, parentdash)

    def get_numbers_by_name(self, value):
        leaf = self.search(value)
        for i, item in enumerate(leaf.values):
            if name_hash(item) == name_hash(value):
                return leaf.keys[i]
        return [] 
    
    def find_names_by_comparison(self, value, comparison='>'):
        result = []
        value_hashed = name_hash(value)
        
        node = self.root
        while not node.check_leaf:
            node = node.keys[0]
        
        while node:
            for name, numbers in zip(node.values, node.keys):
                name_hashed = name_hash(name)
                if (comparison == '>' and name_hashed > value_hashed) or \
                   (comparison == '<' and name_hashed < value_hashed):
                    result.append((name, numbers))
            node = node.nextKey
        return result
    
     # Delete a node
    def delete(self, value, key):
        node_ = self.search(value)

        temp = 0
        for i, item in enumerate(node_.values):
            if item == value:
                temp = 1

                if key in node_.keys[i]:
                    if len(node_.keys[i]) > 1:
                        node_.keys[i].pop(node_.keys[i].index(key))
                    elif node_ == self.root:
                        node_.values.pop(i)
                        node_.keys.pop(i)
                    else:
                        node_.keys[i].pop(node_.keys[i].index(key))
                        del node_.keys[i]
                        node_.values.pop(node_.values.index(value))
                        self.deleteEntry(node_, value, key)
                else:
                    print("Value not in Key")
                    return
        if temp == 0:
            print("Value not in Tree")
            return

    # Delete an entry
    def deleteEntry(self, node_, value, key):

        if not node_.check_leaf:
            for i, item in enumerate(node_.keys):
                if item == key:
                    node_.keys.pop(i)
                    break
            for i, item in enumerate(node_.values):
                if item == value:
                    node_.values.pop(i)
                    break

        if self.root == node_ and len(node_.keys) == 1:
            self.root = node_.keys[0]
            node_.keys[0].parent = None
            del node_
            return
        elif (len(node_.keys) < int(math.ceil(node_.order / 2)) and node_.check_leaf == False) or (len(node_.values) < int(math.ceil((node_.order - 1) / 2)) and node_.check_leaf == True):

            is_predecessor = 0
            parentNode = node_.parent
            PrevNode = -1
            NextNode = -1
            PrevK = -1
            PostK = -1
            for i, item in enumerate(parentNode.keys):

                if item == node_:
                    if i > 0:
                        PrevNode = parentNode.keys[i - 1]
                        PrevK = parentNode.values[i - 1]

                    if i < len(parentNode.keys) - 1:
                        NextNode = parentNode.keys[i + 1]
                        PostK = parentNode.values[i]

            if PrevNode == -1:
                ndash = NextNode
                value_ = PostK
            elif NextNode == -1:
                is_predecessor = 1
                ndash = PrevNode
                value_ = PrevK
            else:
                if len(node_.values) + len(NextNode.values) < node_.order:
                    ndash = NextNode
                    value_ = PostK
                else:
                    is_predecessor = 1
                    ndash = PrevNode
                    value_ = PrevK

            if len(node_.values) + len(ndash.values) < node_.order:
                if is_predecessor == 0:
                    node_, ndash = ndash, node_
                ndash.keys += node_.keys
                if not node_.check_leaf:
                    ndash.values.append(value_)
                else:
                    ndash.nextKey = node_.nextKey
                ndash.values += node_.values

                if not ndash.check_leaf:
                    for j in ndash.keys:
                        j.parent = ndash

                self.deleteEntry(node_.parent, value_, node_)
                del node_
            else:
                if is_predecessor == 1:
                    if not node_.check_leaf:
                        ndashpm = ndash.keys.pop(-1)
                        ndashkm_1 = ndash.values.pop(-1)
                        node_.keys = [ndashpm] + node_.keys
                        node_.values = [value_] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                p.values[i] = ndashkm_1
                                break
                    else:
                        ndashpm = ndash.keys.pop(-1)
                        ndashkm = ndash.values.pop(-1)
                        node_.keys = [ndashpm] + node_.keys
                        node_.values = [ndashkm] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(p.values):
                            if item == value_:
                                parentNode.values[i] = ndashkm
                                break
                else:
                    if not node_.check_leaf:
                        ndashp0 = ndash.keys.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.keys = node_.keys + [ndashp0]
                        node_.values = node_.values + [value_]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndashk0
                                break
                    else:
                        ndashp0 = ndash.keys.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.keys = node_.keys + [ndashp0]
                        node_.values = node_.values + [ndashk0]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndash.values[0]
                                break

                if not ndash.check_leaf:
                    for j in ndash.keys:
                        j.parent = ndash
                if not node_.check_leaf:
                    for j in node_.keys:
                        j.parent = node_
                if not parentNode.check_leaf:
                    for j in parentNode.keys:
                        j.parent = parentNode

# Print the tree
def printTree(tree):
    lst = [tree.root]
    level = [0]

    while lst:
        node = lst.pop(0)
        lev = level.pop(0)
        print("Level", lev, "Values:", node.values)

        if not node.check_leaf:
            for child in node.keys:
                if isinstance(child, Node):
                    lst.append(child)
                    level.append(lev + 1)

def print_tree(tree):
    if not tree.root:
        print("Tree is empty")
        return

    queue = [(tree.root, 0)]
    current_level = 0

    print(f"Level {current_level}:")

    while queue:
        node, level = queue.pop(0)

        if level > current_level:
            current_level = level
            print(f"\nLevel {current_level}:")

        if node.check_leaf:
            print(f"Leaf: {node.values}", end=" | ")
        else:
            print(f"Internal: {node.values}", end=" | ")
            for child in node.keys:
                queue.append((child, level + 1))
    print("\n")


record_len = 4
bplustree = BplusTree(record_len)
print("=== Step 1: Inserting 'Alex' ===")
bplustree.insert("Alex", "0951234567")
printTree(bplustree)
print("=" * 40)

print("=== Step 2: Inserting 'Abby' ===")
bplustree.insert("Abby", "0955555555")
printTree(bplustree)
print("=" * 40)

print("=== Step 3: Inserting 'Andrew' ===")
bplustree.insert("Andrew", "0501122334")
printTree(bplustree)
print("=" * 40)

print("=== Step 4: Inserting 'Maria' ===")
bplustree.insert("Maria", "0639876543")
printTree(bplustree)
print("=" * 40)

print("=== Step 5: Inserting 'Zara' ===")
bplustree.insert("Zara", "0674455667")
printTree(bplustree)
print("=" * 40)

print("=== Step 6: Inserting 'Irene' ===")
bplustree.insert("Irene", "0937788990")
printTree(bplustree)
print("=" * 40)

print("=== Step 7: Inserting 'David' ===")
bplustree.insert("David", "0911111111")
printTree(bplustree)
print("=" * 40)

print("=== Step 8: Inserting 'Sophie' ===")
bplustree.insert("Sophie", "0922222222")
printTree(bplustree)
print("=" * 40)

print("=== Step 9: Inserting 'Bob' ===")
bplustree.insert("Bob", "0933333333")
printTree(bplustree)
print("=" * 40)

print("=== Step 10: Inserting 'John' ===")
bplustree.insert("John", "0944444444")
printTree(bplustree)
print("=" * 40)

print("=== Step 11: Inserting 'Emily' ===")
bplustree.insert("Emily", "0955555555")
printTree(bplustree)
print("=" * 40)

print_tree(bplustree)

# if(bplustree.find('Sophie', '34')):
#     print("Found")
# else:
#     print("Not found")

# print(name_hash("Abby") < name_hash("Alex"))
# print(name_hash("Alex"))
# print(name_hash("Abby"))
# print(name_hash("Andrew"))
# print(name_hash("Maria"))

# print(bplustree.get_numbers_by_name("Maria"))
greater_than = bplustree.find_names_by_comparison("Andrew", ">")
less_than = bplustree.find_names_by_comparison("Andrew", "<")

print("Імена, більші за 'Andrew':")
for name in greater_than:
    print(" -", name)

print("\nІмена, менші за 'Andrew':")
for name in less_than:
    print(" -", name)

bplustree.delete("John", "0944444444")
printTree(bplustree)

bplustree.delete("David", "0911111111")
printTree(bplustree)


