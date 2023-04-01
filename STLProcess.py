import numpy as np
import struct
import math
import tfil
import time
times = [0,0,0,0]
tfil.getConfig()
# Adjusts scale of 3d object coordinates
def objRotate(coords,rots):
    x = np.array([1,0,0,0,math.cos(rots[0]),-math.sin(rots[0]),0,math.sin(rots[0]),math.cos(rots[0])]).reshape(3,3)
    y = np.array([math.cos(rots[1]),0,math.sin(rots[1]),0,1,0,-math.sin(rots[1]),0,math.cos(rots[1])]).reshape(3,3)
    z = np.array([math.cos(rots[2]),-math.sin(rots[2]),0,math.sin(rots[2]),math.cos(rots[2]),0,0,0,1]).reshape(3,3)
    newCoords = np.dot(z,np.dot(y,np.dot(x,coords)))
    return(newCoords)
def objTranslate(coords,translator):
    newCoords=np.add(coords,translator)
    return(newCoords)
def objScale(coords,scalar):
    newCoords = np.multiply(coords,scalar)
    return(newCoords)
def objAdjustVertex(coords,fn):
    newCoords = objTranslate(objScale(objRotate(coords,tfil.config["objRotate"][fn]),tfil.config["objScale"][fn]),tfil.config["objTranslate"][fn])
    return(newCoords)
# Loads STLs unpacking the triangle vertices stored as binary data.
def loadBinarySTLs(filenames):
    global numFaces
    faces = []
    numFaces = 0
    for fn in range(len(filenames)):
        with open(filenames[fn], 'rb') as stl:
            # Reading past header (first 80 bytes) (1.3.11.1)
            stl.read(80)
            # Number of triangles (4 bytes) (1.3.11.1)
            fileNumFaces = struct.unpack('i', stl.read(4))[0]
            # print("Faces:")
            for i in range(fileNumFaces): 
                face = np.zeros((5,3))
                # For each triangle (1.3.11.2)
                # Datatype 'f' is 4 bytes, datatype 'fff' is 12 bytes
                stl.read(12) # reading past normal
                face[1] = objAdjustVertex(struct.unpack('fff', stl.read(12)),fn) # Vertex 1
                face[2] = objAdjustVertex(struct.unpack('fff', stl.read(12)),fn) # Vertex 2
                face[3] = objAdjustVertex(struct.unpack('fff', stl.read(12)),fn) # Vertex 3
                # Calculating Normal
                AB = np.subtract(face[2],face[1])
                AC = np.subtract(face[3],face[1])
                face[0] = np.cross(AB,AC)
                # d value for plane equation of v1.N=d, storing with triangle in face[4][0]
                face[4][0] = np.dot(face[1], face[0])
                # Null buffer
                stl.read(2)
                # print(face)
                faces.append(face)
            # print(i)
            numFaces += fileNumFaces
    print('Number of faces:' + str(numFaces))
    return(np.array(faces))

def loadLightSources(filename):
    global numLights
    lights = np.array(tfil.readJson(filename))
    numLights = len(lights)
    print("Lights:")
    for i in range(len(lights)):
        # Light face Normal
        AB = np.subtract(lights[i][1],lights[i][2])
        AC = np.subtract(lights[i][1],lights[i][3])
        lights[i][0] = np.cross(AB,AC)
        # Normalizing light face normal
        lights[i][0] = lights[i][0]/np.linalg.norm(lights[i][0])
        # d value for plane equation of v1.N=d, storing with light source in lights[i][4][0]
        lights[i][4][0] = np.dot(lights[i][1], lights[i][0])
        print(lights[i])
        # Where lights[4][1] is the light power
    return(lights)
# Test whether a point is in the bounds of a face triangle
def testInBounds(face,point,acc):
    # Calculate minimum distances of point to lines AB, BC, CA
    a = face[1]
    b = face[2]
    c = face[3] 
    i = point
    ab = [b[0]-a[0],
        b[1]-a[1],
        b[2]-a[2]]
    ai = [i[0]-a[0],
        i[1]-a[1],
        i[2]-a[2]]
    bc = [c[0]-b[0],
        c[1]-b[1],
        c[2]-b[2]]
    AICrossBC = [
        ai[1]*bc[2]-ai[2]*bc[1],
        ai[2]*bc[0]-ai[0]*bc[2],
        ai[0]*bc[1]-ai[1]*bc[0]]
    denominator = AICrossBC[0]*AICrossBC[0]+AICrossBC[1]*AICrossBC[1]+AICrossBC[2]*AICrossBC[2]
    if denominator == 0:
        # print ("Zero division error: ray is parallel to a face plane")
        return(False)
    numerator = (ai[0]*ab[0]+ai[1]*ab[1]+ai[2]*ab[2])*(bc[0]*bc[0]+bc[1]*bc[1]+bc[2]*bc[2])-(bc[0]*ai[0]+bc[1]*ai[1]+bc[2]*ai[2])*(ab[0]*bc[0]+ab[1]*bc[1]+ab[2]*bc[2])
    if numerator == 0:
        print("numerator=0")
    m = numerator/denominator
    p = [ai[0]*m,
        ai[1]*m,
        ai[2]*m]
    # Lambda for location of O on line BC (Figure 3.1.1.7)
    if not bc[0]==0:
        OlamBC = (a[0]+p[0]-b[0])/bc[0]
    elif not bc[1]==0:
        # print ("Zero division error: Bx==Cx")
        OlamBC = (a[1]+p[1]-b[1])/bc[1]
    elif not bc[2]==0:
        # print ("Zero division error: By==Cy")
        OlamBC = (a[2]+p[2]-b[2])/bc[2]
    else:
        print ("Zero division error: Coordinates B and C are the same")
        return(False)
    # Mew for location of I on line AO (Figure 3.1.1.7)
    if not m==0:
        ImewAO = acc/m
    else:
        print ("Zero division error: Coordinates O and A are the same so P=0",a,i)
        ImewAO = 0
        # return(False)
    # Is O is in bounds of BC and I is in bounds of AO
    truOlamBC = (OlamBC//acc)*acc
    truImewAO = (ImewAO//acc)
    result = 0 <= truOlamBC and truOlamBC <= 1 and 0 <= truImewAO and truImewAO < 1
    return(result)
faces = loadBinarySTLs(tfil.config["stlFiles"])
lights = loadLightSources(tfil.config["lightSources"])
if tfil.config["diffuseChildren"][0]%2==0:
    posHalf = 0.5
else:
    posHalf = 0