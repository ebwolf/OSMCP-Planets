# osmcp_planet_fgdb.py

# Creates an Esri fgdb from the OSMCP Planet File

# This is designed to run on a Windows machine. The paths are hard-coded:


import sys, os
from datetime import date, timedelta
import urllib
from osmtools import osmplanet

print "OSMCP Planet to FGDB V1.9"

planetURL = "http://navigator.er.usgs.gov/planet/"

# Should we download new files our just use what we've got? 
# Normally  set to True, False is for debugging only
download = True


# Note: Python uses '\' as an escape character. All file system operations know
#       to convert between '/' and '\' depending on the file system.

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

planetFile = "planet-" + planetDate + ".osm"
userFile = "users-" + planetDate + ".csv"
changeFile = "changes-" + planetDate + ".csv"



# Grab the current date and use it as a hash for the geodatabase name
outGDB = workDir + planetDate + ".gdb"

destFC = "Planet"

import arcgisscripting

gp = arcgisscripting.create(9.3)

agInfo = gp.GetInstallInfo('Desktop')

gp.overwriteoutput = 1

# OSM/OSMCP is simply WGS84
gp.outputCoordinateSystem =  "GEOGCS['GCS_WGS_1984'," \
  "DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]]," \
   "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

# Does the GDB and Feature Class exist? 
if gp.Exists(outGDB + "\\" + destFC):
    # If so, exit cleanly with an error
    print "ERROR: File Geodatabase already exists, " + outGDB
    print "       You probably already ran this today."
    print "       You can delete the existing Geodatabase and run again."
    sys.exit(5)


# Download the user file
if download:
    try:
        print "Retrieving user file: " + planetURL + userFile
        (pFile, headers) = urllib.urlretrieve(planetURL + userFile, userFile)
    except:
        print "Error retreiving " + userFile
        sys.exit(5)

users = dict()

# Python has a great standard module for reading CSVs
import csv

csvFile = csv.reader(open(userFile, "rb"))

for row in csvFile:
    if row[0].isdigit():  # Skips the header row
        users[int(row[0])] = row[1]
    
del csvFile

# Get the changes.csv file

# Download the changes file
if download:
    try:
        print "Retrieving changes file: " + planetURL + changeFile
        (pFile, headers) = urllib.urlretrieve(planetURL + changeFile, changeFile)
    except:
        print "Error retreiving " + changeFile
        sys.exit(5)


# Create the File GDB
try:
    (p, f) = os.path.split(outGDB)
    v = agInfo['Version'].split('.')
    if int(v[0] > 9):
        # Specify GDB version 9.3 if we are using ArcGIS 10 or higher.
        gp.CreateFileGDB_management(p, f, "9.3")
    else:
        gp.CreateFileGDB_management(p, f)
except:
    print "Error creating FGDB." + p + f
    print gp.GetMessages()
    del gp
    exit(-1)


# Create the "Planet" Feature Class
try:
    gp.CreateFeatureClass(outGDB, destFC, "POINT")
    gp.AddMessage("Created the new feature class.")
except:
    print "Error creating Feature Class " + outGDB + "\\" + destFC
    print gp.GetMessages()
    del gp
    exit(-1)


# Set the geoprocessor workspace to the file geodatabase
gp.workspace = outGDB

# Load changes.csv into the file geodatabase
gp.Copyrows_management(changeFile, "Changes")

# Load users.csv into the file geodatabase
gp.Copyrows_management(userFile, "Users")


desc = gp.Describe(destFC)
fields = desc.Fields


# Fields for the Geodatabase - we ignore all other tags.
fcFields = [[ 'FCode', 'LONG', '' ],
            [ 'FType', 'LONG', '' ],
            [ 'Name', 'TEXT', '120'], 
            [ 'AddressBuildingName', 'TEXT', '60'],
            [ 'Address', 'TEXT', '100' ],
            [ 'City', 'TEXT', '75' ],
            [ 'State', 'TEXT', '2' ],
            [ 'Zipcode', 'TEXT', '32' ],
            [ 'Status', 'TEXT', '50' ],
            [ 'Validated', 'TEXT', '50' ],
            [ 'AttributeSource', 'LONG', ''],
            [ 'AttributeSourceComments', 'TEXT', '255'],
            [ 'GAZ_ID', 'LONG', '' ],
            [ 'OSM_ID', 'LONG', '' ],
            [ 'Version', 'LONG', '' ],
            [ 'TimeStamp', 'DATE', '' ],
            [ 'Changeset', 'LONG', '' ], 
            [ 'UserName', 'TEXT', '255'  ],
            [ 'UserEmail', 'TEXT', '255'  ],
            [ 'UserID', 'LONG', '' ],
            
            [ 'PlanetDate', 'TEXT', 10 ],
            
            # These are to build easy links out to the data in other databases
            [ "OSM_LINK", 'TEXT', '255' ],
            [ "GNIS_LINK", 'TEXT', '255' ],
            [ "CSET_LINK", 'TEXT', '255' ],
            [ "USER_LINK", 'TEXT', '255' ]]

count = 0

try:
    # Make sure we have all of our necessary fields
    for f in fcFields:
        if f[0] not in fields:
            if f[1] == 'LONG':
                gp.AddField(destFC, f[0], 'LONG')
            elif f[1] == 'DATE':
                gp.AddField(destFC, f[0], 'DATE')
            else:
                gp.AddField(destFC, f[0], 'TEXT', '#', '#', f[2])

    print "Created necessary fields."
