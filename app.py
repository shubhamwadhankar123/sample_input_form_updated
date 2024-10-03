from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField, FloatField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Shubhamw@1234'
app.config['MYSQL_DB'] = 'urbanseva'
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.secret_key = 'your_secret_key'

mysql = MySQL(app)

# Service Form Definition
class ServiceForm(FlaskForm):
    service_image = FileField('Service Image', validators=[DataRequired()])
    service_name = SelectField('Service Name', choices=[('Electrician', 'Electrician'), ('Plumber', 'Plumber'), ('Carpenter', 'Carpenter'), ('Painter', 'Painter'), ('Gardener', 'Gardener')], validators=[DataRequired()])
    service_provider_name = StringField('Service Provider Name', validators=[DataRequired()])
    service_details = TextAreaField('Service Details', validators=[DataRequired()])
    city = SelectField('City', choices=[('Mumbai', 'Mumbai'), ('Delhi', 'Delhi')], validators=[DataRequired()])
    state = SelectField('State', choices=[('Maharashtra', 'Maharashtra'), ('Delhi', 'Delhi')], validators=[DataRequired()])
    full_address = StringField('Full Address', validators=[DataRequired()])
    mobile_no = StringField('Mobile No', validators=[DataRequired()])
    ratings = FloatField('Ratings (1-5)', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Home Page Route
@app.route('/')
def home():
    # Query to get all services for the homepage
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, service_name FROM services")  # Adjust the query as needed
    services = cur.fetchall()
    cur.close()
    return render_template('homepage.html', services=services)

# Add New Service Route
@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service_image = form.service_image.data
        service_image_filename = service_image.filename
        service_image.save(os.path.join(app.config['UPLOAD_FOLDER'], service_image_filename))
        
        service_name = form.service_name.data
        service_provider_name = form.service_provider_name.data
        service_details = form.service_details.data
        city = form.city.data
        state = form.state.data
        full_address = form.full_address.data
        mobile_no = form.mobile_no.data
        ratings = form.ratings.data

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO services(service_image, service_name, service_provider_name, service_details, city, state, full_address, mobile_no, ratings) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (service_image_filename, service_name, service_provider_name, service_details, city, state, full_address, mobile_no, ratings))
        mysql.connection.commit()
        cur.close()

        flash('Service added successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('form.html', form=form)

# View Services by Category
@app.route('/services/<service_name>')
def view_services(service_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services WHERE service_name = %s", (service_name,))
    services = cur.fetchall()  # This will return a list of tuples
    cur.close()

    # Pass the service_name and services to the template
    return render_template('services.html', services=services, service_name=service_name)

# Delete Service Route
@app.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
    mysql.connection.commit()
    cur.close()
    
    flash('Service deleted successfully!', 'success')
    return redirect(url_for('home'))

# Book Service Route
@app.route('/book_service/<int:service_id>', methods=['GET', 'POST'])
def book_service(service_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    cur.close()

    if service:
        if request.method == 'POST':
            # Implement booking logic here (e.g., save booking to a database)
            flash('Service booked successfully!', 'success')
            return redirect(url_for('home'))
        return render_template('book_service.html', service=service)
    else:
        flash('Service not found!', 'error')
        return redirect(url_for('home'))

# Service Detail Page Route
@app.route('/service/<int:service_id>')
def service_page(service_id):
    # Query to get service details by ID
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM services WHERE id = %s", (service_id,))
    service = cur.fetchone()
    cur.close()
    return render_template('service.html', service=service)

if __name__ == '__main__':
    app.run(debug=True)
