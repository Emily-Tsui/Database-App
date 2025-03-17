/*
    Programming Pals(Group 71)
    Kyle Gonzales
    Emily Yau Yee Tsui
    CS 340 - Project Step 3 Final
    Date 2/22/2024

    Adapted sources from: Advanced SQL assignment, module 6 Database Application Design.
*/

/*  There will be 6 tabs in our website including an index.html for an
    introduction.
                Pages
            -------------
            Customers
            Employees
            Services
            Invoices
            Invoice Details     --> Intersection table for services_invoices
*/

-- ----------------------------------------------------------------------------
-- Get all the Customer ID and names to populate the Customers page
SELECT
	customer_id AS 'Customer ID',
    CONCAT(first_name, ' ', last_name) AS 'Name',
    CONCAT(address, ', ', city, ', ', state, ' ', zipcode) AS 'Address',
    email AS 'Email',
    phone AS 'Phone'
FROM Customers;

-- Add Customer information with form
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
    (%fname, %lname, %address, %city, %state, %zipcode, %email, %phone);
    -- These are variables(%) that will be gathered from the form using python

-- Update a Customer ID 1's information with the form
UPDATE Customers
SET
    first_name = %fname,
    last_name = %lname,
    address = %address,
    city = %city,
    state = %state,
    zipcode = %zipcode,
    email = %email,
    phone = %phone
    -- These are variables(%) that will be gathered from the form using python
WHERE customer_id = %customer_id;

-- Delete a Customer with the form
DELETE FROM Customers
WHERE customer_id = %customer_id;
    -- This is a variable(%) that will be gathered from the form using python

-- ----------------------------------------------------------------------------
-- Get all the Employee ID, name, and phone number
SELECT
	employee_id AS 'Employee ID',
    CONCAT(employee_fname, ' ', employee_lname) AS 'Name',
    phone_number AS 'Phone'
FROM Employees;

-- Get specific employee record
SELECT *
FROM
    Employees
WHERE
    employee_id = %s;

-- Add Employee information with form
INSERT INTO Employees (
    employee_fname,
    employee_lname,
    phone_number
)
VALUES
	(%fname, %lname, %phone);
    -- These are variables(%) that will be gathered from the form using python

-- Update an Employee ID's' information with the form
UPDATE Employees
SET
    employee_fname = %fname,
    employee_lname = %lname,
    phone_number = %phone
WHERE employee_id = %emp_id;
    -- These are variables(%) that will be gathered from the form using python

-- Delete an Employee
DELETE FROM Employees
WHERE customer id = %emp_id;
    -- This is a variable(%) that will be gathered from the form using python

-- ----------------------------------------------------------------------------
-- Get all the Services ID, Names, and Cost Per Hour
SELECT
	service_id AS 'Service ID',
    name AS 'Name',
    CONCAT("$", cost_per_hour) AS 'Cost Per Hour'
FROM services;

-- Get specific service record
SELECT *
FROM
    Services
WHERE
    service_id = %s;

-- Get services cost
SELECT
    cost_per_hour
FROM
    Services
WHERE
    name = %s;

-- Add Service information with form
INSERT INTO Services (
    name,
    cost_per_hour
)
VALUES
	(%name, %cost);
    -- These are variables(%) that will be gathered from the form using python

-- Update a Service ID's information
UPDATE Services
SET
    name = %name,
    cost_per_hour = %cost
WHERE service_id = %s;
    -- These are variables(%) that will be gathered from the form using python

-- Delete a Service
DELETE FROM Services
WHERE service_id = %service_id;
    -- This is a variable(%) that will be gathered from the form using python


-- ----------------------------------------------------------------------------
-- Get all Invoices information
SELECT
    Invoices.invoice_id AS 'Invoice ID',
    Invoices.date_created AS 'Date Created',
    CONCAT(Customers.first_name, ' ', Customers.last_name) AS 'Customer Name',
    CONCAT(Employees.employee_fname, ' ', Employees.employee_lname) AS 'Employee Name',
    GROUP_CONCAT(Services.name) AS Service,
    CONCAT('$', SUM(Services_Invoices.line_subtotal)) AS Total
FROM
    Invoices
        LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id
        LEFT JOIN Employees ON Invoices.employee_id = Employees.employee_id
        LEFT JOIN Services_Invoices ON Invoices.invoice_id = Services_Invoices.invoice_id
        LEFT JOIN Services ON Services_Invoices.service_id = Services.service_id
GROUP BY Invoices.invoice_id
ORDER BY Invoices.invoice_id ASC;

-- Get invoice info for specific record
SELECT *
FROM
    Invoices
WHERE
    invoice_id = %s;

