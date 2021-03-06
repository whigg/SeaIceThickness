"""
Script reads PIOMAS binary files for select variables and regrids
according to selected grid style (e.g., NSIDC EASE grid data). Plotting
function also available for PIOMAS data.

*Dark Figure Format
 
Source : http://psc.apl.washington.edu/zhang/IDAO/data_piomas.html
Author : Zachary Labe
Date : 11 July 2016
"""

### Import Modules
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as c
from scipy.interpolate import griddata as g
import datetime

### Define directories
directorygrid = '/home/zlabe/Documents/SeaIceObs/Data/'
directorydata = '/home/zlabe/Surtsey/seaice_obs/PIOMAS/'    
directoryfigure = '/home/zlabe/Documents/Research/SeaIceThickness/Figures/' 

yearmin = 1979
yearmax = 2016
years = np.arange(yearmin,yearmax+1,1)
       
### Define time           
now = datetime.datetime.now()
currentmn = str(now.month)
currentdy = str(now.day)
currentyr = str(now.year)
currenttime = currentmn + '_' + currentdy + '_' + currentyr
titletime = currentmn + '/' + currentdy + '/' + currentyr

print '\n' 'PIOMAS Read & Regrid - %s' '\n' % titletime 

def readPiomas(directory,vari,years,thresh):
    """
    Reads binary PIOMAS data
    """
    
    ### Retrieve Grid
    grid = np.genfromtxt(directory + 'grid.txt')
    grid = np.reshape(grid,(grid.size))  
    
    ### Define Lat/Lon
    lon = grid[:grid.size/2]   
    lons = np.reshape(lon,(120,360))
    lat = grid[grid.size/2:]
    lats = np.reshape(lat,(120,360))
    
    ### Call variables from PIOMAS
    if vari == 'thick':
        files = 'heff'
        directory = directory + 'Thickness/'
    elif vari == 'sic':
        files = 'area'
        directory = directory + 'SeaIceConcentration/'
    elif vari == 'snow':
        files = 'snow'
        directory = directory + 'SnowCover/'   
    elif vari == 'oflux':
        files = 'oflux'
        directory = directory + 'OceanFlux/'
    
    ### Read data from binary into numpy arrays
    var = np.empty((len(years),12,120,360))
    for i in xrange(len(years)):
        data = np.fromfile(directory + files + '_%s.H' % (years[i]),
                           dtype = 'float32')

    ### Reshape into [year,month,lat,lon]
        months = data.shape[0]/(120*360)
        if months != 12:
            lastyear = np.zeros((12,120,360))
            dataq = np.reshape(data,(120,360))
            lastyear[:,:,:] = dataq
            var[i,:,:,:] = lastyear
        else:
            dataq = np.reshape(data,(12,120,360))        
            var[i,:,:,:] = dataq
    
    ### Mask out threshold values
    var[np.where(var <= thresh)] = np.nan

    print 'Completed: Read "%s" data!' % (vari)   
    
    return lats,lons,var
    
def gridData(directory):
    """
    Reads CryoSat-2 data that is AWI processed onto EASE100 grid
    """
    
    files = 'cryoSat_seaice_thickness_month_2011.nc' 
    filename = directory + files
    data1 = Dataset(filename)
    lats = data1.variables['lat'][:]
    lons = data1.variables['lon'][:]
    data1.close()
    lons[np.where(lons == -999)] = np.nan
    lats[np.where(lats == -999)] = np.nan
    
    print 'Completed: Read grid data!' '\n'
    
    return lats,lons
    
