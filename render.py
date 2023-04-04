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
    minInter = inters[0]
    minInterFace = minInter[0]
    inter = minInter[1]
    # Ịnitialising distance as first distance
    minDistance = np.linalg.norm(np.subtract(point, inter))
    # For each intersection compare the distance to the previous smallest distance
    for m in inters:
        distance = np.linalg.norm(np.subtract(point, m[1]))
        if distance < minDistance:
            minInterFace = m[0]
            inter = m[1]
            minDistance = distance
    return([minInterFace,minDistance,inter])

def testForIntersections(point,vector,faces,facesLength):
    inters = []
    acc = 0.1**tfil.config["decimalAccuracy"]
    # For each face in the STL
    for l in range(facesLength):
        face = faces[l]
        N = face[0]
        NdotV = N[0]*vector[0]+N[1]*vector[1]+N[2]*vector[2]
        #  If there is an intersection
        if not (NdotV == 0):
            # x = (d-dot(N,point))/(dot(N,vector))
            x = (face[4][0]-(N[0]*point[0]+N[1]*point[1]+N[2]*point[2]))/NdotV
            r = [point[0] + vector[0] * x,
                point[1] + vector[1] * x,
                point[2] + vector[2] * x]
            # If the intersection is in front of the ray origin
            if x>acc:
                if STLProcess.testInBounds(face,r,acc):
                    # If intersection is valid
                    inters.append([face,r])
        # else:
            # print("N perpendicular to V", str(N), str(vector))
            # Cross section of plane from perspective of ray is 0 so no interaction
    return(inters)

def rotate(A,B,theta):
    # Function to rotate vector A around vector B by angle theta:
    # Code:
    # Normalising  B:
    bMag = np.linalg.norm(B)
    if bMag < 10 **(-1*tfil.config["decimalAccuracy"]):
        print("bMag=0")
    B = B/bMag
    vec = np.add(np.add(np.multiply(np.cos(theta),A),np.multiply(np.sin(theta),np.cross(B,A))),np.multiply(np.dot(B,A)*(1-np.cos(theta)),B))
    return(vec)
def reflectRay(point,vector,face,count):
    N = face[0][0]
    d = face[0][4][0]
    I = face[2]
    A = np.subtract(I,vector)
    M = np.add(A,((d-(A[0]*N[0]+A[1]*N[1]+A[2]*N[2]))/(N[0]*N[0]+N[1]*N[1]+N[2]*N[2]))*N)
    V = np.add(I,np.subtract(A,2*M))
    spec = 0
    specMults = 0
    # For each Specular ray
    # Lambert cosine law
    lambertNum = (V[0]*N[0]+V[1]*N[1]+V[2]*N[2])
    if lambertNum == 0:
        lambert = 0
    else:
        lambertDenom = np.sqrt((V[0]*V[0]+V[1]*V[1]+V[2]*V[2])*(N[0]*N[0]+N[1]*N[1]+N[2]*N[2]))
        lambert = lambertNum/lambertDenom
    # Recursively simulate the ray
    mult = simulateRay(I, V, count+1)
    # Accounting for surface reflectivity and lambert cosine law
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
            mult = simulateRay(I, V, count+1)
            # Difuse Component
            # Accounting for surface reflectivity and lambert cosine law
            glossMults += mult[0]*tfil.config["surfaceGlossyness"]*multiplier
        # Calculate average of all children
        gloss = calcLightIntensity(diffMults/tfil.config["diffuseChildren"],mult[1])
    diff = 0
    if count <= tfil.config["maxDiffDepth"]:
        if tfil.config["diffuseChildren"][0] !=0 and tfil.config["diffuseChildren"][1] != 0:
            diffMults = 0
            if N[0] == 0:
                C = [1,0,0]
            else:
                C = [N[1],-1*N[0],0]
            for n in range(tfil.config["diffuseChildren"][0]):
                theta = (n+STLProcess.posHalf)*2*np.pi/tfil.config["diffuseChildren"][0]
                # Rotate normal around perpendicular vector to normal
                vec = np.add(rotate(N,C,theta), N)
                for m in range(tfil.config["diffuseChildren"][1]):
                    alpha = (m+STLProcess.posHalf)*np.pi/tfil.config["diffuseChildren"][1]
                    # For each child ray
                    # Varying direction of child rays
                    # Rotate around  normal
                    V = rotate(vec,N,alpha)
                    lambert = (V[0]*N[0]+V[1]*N[1]+V[2]*N[2])/(np.sqrt((V[0]*V[0]+V[1]*V[1]+V[2]*V[2])*(N[0]*N[0]+N[1]*N[1]+N[2]*N[2])))
                    # Recursively simulate the ray
                    mult = simulateRay(I, V, count+1)
                    # Diffuse Component
                    # Accounting for surface reflectivity and lambert cosine law
                    diffMults += calcLightIntensity(mult[0]*tfil.config["surfaceDiffusivity"]*lambert,mult[1])
            # Calculate average of all children
            diff = diffMults/(tfil.config["diffuseChildren"][0]*tfil.config["diffuseChildren"][1])
    fMult = spec+gloss+diff
    return(fMult)