-- Add Invoice information with form
-- Users are able to add many services to one invoice. For every invoice created the "insert into
-- invoices" script is run once, but the "insert into intersection table" script may run multiple times
-- (it will run the same number of times as number of services in the invoice).
INSERT INTO Invoices (
    customer_id,
    employee_id,
    date_created
)
VALUES
    ((SELECT customer_id FROM Customers WHERE first_name = %cust_fname AND last_name = %cust_lname),
		(SELECT employee_id FROM Employees WHERE employee_fname= %employee_fname AND employee_lname = %employee_lname),
        %date);
        -- These are variables(%) that will be gathered from the form using python

    -- Records must now be added to the intersection table using the new invoice id generated above 
INSERT INTO Services_Invoices (
    service_id,
    invoice_id,
    qty,
    line_subtotal
)
VALUES
    (%service_id, %invoice_id, %qty, %line_subtotal)
    -- These are variables(%) that will be gathered from the form using python
    -- This insert script will run once for every service_id chosen on the form

-- Update Invoice ID's information
-- This can influence the intersection table in 3 ways, 1. Updating row, 2. Inserting rows, 3. Deleting rows
UPDATE Invoices
SET
    customer_id = %cust_id,
    employee_id = %emp_id,
    data_created = %date
WHERE invoice_id = %invoice_id;
    -- These are variables(%) that will be gathered from the form using python

    -- 1. Update intersection table rows
UPDATE Services_Invoices
SET
    service_id = %service_id,
    invoice_id = %invoice_id,
    qty = %qty,
    line_subtotal = %line_subtotal
WHERE invoice_id = %invoice_id  AND service_id = service_id;
    -- These are variables(%) that will be gathered from the form using python

-- When a new service is selected for an invoice, the row must be added to the intersection table
-- This will run for as many new services were selected
    -- 2. Insert intersection table rows
INSERT INTO Services_Invoices (
    service_id,
    invoice_id,
    qty,
    line_subtotal
)
VALUES
    (%service_id, %invoice_id, %qty, %line_subtotal)
    -- These are variables(%) that will be gathered from the form using python

-- When a service is de-selected from an invoice, the row must be deleted from the intersection table
-- This will run for as many services were de-selected
    -- 3. Delete intersection tables rows
DELETE FROM Services_Invoices
WHERE service_id = %service_id

-- Delete an Invoice
-- This cascade deletes from the intersection table
DELETE FROM Invoices
WHERE invoice_id = %invoice_id;
    -- These are variables(%) that will be gathered from the form using python

-- ----------------------------------------------------------------------------
-- Invoice details page aka Intersection table Services_Invoices
SELECT
	services_invoices.services_invoices_id AS 'Details ID',
    CONCAT(customers.first_name, ' ', customers.last_name, ', ', invoices.date_created) AS 'Invoice',
    services.name AS 'Service',
    qty AS 'Hours Billed',
    CONCAT('$', line_subtotal) AS 'Line Total'
FROM
	services_invoices
		LEFT JOIN invoices ON services_invoices.invoice_id = invoices.invoice_id
        LEFT JOIN customers ON invoices.customer_id = customers.customer_id
        LEFT JOIN services ON services_invoices.service_id = services.service_id
ORDER BY
	services_invoices.services_invoices_id;

-- Get line items from intersection table for specific invoice record
SELECT
    Services.name,
    Services_Invoices.qty
FROM
    Services_Invoices
        LEFT JOIN Services ON Services_Invoices.service_id = Services.service_id
WHERE Services_Invoices.invoice_id = %s;

-- ----------------------------------------------------------------------------
-- Drop down menu queries

-- Customers
SELECT
    customer_id,
    CONCAT(customer_id, ' | ', first_name, ' ', last_name) AS 'Name'
FROM
    Customers
ORDER BY
    customer_id;

-- Employees
SELECT
    employee_id,
    CONCAT(employee_id, ' | ', employee_fname, ' ', employee_lname) AS 'Name'
FROM
    Employees
ORDER BY
    employee_id

-- Invoices
SELECT
    Invoices.invoice_id,
    CONCAT(Invoices.invoice_id, ' | ', Invoices.date_created, ' | ', Customers.first_name, ' ', Customers.last_name) AS 'Name'
FROM
    Invoices
        LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id
ORDER BY
    Invoices.invoice_id ASC;

-- Services
-- Get services info
SELECT
    service_id,
    CONCAT(service_id, ' | ', name) AS 'Name'
FROM
    Services
ORDER BY
	service_id;

-- Service dropdown by name
SELECT
    service_id,
    name AS 'Name',
    cost_per_hour AS 'Cost Per Hour'
FROM Services;