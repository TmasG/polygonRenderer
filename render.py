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
    if np.dot(N,V) == 0:
        print("N perpendicular to V", str(N), str(V))
        inter = False
        r = [0,0,0]
    else:
        inter = True
        x = (d-np.dot(N,P))/(np.dot(N,V)) 
        r = np.add(P,V*x)
    # returns if there is an intersection and the distance if so
    return(inter,r)

def switchXY(pixels):
    newPixels = np.zeros((tfil.config["resolution"][1],tfil.config["resolution"][0]))
    for i in range(tfil.config["resolution"][1]):
        for j in range(tfil.config["resolution"][0]):
            newPixels[i][j] = pixels[j][tfil.config["resolution"][1]-i-1]
    return(newPixels)

def renderShadow():
    pixels = np.zeros((tfil.config["resolution"][0],tfil.config["resolution"][1]))
    for i in range(tfil.config["resolution"][0]):
        for j in range(tfil.config["resolution"][1]):
            # For pixel i,j:
            focalPoint = np.array(tfil.config["focalPoint"])
            # Vector of ray from focal point to pixel
            pixel = np.array([i-0.5*tfil.config["resolution"][0],0,j-0.5*tfil.config["resolution"][1]])
            rayVector = np.subtract(pixel,focalPoint)
            for k in range(STLProcess.numFaces):
                intersection = lineFaceInter(focalPoint,rayVector,STLProcess.faces[k])
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
pixels = renderShadow()
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
# do boundary tests on loadBinarySTL.
# fix loadBinarySTL