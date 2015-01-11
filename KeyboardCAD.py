###########################################################################
#USER PARAMETERS
###########################################################################
FREECADPATH = 'C://Program Files//FreeCAD 0.14//bin' # path to your FreeCAD.so or FreeCAD.dll file.  Bin folder
FREECADPATH2 = 'C://Program Files//FreeCAD 0.14//lib'# same as above, but to the lib folder
SAVEPATH = 'C:/Users/Nicholas/Desktop/new2.FCStd' #path indicating where and with what name you want to save the file
layoutPath = 'C:/Users/Nicholas/Desktop/layout2.txt' # path to a text file containing the raw data from http://www.keyboard-layout-editor.com/
plateXDim = 381 #overall length of the plate to be made, in mm
plateYDim = 152.4 #overall width of the plate to be made, in mm
xStart = 0 #Distance from left edge of plate to first key (not to first switch hole)
yStart = 0 #Distance from top edge of plate to first key (not to first switch hole)
plateThickness = 1.5 #plate thickness in mm. Not important if exporting to a 2D format
includeCutOuts = True #include four cutouts on the plate around each switch for the disassembly of switches while they are installed 
rotateSwitches = False #rotate all switches with cutouts by 90 degrees (so that cutouts are on the top and bottom)
includeStabilizers = "costar"  #make cutouts for stabilizers? Possible values: False, "costar", "cherry", "both"

###########################################################################
#LABEL PARAMETERS
###########################################################################
#Include these strings in the labels per key in the layout editor
#!r! for rotating a switch with cutouts by 90 degrees (so that cutouts are on the top and bottom)
#!c! for toggling the presence of a cutout on a switch
###########################################################################

###########################################################################
#MEASUREMENTS
###########################################################################
#SWITCH
KEYUNIT = 19.05 #the value of one unit
SWITCHSIZE = 13.9954 #in mm, each switch cut-out is a square with sides of this length. 13.9954 is for Cherry MX switches.
#CUTOUTS
CUTOUTLENGTH = 3.81 #each switch can have four cut-outs around it for switch disassembly. 
CUTOUTWIDTH = 1.016
CUTOUTSEPARATION = 5.3594 #distance between two cutouts on the same side of a switch
CUTOUTDST = (SWITCHSIZE - (2*CUTOUTLENGTH + CUTOUTSEPARATION))/2 #distance from top side of switch to the top of the first cutout. 0.508 
#STABILIZERS
MINIMUMLONGSTABLENGTH = 3 #If key is this wide or wider, use the long stabilizer. Since keys between 3 and units 6 units are unusual, this value can vary without changing anything.
COSTARLENGTH = 13.97 
COSTARWIDTH = 3.3 
COSTARSHORTSEPARATION = 20.57
COSTARLONGSEPARATION = 96.774 #long is for a spacebar. 
COSTARLONGSEPARATION2 = 63.353 # If you want two possible spacebar stabilizer positions to be cut out, add a value here. 
COSTARDST = 0.76
CHERRYLENGTH = 12.294
CHERRYWIDTH = 6.655
CHERRYSHORTSEPARATION = 17.22
CHERRYLONGSEPARATION = 93.421 #long is for a spacebar. 
CHERRYLONGSEPARATION2 = 60 # If you want two possible spacebar stabilizer positions to be cut out, add a value here
CHERRYDST = 1.3 
WIREWIDTH = 2.794 #for cherry only. Width of the cutout that connects the switch cutout to the stab cutout for wire installation.
WIREDST = 4.7 #cherry only. distance from top of switch cutout to top of the wire cutout.
WIREADDLENGTH = 0.89 #cherry only. Distance that the wire cutout extends past the stab cutout.
ADDCUTFORSHORT = True #more area beside the switch will be cut for short cherry stabilizers with cutouts present, if this is true. May not be desired for different switch/cutout sizes
###########################################################################


def main():
	getLayoutData()
	initializeCAD()	
	drawSwitches()
	drawStabilizers()
	save()
	
#FreeCAD methods
	
