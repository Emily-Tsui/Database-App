"""
Programming Pals(Group 71)
Kyle Gonzales
Emily Yau Yee Tsui
CS 340 - Project Step 6 FINAL
Date 03/16/2024

CITATIONS
2.
Flask starter code and formatting is copied and adapted from the OSU CS340 GitHub flask_starter_app
Date: 2/29/2024
Copied and adapted from:
Source URL: https://github.com/osu-cs340-ecampus/flask-starter-app/blob/master/bsg_people_app/templates/edit_people.j2

8.
Favicon route and import send_from_directory
Date: 3/11/2024
Copied and adapted from:
Source URL: https://flask.palletsprojects.com/en/2.3.x/patterns/favicon/
"""

from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from flask import request
import os
# BEGIN ADAPTATION CITATION 8
from flask import send_from_directory
# END ADAPTATION CITATION 8

# ONLY USED FOR RELOADING DB TO DEFAULT VALUES
from reload_db import reload_query

app = Flask(__name__)

# Database Credentials
app.config["MYSQL_HOST"] = ""
app.config["MYSQL_USER"] = ""
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = ""
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Routes
# ====================================================================================================
# Home Page

# BEGIN FORMAT ADAPTED FROM CITATION 2, CONTENT IS ORIGINAL WORK (goes to end)
@app.route('/', methods=["GET", "POST"])
def index():
    # Populate home page with summary data
    if request.method == "GET":
        # Retrieve data from DB
        query = """SELECT
                        temp_customer.total_customers AS 'Total Customers',
                        temp_employee.total_employees AS 'Total Employees',
                        temp_income.total_income AS 'Total Income'
                    FROM (
                        SELECT COUNT(DISTINCT Customers.customer_id) AS total_customers
                        FROM Customers) temp_customer,
                        (	
                        SELECT COUNT(DISTINCT Employees.employee_id) AS total_employees
                        FROM Employees) temp_employee,
                        (	
                        SELECT SUM(Services_Invoices.line_subtotal) AS total_income
                        FROM Services_Invoices) temp_income;"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        summarydata = cur.fetchall()

        return render_template("index.j2", summary_data = summarydata)
    
    # SQL to reload database to default values
    elif request.method == "POST":
        if request.form.get("reload_db"):
            cur = mysql.connection.cursor()
            cur.execute(reload_query)

            return redirect("/")

# ====================================================================================================
        
# BEGIN COPIED FROM CITATION 8
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
# END COPIED FROM CITATION 8

# ====================================================================================================
# Customers Page

@app.route('/customers/', methods=["GET", "POST"])
def customers():
    # Populate customers page with customer data
    if request.method == "GET":
        # Retrieve data from DB
        query = """SELECT
                        customer_id AS 'Customer ID',
                        CONCAT(first_name, ' ', last_name) AS 'Name',
                        CONCAT(address, ', ', city, ', ', state, ' ', zipcode) AS 'Address',
                        email AS 'Email', phone AS 'Phone'
                    FROM
                        Customers;"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        customers_data = cur.fetchall()

        # Query to display a dropdown list with customer ID and corresponding name
        query = """SELECT
                        customer_id,
                        CONCAT(customer_id, ' | ', first_name, ' ', last_name) AS 'Name'
                    FROM
                        Customers;"""
        cur.execute(query)
        dropdowndata = cur.fetchall()

        return render_template("customers.j2", customers = customers_data, dropdown_data = dropdowndata)
    
    
    # Adding/inserting/deleting into Customers entity
    elif request.method == "POST":
    # Add customer
        if request.form.get("add_customer"):
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            address = request.form["address"]
            city = request.form["city"]
            state = request.form["state"]
            zipcode = request.form["zipcode"]
            email = request.form["email"]
            phone = request.form["phone"]
        
            # NULL email field check
            if email == "" or email == "None":
                email = None

            # Insert customer data to DB
            query = """INSERT INTO Customers (
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
                            (%s, %s, %s, %s, %s, %s, %s, %s);"""
            cur = mysql.connection.cursor()
            cur.execute(query, (first_name, last_name, address, city, state, zipcode, email, phone))
            mysql.connection.commit()

            return redirect("/customers/")

    # Delete customer
        elif request.form.get("delete_customer"):
            customer_id = request.form['cust_ID']
            query = """DELETE FROM Customers WHERE customer_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (customer_id,))
            mysql.connection.commit()

            return redirect("/customers/")

    # Update customer
        # Get customer data and populate edit customer page
        elif request.form.get("edit_customer"):
            customer_id = request.form['cust_ID']
            query = """SELECT * FROM Customers WHERE customer_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (customer_id,))
            data = cur.fetchall()

            # NULL email field check
            if data[0]['email'] == None:
                data[0]['email'] = ""

            return render_template("edit_customers.j2", form_data=data)

        # Retrieve customer data and update DB
        elif request.form.get("update"):
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            address = request.form["address"]
            city = request.form["city"]
            state = request.form["state"]
            zipcode = request.form["zipcode"]
            email = request.form["email"]
            phone = request.form["phone"]
            customer_id = request.form["cust_ID"]
        
            # NULL email field check
            if email == "" or email == "None":
                email = None


            # Update Customers table in DB
            query = """UPDATE Customers
                            SET
                                first_name = %s,
                                last_name = %s,
                                address = %s,
                                city = %s,
                                state = %s,
                                zipcode = %s,
                                email = %s,
                                phone = %s
                            WHERE customer_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (first_name, last_name, address, city, state, zipcode, email, phone, customer_id))
            mysql.connection.commit()

            return redirect("/customers/")

# ====================================================================================================
# Invoices Page

@app.route('/invoices/', methods=["GET", "POST"])
def invoices():
# Populate invoices page
    if request.method == "GET":
        # Retrieve data from DB
        query = """SELECT
                        Invoices.invoice_id AS 'Invoice ID',
                        Invoices.date_created AS 'Date Created',
                        CONCAT(Customers.first_name, ' ', Customers.last_name) AS 'Customer Name',
                        CONCAT(Employees.employee_fname, ' ', Employees.employee_lname) AS 'Employee Name',
                        GROUP_CONCAT(Services.name) AS 'Service',
                        CAST(CONCAT('$', SUM(Services_Invoices.line_subtotal)) AS char(50)) AS 'Total'
                    FROM
                        Invoices
                            LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id
                            LEFT JOIN Employees ON Invoices.employee_id = Employees.employee_id
                            LEFT JOIN Services_Invoices ON Invoices.invoice_id = Services_Invoices.invoice_id
                            LEFT JOIN Services ON Services_Invoices.service_id = Services.service_id
                    GROUP BY Invoices.invoice_id
                    ORDER BY Invoices.invoice_id ASC;"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        # Dropdown list with customer ID and name
        query = """SELECT
                        customer_id,
                        CONCAT(customer_id, ' | ', first_name, ' ', last_name) AS 'Name'
                    FROM
                        Customers;"""
        cur.execute(query)
        customerdropdowndata = cur.fetchall()

        # Dropdown list with employee ID and name
        query = """SELECT
                        employee_id,
                        CONCAT(employee_id, ' | ', employee_fname, ' ', employee_lname) AS 'Name'
                    FROM
                        Employees;"""
        cur.execute(query)
        employeedropdowndata = cur.fetchall()

        # Get all services for invoice creation tab
        query = """SELECT
                        service_id,
                        name
                    FROM
                        Services;"""
        cur.execute(query)
        servicedata = cur.fetchall()

        # Get invoice info for update/delete tab dropdown list
        query = """SELECT
                        Invoices.invoice_id,
                        CONCAT(Invoices.invoice_id, ' | ', Invoices.date_created, ' | ', Customers.first_name, ' ', Customers.last_name) AS 'Name'
                    FROM
                        Invoices
                            LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id
                    ORDER BY
                        Invoices.invoice_id ASC;"""
        cur.execute(query)
        findinvoice = cur.fetchall()

        return render_template("invoices.j2", invoice_data = data, customer_dropdown_data = customerdropdowndata, employee_dropdown_data = employeedropdowndata, service_data = servicedata, find_invoice = findinvoice)

