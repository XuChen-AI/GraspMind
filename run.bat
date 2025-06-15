@echo off
chcp 65001 >nul
echo 🤖 GraspMind 智能抓取系统
echo ================================

:MENU
echo.
echo 请选择操作:
echo 1. 安装依赖包
echo 2. 验证安装
echo 3. 系统测试
echo 4. 运行演示
echo 5. 查看状态
echo 6. 退出
echo.
set /p choice="请输入选择 (1-6): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto VERIFY
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto DEMO
if "%choice%"=="5" goto STATUS
if "%choice%"=="6" goto EXIT
echo 无效选择，请重新输入
goto MENU

:INSTALL
echo.
echo 📦 正在安装Python依赖包...
pip install -r requirements.txt
if %errorlevel%==0 (
    echo ✅ 依赖安装完成
) else (
    echo ❌ 依赖安装失败，请检查Python环境
)
pause
goto MENU

:VERIFY
echo.
echo 🔍 正在验证系统安装...
python verify_install.py
pause
goto MENU

:TEST
echo.
echo 🧪 正在运行系统测试...
python main.py --test
pause
goto MENU

:DEMO
echo.
echo 🎮 启动演示模式...
python demo.py
goto MENU

:STATUS
echo.
echo 📊 系统状态信息...
python main.py --status
pause
goto MENU

:EXIT
echo.
echo 👋 感谢使用GraspMind!
exit /b 0
