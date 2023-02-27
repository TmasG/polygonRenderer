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
    x = (d-np.dot(N,P))/(np.dot(N,V))
    r = np.add(P,V*x)

    # print(r,V,N)
    return(r)

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
            inter = False
            for k in range(STLProcess.numFaces):
                intersection = lineFaceInter(focalPoint,rayVector,STLProcess.faces[k])
                if STLProcess.testInBounds(STLProcess.faces[k],intersection):
                    inter = True
                    break
            if not inter:
                pixels[i][j] = 255
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
# print(lineFaceInter(np.array([0,0,0]),np.array([0,1,0]),np.array([[0,1,0],[0,0,0],[0,0,0],[0,1,0],[4,0,0]])))

# Todo:
# Test that lambda equation works
# Go through render function and test each part 1 by 1
# Fix render