def sketchRectangle(posX, posY, xDim, yDim, rotation):
	global doc
	global sketchCount
	
	rectangle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))
	
	if not sketchCount == 0: #if it is the first sketch, then the pad doesn't exist yet
		rectangle.Support = (doc.Pad,["Face6"])
		
	sketchCount = sketchCount + 1
	
	#   0_______________3
	#	|				|
	#	|				|
	#	|				|
	#	|				|
	#	|				|
	#	|				|
	#  1|_______________|2
	
	x = [0]*4
	y = [0]*4
	
	x[0] = posX       
	y[0] = -posY
	x[2] = posX + xDim
	y[2] = -posY - yDim
	
	x[1] = x[0]
	y[1] = y[2]
	x[3] = x[2]
	y[3] = y[0]
	
	if rotation:
		for n in range(4):
			x[n], y[n] = rotatePoint((rotation[0],rotation[1]), (x[n],y[n]), rotation[2])
	
	for i in range(3):
		rectangle.addGeometry(Part.Line(App.Vector(x[i],y[i],0),App.Vector(x[i+1],y[i+1],0)))
	rectangle.addGeometry(Part.Line(App.Vector(x[3],y[3],0),App.Vector(x[0],y[0],0)))
	
	for j in range(3):
		rectangle.addConstraint(Sketcher.Constraint('Coincident',j,2,j+1,1)) 
	rectangle.addConstraint(Sketcher.Constraint('Coincident',3,2,0,1))

	for k in range(4):
		rectangle.addConstraint(Sketcher.Constraint('DistanceX',k,1,x[k])) 
		rectangle.addConstraint(Sketcher.Constraint('DistanceY',k,1,y[k])) 
	
	doc.recompute()
	
	return rectangle
	
def sketchSwitchWithCutOuts(posX, posY, rotation, rotate90):
	global doc
	global sketchCount
	
	rectangle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))
	
	rectangle.Support = (doc.Pad,["Face6"])
		
	sketchCount = sketchCount + 1
	
	#   0_______________ 19
	#2 _|1			  18|_  17
	# |					  |
	#3|_ 4			  15 _| 16
	#6 _|5			  14|_ 13
	# |				      |
	#7|_ 8			  11 _| 12
	# 9 |_______________| 10
	
	x = [0]*20
	y = [0]*20
	
	x[0] = posX    
	y[0] = -posY
	x[1] = x[0]
	y[1] = y[0] - CUTOUTDST 
	x[2] = x[0] - CUTOUTWIDTH
	y[2] = y[1]
	x[3] = x[2]
	y[3] = y[2] - CUTOUTLENGTH
	x[4] = x[0]
	y[4] = y[3]
	x[5] = x[0]
	y[5] = y[4] - CUTOUTSEPARATION
	x[6] = x[2]
	y[6] = y[5]
	x[7] = x[2]
	y[7] = y[6] - CUTOUTLENGTH
	x[8] = x[0]
	y[8] = y[7]
	x[9] = x[0]
	y[9] = y[8] - CUTOUTDST # -posY - SWITCHSIZE
	x[10] = posX + SWITCHSIZE
	y[10] = -posY - SWITCHSIZE
	x[11] = x[10]
	y[11] = y[8]
	x[12] = x[10] + CUTOUTWIDTH
	y[12] = y[11]
	x[13] = x[12]
	y[13] = y[6]
	x[14] = x[10]
	y[14] = y[13]
	x[15] = x[10]
	y[15] = y[4]
	x[16] = x[12]
	y[16] = y[15]
	x[17] = x[12]
	y[17] = y[2]
	x[18] = x[10]
	y[18] = y[1]
	x[19] = x[10]
	y[19] = y[0]
	
	if rotate90:
		centerPoint = (x[0] + SWITCHSIZE/2, y[0] - SWITCHSIZE/2)
		for n in range(20):
			x[n], y[n] = rotatePoint(centerPoint, (x[n],y[n]), 90)
		
	if rotation:
		for n in range(20):
			x[n], y[n] = rotatePoint((rotation[0],rotation[1]), (x[n],y[n]), rotation[2])

	
	for i in range(19):
		rectangle.addGeometry(Part.Line(App.Vector(x[i],y[i],0),App.Vector(x[i+1],y[i+1],0)))
	rectangle.addGeometry(Part.Line(App.Vector(x[19],y[19],0),App.Vector(x[0],y[0],0)))
	
	for j in range(19):
		rectangle.addConstraint(Sketcher.Constraint('Coincident',j,2,j+1,1)) 
	rectangle.addConstraint(Sketcher.Constraint('Coincident',19,2,0,1))
	
	for k in range(20):
		rectangle.addConstraint(Sketcher.Constraint('DistanceX',k,1,x[k])) 
		rectangle.addConstraint(Sketcher.Constraint('DistanceY',k,1,y[k])) 
	
	doc.recompute()
	
	return rectangle
	
	
