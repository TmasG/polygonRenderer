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
def objScale(coords,scaler):
    newCoords = np.multiply(coords,scaler)
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
            # faces = np.zeros((fileNumFaces,5,3))
            print("Faces:")
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
                print(face)
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
def testInBounds(face,point):
    # Calculate minimum distances of point to lines AB, BC, CA
    a = face[1]
    b = face[2]
    c = face[3] 
    i = point
    # O is Where AI meets BC (Figure 2.1.1.15c)
    c1 = np.cross(np.subtract(b,a),np.subtract(c,b))
    c2 = np.cross(np.subtract(i,a),np.subtract(c,b))
    numerator = np.dot(c1,c2)
    TimeA = time.time()
    c1 = np.subtract(i,a)
    c2 = np.subtract(c,b)
    TimeB = time.time()
    c3 = np.cross(c1,c2)
    TimeC = time.time()
    denominator = c3[0]**2+c3[1]**2+c3[2]**2
    # denominator = np.linalg.norm(c3)**2
    TimeD = time.time()
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
    # Is O is in bounds of BC and I is in bounds of AO (Figure 3.1.1.x)
    result = 0<=np.around(OlamBC,tfil.config["decimalAccuracy"]) and np.around(OlamBC,tfil.config["decimalAccuracy"])<=1 and 0<=np.around(ImewAO,tfil.config["decimalAccuracy"]) and np.around(ImewAO,tfil.config["decimalAccuracy"])<1
    times[1] += TimeB-TimeA
    times[2] += TimeC-TimeB
    times[3] += TimeD-TimeC
    return(result)
faces = loadBinarySTLs(tfil.config["stlFiles"])
lights = loadLightSources(tfil.config["lightSources"])