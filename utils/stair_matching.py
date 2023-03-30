from math import sqrt

class Stair_point():
    def __init__(self, point, children=[], error=.05):
        self.children = list()
        self.point = point
        self.error = error
        for child in children:
            self.children.append((self.point[0]-child[0], self.point[1]-child[1], child))
        self.children.sort(reverse=True)

    def add_children(self, child):
        self.children.append((self.point[0]-child[0], self.point[1]-child[1], child))
        self.children.sort(reverse=True)

    def calc_ratio(self, x, y, x_dif, y_dif):
        return sqrt(x**2+y**2)/sqrt(x_dif**2+y_dif**2)

    def near(self, x_dif, y_dif):
        for x, y, n in self.children:
            temp = (sqrt(x**2+y**2)/sqrt(x_dif**2+y_dif**2))
            x = x/temp
            y = y/temp
            low = temp*(1+self.error)
            high = temp*(1-self.error)
            if (float(x*high) <= x_dif <= float(x*low)) and ((float(y*low) <= y_dif <= float(y*high)) or (float(y*high) <= y_dif <= float(y*low))):
                return n
        return None

    def align(self, target_points):
        matches = []
        for point in target_points:
            match = [(self.point, point.point)]

            for x_dif, y_dif, p in point.children:
                if self.near(x_dif, y_dif):
                    match.append((self.near(x_dif, y_dif), p))
            matches.append(match)
        return matches

def average(x1, x2, y1, y2):
    return ((x1+x2)/2, (y1+y2)/2)

def average_list(list1):
    toReturn = []
    for point in list1:
        toReturn.append(average(point[0], point[1], point[2], point[3]))
    return toReturn

def asign_points(list1):
    toReturn = []
    for i in range(len(list1)):
        temp = list1.pop(0)
        toReturn.append(Stair_point(temp, list1))
        list1.append(temp)
    return toReturn

def compare(l1, l2):
    toReturn = []
    for ele in l1:
        if ele not in l2:
            toReturn.append(ele)
    return toReturn

def create_dictionary(l1):
    toReturn = []
    for i in range(len(l1[0])):
        temp = dict()
        toReturn.append(temp)
    for i in range(len(l1)):
        for j in range(len(l1[0])):
            toReturn[j][l1[i][j][0]]

def find_alignments(stair_points):
    n = 1
    x = asign_points(stair_points[0])
    y = asign_points(stair_points[n])
    best = (0, [])
    highs = []
    for i in range(len(x)):
        temp = x[i].align(y)
        for j in range(len(temp)):
            print(temp[j], len(temp[j]), end="\n\n")
            if len(temp[j]) > best[0]:
                best = [len(temp[j]), (temp[j])]

    
    
# x = ([[267, 76], [1008, 84], [364, 95], [617, 137], [422, 153], [276, 236], [813, 239], 
# [509, 292], [655, 509], [1100, 533], [352, 664], [957, 672], [687, 799]])
# y = ([[461, 13], [771, 63], [141, 72], [386, 112], [199, 130], [60, 206], [576, 206], 
# [284, 270], [426, 474], [856, 497], [133, 624], [726, 636], [457, 760]])

# x.sort()
# y.sort()

# x = asign_points(x)
# y = asign_points(y)
# best = (0, [])
# highs = []
# for i in range(len(x)):
#     temp = x[i].align(y)
#     for j in range(len(temp)):
#         print(temp[j], len(temp[j]), end="\n\n")
#         if len(temp[j]) > best[0]:
#             best = [len(temp[j]), (temp[j])]
#         if len(temp[j]) > 7:
#             highs.append(temp[j])
#     print("#")
#     print()
# print(best[1], best[0])
# for l in highs:
#     print(l, len(l), end="]\n\n")
# print(compare(highs[0], highs[1]))
# print(compare(highs[1], highs[0]))