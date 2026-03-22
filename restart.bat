@echo off
echo Restarting Garage...
docker-compose -p garage down
docker-compose -p garage up -d
timeout /t 3
start http://localhost:8000
echo Garage restarted.
pause