# Add/Update/Delete from Invoices entity
    elif request.method == "POST":
    # Add invoice
        if request.form.get("add_invoice"):
            form_output = request.form
            customer_id = request.form["customer_ID"]
            employee_id = request.form["employee_ID"]
            date_created = request.form["date_created"]

            # Check for NULL employee field
            if employee_id == 'None':
                employee_id = None
    
            # Invoice table insert statement
            query = """INSERT INTO Invoices (
                            customer_id,
                            employee_id,
                            date_created
                        )
                        VALUES
                            (%s, %s, %s);"""
            cur = mysql.connection.cursor()
            cur.execute(query, (customer_id, employee_id, date_created))
            mysql.connection.commit()

        # Services_Invoices (intersection table) insert for each service
            # Remove all data from form data except for services
            form_output = form_output.to_dict(flat=True)
            del form_output["customer_ID"]
            del form_output["employee_ID"]
            del form_output["date_created"]
            del form_output["add_invoice"]

            # Find every non-NULL service
            for key in form_output:
                # Skip NULL services
                if form_output[key] == '0':
                    continue
            
                # Get service cost
                query = """SELECT
                                cost_per_hour
                            FROM
                                Services
                            WHERE
                                name = %s;"""
                cur = mysql.connection.cursor()
                cur.execute(query, (key,))
                cost = cur.fetchone()

                # Get total cost (service cost * qty)
                total = cost['cost_per_hour'] * int(form_output[key])

                # Insert service to DB
                query = """INSERT INTO Services_Invoices (
                                service_id,
                                invoice_id,
                                qty,
                                line_subtotal
                            )
                            VALUES
                                ((SELECT service_id FROM Services WHERE name = %s),
                                (SELECT DISTINCT invoice_id FROM Invoices WHERE customer_id = %s AND date_created = %s),
                                %s,
                                %s)"""
                cur = mysql.connection.cursor()
                cur.execute(query, (key, customer_id, date_created, form_output[key], total))
                mysql.connection.commit()

            return redirect("/invoices/")

    # Delete invoice
        elif request.form.get("delete_invoice"):
            invoice_id = request.form['invoice_ID']
            query = """DELETE FROM Invoices WHERE invoice_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (invoice_id,))
            mysql.connection.commit()

            return redirect("/invoices/")

    # Update Invoice
        # Get invoice data and populate edit invoice page
        elif request.form.get("edit_invoice"):
            invoice_id = request.form['invoice_ID']
            query = """SELECT * FROM Invoices WHERE invoice_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (invoice_id,))
            invoicedata = cur.fetchall()

            # Check for NULL employee ID
            if invoicedata[0]['employee_id'] == None:
                invoicedata[0]['employee_id'] = 'None'

            # Get invoice line items
            query = """SELECT
                            Services.name,
                            Services_Invoices.qty
                        FROM
                            Services
                                LEFT JOIN Services_Invoices ON Services_Invoices.service_id = Services.service_id
                        WHERE Services_Invoices.invoice_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (invoice_id,))
            lineitems = cur.fetchall()

            # Dropdown list with customer ID and name
            query = """SELECT
                            customer_id,
                            CONCAT(customer_id, ' | ', first_name, ' ', last_name) AS 'Name'
                        FROM
                            Customers;"""
            cur.execute(query)
            customerdropdowndata = cur.fetchall()

            # Dropdown list with employee ID and name
            query = """SELECT
                            employee_id,
                            CONCAT(employee_id, ' | ', employee_fname, ' ', employee_lname) AS 'Name'
                        FROM
                            Employees;"""
            cur.execute(query)
            employeedropdowndata = cur.fetchall()

            # Get all services for invoice creation tab
            query = """SELECT
                            name
                        FROM
                            Services;"""
            cur.execute(query)
            servicedata = cur.fetchall()

        # Create custom dictionary of all services - {service name: quantity}
            # List of all offered services
            servicelist = []
            for service in servicedata:
                servicelist.append(service['name'])

            # Dictionary of services already on selected invoice
            servicedict = {}
            for element in lineitems:
                servicedict[element['name']] = element['qty']

            # Merge all services and services on selected invoice
            for service in servicelist:
                if service not in servicedict:
                    servicedict[service] = 0

            return render_template("edit_invoices.j2", invoice_data = invoicedata, customer_dropdown_data = customerdropdowndata, employee_dropdown_data = employeedropdowndata, line_items = servicedict)

        # Retrieve data from edit invoice page and update DB
        elif request.form.get("update"):
            form_output = request.form.to_dict(flat=True)
            invoice_id = request.form["invoice_ID"]
            customer_id = request.form["customer_ID"]
            employee_id = request.form["employee_ID"]
            date_created = request.form["date_created"]

            # Check for NULL employee ID
            if employee_id == 'None':
                employee_id = None

            # Update Invoices table
            query = """UPDATE Invoices
                            SET
                                customer_id = %s,
                                employee_id = %s,
                                date_created = %s
                            WHERE invoice_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (customer_id, employee_id, date_created, invoice_id))
            mysql.connection.commit()

        # Reflect changes in Services_Invoices table
            # Remove service line items from DB
            query = """DELETE FROM Services_Invoices WHERE invoice_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (invoice_id,))
            mysql.connection.commit()
            
            # Remove all form data except for services
            del form_output["customer_ID"]
            del form_output["employee_ID"]
            del form_output["invoice_ID"]
            del form_output["date_created"]
            del form_output["update"]

            # Find every non-NULL service
            for service in form_output:
                # Skip NULL services
                if form_output[service] == '0':
                    continue
            
                # Get service cost
                query = """SELECT
                                cost_per_hour
                            FROM
                                Services
                            WHERE
                                name = %s;"""
                cur = mysql.connection.cursor()
                cur.execute(query, (service,))
                cost = cur.fetchone()

                # Get total cost (service cost * qty)
                total = cost['cost_per_hour'] * int(form_output[service])

                # Insert service line item
                query = """INSERT INTO Services_Invoices (
                                service_id,
                                invoice_id,
                                qty,
                                line_subtotal
                            )
                            VALUES
                                ((SELECT service_id FROM Services WHERE name = %s),
                                (SELECT DISTINCT invoice_id FROM Invoices WHERE customer_id = %s AND date_created = %s),
                                %s,
                                %s)"""
                cur = mysql.connection.cursor()
                cur.execute(query, (service, customer_id, date_created, form_output[service], total))
                mysql.connection.commit()

            return redirect("/invoices/")

# ====================================================================================================
# Employees Page
        
@app.route('/employees/', methods=["GET", "POST"])
def employees():
    # Populate employees page with employee data
    if request.method == "GET":
        query = """SELECT
                        employee_id AS 'Employee ID',
                        CONCAT(employee_fname, ' ', employee_lname) AS 'Name',
                        phone_number AS 'Phone'
                    FROM
                        Employees"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        employees_data = cur.fetchall()

        # Dropdown list with employee ID and name
        query = """SELECT
                        employee_id,
                        CONCAT(employee_id, ' | ', employee_fname, ' ', employee_lname) AS 'Name'
                    FROM
                        Employees;"""
        cur.execute(query)
        dropdowndata = cur.fetchall()

        return render_template("employees.j2", employees = employees_data, dropdown_data = dropdowndata)

