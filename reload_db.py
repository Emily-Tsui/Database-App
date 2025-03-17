reload_query = """

SET FOREIGN_KEY_CHECKS = 0;
SET AUTOCOMMIT = 0;

DROP TABLE IF EXISTS Customers, Employees, Invoices, Services, Services_Invoices;
CREATE TABLE Customers (
    customer_id int NOT NULL AUTO_INCREMENT,
    first_name varchar(125) NOT NULL,
    last_name varchar(125) NOT NULL,
    address varchar(125) NOT NULL,
    city varchar(125) NOT NULL,
    state varchar(2) NOT NULL,
    zipcode varchar(10) NOT NULL,
    email varchar(125),             -- allowing null values for email
    phone varchar(12) NOT NULL,
    PRIMARY KEY (customer_id)
);

CREATE TABLE Employees (
    employee_id int NOT NULL AUTO_INCREMENT,
    employee_fname varchar(125) NOT NULL,
    employee_lname varchar(125) NOT NULL,
    phone_number varchar(12) NOT NULL,
    PRIMARY KEY (employee_id)
);

CREATE TABLE Invoices (
    invoice_id int NOT NULL AUTO_INCREMENT,
    customer_id int NOT NULL,
    employee_id int,                  -- Nullable FK relationship
    date_created date NOT NULL,
    PRIMARY KEY (invoice_id),
    CONSTRAINT customer_invoice_FK FOREIGN KEY (customer_id)
    REFERENCES Customers(customer_id)
    ON DELETE CASCADE,
    CONSTRAINT employee_invoice_FK FOREIGN KEY (employee_id)
    REFERENCES Employees(employee_id)
    ON DELETE SET NULL
);

CREATE TABLE Services (
    service_id int NOT NULL AUTO_INCREMENT,
    name varchar(125) NOT NULL UNIQUE,
    cost_per_hour int NOT NULL,
    PRIMARY KEY (service_id)
);

CREATE TABLE Services_Invoices (
    services_invoices_id int NOT NULL AUTO_INCREMENT,
    service_id int NOT NULL,
    invoice_id int NOT NULL,
    qty int NOT NULL,
    line_subtotal int NOT NULL,
    PRIMARY KEY (services_invoices_id),
    CONSTRAINT service_FK FOREIGN KEY (service_id)
    REFERENCES Services(service_id)
    ON DELETE CASCADE,
    CONSTRAINT invoice_FK FOREIGN KEY (invoice_id)
    REFERENCES Invoices(invoice_id)
    ON DELETE CASCADE
);

INSERT INTO Customers (
    first_name,
    last_name,
    address,
    city,
    state,
    zipcode,
    email,
    phone
)
VALUES
    ('Brandon', 'Sanderson', '12345 Twin Peaks Drive', 'Coos Bay', 'OR', '93845', 'bsand@email.com', '123-456-7890'),
    ('Patrick', 'Rothfuss', '67890 Mayflower Street', 'Bandon', 'OR', '98312', 'proth@email.com', '123-456-7891'),
    ('Bill', 'Waterson', '98311 Bonita Avenue', 'Coquille', 'OR', '98622', NULL, '123-456-7892'),
    ('Brent', 'Weeks', '98744 Daisy Road', 'Coos Bay', 'OR', '93845', 'bweek@email.com', '123-456-7893'),
    ('April', 'Jackson', '98411 Poppy Street', 'Bandon', 'OR', '98312', NULL, '123-456-7894');


INSERT INTO Employees (
    employee_fname,
    employee_lname,
    phone_number
)
VALUES
    ('John', 'Gardener', '123-456-7895'),
    ('Frank', 'Weed', '123-456-7896'),
    ('Joe', 'Lawn', '123-456-7897'),
	('Cindy', 'Mulch', '123-456-7898'),
	('May', 'Flowers', '123-456-7899');


INSERT INTO Invoices (
    customer_id,
    employee_id,
    date_created
)
VALUES
    ((SELECT customer_id FROM Customers WHERE first_name='Bill' AND last_name='Waterson'),
		(SELECT employee_id FROM Employees WHERE employee_fname='Frank' AND employee_lname='Weed'),
        '2024-01-31'),
	((SELECT customer_id FROM Customers WHERE first_name='Patrick' AND last_name='Rothfuss'),
		(SELECT employee_id FROM Employees WHERE employee_fname='Frank' AND employee_lname='Weed'),
        '2024-01-30'),
	((SELECT customer_id FROM Customers WHERE first_name='April' AND last_name='Jackson'),
		(SELECT employee_id FROM Employees WHERE employee_fname='Joe' AND employee_lname='Lawn'),
        '2024-01-31'),
	((SELECT customer_id FROM Customers WHERE first_name='Brandon' AND last_name='Sanderson'),
		(SELECT employee_id FROM Employees WHERE employee_fname='May' AND employee_lname='Flowers'),
        '2024-01-20'),
	((SELECT customer_id FROM Customers WHERE first_name='Bill' AND last_name='Waterson'),
		(SELECT employee_id FROM Employees WHERE employee_fname='Cindy' AND employee_lname='Mulch'),
        '2024-01-20');
        
INSERT INTO Services (
    name,
    cost_per_hour
)
VALUES
    ('Mowing', 60),
    ('Tree trimming', 120),
    ('Mulching', 100),
	('Planting', 90),
	('Irrigation installation', 130);


INSERT INTO Services_Invoices (
    service_id, 
    invoice_id, 
    qty,            -- qty is quantity of hours it took for that service
    line_subtotal)  -- service cost_per_hour x qty
VALUES
    ((SELECT service_id FROM Services WHERE name = 'Tree Trimming'),
        (SELECT invoice_id FROM Invoices WHERE date_created = '2024-01-31' AND customer_id IN (SELECT customer_id FROM Customers WHERE first_name = 'April' AND last_name = 'Jackson')),
	     7, 840),
	((SELECT service_id FROM Services WHERE name = 'Mowing'),
		(SELECT invoice_id FROM Invoices WHERE date_created = '2024-01-31' AND customer_id IN (SELECT customer_id FROM Customers WHERE first_name = 'Bill' AND last_name = 'Waterson')),
         4, 240),
	((SELECT service_id FROM Services WHERE name = 'Tree Trimming'),
		(SELECT invoice_id FROM Invoices WHERE date_created = '2024-01-31' AND customer_id IN (SELECT customer_id FROM Customers WHERE first_name = 'Bill' AND last_name = 'Waterson')),
         6, 720),
	((SELECT service_id FROM Services WHERE name = 'Planting'),
		(SELECT invoice_id FROM Invoices WHERE date_created = '2024-01-30' AND customer_id IN (SELECT customer_id FROM Customers WHERE first_name = 'Patrick' AND last_name = 'Rothfuss')),
         4, 360),
	((SELECT service_id FROM Services WHERE name = 'Irrigation Installation'),
		(SELECT invoice_id FROM Invoices WHERE date_created = '2024-01-20' AND customer_id IN (SELECT customer_id FROM Customers WHERE first_name = 'Brandon' AND last_name = 'Sanderson')),
         8, 1040);

SET FOREIGN_KEY_CHECKS = 1;
COMMIT;

"""