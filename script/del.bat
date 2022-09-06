@echo off
set INTERVAL=600
:loop
del /f/q/s C:\assemblage\Builds > NUL
rmdir /q/s C:\assemblage\Builds > NUL
del /f/q/s C:\assemblage\Binaries > NUL
rmdir /q/s C:\assemblage\Binaries > NUL
timeout %INTERVAL%
goto:loop
