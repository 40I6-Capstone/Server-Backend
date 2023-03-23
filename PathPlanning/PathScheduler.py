import numpy as np

class PathScheduler:

    def __init__(self, nodeCount, paths):
        self.paths = paths
        self.nodeCount = nodeCount
        self.pathCosts = [0] * nodeCount
        self.assignedPathIndexes = []
        for i in range(nodeCount):
            self.assignedPathIndexes.append([])
        self.costAssign(self.lengthCost)


    # Print out the assignments computed by the scheduler
    def printAssignments(self,costFunction):
        print()
        print(f'Goal Mean: {self.getMeanCost(costFunction)}')
        for i in range(self.nodeCount):
            print(f'N: {i} Path: {self.assignedPathIndexes[i]} Cost: {self.pathCosts[i]}')

    # Return the cost of a path, represented by length
    def lengthCost(self,path):
        return path.length

    # Get the mean of the path costs
    def getMeanCost(self,costFunction):
        totalCost = 0
        for path in self.paths:
            totalCost += costFunction(path)
        mean = totalCost/self.nodeCount
        return mean

    # Assign a path to a node, updating the tracked total cost handled by the node
    def assignPath(self,nodeIndex,pathIndex,pCost):
        # print(f'Assigning path {pathIndex} to node {nodeIndex}')
        self.assignedPathIndexes[nodeIndex].append(pathIndex)
        self.pathCosts[nodeIndex] = self.pathCosts[nodeIndex] + pCost

    # Assign costs to nodes with some arbitrary cost function
    def costAssign(self, costFunction):
        # # Remember orignal path indexes
        # for index, path in enumerate(self.paths):
        #     path.presortIndex = index; 
        # Sort paths by cost, largest first
        self.paths.sort(key= (lambda path: path.length), reverse=True)
        mean = self.getMeanCost(costFunction)
        # Iterate thorugh the paths
        nodeIndex = 0
        for pathIndex, path in enumerate(self.paths):
            pCost = costFunction(path)
            # Iterate through each node, trying to assign a path to one of them
            assigned = False
            loopCount = 0
            while(not(assigned) and loopCount != self.nodeCount):
                if self.pathCosts[nodeIndex] + pCost  <= mean:
                    self.assignPath(nodeIndex,pathIndex,pCost)
                    assigned = True
                else:
                    nodeIndex = (nodeIndex + 1)%self.nodeCount
                loopCount = loopCount + 1
            if(not(assigned)):
                self.assignPath(nodeIndex,pathIndex,pCost)
                nodeIndex = (nodeIndex + 1)%self.nodeCount
        self.printAssignments(costFunction)