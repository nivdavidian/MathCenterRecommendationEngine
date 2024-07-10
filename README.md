# MathCenterRecommendationEngine

Python version: 3.12
Flutter Version: 
    Flutter 3.19.2 • channel stable • https://github.com/flutter/flutter.git
    Framework • revision 7482962148 (4 months ago) • 2024-02-27 16:51:22 -0500
    Engine • revision 04817c99c9
    Tools • Dart 3.3.0 • DevTools 2.31.1
MYSQL using AWS.
    Connection host: "database-1.cxs6kmykemnz.eu-north-1.rds.amazonaws.com"
    Connection port: 3306
    DB Name: mathCenterDB

*Python Server Setup:*
1. Clone the project into your home directory
2. Open venv:
    cd /path_to_home/MathCenterRecommendationEngine/python-server
    python3.12 -m venv venv
3. Install requirements:
    pip install -r requirements.txt
4. Change Path to env file in sql_pool.py containing the DB credentials of Math-Center.org
    load_dotenv('Path_to_env_file.env')
5. Create service file for the program in /etc/systemd/system/
    Example: gunicorn.service
6. Run the service: 
    sudo systemctl daemon-reload
    sudo systemctl start Name_of_service.service
7. Create a new Nginx server block configuration file:
    sudo vim /etc/nginx/sites-available/myproject
    Example configuration file: myproject_without_gui.com

*Flutter Client Setup:*
1. Install nginx
2. Build the web flutter app: 
    cd /Path_to_home/MathCenterRecommendationEngine/recui
    flutter build web
3. Move the compiled web flutter app to /var/www/html/my_web_name
    sudo mv build/web/* /var/www/html/my_web_name/
4. Create a new Nginx server block configuration file:
    sudo vim /etc/nginx/sites-available/myproject
    Example configuration file: myproject.com
5. Enable the new server block configuration by creating a symbolic link to it in the sites-enabled directory:
    sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
6. Test the Nginx configuration to ensure there are no syntax errors:
    sudo nginx -t
7. restart Nginx to apply the changes:
    sudo systemctl restart nginx


For Further Information:
Email: nivdavidian@gmail.com


