CREATE DATABASE ventascasaxcasas;
USE ventascasaxcasas;

CREATE TABLE users (
    user_id int(11) NOT NULL AUTO_INCREMENT,
    username varchar(80) NOT NULL,
    password_hash varchar(80) NOT NULL,
    mail varchar(255) NOT NULL,
    image varchar(255),
    PRIMARY KEY (user_id)
); 

CREATE TABLE clients (
    client_id int(11) NOT NULL AUTO_INCREMENT,
    clientname varchar(80) NOT NULL,
    mail varchar(255) NOT NULL,
    user_id int NOT NULL,
    address varchar(255) NOT NULL,
    phonenumber varchar(255) NOT NULL,
    PRIMARY KEY (client_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
); 

CREATE TABLE stores (
    store_id int NOT NULL AUTO_INCREMENT,
    storename varchar(200) NOT NULL,
    descripcion varchar(200),
    user_id int NOT NULL,
    PRIMARY KEY (store_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE products (
    product_id int NOT NULL AUTO_INCREMENT,
    productname varchar(200) NOT NULL,
    description varchar(200),
    stock int NOT NULL,
    costprice double NOT NULL,
    sellingprice double NOT NULL,
    user_id int NOT NULL,
    image varchar(255),
    PRIMARY KEY (product_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


CREATE TABLE sales (
    sale_id int NOT NULL AUTO_INCREMENT,
    salename varchar(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id int NOT NULL,
    client_id int NOT NULL,
    PRIMARY KEY (sale_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
);

CREATE TABLE product_in_sale (
    product_in_sale_id int NOT NULL AUTO_INCREMENT,
    product_id int NOT NULL,
    quantity int NOT NULL,
    sale_id int NOT NULL,
    PRIMARY KEY (product_in_sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
);