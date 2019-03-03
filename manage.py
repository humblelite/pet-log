import os
from project import migrate, manager  # migrate and manager in init.py file.
from flask_migrate import MigrateCommand

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

# flask-migrate manage.py file to create migrations for database models.
