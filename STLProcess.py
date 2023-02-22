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
    i = point
    # O is Where AI meets BC (Figure 2.1.1.15c)
    o = np.add(a,(np.subtract(i,a))*(np.dot(np.cross(np.subtract(b,a),np.subtract(c,b)),np.cross(np.subtract(i,a),np.subtract(c,b)))/np.linalg.norm(np.cross(np.subtract(i,a),np.subtract(c,b)))**2))
    # Lambda for location of O on line BC (Figure 3.1.1.x)
    OlamBC = (o[0]-b[0])/(c[0]-b[0])
    # Mew for location of I on line AO (Figure 3.1.1.x)
    ImewAO = (i[0]-a[0])/(o[0]-a[0])
    # Check if O is in bounds of BC and I is in bounds of AO (Figure 3.1.1.x)
    result = 0<OlamBC and OlamBC<1 and 0<ImewAO and ImewAO<1
    return(result)

faces = loadBinarySTL('houseExa.stl')
# print(faces)
# testInBounds(faces[2],np.array([1,1,1]))
print(testInBounds([[0,0,1],np.array([-2,-2,0]),np.array([4,-2,0]),np.array([0,5,0])],np.array([1,6,0])))