except:
    print "Error creating fields in " + destFC + "."
    print gp.GetMessages()
    del gp
    exit(-1)

desc = gp.Describe(destFC)
fields = desc.Fields

pnt = gp.CreateObject("Point")

cur = gp.InsertCursor(destFC)


# Download the planet file
if download:
    try:
        print "Retrieving planet file: " + planetURL + planetFile
        (pFile, headers) = urllib.urlretrieve(planetURL + planetFile, planetFile)
    except:
        print "Error retreiving " + planetFile
        sys.exit(5)


# Open the planet file
try:
    planet = osmplanet.OsmPlanet(planetFile)
except:
    print "Error opening planet file. " + planetFile
    del gp
    sys.exit(5)


# Read through the planet file
while True:
    try:
        obj = planet.getNextObject()
    except:
        print "Failed retrieving next node (after " + str(obj['id']) + ")\n\n"
        del planet
        del gp
        sys.exit(5)
    
    if obj == '':
        break
    
    # Only work with nodes
    if not obj['type'] == u'node':
        continue
    
    # Skip deleted nodes... What about history?
    #if obj['visible'] == False:
    #    continue

    # Filter on FCode
    #if 'FCode' not in obj['tag']:
    #    continue

    row = cur.NewRow()
    
    count += 1
    
    # Null out all the fields because ArcGIS doesn't.
    for field in fields:
        if field.Type in ["Integer", "SmallInteger", "Single", "Double"]:
            row.SetValue(field.Name, 0)
        elif field.Type == "String":
            row.SetValue(field.Name, "")
            
    
    pnt.x = float(obj['lon'])
    pnt.y = float(obj['lat'])
    
    row.shape = pnt
      
    row.SetValue('OSM_ID', int(obj['id']))
    row.SetValue('Changeset', obj['changeset'])
    row.SetValue('UserID', obj['uid'])
    row.SetValue('UserName', obj['user'])
    row.SetValue('Version', obj['version'])

    if obj['uid'] in users:
        row.SetValue('UserEmail', users[obj['uid']])

    (sDay, sTime) = obj['timestamp'].split('T')
    sTime = sTime.strip('Z')
    timeStamp = sDay + ' ' + sTime
    row.SetValue('TimeStamp', timeStamp)    

    base_url = 'http://navigator.er.usgs.gov/browse/'
    
    link = base_url + 'node/' + str(obj['id'])
    row.SetValue('OSM_LINK', link)
    link = base_url + 'user/' + str(obj['uid'])
    row.SetValue('USER_LINK', link)
    link = base_url + 'changeset/' + str(obj['changeset'])
    row.SetValue('CSET_LINK', link)
        
    if 'FCode' in obj['tag']:
        if obj['tag']['FCode'] != None:
            if obj['tag']['FCode'] != '':
                row.SetValue('FCode', int(obj['tag']['FCode']))
        
    if 'FType' in obj['tag']:
        if obj['tag']['FType'] != None:
            if obj['tag']['FType'] != '':
                row.SetValue('FType', int(obj['tag']['FType']))

    if 'Name' in obj['tag']:
        if obj['tag']['Name'] != None:
            row.SetValue('Name', obj['tag']['Name'])

    if 'Address' in obj['tag']:
        if obj['tag']['Address'] != None:
            row.SetValue('Address', obj['tag']['Address'])

            
    if 'AddressBuildingName' in obj['tag']:
        if obj['tag']['AddressBuildingName'] != None:
            row.SetValue('AddressBuildingName', obj['tag']['AddressBuildingName'])

    if 'City' in obj['tag']:
        if obj['tag']['City'] != None:
            row.SetValue('City', obj['tag']['City'])

    if 'State' in obj['tag']:
        if obj['tag']['State'] != None:
            row.SetValue('State', obj['tag']['State'][0:2])

    if 'Zipcode' in obj['tag']:
        if obj['tag']['Zipcode'] != None:
            row.SetValue('Zipcode', obj['tag']['Zipcode'])

    if 'Status' in obj['tag']:
        if obj['tag']['Status'] != None:
            row.SetValue('Status', obj['tag']['Status'])

    if 'Validated' in obj['tag']:
        if obj['tag']['Validated'] != None:
            row.SetValue('Validated', obj['tag']['Validated'])
            row.SetValue('Status', '2')
            

    if 'AttributeSource' in obj['tag']:
        if obj['tag']['AttributeSource'] != None:
            row.SetValue('AttributeSource', obj['tag']['AttributeSource'])

    if 'AttributeSourceComments' in obj['tag']:
        if obj['tag']['AttributeSourceComments'] != None:
            row.SetValue('AttributeSourceComments', obj['tag']['AttributeSourceComments'])

    if 'GAZ_ID' in obj['tag']:
        if obj['tag']['GAZ_ID'] != None:
            if obj['tag']['GAZ_ID'] != '':
                row.SetValue('GAZ_ID', int(obj['tag']['GAZ_ID']))
                row.SetValue('GNIS_LINK', 'http://geonames.usgs.gov/pls/gnispublic/f?p=gnispq:3:::NO::P3_FID:' + obj['tag']['GAZ_ID'])

    row.SetValue('PlanetDate', planetDate)

    cur.InsertRow(row)
          
    #print "Node ID: " + str(obj['id'])

print "Added " + str(count) + " nodes successfully!"

del planet
del gp

sys.exit(0)