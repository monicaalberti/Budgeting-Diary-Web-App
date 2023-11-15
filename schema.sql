DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL
);


DROP TABLE IF EXISTS groceries_expenses;

CREATE TABLE groceries_expenses
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS healthcare_expenses;

CREATE TABLE healthcare_expenses
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS beauty_expenses;

CREATE TABLE beauty_expenses
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS transport_expenses;

CREATE TABLE transport_expenses
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS restaurants_expenses;

CREATE TABLE restaurants_expenses
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS other_expenses;

CREATE TABLE other_expenses
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS last_month_groceries;

CREATE TABLE last_month_groceries
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS last_month_healthcare;

CREATE TABLE last_month_healthcare
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS last_month_restaurants;

CREATE TABLE last_month_restaurants
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS last_month_beauty;

CREATE TABLE last_month_beauty
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS last_month_transport;

CREATE TABLE last_month_transport
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);

DROP TABLE IF EXISTS last_month_other;

CREATE TABLE last_month_other
(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    date DATE NOT NULL,
    amount FLOAT NOT NULL
);
