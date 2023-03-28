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
    P = point
    V = vector
    NdotV = N[0]*V[0]+N[1]*V[1]+N[2]*V[2]
    inter = not (NdotV == 0)
    if inter:
        # x = (d-dot(N,P))/(dot(N,V))
        x = (face[4][0]-(N[0]*P[0]+N[1]*P[1]+N[2]*P[2]))/NdotV
        r = np.add(P,V*x)
    else:
        # print("N perpendicular to V", str(N), str(V))
        #  Fix this, this shouble reflect back the ray (i think)
        x = 0
        r = [0,0,0]
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
    TimeA = time.time()
    for l in range(facesLength):
        intersection = lineFaceInter(point,vector,faces[l])
        # If there is an intersection and said intersection is in front of the ray
        if intersection[0] and intersection[2]>10**(-1*tfil.config["decimalAccuracy"]):
            if STLProcess.testInBounds(faces[l],intersection[1]):
                # If intersection is valid
                inters.append([faces[l],intersection[1]])
    return(inters)

def rotate(A,B,theta):
    # Function to rotate vector A around vector B by angle theta:
    # Code:
    # Normalising  B:
    B = B/np.linalg.norm(B)
    vec = np.add(np.add(np.multiply(np.cos(theta),A),np.multiply(np.sin(theta),np.cross(B,A))),np.multiply(np.dot(B,A)*(1-np.cos(theta)),B))
    return(vec)
def reflectRay(point,vector,face,count,distance):
    N = face[0][0]
    d = face[0][4][0]
    I = face[2]
    A = np.subtract(I,vector)
    M = np.add(A,((d-(A[0]*N[0]+A[1]*N[1]+A[2]*N[2]))/(N[0]*N[0]+N[1]*N[1]+N[2]*N[2]))*N)
    V = np.add(I,np.subtract(A,2*M))
    specMults = 0
    # For each Specular ray
    # Lambert cosine law
    lambert = (V[0]*N[0]+V[1]*N[1]+V[2]*N[2])/(np.sqrt((V[0]*V[0]+V[1]*V[1]+V[2]*V[2])*(N[0]*N[0]+N[1]*N[1]+N[2]*N[2])))
    # Recursively simulate the ray
    mult = simulateRay(I, V, count+1,distance)
    # Accounting for surface reflectivity and lambert cosine law
    distance += mult[1]
    # Specular Component
    specMults += mult[0]*tfil.config["surfaceReflectivity"]
    # Difuse Component
    specMults += mult[0]*tfil.config["surfaceDiffusivity"]*lambert
    spec = calcLightIntensity(specMults,mult[1])
    gloss = 0
    if tfil.config["glossyChildren"] !=0:
        glossMults = 0
        for i in range(tfil.config["glossyChildren"]):
            # For each child ray
            # Varying direction of child rays
            # Should vary around the normal
            V = N
            multiplier = 0
            # Recursively simulate the ray
            mult = simulateRay(I, V, count+1,distance)
            # Difuse Component
            # Accounting for surface reflectivity and lambert cosine law
            glossMults += mult[0]*tfil.config["surfaceGlossyness"]*multiplier
        # Calculate average of all children
        gloss = calcLightIntensity(diffMults/tfil.config["diffuseChildren"],mult[1])

    diff = 0
    if tfil.config["diffuseChildren"][0] !=0 and tfil.config["diffuseChildren"][1] != 0:
        diffMults = 0
        if N[2] == 0:
            C = [0,0,1]
        else:
            mag = np.sqrt(N[0]*N[0]+N[1]*N[1])
            C = np.array([N[1],N[0],0])
        for n in range(tfil.config["diffuseChildren"][0]):
            theta = (n+0.5)*2*np.pi/tfil.config["diffuseChildren"][0]
            # Rotate normal around perpendicular vector to normal
            vec = np.add(rotate(N,C,theta), N)
            for m in range(tfil.config["diffuseChildren"][1]):
                alpha = (m+0.5)*np.pi/tfil.config["diffuseChildren"][1]
                # For each child ray
                # Varying direction of child rays
                # Rotate around  normal
                V = rotate(vec,N,alpha)
                lambert = (V[0]*N[0]+V[1]*N[1]+V[2]*N[2])/(np.sqrt((V[0]*V[0]+V[1]*V[1]+V[2]*V[2])*(N[0]*N[0]+N[1]*N[1]+N[2]*N[2])))
                # Recursively simulate the ray
                mult = simulateRay(I, V, count+1,distance)
                # Diffuse Component
                # Accounting for surface reflectivity and lambert cosine law
                diffMults += calcLightIntensity(mult[0]*tfil.config["surfaceDiffusivity"]*lambert,mult[1])
        # Calculate average of all children
        diff = diffMults/(tfil.config["diffuseChildren"][0]*tfil.config["diffuseChildren"][1])
    fMult = spec+gloss+diff
    return(fMult,distance)

def calcLightIntensity(power,distance):
    return(power/(4*np.pi*distance**2))
    
def simulateRay(point, vector, count,distance):
    # Terminate ray if too old?
    if count > tfil.config["maxBounces"]:
        return(0,0)
    # Does ray intersect with and light sources?
    lightInters = testForIntersections(point,vector,STLProcess.lights,STLProcess.numLights)
    # Going through each valid light source intersection and finding the first one to occur
    lInter = len(lightInters) != 0
    if len(lightInters) != 0:
        light = firstIntersection(point, lightInters)
    # Does ray intersect with any faces?
    faceInters = testForIntersections(point,vector,STLProcess.faces,STLProcess.numFaces)
    # faceInters = []
    # Going through each valid face intersection and finding the first one to occur
    fInter = len(faceInters) != 0
    if len(faceInters) != 0:
        face = firstIntersection(point, faceInters)
        fMult = reflectRay(point,vector,face,count,distance)
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
                    subPixels += ray[0]*tfil.config["gain"]
                    # subPixels += calcLightIntensity(ray[0],ray[1])*tfil.config["gain"]
                    # subPixels += ray[0]*tfil.["gain"]
            pixels[i][j] = 255*subPixels/(tfil.config["subRays"][0])
        STLProcess.times[0] = time.time()-a
        print(i, str(STLProcess.times))
    # Ạdding a test pixel halfway along the x and y axes
    # pixels[int(tfil.config["resolution"][0]/2)-1][0] = 255
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


# Debugging:
# if (i == 23 and j == 3) or (i==24 and j==0) or (i==25 and j ==3):
    # print(pixel, rayVector, ray, pixels[23][3],subPixels)

# Result:

# Erroneously black
# [11.5  0.   1.5] [ 11.5 100.    1.5] (0.0, 402.68101519689253) 0.0 0.0

# Normal black:
# [12.  0.  0.] [ 12. 100.   0.] (0, 100.71742649611338) 0.0 0.0

# Normal white:
# [12.5  0.   1.5] [ 12.5 100.    1.5] (3000000.0, 634.5512429875821) 0.0 0.8300533908607891
