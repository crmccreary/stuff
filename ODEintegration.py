#Tutorial on numerical integration of ODE.
#Lesson plan:
#     (1) Euler method. Setup for 1D ODE. Exponential decay
#         and logistic equation
#
#     (2) How to set up a second order equation. Comparison of
#         linear undamped harmonic oscillator between Euler,
#         midpoint, and RK
#-------------------------------------------------------------
#
#     (3) Van der Pol.  Limit cycles
#
#     (4) Undamped anharmonic oscillator. Determining the period.
#         Period depends on amplitude

import Numeric,math
from ClimateUtilities import *

class midpoint:
  def __init__(self, derivs,xstart,ystart,dx=None):
    self.derivs = derivs
    self.x = xstart
    #The next statement is a cheap trick to initialize
    #y with a copy of ystart, which works whether y is
    #a regular scalar or a Numeric array.  
    self.y = 0.+ ystart
    self.dx = dx #Can instead be set with the first call to next()
    self.params = None
  #Sets the parameters for the integrator (optional).
  #The argument can be any Python entity at all. It is
  #up to the user to make sure the derivative function can
  #make use of it.
  def setParams(self,params):
      self.params = params
  #Computes next step.  Optionally, takes the increment
  #in the independent variable as an argument.  The
  #increment can be changed at any time, and the most
  #recently used value is remembered, as a default
  #
  #Method for integration using midpoint algoritm
  def next(self,dx = None):
     if not (dx == None):
         self.dx = dx
     h = self.dx
     dydx = self.derivs(self.x,self.y,self.params)
     ymid =self.y + .5*h*dydx
     self.y = self.y + h*self.derivs(self.x+ .5*h,ymid,self.params)
     self.x = self.x + h
     return self.x,self.y
  #
  #Method for integration using Euler algorithm
  def nextEuler(self,dx = None):
     if not (dx == None):
         self.dx = dx
     h = self.dx
     dydx = self.derivs(self.x,self.y,self.params)
     self.y =self.y + h*dydx
     self.x = self.x + h
     return self.x,self.y

#Some simple plotting utilities

#Plot curves of dependent variable(s) vs. time
#This takes a list of time and a corresonding list
#of dependant variable values as argument. The
#dependant variable list can be either a list of
#floats, or a list of Numeric arrays.
def plotT(timeList,YList):
    c = Curve()
    c.addCurve(timeList,'t')
    #Check for what kind of thing the dependant variable is.
    #We assume that all the elements in the list are the same
    #type as the first one. 
    if type(YList[0]) == type(1.):
        c.addCurve(YList,'Y')
    else:
        #This block tries to build separate lists for
        #each dependant variable, and returns an error
        #if it doesn't work.
        try:
            for i in range(len(YList[0])):
                Y = [yy[i] for yy in YList]
                c.addCurve(Y,'Y%d'%i)
        except:
            print "I'm afraid I can't do that ... Dave"
            return None
    return plot(c)

#Plot orbit of a 2D system on the phase plane
def plotPoints(pointList):
    c = Curve()
    c.addCurve([pointList[i][0] for i in range(len(pointList))])
    c.addCurve([pointList[i][1] for i in range(len(pointList))])
    return plot(c)
    

#-----Main Script starts here----

#Part 1: 1D integration.

#Example 1a: The logistic equation

#Define the function. t and param aren't used, but they
#have to be there.
def fLogistic(t,C,param):
    return C*(1.-C)

#Carry out the integration
#   Try re-running this with different dt and with Euler method
#   instead of midpoint method.  For Euler, use m.nextEuler()
#   of m.next()
CStart = .1
tStart =0.
dt = .1
m = midpoint(fLogistic,tStart,CStart,dt)
tList = [tStart]
CList = [CStart]

t = tStart
while t < 20.:
    t,C = m.next()
    tList.append(t)
    CList.append(C)

plotT(tList,CList)

#Example 1b: Temperature equation with a time-varying forcing
#Here, we treat the constants S and omega as globals
def fTemperature(t,T,param):
    return -T**4 + S*(1.-math.cos(omega*t))/2.

TStart = 0.
tStart =0.
dt = .1
m = midpoint(fTemperature,tStart,CStart,dt)
tList = [tStart]
TList = [TStart]

t = tStart
S = 1. # Set global
omega = 2. #Set global
while t < 10.*math.pi:
    t,T = m.next()
    tList.append(t)
    TList.append(T)

plotT(tList,TList)