def plotPiomas(directory,lats,lons,var,vari,month,year,years):
    """
    Plots Piomas data for curved or regrid interpolation schemes
    """
    
    def colormapSIC():
        cmap = plt.get_cmap('RdPu')
        cmaplist = [cmap(i) for i in xrange(0,cmap.N-20)]
        cms_sic = c.ListedColormap(cmaplist)
        return cms_sic
    
    def colormapSIT():
        cmap1 = plt.get_cmap('BuPu')
        cmap2 = plt.get_cmap('RdPu_r')
        cmap3 = plt.get_cmap('gist_heat_r')
        cmaplist1 = [cmap1(i) for i in xrange(cmap1.N-10)]
        cmaplist2 = [cmap2(i) for i in xrange(15,cmap2.N)]
        cmaplist3 = [cmap3(i) for i in xrange(cmap2.N)]
        cms_sit = c.ListedColormap(cmaplist1 + cmaplist2 + cmaplist3)
        return cms_sit
        
    def colormapSnow():
        cmap1 = plt.get_cmap('viridis')
        cms_snow = cmap1 
        return cms_snow
        
    def setcolor(x, color):
        for m in x:
            for t in x[m][1]:
                t.set_color(color)
    
    ### Call parameters
    plt.rc('text',usetex=True)
    plt.rc('font',**{'family':'sans-serif','sans-serif':['Avant Garde']}) 
    plt.rc('savefig',facecolor='black')
    plt.rc('axes',edgecolor='white')
    plt.rc('xtick',color='white')
    plt.rc('ytick',color='white')
    plt.rc('axes',labelcolor='white')
    plt.rc('axes',facecolor='black')
    plt.rcParams['axes.linewidth'] = 0.8
    
    ### Define figure
    fig = plt.figure()
    ax = plt.subplot(111)
    
    m = Basemap(projection='ortho',lon_0=-90,
                lat_0=70,resolution='l',round=True)
    m.drawmapboundary(fill_color='white')
    m.drawcoastlines(color='k',linewidth=0.5)
    parallels = np.arange(50,90,10)
    meridians = np.arange(-180,180,30)
    par = m.drawparallels(parallels,labels=[False,False,False,False],
                    linewidth=0.5,color='k',fontsize=9)
    mer = m.drawmeridians(meridians,labels=[True,True,False,False],
                    linewidth=0.5,color='k',fontsize=9)
    setcolor(mer,'white')
    m.drawlsmask(land_color='peru',ocean_color='mintcream')
#    m.shadedrelief()
    
    ### Adjust maximum limits
    if vari == 'thick':
        values = np.arange(0,7.1,0.2)  
        var[np.where(var >= 7.0)] = 7.0
        info = 'Sea Ice Thickness'
    elif vari == 'sic':
        values = np.arange(0.2,1.05,0.05)
        var[np.where(var >= 1.0)] = 1.0
        var[np.where(var == 1.0)] = np.nan
        info = 'Sea Ice Concentration'
    elif vari == 'snow':
        values = np.arange(0,0.31,0.01)
        var[np.where(var >= 0.3)] = 0.3
        info = 'Snow Cover'
    
    ### Plot filled contours    
    cs = m.contourf(lons[:,:],lats[:,:],var[year,month,:,:],
                    values,latlon=True,extend='max')
                    
    ### Set colormap                
    if vari == 'thick':                
        cs.set_cmap(colormapSIT())
    elif vari == 'sic':
        cs.set_cmap(colormapSIC())
    elif vari == 'snow':
        cs.set_cmap(colormapSnow())
    
    ### Set colorbar
    cbar = m.colorbar(cs,drawedges=True,location='right',pad = 0.55)
    
    if vari == 'thick':
        cbar.set_ticks(np.arange(0,7.1,1))
        cbar.set_ticklabels(map(str,np.arange(0,8,1)))    
        cbar.set_label(r'\textbf{Thickness (meters)}')
    elif vari == 'sic':
        cbar.set_ticks(np.arange(0.2,1.1,.1))
        cbar.set_ticklabels(map(str,np.arange(0.2,1.1,0.1)))
        cbar.set_label(r'\textbf{SIC Fraction}')
    elif vari == 'snow':
        cbar.set_ticks(np.arange(0.0,0.31,0.05))
        cbar.set_ticklabels(map(str,np.arange(0.0,0.31,0.05)))
        cbar.set_label(r'\textbf{Snow Depth (meters)}')
    
    ### Date and title/adjustments
    dateyr = years[year]    
    datemo = datetime.date(dateyr,month+1,1).strftime('%B')
        
    fig.suptitle(r'\textbf{%s %s, %s}' % (datemo,dateyr,info),
             fontsize=19,color='white')
    fig.subplots_adjust(top=0.9)
    
    plt.annotate(r'\textbf{Data:} PIOMAS [Zhang and Rothrock, 2003]',xy=(150,90),
             xycoords='figure pixels',color='white',fontsize=8) 
    plt.annotate(r'\textbf{Graphic:} Zachary Labe (@ZLabe)',xy=(150,30),
             xycoords='figure pixels',color='white',fontsize=8,
             bbox=dict(boxstyle="square, pad=0.3",fc='k',edgecolor='w',
                       linewidth=0.2)) 
    
    ### Save figure
    plt.savefig(directory +'%s_%s%s_dark.png' % (vari,datemo[0:3],dateyr),
                dpi=300)

### Call functions
lats,lons,sit = readPiomas(directorydata,'thick',years,0.0)
#lats,lons,sic = readPiomas(directorydata,'sic',years,0.0)
#lats,lons,snow = readPiomas(directorydata,'snow',years,0.0)
#lats,lons,oflux = readPiomas(directorydata,'oflux',years,0.0)

latsq,lonsq = gridData(directorygrid)

plotPiomas(directoryfigure,lats,lons,sit,'thick',0,-2,years)

print 'Completed: Script finished!'