import tfil
import STLProcess
import numpy as np
import time
from PIL import Image
def saveImage(pixels):
    img = Image.fromarray(pixels)
    if img.mode != "rgb":
        img = img.convert("RGB")
    img.save(tfil.config["outputFileName"])

def lineFaceInter(point,vector,face):
    N = face[0]
    d = face[4][0]
    P = point
    V = vector
    x = 0
    if np.dot(N,V) == 0:
        # print("N perpendicular to V", str(N), str(V))
        #  Fix this, this shouble reflect back the ray (i think)
        inter = False
        r = [0,0,0]
    else:
        inter = True
        x = (d-np.dot(N,P))/(np.dot(N,V)) 
        r = np.add(P,V*x)
    # returns if there is an intersection and the location and distance if so
    return(inter,r,x)

def switchXY(pixels):
    newPixels = np.zeros((tfil.config["resolution"][1],tfil.config["resolution"][0]))
    for i in range(tfil.config["resolution"][1]):
        for j in range(tfil.config["resolution"][0]):
            newPixels[i][j] = pixels[j][tfil.config["resolution"][1]-i-1]
    return(newPixels)

def firstIntersection(point, inters):
    minInterFace = inters[0][0]
    inter = inters[0][1]
    # Ịnitialising distance as first distance
    minDistance = np.linalg.norm(np.subtract(point, inters[0][1]))
    # For each intersection compare the distance to the previous smallest distance
    for m in range(len(inters)):
        distance = np.linalg.norm(np.subtract(point, inters[m][1]))
        if distance < minDistance:
            minInterFace = inters[m][0]
            inter = inters[m][1]
        minDistance = distance
    return([minInterFace,minDistance,inter])

def testForIntersections(point,vector,faces,facesLength):
    inters = []
    for l in range(facesLength):
        c = time.time()
        intersection = lineFaceInter(point,vector,faces[l])
        d = time.time()
        # If there is an intersection and said intersection is in front of the ray
        if intersection[0] and intersection[2]>0:
            if STLProcess.testInBounds(faces[l],intersection[1]):
                # If intersection is valid
                inters.append([faces[l],intersection[1]])
        e = time.time()
    return(inters)

def reflectRay(point,vector,face,count,distance):
    mults = 0
    N = face[0][0]
    d = face[0][4][0]
    I = face[2]
    A = np.subtract(I,vector)
    M=np.add(A,((d-np.dot(A,N))/np.dot(N,N))*N)
    baseReflectedVector = np.add(I,np.subtract(A,2*M))
    for i in range(tfil.config["rayChildren"]):
        # For each child ray
        # Varying direction of child rays
        reflectedVector = baseReflectedVector
        # Lambert cosine law
        lambert = 1
        # Recursively simulate the ray
        mult = simulateRay(I, reflectedVector, count+1,distance)
        # Accounting for surface reflectivity and lambert cosine law
        distance += mult[1]
        mults += mult[0]*(tfil.config["surfaceReflectivity"] * lambert)
    # Calculate average of all children
    fMult = mults/tfil.config["rayChildren"]
    return(fMult,distance)

def calcLightIntensity(power,distance):
    return(power/(4*np.pi*distance**2))
    
def simulateRay(point, vector, count,distance):
    # Terminate ray if too old?
    TimeA = time.time()
    if count > tfil.config["maxBounces"]:
        return(0,0)
    # Does ray intersect with and light sources?
    lightInters = testForIntersections(point,vector,STLProcess.lights,STLProcess.numLights)
    # Going through each valid light source intersection and finding the first one to occur
    lInter = len(lightInters) != 0
    if len(lightInters) != 0:
        light = firstIntersection(point, lightInters)
    TimeB = time.time()
    # Does ray intersect with any faces?
    faceInters = testForIntersections(point,vector,STLProcess.faces,STLProcess.numFaces)
    # faceInters = []
    # Going through each valid face intersection and finding the first one to occur
    fInter = len(faceInters) != 0
    TimeC = time.time()
    if len(faceInters) != 0:
        face = firstIntersection(point, faceInters)
        fMult = reflectRay(point,vector,face,count,distance)
    TimeD = time.time()
    # bMult represents the brightness multiplier
    if fInter or lInter:
        if lInter:
            if fInter:
                if face[1] < light[1]:
                    # Face in front
                    bMult = fMult[0]
                    distance += fMult[1]
                else:
                    # Light in front
                    bMult = light[0][4][1]
                    distance += light[1]
            else:
                # Just light
                bMult = light[0][4][1]
                distance += light[1]
        else:
            # Just face
            bMult = fMult[0]
            distance += fMult[1]
    else:
        # No intersections
        bMult = 0
        # print("a")
    STLProcess.times[1] += TimeB-TimeA
    STLProcess.times[2] += TimeC-TimeB
    STLProcess.times[3] += TimeD-TimeC
    return(bMult,distance)
    
def render():
    global pixels
    pixels = np.zeros((tfil.config["resolution"][0],tfil.config["resolution"][1]))
    focalPoint = np.array(tfil.config["focalPoint"])
    for i in range(tfil.config["resolution"][0]):
        a = time.time()
        STLProcess.times = [0,0,0,0]
        for j in range(tfil.config["resolution"][1]):
            subPixels = 0
            for x in range(tfil.config["subRays"][0]):
                for y in range(tfil.config["subRays"][1]):
                    # pixel = np.array([(i*tfil.config["cameraSize"][0]/tfil.config["resolution"][0])+(-0.5*i*tfil.config["cameraSize"][0]/tfil.config["resolution"][0])+((x/tfil.config["subRays"][0])*(tfil.config["cameraSize"][0]/tfil.config["resolution"][0])),0,(j*tfil.config["cameraSize"][1]/tfil.config["resolution"][1])+(-0.5*j*tfil.config["cameraSize"][1]/tfil.config["resolution"][1])+((y/tfil.config["subRays"][1])*(tfil.config["cameraSize"][1]/tfil.config["resolution"][1]))])
                    pixel = np.array([tfil.config["cameraSize"][0]/tfil.config["resolution"][0]*(i/2+x/tfil.config["subRays"][0]),0,tfil.config["cameraSize"][1]/tfil.config["resolution"][1]*(j/2+y/tfil.config["subRays"][1])])
                    rayVector = np.subtract(pixel,focalPoint)
                    ray = simulateRay(focalPoint,rayVector,0,np.linalg.norm(rayVector))
                    subPixels += calcLightIntensity(ray[0],ray[1])*tfil.config["gain"]
                    # subPixels += ray[0]*tfil.config["gain"]
            pixels[i][j] = 255*subPixels/(tfil.config["subRays"][0])
        STLProcess.times[0] = time.time()-a
        print(i, str(STLProcess.times))
    # Ạdding a test pixel halfway along the x and y axes
    pixels[int(tfil.config["resolution"][0]/2)-1][0] = 255
    pixels[0][int(tfil.config["resolution"][1]/2)-1] = 255
    return(switchXY(pixels))

a = time.time()
pixels = render()
b = time.time()
print(b-a)
count = 0
for i in pixels:
    for j in i:
        if j==1:
            count+=1
print(count)
saveImage(pixels)

# Todo:
# still need to do distribution and lambert