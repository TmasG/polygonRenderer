import numpy as np
import struct
import math
import tfil
tfil.getConfig()
# Adjusts scale of 3d object coordinates
def objRotate(coords):
    x = np.array([1,0,0,0,math.cos(tfil.config["objRotate"][0]),-math.sin(tfil.config["objRotate"][0]),0,math.sin(tfil.config["objRotate"][0]),math.cos(tfil.config["objRotate"][0])]).reshape(3,3)
    y = np.array([math.cos(tfil.config["objRotate"][1]),0,math.sin(tfil.config["objRotate"][1]),0,1,0,-math.sin(tfil.config["objRotate"][1]),0,math.cos(tfil.config["objRotate"][1])]).reshape(3,3)
    z = np.array([math.cos(tfil.config["objRotate"][2]),-math.sin(tfil.config["objRotate"][2]),0,math.sin(tfil.config["objRotate"][2]),math.cos(tfil.config["objRotate"][2]),0,0,0,1]).reshape(3,3)
    newCoords = np.dot(z,np.dot(y,np.dot(x,coords)))
    return(newCoords)
def objTranslate(coords):
    newCoords=np.add(coords,tfil.config["objTranslate"])
    return(newCoords)

def objScale(coords):
    newCoords = np.multiply(coords,tfil.config["objScale"])
    return(newCoords)

def objAdjustVertex(coords):
    newCoords = objTranslate(objScale(objRotate(coords)))
    return(newCoords)

# Loads STL unpacking the triangle vertices stored as binary data.
def loadBinarySTL(filename):
    global numFaces
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
            stl.read(12) # reading past normal
            faces[i][1] = objAdjustVertex(struct.unpack('fff', stl.read(12))) # Vertex 1
            faces[i][2] = objAdjustVertex(struct.unpack('fff', stl.read(12))) # Vertex 2
            faces[i][3] = objAdjustVertex(struct.unpack('fff', stl.read(12))) # Vertex 3
            # Calculating Normal
            AB = np.subtract(faces[i][2],faces[i][1])
            AC = np.subtract(faces[i][3],faces[i][1])
            faces[i][0] = np.cross(AB,AC)
            # d value for plane equation of v1.N=d, storing with triangle in  faces[i][4][0]
            faces[i][4][0] = np.dot(faces[i][1], faces[i][0])
            # Null buffer
            stl.read(2)
            print(faces[i][1:4])
    return(faces)

# Test whether a point is in the bounds of a face triangle
def testInBounds(face,point):
    # Calculate minimum distances of point to lines AB, BC, CA
    a = face[1]
    b = face[2]
    c = face[3] 
    i = point
    # O is Where AI meets BC (Figure 2.1.1.15c)

    numerator = np.dot(np.cross(np.subtract(b,a),np.subtract(c,b)),np.cross(np.subtract(i,a),np.subtract(c,b)))
    denominator = np.linalg.norm(np.cross(np.subtract(i,a),np.subtract(c,b)))**2
    if 0 == denominator :
        # print ("Zero division error: ray is parallel to a face plane")
        return(False)
    o = np.add(a,(np.subtract(i,a))*(numerator/denominator))
    # Lambda for location of O on line BC (Figure 3.1.1.y)
    if b[0]!=c[0]:
        # print ("Zero division error: Bx==Cx")
        OlamBC = (o[0]-b[0])/(c[0]-b[0])
    elif b[1]!=c[1]:
        # print ("Zero division error: By==Cy")
        OlamBC = (o[1]-b[1])/(c[1]-b[1])
    elif b[2]!=c[2]:
        # print ("Zero division error: Bz==Cz" + str(np.equal(b,c)))
        OlamBC = (o[2]-b[2])/(c[2]-b[2])
    else:
        print ("Zero division error: Coordinates B and C are the same")
        return(False)

    # Mew for location of I on line AO (Figure 3.1.1.y)
    if o[0]!=a[0]:
        ImewAO = (i[0]-a[0])/(o[0]-a[0])
    elif o[1]!=a[1]:
        # print ("Zero division error: Ox==Ax")
        ImewAO = (i[1]-a[1])/(o[1]-a[1])
    elif o[2]!=a[2]:
        # print ("Zero division error: Oy==Ay" + str(np.equal(o,a)))
        ImewAO = (i[2]-a[2])/(o[2]-a[2])
    else:
        print ("Zero division error: Coordinates O and A are the same")
        return(False)
    # Check if O is in bounds of BC and I is in bounds of AO (Figure 3.1.1.x)
    result = 0<=OlamBC and OlamBC<=1 and 0<=ImewAO and ImewAO<1
    return(result)

# print(testInBounds(np.array([[0,0,1],[0,0,0],[5,0,0],[-1,6,0]]),np.array([0,100,0])))

faces = loadBinarySTL(tfil.config["stlFile"])
# print(faces)

# faces = np.array([[[0,0,0],[-100,0,-100],[-100,0,100],[0,0,-100],[0,0,0]],
#     [[0,0,0],[0,0,100],[-100,0,100],[0,0,-100],[0,0,0]],
#     [[0,0,0],[-100,0,-100],[-100,0,100],[-100,50,-100],[0,0,0]],
#     [[0,0,0],[0,0,100],[0,0,-100],[0,50,-100],[0,0,0]],
#     [[0,0,0],[-100,0,-100],[0,0,-100],[-100,50,-100],[0,0,0]],
#     [[0,0,0],[-100,50,-100],[0,50,-100],[0,0,-100],[0,0,0]],
#     [[0,0,0],[-100,50,-100],[-100,0,100],[0,50,-100],[0,0,0]],
#     [[0,0,0],[0,50,-100],[0,0,100],[-100,0,100],[0,0,0]]
#     ])
# numFaces = len(faces)
# for i in range(len(faces)):
#     # Adjusting normal and vertices
#     faces[i][1] = objAdjustVertex(faces[i][1])
#     faces[i][2] = objAdjustVertex(faces[i][2])
#     faces[i][3] = objAdjustVertex(faces[i][3])
#     AB = np.subtract(faces[i][2],faces[i][1])
#     AC = np.subtract(faces[i][3],faces[i][1])
#     # Calculating normal
#     faces[i][0] = np.cross(AB,AC)
#     faces[i][4][0] = np.dot(faces[i][1], faces[i][0])