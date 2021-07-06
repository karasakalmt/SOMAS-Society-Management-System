SET FOREIGN_KEY_CHECKS=0;


CREATE TABLE Administrator(
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Advisor(
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL, 
    dept SMALLINT NOT NULL
);
CREATE TABLE Society(
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL, #check
    budget float, #5 digit for integer, 3 for fractional
    description VARCHAR(500),
    admin_mail VARCHAR(255) NOT NULL,
    advisor_mail VARCHAR(255) NOT NULL,
    FOREIGN KEY (admin_mail) REFERENCES Administrator(email),
    FOREIGN KEY (advisor_mail) REFERENCES Advisor(email)
);

CREATE TABLE Advised(
	adv_email VARCHAR(255) NOT NULL,
	soc_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (adv_email) REFERENCES Advisor(email),
    FOREIGN KEY (soc_email) REFERENCES Society(email),
    PRIMARY KEY(adv_email, soc_email)
);

CREATE TABLE User(
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    dept SMALLINT NOT NULL
);

CREATE TABLE Student(
	email VARCHAR(255) NOT NULL PRIMARY KEY,
    year VARCHAR(4),
    student_id VARCHAR(7) NOT NULL,
    FOREIGN KEY (email) REFERENCES User(email)
);



CREATE TABLE SocietyMembers(
	user_email VARCHAR(255) NOT NULL,
	soc_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_email) REFERENCES User(email),
    FOREIGN KEY (soc_email) REFERENCES Society(email),
    PRIMARY KEY(user_email, soc_email)
);

CREATE TABLE Event(
	event_name VARCHAR(100) NOT NULL,
    e_date DATETIME,
    slug VARCHAR(100),
    status TINYINT,#Be enumarated
    description VARCHAR(500),
    soc_email VARCHAR(255) NOT NULL,
    adv_email VARCHAR(255) NOT NULL,
    adm_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (soc_email) REFERENCES Society(email),
    FOREIGN KEY (adv_email) REFERENCES Advisor(email),
    FOREIGN KEY (adm_email) REFERENCES Administrator(email),
    PRIMARY KEY(soc_email, event_name)
);


CREATE TABLE Event_Guest(
	soc_email VARCHAR(255) NOT NULL,
	e_name VARCHAR(100) NOT NULL,
    guest VARCHAR(255),
   FOREIGN KEY (soc_email,e_name) REFERENCES Event(soc_email,event_name),
   PRIMARY KEY(soc_email, e_name, guest)
);

CREATE TABLE Payment(
	e_name VARCHAR(100) NOT NULL,
	soc_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (soc_email,e_name) REFERENCES Event(soc_email,event_name),
    bill_detail VARCHAR(100),
    cost SMALLINT,
    PRIMARY KEY(soc_email, e_name, bill_detail)
);

CREATE TABLE Attendee(
	soc_email VARCHAR(255) NOT NULL,
	e_name VARCHAR(100) NOT NULL,
	user_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_email) REFERENCES User(email),
    FOREIGN KEY (soc_email,e_name) REFERENCES Event(soc_email,event_name),
    PRIMARY KEY (user_email,e_name,user_email)
);

INSERT INTO Administrator VALUES ("admin@metu.edu.tr","Admin",MD5("password"));
SET FOREIGN_KEY_CHECKS=1;