OMSCP-Planets

Downloads the planet file from the USGS VGI Structures server and converts
it into an ESRI File Geodatabase for in-house processing.

get_planet.bat

   Batch file meant to run under Microsoft Windows as a scheduled task. 
   It has some funky bits that allow it to run as a scheduled task and
   find the correct version of ArcGIS.

   All output is appended to get_planet.log


osmcp_planet_fgdb.py

   The main program. It depends on OSMtools to parse the Planet file and 
   ESRI ArcGISscripting to create the file geodatabase. 

   If looks for a users.csv and changes.csv on the server to populate fields 
   not normally in the planet file.

   In addition to just converting the data, it sets the "Status" field based
   on a few different tags.

osmcp_planet_clip_states.py

   This clips the resulting planet data into separate feature datasets
   based on the state outlines in States.gdb in the current directory.