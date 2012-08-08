@echo off

REM get_planet.bat
REM
REM Runs python scripts to download the OSMCP planet file and convert to Esri File Geodatabase
REM
REM Make sure all of the necessary files are together in the current directory

echo . >> %~dp0get_planet.log
echo ====================================================================== >> %~dp0get_planet.log
echo . >> %~dp0get_planet.log
echo get_planet.bat >> %~dp0get_planet.log
echo Username %username% >> %~dp0get_planet.log
echo Running in %~dp0 >> %~dp0get_planet.log

REM %~dp0 is the path to the batch file
pushd %~dp0

REM This makes sure Python.exe is where it should be
if exist c:\arcgis\python25\python.exe SET PPATH=c:\arcgis\python25\python.exe
if exist c:\python26\arcgis10.0\python.exe SET PPATH=c:\python26\arcgis10.0\python.exe

if "%PPATH%" == "" goto ERROR_PPATH

echo Using Python in %PPATH% >> %~dp0get_planet.log
%PPATH% %~dp0osmcp_planet_fgdb.py %~dp0 %1 >> %~dp0get_planet.log

if errorlevel 5 goto ERROR

REM Split the Planet file by state
%PPATH% %~dp0osmcp_planet_clip_states.py %~dp0 %1 >> %~dp0get_planet.log
goto EXIT

:ERROR_PPATH
echo Error: Can't find Python.exe >> %~dp0get_planet.log
echo . >> %~dp0get_planet.log
rem pause
goto END


:ERROR
echo An error occured getting the planet file >> %~dp0get_planet.log
echo . >> %~dp0get_planet.log
rem pause
goto END

:EXIT
echo Planet %1 Success!!!
echo . >> %~dp0get_planet.log

:END
echo . >> %~dp0get_planet.log