#Drawing methods
	
def	initializeCAD():	
	global doc
	doc = FreeCAD.newDocument()
	
	pad(sketchRectangle(0, 0, plateXDim, plateYDim, False))	

	
def drawSwitches():
	for prop in props:
		coord = findCoord(prop[0], prop[1], prop[2], prop[3]) 
		rotation = prop[4]
		if "!c!" in labels[props.index(prop)]:
			drawSwitchWithCutOuts(coord[0], coord[1], rotation, "!r!" in labels[props.index(prop)])
		else:
			drawSwitch(coord[0], coord[1], rotation)
		
def drawStabilizers():
	if includeStabilizers:
		if includeStabilizers == "cherry":
			drawStabilizersHelper(True)
		elif includeStabilizers == "costar":
			drawStabilizersHelper(False)
		elif includeStabilizers == "both":
			drawStabilizersHelper(True)
			drawStabilizersHelper(False)
		else:
			print includeStabilizers + " is not a valid value for includeStabilizers"
			return
			
	
def drawSwitch(x, y, rotation):
	pocket(sketchRectangle(x, y, SWITCHSIZE, SWITCHSIZE, rotation))
	
	
def drawSwitchWithCutOuts(x, y, rotation, rotate90):
	pocket(sketchSwitchWithCutOuts(x, y, rotation, rotate90))
	
	
def pocket(sketch):
	global doc	
	pocket = doc.addObject("PartDesign::Pocket","Pocket" + str(sketchCount - 1))
	pocket.Sketch = sketch
	pocket.Length = 5.0
	pocket.Type = 1
	pocket.UpToFace = None
	doc.recompute()
	
	
def pad(sketch):
	global doc	
	pad = doc.addObject("PartDesign::Pad","Pad")
	pad.Sketch = sketch
	pad.Length = plateThickness
	pad.Reversed = 0
	pad.Midplane = 0
	pad.Length2 = 100.000000
	pad.Type = 0
	pad.UpToFace = None
	doc.recompute()	

			
def drawStabilizersHelper(cherry):		
	for prop in props:
		if prop[2] >= 2 or prop[3] >= 2: 
			coord = findCoord(prop[0], prop[1], prop[2], prop[3])
			cutout = "!c!" in labels[props.index(prop)]
			rotated90 = "!r!" in labels[props.index(prop)]
			rotation = prop[4]
			if prop[2] >= MINIMUMLONGSTABLENGTH:#spacebar
				drawHorizontalStabilizer(coord[0], coord[1], False, cherry, cutout, rotated90, rotation)
				global CHERRYLONGSEPARATION
				global COSTARLONGSEPARATION
				global CHERRYLONGSEPARATION2
				global COSTARLONGSEPARATION2
				if cherry and CHERRYLONGSEPARATION2 or not(cherry) and COSTARLONGSEPARATION2: #if a second value is given, swap and then draw again.
					tmpCherry = CHERRYLONGSEPARATION
					tmpCostar = COSTARLONGSEPARATION
					CHERRYLONGSEPARATION = CHERRYLONGSEPARATION2
					COSTARLONGSEPARATION = COSTARLONGSEPARATION2
					CHERRYLONGSEPARATION2 = tmpCherry
					COSTARLONGSEPARATION2 = tmpCostar
					drawHorizontalStabilizer(coord[0], coord[1], False, cherry, cutout, rotated90, rotation)
			elif prop[3] >= 2: #if taller than 2, stab will be vertical, for iso, big-ass enter, + on numpad, etc..
				drawVerticalStabilizer(coord[0], coord[1], cherry, cutout, rotated90, rotation)
			else: #standard wide key
				drawHorizontalStabilizer(coord[0], coord[1], True, cherry, cutout, rotated90, rotation)
				
				
