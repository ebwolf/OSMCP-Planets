# osmcp_fix.py


import sys, time, os
import urllib
from osmtools import osmplanet

print "OSMCP Planet Fix V2.7"

planetURL = "http://navigator.er.usgs.gov/planet/"

# Note: Python uses '\' as an escape character. All file system operations know
#       to convert between '/' and '\' depending on the file system.

# Get the working directory. This can be specified on the command line 
workDir = os.getcwd() + "\\"

# If there is a second argument, then it's the date in YYYYMMDD format to be processed
if len(sys.argv) > 1:
    planetDate = sys.argv[1]
    planetFile = "planet-" + planetDate + ".osm"
    userFile = "users-" + planetDate + ".csv"
    changeFile = "changes-" + planetDate + ".csv"
else:
    planetDate = time.strftime("%Y%m%d", time.localtime(time.time()))
    planetFile = "planet.osm"
    #planetFile = "test.osm"
    userFile = "users.csv"
    changeFile = "changes.csv"



# Grab the current date and use it as a hash for the geodatabase name
outGDB = workDir + planetDate + ".gdb"

destFC = "Planet"

import arcgisscripting

gp = arcgisscripting.create(9.3)

agInfo = gp.GetInstallInfo('Desktop')

gp.overwriteoutput = 1


# Download the user file
try:
    print "Retrieving user file: " + planetURL + userFile
    (pFile, headers) = urllib.urlretrieve(planetURL + userFile, userFile)
except:
    print "Error retreiving " + userFile
    sys.exit(5)

# Get the changes.csv file

# Download the changes file
try:
    print "Retrieving changes file: " + planetURL + changeFile
    (pFile, headers) = urllib.urlretrieve(planetURL + changeFile, changeFile)
except:
    print "Error retreiving " + changeFile
    sys.exit(5)

# Set the geoprocessor workspace to the file geodatabase
gp.workspace = outGDB

try:
    gp.Delete_management("Changes")
except:
    print "Error deleting 'Changes'"
    
# Load changes.csv into the file geodatabase
gp.Copyrows_management(changeFile, "Changes")

try:
    gp.Delete_management("Users")
except:
    print "Error deleting 'Users'"

# Load users.csv into the file geodatabase
gp.Copyrows_management(userFile, "Users")

del gp

sys.exit(0)