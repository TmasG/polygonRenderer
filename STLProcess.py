import numpy as np
import struct
# Loads STL unpacking the triangle vertexes stored as binary data.
def loadBinarySTL(filename):
    with open(filename, 'rb') as stl:
        # Reading past header (first 80 bytes) (1.3.11.1)
        stl.read(80)
        # Number of triangles (4 bytes) (1.3.11.1)
        numFaces = struct.unpack('i', stl.read(4))[0]
        print('Number of faces:' + str(numFaces))
        faces = np.zeros((numFaces,5,3))
        for i in range(numFaces):
            # For each triangle (1.3.11.2)
            # Datatype 'i' is 4 bytes, datatype 'iii' is 12 bytes
            faces[i][0] = struct.unpack('iii', stl.read(12)) # Normal vector
            faces[i][1] = struct.unpack('iii', stl.read(12)) # Vertex 1
            faces[i][2] = struct.unpack('iii', stl.read(12)) # Vertex 2
            faces[i][3] = struct.unpack('iii', stl.read(12)) # Vertex 3
            # d value for plane equation of v1.N=d
            d = faces[i][0][0]*faces[i][1][0]+faces[i][0][1]*faces[i][1][1]+faces[i][0][2]*faces[i][1][2]
            faces[i][4][0] = d
            # Null buffer
            stl.read(2)
    return(faces)

# Test whether a point is in the bounds of a face triangle
def testInBounds(face,point):
    # Calculate minimum distances of point to lines AB, BC, CA
    A = face[1]
    C = face[2]
    D = face[3] 
    B = point
    o = np.add(A,(np.subtract(B,A))*((np.dot(np.cross(np.subtract(C,A),np.subtract(D,C)),np.cross(np.subtract(B,A),np.subtract(D,C))))/np.linalg.norm(np.cross(np.subtract(B,A),np.subtract(D,C)))**2))
    print(o)
    # print(face)
    # print(point)

faces = loadBinarySTL('houseExa.stl')
# print(faces)
# testInBounds(faces[2],np.array([1,1,1]))
testInBounds([[0,0,1],np.array([0,0,0]),np.array([2,0,0]),np.array([1,1,0])],np.array([1,-1,0]))




# Next todo:
# Step 1: Figure out why distances can be negative
# Step 2: Find better way of finding minimum distance
# Step 3: Find where line from intersection point to closest line point makes 2nd intersection. (what line does the perpendicular line intersect with)
# Step 4: Detect if intersection point is in triangle bound
# Step 5: Profit