def drawHorizontalStabilizer(x, y, short, cherry, cutout, rotated90, rotation):
	if cherry:
		width = CHERRYWIDTH
		length = CHERRYLENGTH
		if short:
			separation = CHERRYSHORTSEPARATION
		else:
			separation = CHERRYLONGSEPARATION
		dst = CHERRYDST
	else:
		width = COSTARWIDTH
		length = COSTARLENGTH
		if short:
			separation = COSTARSHORTSEPARATION
		else:
			separation = COSTARLONGSEPARATION
			separation2 = COSTARLONGSEPARATION2
		dst = COSTARDST
		
	y = y + dst
	xLeft = x + SWITCHSIZE/2 - separation/2 - width
	xRight = x + SWITCHSIZE/2 + separation/2		
	
	pocket(sketchRectangle(xLeft, y, width, length, rotation))
	pocket(sketchRectangle(xRight, y, width, length, rotation))
	
	if cherry:
		xWire = xLeft - WIREADDLENGTH 
		yWire = y + WIREDST
		wWire = separation + 2*width + 2*WIREADDLENGTH
		pocket(sketchRectangle(xWire, yWire, wWire, WIREWIDTH, rotation))
		if cutout and not(rotated90) and short and ADDCUTFORSHORT: #Another cut will be performed since the remaining plate will be very narrow in this area, if cutouts.
			pocket(sketchRectangle(xLeft + width, y, separation, length, rotation))
			
	
def drawVerticalStabilizer(x, y, cherry, cutout, rotated90, rotation):
	if cherry:
		width = CHERRYWIDTH
		length = CHERRYLENGTH
		separation = CHERRYSHORTSEPARATION
		dst = CHERRYDST
	else:
		width = COSTARWIDTH
		length = COSTARLENGTH
		separation = COSTARSHORTSEPARATION
		dst = COSTARDST
	
	x = x + dst
	
	yTop = y + SWITCHSIZE/2 - separation/2 - width
	pocket(sketchRectangle(x, yTop, length, width, rotation))
	
	yBottom = y + SWITCHSIZE/2 + separation/2
	pocket(sketchRectangle(x, yBottom, length, width, rotation))
	
	if cherry:
		yWire = yTop - WIREADDLENGTH 
		xWire = x + WIREDST
		hWire = separation + 2*width + 2*WIREADDLENGTH
		pocket(sketchRectangle(xWire, yWire, WIREWIDTH, hWire, rotation))
		if cutout and rotated90 and ADDCUTFORSHORT: #Another cut will be performed since the remaining plate will be very narrow in this area. only if rotated and cutouts.
			pocket(sketchRectangle(x, yTop + width, length, separation, rotation))

			
#Calculation methods
			
def findCoord(x, y, w, h):
	x = x*KEYUNIT
	y = y*KEYUNIT
	w = w*KEYUNIT
	h = h*KEYUNIT
	xPos = x + w/2 - SWITCHSIZE/2
	yPos = y + h/2 - SWITCHSIZE/2
	xPos = xPos + xStart
	yPos = yPos + yStart
	return (xPos, yPos)
	
	
def rotatePoint(centerPoint, point, angle):
	tempPoint = (point[0]-centerPoint[0], point[1]-centerPoint[1])
	if angle == 10:
		tempPoint = (-tempPoint[1], tempPoint[0])
	else:
		angle = math.radians(angle)
		tempPoint = (tempPoint[0]*math.cos(angle)-tempPoint[1]*math.sin(angle), tempPoint[0]*math.sin(angle)+tempPoint[1]*math.cos(angle))
	tempPoint = (tempPoint[0]+centerPoint[0], tempPoint[1]+centerPoint[1])
	return tempPoint
	
	