# Add/Update/Delete Employees entity
    elif request.method == "POST":
    # Add employee
        if request.form.get("add_employee"):
            employee_fname = request.form["first_name"]
            employee_lname = request.form["last_name"]
            phone = request.form["phone"]

            query = """INSERT INTO Employees (
                            employee_fname,
                            employee_lname,
                            phone_number
                        )
                        VALUES
                            (%s, %s, %s);"""
            cur = mysql.connection.cursor()
            cur.execute(query, (employee_fname, employee_lname, phone))
            mysql.connection.commit()
            
            return redirect("/employees/")

    # Delete employee
        elif request.form.get("delete_employee"):
            employee_id = request.form['employee_ID']
            query = """DELETE FROM Employees WHERE employee_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (employee_id,))
            mysql.connection.commit()

            return redirect("/employees/")

    # Update Employee
        # Get employee data and populate edit employee page
        elif request.form.get("edit_employee"):
            employee_id = request.form['employee_ID']
            query = """SELECT * FROM Employees WHERE employee_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (employee_id,))
            data = cur.fetchall()

            return render_template("edit_employees.j2", form_data=data)
        
        # Get employee data from form
        elif request.form.get("update"):
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            phone = request.form["phone"]
            employee_id = request.form["employee_ID"]

            # Update statement for employee table
            query = """UPDATE Employees
                            SET
                                employee_fname = %s,
                                employee_lname = %s,
                                phone_number = %s
                            WHERE employee_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (first_name, last_name, phone, employee_id))
            mysql.connection.commit()

            return redirect("/employees/")

# ====================================================================================================
# Services Page

@app.route('/services/', methods=["GET", "POST"])
def services():
# Populate services page with service data
    if request.method == "GET":
        query = """SELECT
                        service_id AS 'Service ID',
                        name AS 'Name',
                        CONCAT("$", cost_per_hour) AS 'Cost Per Hour'
                    FROM
                        Services"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        services_data = cur.fetchall()

        # Dropdown list with service ID and name
        query = """SELECT
                        service_id,
                        name AS 'Name',
                        cost_per_hour AS 'Cost Per Hour'
                    FROM Services;"""
        cur.execute(query)
        dropdowndata = cur.fetchall()

        return render_template("services.j2", services = services_data, dropdown_data=dropdowndata)
    
