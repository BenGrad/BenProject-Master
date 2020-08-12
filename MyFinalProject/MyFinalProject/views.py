"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from MyFinalProject import app
from MyFinalProject.Models.LocalDatabaseRoutines import create_LocalDatabaseServiceRoutines


from datetime import datetime
from flask import render_template, redirect, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from MyFinalProject.Models.QueryFormStructure import ExpandForm
from MyFinalProject.Models.QueryFormStructure import CollapseForm

import json 
import requests

import io
import base64

from os import path

from flask   import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms import TextField, TextAreaField, SubmitField, SelectField, DateField
from wtforms import ValidationError
from wtforms.fields.html5 import DateField , DateTimeField

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from MyFinalProject.Models.QueryFormStructure import QueryForm
from MyFinalProject.Models.QueryFormStructure import QueryFormStructure 
from MyFinalProject.Models.QueryFormStructure import LoginFormStructure 
from MyFinalProject.Models.QueryFormStructure import UserRegistrationFormStructure 

###from DemoFormProject.Models.LocalDatabaseRoutines import IsUserExist, IsLoginGood, AddNewUser 
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
db_Functions = create_LocalDatabaseServiceRoutines() 

#Function for selecting mehozot
def get_mehozot_choices():
    df_short_state = pd.read_csv(path.join(path.dirname(__file__), "..\\static\\data\\FireDataset.csv"))
    df1 = df_short_state.groupby('מחוז').sum()
    l = df1.index
    m = list(zip(l , l))
    return m



@app.route('/')
@app.route('/home')
def home():

    print("Home")

    """Renders the home page."""
    
    return render_template(
        'index.html',
        title='Home Page',
        img_OnFire = '/static/imgs/OnFire.jpg',
        year=datetime.now().year
    )

@app.route('/contact')
def contact():

    print("Contact")

    """Renders the contact page."""

    return render_template(
        'contact.html',
        year=datetime.now().year,
        img_tichonet = '/static/imgs/tichonet.png',
        img_ben = '/static/imgs/Ben.jpg'
        
    )

@app.route('/about')
def about():

    print("About")

    """Renders the about page."""
    return render_template(
        'about.html',
        year=datetime.now().year,
        img_tichonet = '/static/imgs/tichonet.png'
    )

@app.route('/data')
def data():

    print("Data")

    """Renders the about page."""
    return render_template(
        'data.html',
        title='Data',
        year=datetime.now().year,
        message='My data page.',
        car_accident1 = '/static/imgs/OnFire.jpg',
        car_accident2 = '/static/imgs/Fire1.jpg',
        
    )


@app.route('/hebrew_text')
def hebrew_text():
    """Renders the about page."""
    return render_template(
        'hebrew_text.html'
    )


@app.route('/data/FireDataset' , methods = ['GET' , 'POST'])
def Teonot2017():

    print("Fire Dataset")

    """Renders the about page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/data/FireDataset.csv'))
    raw_data_table = ''

    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
            raw_data_table = df.to_html(classes = 'table table-hover')
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
        

    

    return render_template(
        'FireDataset.html',
        title='FireDataset',
        year=datetime.now().year,
        message='Fire Dataset.',
        raw_data_table = raw_data_table,
        form1 = form1,
        form2 = form2
           
    )



@app.route('/register', methods=['GET', 'POST'])
def Register():
    form = UserRegistrationFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (not db_Functions.IsUserExist(form.username.data)):
            db_Functions.AddNewUser(form)
            db_table = ""

            flash('Thanks for registering new user - '+ form.FirstName.data + " " + form.LastName.data )
            # Here you should put what to do (or were to go) if registration was good
        else:
            flash('Error: User with this Username already exist ! - '+ form.username.data)
            form = UserRegistrationFormStructure(request.form)

    return render_template(
        'register.html', 
        form=form, 
        title='Register New User',
        year=datetime.now().year,
        repository_name='Pandas',
        )

@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (db_Functions.IsLoginGood(form.username.data, form.password.data)):
            flash('Login approved!')
            return redirect('DataQuery')
        else:
            flash('Error in - Username and/or password')
   
    return render_template(
        'login.html', 
        form=form, 
        title='Login to data analysis',
        year=datetime.now().year,
        )




@app.route('/DataQuery' , methods = ['GET' , 'POST'])
def DataQuery():


    form1 = QueryForm()
    chart1 = ""
    fig_image = ""

    #take the variable df and put the dataset inside of it
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/data/FireDataset.csv'))

    #creating a new datetime column
    df['DateTime'] = pd.to_datetime(df[['Year','Month','Day']])
    #delete the unnecessary columns (year,month,date,region,country,state) (1 stands for columns)
    df = df.drop(['Year','Month','Day','Region', 'Country', 'State',],1)


    #Create new variable called city_Pulldown and filter it to have only the cities by using the command ("df.City.to_list()")
    city_Pulldown = df.City.to_list()

    #create a new object from type set which automatically takes only one of each name that appears
    #thereby removing duplicates and then converts it back to a list called city_Pulldown
    city_Pulldown = list(set(city_Pulldown))

    #create a new format of cities that presents as city1,city1 in order to take the first city as the option you select 
    #in the dropdown menu and the second city as the one that's sent to the server for all the code and calculations
    city_Pulldown = list(zip(city_Pulldown,city_Pulldown))
      


    #bring city pulldown and take choices into variable
    form1.cities.choices = city_Pulldown
    



    if request.method == 'POST':

        
        #start_date takes the startdate from form1 (IE the input in DataQuery.html)
        start_date = form1.start_date.data
        #same as start_date
        end_date = form1.end_date.data
        cities = form1.cities.data



        city_List = cities

        #this is where you filter out the other cities
        df = df[df.City.isin(city_List)]

        #use the second variable (df1) and use unstack to set the city's names
        # as the columns title for the temperature of each city (groupby sets it by date)
        df1 = df.groupby(['DateTime', 'City']).mean().unstack()

        
        #create new variable called df2 and take df1 with the dates that the user input.
        df2 = df1[start_date : end_date]

        # create plot object ready for graphs
        fig = plt.figure()
        ax = fig.add_subplot()



       

        df2.plot(ax = ax, grid=True)
        fig_image = plot_to_img(fig)
        #df2 = plot_to_img(fig)

    else:
        form1.start_date.data = df.DateTime.min() 
        form1.end_date.data = df.DateTime.max()

    return render_template(
        'DataQuery.html',
        form1 = form1,
        fig_image = fig_image, #this is the one thats displayed
    )

def plot_to_img(fig):
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    return pngImageB64String








