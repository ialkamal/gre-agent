@echo off
setlocal enabledelayedexpansion

set BASEPATH=c:\Users\nawatt\Documents\gre agents\gre-grading-system

mkdir "%BASEPATH%\backend"
mkdir "%BASEPATH%\backend\app"
mkdir "%BASEPATH%\backend\app\api"
mkdir "%BASEPATH%\backend\app\api\routes"
mkdir "%BASEPATH%\backend\app\agents"
mkdir "%BASEPATH%\backend\app\agents\grading_agents"
mkdir "%BASEPATH%\backend\app\graph"
mkdir "%BASEPATH%\backend\app\memory"
mkdir "%BASEPATH%\backend\app\tools"
mkdir "%BASEPATH%\backend\app\models"
mkdir "%BASEPATH%\backend\app\schemas"
mkdir "%BASEPATH%\backend\app\db"
mkdir "%BASEPATH%\backend\tests"
mkdir "%BASEPATH%\frontend"
mkdir "%BASEPATH%\frontend\src"

echo Directory structure created successfully at: %BASEPATH%
dir /s "%BASEPATH%"
