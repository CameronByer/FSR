class Line:
    def __init__(self, p1, p2):
        if p1[0] == p2[0]:
            self.xint = p1[0]
            self.yint = None
            self.slope = None
        else:
            self.slope = (p2[1]-p1[1])/(p2[0]-p1[0])
            self.yint = p1[1]-p1[0]*self.slope
            self.xint = self.getx(0)
    def getx(self, y):
        if self.slope == 0:
            return None
        if self.slope == None:
            return self.xint
        return (y-self.yint)/self.slope
    def gety(self, x):
        if self.slope == None:
            return None
        return self.yint+x*self.slope

def mergelists(a, b):
    merged = []
    while a!=[] and b!=[]:
        if a[0]<b[0]:
            merged.append(a.pop(0))
        else:
            merged.append(b.pop(0))
    return merged+a+b
