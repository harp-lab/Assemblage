@echo off
set INTERVAL=600
:loop
del /f/q/s assemblage\Builds
rmdir /q/s assemblage\Builds
del /f/q/s assemblage\Binaries
rmdir /q/s aassemblage\Binaries
timeout %INTERVAL%
goto:loop