#Example 1c: Use of the parameter argument to pass a constant
#Example 1d: Use of the parameter argument to pass an array of constants
#Example 1e: Use of the parameter argument to pass a set of constants
#            as an object
#Example 1f: Use of the parameter argument to pass more complicated
#            stuff as an object

    
#Part 2: 2D integration.

#Example 2a: Testing the integration with an oscillator

#Define the oscillator function.  For later use, we'll actually
#define the nonlinear Van der Pol oscillator here, though at
#first we'll use this function with a=b=0, which gives the linear
#harmonic oscillator.  I've introduced some temporary variables
#in the definition of this function, to make it a bit clearer
#how the position and velocity are stuffed into the array. When
#you're more experienced, you can dispense with these temporary
#variables.  y is the position, and v is the velocity. "prime"
#denotes the time derivative

def fOscillator(t,Y,param):
    #Rename variables to make things clearer
    y = Y[0]
    v = Y[1]
    #Time derivatives of dependant variables
    yprime = v
    vprime = -y*(1.-a*y*y) + b*v*(1.- c*v*v)
              #Newton's law: acceleration = force/mass
    return Numeric.array([yprime,vprime])
#
#Set global coefficients to zero, to get harmonic oscillator
a = b = c = 0.
#
#First try the integration with the Euler method

#Start with initial position y=1, initial velocity =0 (at rest).
ystart = 1.
vstart = 0.
Ystart = Numeric.array([ystart,vstart])

n = 20.
dt = 2.*math.pi/n
m = midpoint(fOscillator,0.,Ystart,dt)

points = [Ystart]
tList = [0.]
t = 0.
while t < 10.*(2.*math.pi): #Integrate for 10 periods
    t,Y = m.nextEuler()
    tList.append(t)
    points.append(Y.copy()) #Need to make a copy!
                        #Appending Y won't work. Not Y[:] either!
                        #Y[:] doesn't make a copy for Numeric arrays.
plotT(tList,points)
plotPoints(points)
    
#Wow, that was pretty bad.  The orbit should have been a circle, but
#instead the orbit spirals out towards infinity.  You should try re-running
#with smaller dt (larger n), to see how small you have to make dt
#before the solution starts looking more like it should.

#Next we try with the midpoint method, which is more accurate
#Start with initial position y=1, initial velocity =0 (at rest).
ystart = 1.
vstart = 0.
Ystart = Numeric.array([ystart,vstart])

n = 20.
dt = 2.*math.pi/n
m = midpoint(fOscillator,0.,Ystart,dt)

points = [Ystart]
tList = [0.]
t = 0.
while t < 10.*(2.*math.pi): #Integrate for 10 periods
    t,Y = m.next()
    tList.append(t)
    points.append(Y.copy()) #Need to make a copy!
                        #Appending Y won't work. Not Y[:] either!
                        #Y[:] doesn't make a copy for Numeric arrays.
plotT(tList,points)
plotPoints(points)

#That looks a lot better. The orbit still doesn't close into a perfect
#circle, but over 10 periods, it stays closer to a circle.

#Finally, let's try using 4th order Runge-Kutta, which is the algorithm
#implemented in the ClimateUtilities package

#Start with initial position y=1, initial velocity =0 (at rest).
ystart = 1.
vstart = 0.
Ystart = Numeric.array([ystart,vstart])

n = 20.
dt = 2.*math.pi/n
m = integrator(fOscillator,0.,Ystart,dt) #From ClimateUtilities

points = [Ystart]
tList = [0.]
t = 0.
while t < 10.*(2.*math.pi): #Integrate for 10 periods
    t,Y = m.next()
    tList.append(t)
    points.append(Y.copy()) #Need to make a copy!
                        #Appending Y won't work. Not Y[:] either!
                        #Y[:] doesn't make a copy for Numeric arrays.
plotT(tList,points)
plotPoints(points)

#Now we're really looking good.  Even though we've used a pretty
#coarse time step, the orbit closes almost exactly.  The orbit
#looks like a polygon rather than a circle because the large dt
#means the jumps between consecutive points are pretty large.
#However, the fact that the actual points at the vertices
#of the polygon plot on a circle says that the positions themselves
#are pretty accurate.

#That's all for this lesson.  Now we know how to carry out numerical
#integration, and we know something about the performance of the
#algorithms.  In the next session, we'll make use of numerical
#integration to explore the behavior of the nonlinear van der Pol oscillator
