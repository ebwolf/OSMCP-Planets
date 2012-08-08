# Clip to states - this has hard-coded paths!

import os, sys
from datetime import date, timedelta
import arcgisscripting

# Get the working directory. This can be specified on the command line 
# or just use the current working directory
if len(sys.argv) > 1:
    workDir = sys.argv[1]
    os.chdir(workDir)
else:
    workDir = os.getcwd() + "\\"

# If there is a second argument, then it's the date in YYYYMMDD format to be processed
if len(sys.argv) > 2:
    planetDate = sys.argv[2]
else:
    y = date.today() - timedelta(days=1)
    planetDate =  y.strftime("%Y%m%d")
    

# Grab the current date and use it as a hash for the geodatabase name
outGDB = workDir + planetDate + ".gdb"
destFC = "Planet"

statePath = workDir + "States.gdb/"

gp = arcgisscripting.create(9.3)
gp.overwriteoutput = 1
gp.workspace = outGDB

# OSM/OSMCP is simply WGS84
gp.outputCoordinateSystem =  "GEOGCS['GCS_WGS_1984'," \
  "DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]]," \
   "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

print "Clipping to states."

try:
    gp.Clip_analysis(destFC, statePath + "CO", "CO")
except:
    print gp.GetMessages()
    
try:
    gp.Clip_analysis(destFC, statePath + "KS", "KS")
except:
    print gp.GetMessages()

del gp