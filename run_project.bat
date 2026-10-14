@echo off
echo ==========================================
echo    ShopNexus Admin Professional Setup
echo ==========================================

echo [1/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/4] Running migrations...
python manage.py migrate

echo.
echo [3/4] Seeding sample data...
python manage.py seed_data

echo.
echo [4/4] Starting development server...
echo Access the site at http://127.0.0.1:8000/
echo Access Admin at http://127.0.0.1:8000/admin/
python manage.py runserver

pause