#Input data methods	
	
def getLayoutData():
	parseLayout(readFile())
	fixRotations()	
	modifyLabels()
	
	
def readFile():
	return open(layoutPath, 'r').readlines()
	

def parseLayout(layoutList):
	global labels
	for row in layoutList:
		newRow = True
		row = row.rstrip()
		if row[-1:] == ',':
			row = row[1:-2]
		else:
			row = row[1:-1]
		values = row.split(",")
		tmp = ''
		for value in values:
			if not tmp == '':
				value = tmp + "," + value
			if value[:1] == '{' and value[-1:] == '}': #value is a prop
				makeProp(value[1:-1], newRow)
				newRow = False
				tmp = ''
			elif value[:1] == '"' and value[-1:] == '"' and not len(value) == 1: #value is a label
				labels.append(value[1:-1])
				if len(props) < len(labels): #if no prop exists for this label, makes one
					makeProp('', newRow)
				newRow = False
				tmp = ''				
			else: #splitting of the row into values didn't work right because a value contained a comma
				tmp = value	
	

def makeProp(values, newRow):
	global props
	if props:
		prevProp = props[-1]
	else:
		prevProp = (0,-1,0,0,(0,0,0))
	x = 0
	y = 0
	w = 1
	h = 1
	rx = prevProp[4][0]
	ry = prevProp[4][1]
	r = prevProp[4][2]
	if not values == '':
		for value in values.split(","):
			colon = value.find(":")
			if value[:colon] == 'x':
				x = float(value[colon + 1:])
			elif value[:colon] == 'y':
				y = float(value[colon + 1:])
			elif value[:colon] == 'w':
				w = float(value[colon + 1:])
			elif value[:colon] == 'h':
				h = float(value[colon + 1:])
			elif value[:colon] == 'r':
				r = float(value[colon + 1:])
			elif value[:colon] == 'rx':
				rx = float(value[colon + 1:])
			elif value[:colon] == 'ry':
				ry = float(value[colon + 1:])
			else:
				print value + " will be ignored"
	newRotation = (rx,ry,r)
	if newRow:
		x = rx + x
		if newRotation != prevProp[4]:	
			y = ry + y
		else:
			y = prevProp[1] + 1 + y	
	else:
		x = x + prevProp[0] + prevProp[2] 
		y = prevProp[1]
		
	props.append((x,y,w,h,newRotation))
		
		
def modifyLabels():
	global labels
	result = []
	for label in labels:
		newLabel = label
		if includeCutOuts:
			if "!c!" in label:
				c = newLabel.index("!c!")
				newLabel = newLabel[:c] + newLabel[c+3:]
			else:
				newLabel = newLabel + "!c!"
		if rotateSwitches:
			if "!r!" in label:
				r = newLabel.index("!r!")
				newLabel = newLabel[:r] + newLabel[r+3:]
			else:
				newLabel = newLabel + "!r!"
		result.append(newLabel)
	labels = result			

	
def fixRotations():
	global props
	result = []
	for prop in props:
		if prop[4][2] == 0:
			newRotation = False
		else:
			newRotation = (prop[4][0]*KEYUNIT, -prop[4][1]*KEYUNIT, -prop[4][2])
		result.append((prop[0], prop[1], prop[2], prop[3], newRotation))
	props = result
			
	
#Output file methods
				
def save():
	global doc
	if os.path.exists(SAVEPATH):
		print "file already exists"
	else:
		doc.saveAs(SAVEPATH)
	

#global variables
doc = None
sketchCount = 0
props = [] #tuple for each switch, (x,y,w,h,(rx,ry,r))
labels = []	#labels for each switch from the layout editor	
#################
import sys
import os
import math
sys.path.append(FREECADPATH)
sys.path.append(FREECADPATH2)
#################
try:
	import FreeCAD	
	import Sketcher
except ValueError:
	print "error finding the FreeCAD"
else:
	main()

	

