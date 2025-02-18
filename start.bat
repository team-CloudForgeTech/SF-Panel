@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo 正在启动 SFpanel...

:: 启动后端服务
start "SFpanel-Backend" /b cmd /c "python main.py"

:: 等待2秒确保后端启动
timeout /t 2 /nobreak > nul

:: 启动前端服务
cd frontend
start "SFpanel-Frontend" /b cmd /c "npm run dev"
cd ..

echo SFpanel 已启动！
echo 输入 'stop' 停止服务，或按 Ctrl+C 结束...

:loop
set /p "cmd=>"
if /i "%cmd%"=="stop" goto :cleanup
goto :loop

:cleanup
taskkill /fi "windowtitle eq SFpanel-Backend" /f > nul 2>&1
taskkill /fi "windowtitle eq SFpanel-Frontend" /f > nul 2>&1
echo SFpanel 已停止！
timeout /t 1 /nobreak > nul
exit