# Add/Update/Delete services
    elif request.method == "POST":
    # Add service
        if request.form.get("add_service"):
            name = request.form["service_name"]
            cost_per_hour = request.form["cost"]
        
            query = """INSERT INTO Services (name, cost_per_hour) VALUES (%s, %s);"""
            cur = mysql.connection.cursor()
            cur.execute(query, (name, cost_per_hour))
            mysql.connection.commit()
            
            return redirect("/services/")

    # Delete service
        elif request.form.get("delete_service"):
            service_id = request.form['service_ID']
            query = """DELETE FROM Services WHERE service_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (service_id,))
            mysql.connection.commit()

            return redirect("/services/")   

    # Update service
        # Get service data and populate edit service page
        elif request.form.get("edit_service"):
            service_id = request.form['service_ID']
            query = """SELECT * FROM Services WHERE service_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (service_id,))
            data = cur.fetchall()

            return render_template("edit_services.j2", form_data=data)
        
        # Update statement for service table
        elif request.form.get("update_service"):
            service_id = request.form["service_ID"]
            name = request.form["service_name"]
            cost = request.form["cost"]
            query = """UPDATE Services
                            SET
                                name = %s,
                                cost_per_hour = %s
                            WHERE service_id = %s;"""
            cur = mysql.connection.cursor()
            cur.execute(query, (name, cost, service_id))
            mysql.connection.commit()

            return redirect("/services/")

# ====================================================================================================
# Invoice Details Page

@app.route('/invoice_details/')
def invoicedetails():
# Populate invoice details page with invoice details data
    if request.method == "GET":
        query = """SELECT
	                    Services_Invoices.services_invoices_id AS 'Details ID',
                        Invoices.invoice_id AS 'Invoice ID',
                        CONCAT(Customers.first_name, ' ', Customers.last_name, ', ', Invoices.date_created) AS 'Invoice Description',
                        Services.name AS 'Service',
                        qty AS 'Hours Billed',
                        CONCAT('$', line_subtotal) AS 'Line Total'
                    FROM
                        Services_Invoices
                            LEFT JOIN Invoices ON Services_Invoices.invoice_id = Invoices.invoice_id
                            LEFT JOIN Customers ON Invoices.customer_id = Customers.customer_id
                            LEFT JOIN Services ON Services_Invoices.service_id = Services.service_id
                    ORDER BY
                        Services_Invoices.services_invoices_id;"""
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

    return render_template("invoice_details.j2", invoicedetails_data = data)

# ====================================================================================================

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 6656)) 
    app.run(port=port, debug=True)

# END FORMAT ADAPTED FROM CITATION 2, CONTENT IS ORIGINAL WORK
