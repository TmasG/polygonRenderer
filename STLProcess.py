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
    a = face[1]
    b = face[2]
    c = face[3]
    p = point
    # Distances are still represented as type 'iii'

    Dab = np.cross(np.subtract(p,a),np.subtract(p,b))/np.linalg.norm(np.subtract(b,a))
    Dbc = np.cross(np.subtract(p,b),np.subtract(p,c))/np.linalg.norm(np.subtract(c,b))
    Dca = np.cross(np.subtract(p,c),np.subtract(p,a))/np.linalg.norm(np.subtract(a,c))
    print(Dab,Dbc,Dca)
    print(min(int(Dab[0]),int(Dbc[0]),int(Dca[0])))
    print(face)
    print(point)

faces = loadBinarySTL('houseExa.stl')
# print(faces)
testInBounds(faces[2],np.array([1,1,1]))