from project import migrate, manager
from flask_migrate import MigrateCommand

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
