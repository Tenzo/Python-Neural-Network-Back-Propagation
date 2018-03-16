import sys
import numpy as np
import heapq

class NodePoint():
    def __init__(self):
        self._x = np.random.random_sample()/10
        self._y = np.random.random_sample()/10
        
    def x(self):
        return self._x
    def y(self):
        return self._y
    def setX(self, x):
        self._x = x
    def setY(self, y):
        self._y = y
    def __repr__(self):
        return "<%s , %s>" % (self._x, self._y)
    def __str__(self):
        return "<%s , %s>" % (self._x, self._y)

class Vertex:
    def __init__(self, node, nodePoint):
        self.id = node
        self.nodePoint = nodePoint
        self.adjacent = {}
        # Set distance to infinity for all nodes
        self.distance = 100000000
        # Mark all nodes unvisited        
        self.visited = False  
        # Predecessor
        self.previous = None

    def setNodePoint(self, nodePoint):
        self.nodePoint = nodePoint
        
    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def set_distance(self, dist):
        self.distance = dist

    def get_distance(self):
        return self.distance

    def set_previous(self, prev):
        self.previous = prev

    def set_visited(self):
        self.visited = True
        
    def unvisit(self):
        self.visited = False
        self.previous = None
        self.distance = 100000000
        
    def set_id(self, newId):
        self.id = newId
        

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])
    
    def __lt__(self, other):
        return self.distance < other.distance

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node, nodePoint):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node, nodePoint)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return list(self.vert_dict.keys())

    def set_previous(self, current):
        self.previous = current

    def get_previous(self, current):
        return self.previous
    
    def prepareNet(self, size, window):
        
        edgeSize = window/(size-1)
        nodeList = []
        k = 0
        for i in range(size):
            row = []
            
            for j in range(size):
                nodePoint = NodePoint()
                #nodePoint.setX(edgeSize * i)
                #nodePoint.setY(edgeSize * j)
                row.append((chr(b'a'[0]+ k), nodePoint))
                k += 1
            nodeList.append(row)
        
        for row in nodeList:
            for node in row:
                self.add_vertex(node[0], node[1])
                
        #poziome
        for i in range(size):
            for j in range(size - 1):
                self.add_edge(nodeList[i][j][0], nodeList[i][j+1][0], 1)
        
        for i in range(size):
            for j in range(size - 1):
                self.add_edge(nodeList[j][i][0], nodeList[j+1][i][0], 1)
                
    def updateNode(self, node, x, y):
            if node in self.vert_dict:
                updated = NodePoint()
                updated.setX(x)
                updated.setY(y)
                self.vert_dict[node].setNodePoint(updated)
            else:
                print("Node not found - cannot been updated")
    
    def getShortest(self, nodeA, nodeB):
        for node in self.get_vertices():
            self.get_vertex(node).unvisit()
        self.dijkstra( self.get_vertex(nodeA), self.get_vertex(nodeB))

        target = self.get_vertex(nodeB)
        path = [target.get_id()]
        self.shortest(target, path)
        #print ('The shortest path : %s' %(path[::-1])
        return path[::-1]
        

    def shortest(self, v, path):
        ''' make shortest path from v.previous'''
        if v.previous:
            path.append(v.previous.get_id())
            self.shortest( v.previous, path)
        return



    def dijkstra(self, start, target):
        #print('''Dijkstra's shortest path''')
        # Set the distance for the start node to zero 
        start.set_distance(0)
    
        # Put tuple pair into the priority queue
        unvisited_queue = [(v.get_distance(),v) for v in self]
        heapq.heapify(unvisited_queue)
    
        while len(unvisited_queue):
            # Pops a vertex with the smallest distance 
            uv = heapq.heappop(unvisited_queue)
            current = uv[1]
            current.set_visited()
    
            #for next in v.adjacent:
            for next in current.adjacent:
                # if visited, skip
                if next.visited:
                    continue
                new_dist = current.get_distance() + current.get_weight(next)
                
                if new_dist < next.get_distance():
                    next.set_distance(new_dist)
                    next.set_previous(current)
                    #print('updated : current = %s next = %s new_dist = %s' \
                    #        %(current.get_id(), next.get_id(), next.get_distance()))
                #else:
                    #print('not updated : current = %s next = %s new_dist = %s' \
                    #        %(current.get_id(), next.get_id(), next.get_distance()))
    
            # Rebuild heap
            # 1. Pop every item
            while len(unvisited_queue):
                heapq.heappop(unvisited_queue)
            # 2. Put all vertices not visited into the queue
            unvisited_queue = [(v.get_distance(),v) for v in self if not v.visited]
            heapq.heapify(unvisited_queue)
    
if __name__ == '__main__':

    nodes = []
    for i in range(5):
        for j in range(5):
            nodes.append([NodePoint()for x in range(4)])
    graph = Graph()
    graph.prepareNet(4, 500)

    print ('Graph data:')
    for v in graph:
        for w in v.get_connections():
            vid = v.get_id()
            wid = w.get_id()
            #print ('( %s , %s, %3d)'  % ( vid, wid, v.get_weight(w)))
            
    graph.getShortest('g', 'b')
    print(graph.get_vertices())
    graph.updateNode('a', 2, 3)
    for node in list(graph.get_vertices()):
        print (graph.get_vertex(node).nodePoint)