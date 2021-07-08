[![MIT License](https://img.shields.io/github/license/digitalocean/nginxconfig.io.svg?color=blue)](https://github.com/patern0ster/SOMAS-Society-Management-System/blob/master/LICENSE.md)
# :school: SOMAS - Society Management System
This is a Flask web application uses MySQL as DB which we were built for a group project with [berkanttubi](https://github.com/berkanttubi). We have built this application for universities to reduce e-mail traffic between societies, advisors and university administration, also for the students who want to see events and become member of societies and attend to events.
## :man: User Types
### User
This user can register to system by registration page. This user is able to;
- See society list
- See society details (gallery, events, contact)
- See event details
- Attend to an event
- Become member of a society
### Society
This user can only be created by **Administrator** user. This user is able to;
- Create event
- Add payment details into an event
- Add new photos into gallery
- See details of payments done
- Total budget of the society
- Member list of the society
- Attendance lists of the societies' events
- Everything that a normal user can do.
### Advisor
This user can only be created by **Administrator** user. Every society must have an advisor also one Advisor can be assigned more than one society. This user is able to;
- See details of payments done
- Total budget of the society
- Member list of the society
- Attendance lists of the societies' events
- Everything that a normal user can do.
From events apply page:
- Apply or Reject event applications which are created by society.
### Administrator
Administrator user can only be created by **DB administrator** for security purposes. This user is able to;
- Create new advisor accounts
- Create new society accounts  

From society page:
- See details of payments done by societies
- Total budget of societies
- Member list of societies
- Attendance lists of societies

From events apply page:
- Apply or Reject event applications which are applied after societies' advisor.
- Everything that a normal user can do.
## 🚀 How to run SOMAS?
Firstly you have to clone the repo 
```shell
$ git clone git@github.com:patern0ster/SOMAS-Society-Management-System.git
```
After you better create a virtual environment and activate it
```shell
$ virtualenv env
$ source ./env/bin/activate
```
After that you have to install requierements by 
```shell
$ pip -r /etc/requirements.txt
``` 
You have to setup MySQL and create a database.
```mysql
CREATE DATABASE somas;
```
Just simply run the dbconfigure.py
```shell
$ python3 dbconfigure.py
```
Then enter the details into the application and your database will be set. Make sure you have a clean database. You will see a screen like this;
```
Host: localhost
User: root
Password: root
Database: somas
Database configured successfully
Create an admin account [y/n]: y
Admin name: patern0ster
Admin Email: admin@gmail.com
Admin Password: password
Database creation is done.
```

You are all done. As last step just run the app
```
$ python3 app.py
```
## :computer: Demo
Demo link will be coming soon...
## ⭐️ Conclusion
This app is not fully done so you are welcome to check the issues of the repository and contribute. For more readability I will add more comments soon. You are also free to use the project. In case you have any question you can contact me. 
## 📝 Licence
Copyright © 2021 Mete Karasakal.
This project is licensed under the [MIT](https://github.com/patern0ster/SOMAS-Society-Management-System/blob/master/LICENSE.md) license.