def calcLightIntensity(power,distance):
    if power == 0:
        return 0
    return(power/(4*np.pi*distance**2))
    
def simulateRay(point, vector, count):
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
        fMult = reflectRay(point,vector,face,count)
    # bMult represents the brightness multiplier
    if fInter or lInter:
        if lInter:
            if fInter:
                if face[1] < light[1]:
                    # Face in front
                    bMult = fMult
                    distance = face[1]
                else:
                    # Light in front
                    bMult = light[0][4][1]
                    distance = light[1]
            else:
                # Just light
                bMult = light[0][4][1]
                distance = light[1]
        else:
            # Just face
            bMult = fMult
            distance = face[1]
    else:
        # No intersections
        bMult = 0
        distance = 0
    return(bMult,distance)
    
def render():
    global pixels
    pixels = np.zeros((tfil.config["resolution"][0],tfil.config["resolution"][1]))
    focalPoint = np.array(tfil.config["focalPoint"])
    for i in range(tfil.config["resolution"][0]):
        a = time.time()
        STLProcess.columnTime = 0
        for j in range(tfil.config["resolution"][1]):
            subPixels = 0
            for x in range(tfil.config["subRays"][0]):
                for y in range(tfil.config["subRays"][1]):
                    # pixel = np.array([(i*tfil.config["cameraSize"][0]/tfil.config["resolution"][0])+(-0.5*i*tfil.config["cameraSize"][0]/tfil.config["resolution"][0])+((x/tfil.config["subRays"][0])*(tfil.config["cameraSize"][0]/tfil.config["resolution"][0])),0,(j*tfil.config["cameraSize"][1]/tfil.config["resolution"][1])+(-0.5*j*tfil.config["cameraSize"][1]/tfil.config["resolution"][1])+((y/tfil.config["subRays"][1])*(tfil.config["cameraSize"][1]/tfil.config["resolution"][1]))])
                    pixel = np.array([tfil.config["cameraSize"][0]/tfil.config["resolution"][0]*(i/2+x/tfil.config["subRays"][0]),0,tfil.config["cameraSize"][1]/tfil.config["resolution"][1]*(j/2+y/tfil.config["subRays"][1])])
                    rayVector = [pixel[0]-focalPoint[0],
                        pixel[1]-focalPoint[1],
                        pixel[2]-focalPoint[2]]
                    ray = simulateRay(focalPoint,rayVector,0)
                    subPixels += ray[0]*tfil.config["gain"]
            pixels[i][j] = 255*subPixels/(tfil.config["subRays"][0])
        STLProcess.columnTime = time.time()-a
        print("Column:",i, "Previous Column Render Time:", np.round(STLProcess.columnTime,tfil.config["decimalAccuracy"]), "seconds")
    # Ạdding a test pixel halfway along the x and y axes
    # pixels[int(tfil.config["resolution"][0]/2)-1][0] = 255
    return(switchXY(pixels))

a = time.time()
pixels = render()
b = time.time()
print("Total Render Time:", np.round(b-a,tfil.config["decimalAccuracy"]), "seconds")
count = 0
for i in pixels:
    for j in i:
        if j==1:
            count+=1
saveImage(pixels)