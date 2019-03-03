# Virtual Pet Logger

virtual pet logger is a crud application that allows users to keep track of the pets.
Users have a dashboard where a pet can be created, pets can be viewed based on
 type(dogs, cats, birds, fish, critters, and reptiles.) users can also see a 
 Json list of all there pets under All Pets.
App runs on python3. OS system in Virtual Box version 5.2, bento/ubantu-16.04.

## Getting Started

Setting up Vagrant/Virtual Machine
This reporting tool requires the installation of vagrant/virtual machine setup on your system. 
Follow the following steps for installation and setup.

Use this link Virtual Box to install latest virtual box which is version 6.0 at this time.
Once Virtual Box is installed, use this link Vagrant to install vagrant which is version 2.2.2 at this time.
After vagrant and virtual Box are installed on your system, go to thisGithub link FSND fork the repo and clone it.

Running the virtual Machine.
After FSND file is cloned ,cd into folder. Then cd into the vagrant directory and follow these steps.

Run command vagrant up
After vagrant is done installing run command vagrant ssh, to log into bento/ubantu-16.04 system.
Once you are logged in cd /vagrant.

## Setup

First step in setup of application is to install packages from requirements.txt file, with pip install -r requirements.txt. next create .env file and replace these variables with the correct information.
database= your database
SECRET_KEY= your secret key
GITHUB_ID= your github developer id.
GITHUB_SECRET= your github secret key.
GITHUB_USERS_PASS= a secret password for your github users.

After packages are downloaded and variables are replaced a database migration file exist in  package/migrations
 needs to be Upgraded. In command line type
```bash 
python manage.py db upgrade --directory project/migrations
```

after database is created, the categories need to be persisted to the database. for the (id, cat_name) pairs.
0 dogs
1 cats
2 birds
3 fish
4 critters
5 reptiles.

final step is to verify .flaskenv file and run application on.
```bash
flask run
```
a working example is hosted at https://pet-logger.herokuapp.com/.
the login with github button does not work on heroku because github callback url
is set for localhost url port 8000.

## License
[MIT](https://choosealicense.com/licenses/mit/)