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
        inter = False
        r = [0,0,0]
    else:
        inter = True
        x = (d-np.dot(N,P))/(np.dot(N,V)) 
        r = np.add(P,V*x)
    # returns if there is an intersection and the distance if so
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
    return(minInterFace,minDistance,inter)

def testForIntersections(point,vector,faces,facesLength):
    inters = []
    for l in range(facesLength):
        intersection = lineFaceInter(point,vector,faces[l])
        # If there is an intersection and said intersection is in front of the ray
        if intersection[0] and intersection[2]>0:
            if STLProcess.testInBounds(faces[l],intersection[1]):
                # If intersection is valid
                inters.append([faces[l],intersection[1]])
    return(inters)

def reflectRay(point,vector,face,count):
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
        baseReflectedVector
        # Recursively simulate the ray
        mult = simulateRay(I, reflectedVector, count+1)
        # Accounting for surface reflectivity and lambert cosine law
        mult = mult*tfil.config["surfaceReflectivity"] * lambert
        mults += mult
    # Calculate average of all children
    fMult = mults/tfil.config["rayChildren"]
    return(fMult)
def calcLightIntensity(distance, power):
    return(power/(4*np.pi*distance**2))
    
def simulateRay(point, vector, count):
    # Terminate ray if too old?
    if count > tfil.config["maxBounces"]:
        return(0)
    # Does ray intersect with and light sources?
    lightInters = testForIntersections(point,vector,STLProcess.lights,STLProcess.numLights)
    # Going through each valid light source intersection and finding the first one to occur
    lInter = len(lightInters) != 0
    if len(lightInters) != 0:
        light = firstIntersection(point, lightInters)
        intensity = calcLightIntensity(light[1],light[0][4][1])
    # Does ray intersect with any faces?
    faceInters = testForIntersections(point,vector,STLProcess.faces,STLProcess.numFaces)
    # Going through each valid face intersection and finding the first one to occur
    fInter = len(faceInters) != 0
    if len(faceInters) != 0:
        face = firstIntersection(point, faceInters)
        fMult = reflectRay(point,vector,face,count)

    # bMult represents the brightness multiplier
    if fInter or lInter:
        if lInter: 
            if fInter:
                if face[1] < light[1]:
                    # Face in front
                    bMult = fMult
                else:
                    # Light in front
                    bMult = intensity
            else:
                # Just light
                bMult = intensity
        else:
            # Just face
            bMult = fMult
    else:
        # No intersections
        bMult = 0
    return(bMult)
    
def render():
    global pixels
    pixels = np.zeros((tfil.config["resolution"][0],tfil.config["resolution"][1]))
    for i in range(tfil.config["resolution"][0]):
        for j in range(tfil.config["resolution"][1]):
            # For pixel i,j:
            focalPoint = np.array(tfil.config["focalPoint"])
            # Vector of ray from focal point to pixel
            pixel = np.array([tfil.config["cameraSize"][0]*(i/tfil.config["resolution"][0]-0.5),0,tfil.config["cameraSize"][1]*(j/tfil.config["resolution"][1]-0.5)])
            rayVector = np.subtract(pixel,focalPoint)
            pixels[i][j] = 255*simulateRay(focalPoint,rayVector,0)
        print(i)
    # Ạdding a test pixel halfway along the x-axis
    pixels[int(tfil.config["resolution"][0]/2)-1][0] = 255
    return(switchXY(pixels))
def renderShadow():
    global pixels
    pixels = np.zeros((tfil.config["resolution"][0],tfil.config["resolution"][1]))
    for i in range(tfil.config["resolution"][0]):
        for j in range(tfil.config["resolution"][1]):
            # For pixel i,j:
            focalPoint = np.array(tfil.config["focalPoint"])
            # Vector of ray from focal point to pixel
            pixel = np.array([i-0.5*tfil.config["resolution"][0],0,j-0.5*tfil.config["resolution"][1]])
            rayVector = np.subtract(pixel,focalPoint)
            for k in range(STLProcess.numFaces):
                intersection = lineFaceInter(pixel,rayVector,STLProcess.faces[k])
                if not intersection[0]:
                    # If no intersection with face then skip to next face
                    continue
                if STLProcess.testInBounds(STLProcess.faces[k],intersection[1]):
                    # If face intersection is valid then set pixel
                    pixels[i][j] = 255
                    break
        print(i)
    pixels[50][0] = 120
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