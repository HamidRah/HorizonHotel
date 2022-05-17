# Hamidur Rahman: 20009146
DROP DATABASE IF EXISTS HORIZONHOTEL;

CREATE DATABASE HORIZONHOTEL;

USE HORIZONHOTEL;

# Hotels
DROP TABLE IF EXISTS hotels;

CREATE TABLE IF NOT EXISTS hotels (
hotelCity VARCHAR(64) NOT NULL UNIQUE,
numberOfRooms int NOT NULL, 
peakPrice int NOT NULL ,
offpeakPrice int NOT NULL,
PRIMARY KEY(hotelCity)
);

# Users
DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
fullName VARCHAR(64) NOT NULL,
email VARCHAR(64) NOT NULL UNIQUE,
passwordHash VARCHAR(128) NOT NULL UNIQUE,
userType VARCHAR(20) DEFAULT 'standard',
PRIMARY KEY(email)
);

# Delete every user
DELETE FROM users;
# Set the admin
UPDATE users SET userType = 'admin' WHERE fullName = 'admin';

SELECT userType FROM USERS WHERE email = 'admin@admin.com';

-- Room Types
DROP TABLE IF EXISTS roomTypes;

CREATE TABLE IF NOT EXISTS roomTypes (
roomType VARCHAR(20) NOT NULL UNIQUE,
percentageOfRooms FLOAT NOT NULL,
pricePercentage FLOAT NOT NULL,
maxPeople INT NOT NULL,
PRIMARY KEY (roomType) 
);

-- Reservations
DROP TABLE IF EXISTS reservations;

CREATE TABLE IF NOT EXISTS reservations (
reservationID int NOT NULL UNIQUE AUTO_INCREMENT,
email VARCHAR(64),
hotelCity VARCHAR(64),
roomType VARCHAR(64),
checkInDate DATE NOT NULL,
checkOutDate DATE NOT NULL,
totalPrice INT NOT NULL,
numberOfPeople INT NOT NULL,
PRIMARY KEY(reservationID),
FOREIGN KEY(email) REFERENCES users(email) 
	ON DELETE SET NULL 
    ON UPDATE CASCADE,
FOREIGN KEY(hotelCity) REFERENCES hotels(hotelCity)
	ON DELETE SET NULL 
    ON UPDATE CASCADE,
FOREIGN KEY(roomType) REFERENCES roomTypes(roomType)
	ON DELETE SET NULL 
    ON UPDATE CASCADE
);

DELETE FROM reservations;

INSERT INTO hotels VALUES
('Aberdeen', 80, 140, 60),
('Belfast', 80, 130, 60),
('Birmingham', 90, 150, 70),
('Bristol', 90, 140, 70),
('Cardiff', 80, 120, 60),
('Edinburgh', 90, 170, 70),
('Glasgow', 100, 150, 70),
('London', 120, 200, 80),
('Manchester', 110, 180, 80),
('Newcastle', 80, 100, 60),
('Norwich', 80, 100, 60),
('Nottingham', 100, 120, 70),
('Oxford', 80, 180, 70),
('Plymouth', 80, 180, 50),
('Swansea', 80, 120, 50);

INSERT INTO roomTypes VALUES
('Standard', 0.3, 1, 1),
('Double', 0.5, 1.2, 2),
('Family', 0.2, 1.5, 6);

# Select all reservations
SELECT * FROM reservations;


