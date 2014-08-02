import math

def get_sphere_samples(numberOfPoints=45, radius=10):
    """ Returns a list of 3-tuple x,y,z samples of the surface of a sphere.
        converted from:  http://web.archive.org/web/20120421191837/http://www.cgafaq.info/wiki/Evenly_distributed_points_on_sphere ) 
    """
    dlong = math.pi*(3.0-math.sqrt(5.0))  # ~2.39996323 
    dz   =  2.0/numberOfPoints
    longitude =  0.0
    z    =  1.0 - dz/2.0
    ptsOnSphere =[]
    for k in range( 0, numberOfPoints): 
        r    = math.sqrt(1.0-z*z)
        ptNew = (math.cos(longitude)*r * radius, math.sin(longitude)*r * radius, z * radius)
        ptsOnSphere.append(ptNew)
        z    = z - dz
        longitude = longitude + dlong
    return ptsOnSphere

if __name__ == '__main__':                
    ptsOnSphere = get_sphere_samples(300, 10)    
    # for pt in ptsOnSphere:  print( pt)

    #toggle True/False to plot them
    from numpy import *
    import pylab as p
    import mpl_toolkits.mplot3d.axes3d as p3

    fig=p.figure()
    ax = p3.Axes3D(fig)

    x_s=[];y_s=[]; z_s=[]

    for pt in ptsOnSphere:
        x_s.append( pt[0]); y_s.append( pt[1]); z_s.append( pt[2])

    ax.scatter3D( array( x_s), array( y_s), array( z_s) )                
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    p.show()
