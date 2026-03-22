@echo off
echo Stopping Garage...
docker-compose -p garage down
echo Garage stopped.
pause