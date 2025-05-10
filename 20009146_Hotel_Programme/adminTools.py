# Hamidur Rahman: 20009146
import email
from pyexpat.errors import messages
from flask import Flask, Blueprint, render_template, request, session, make_response, url_for, redirect, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
import hotelDB, mysql.connector
from datetime import datetime, date, time, timedelta
from dateutil.parser import parse

adminTools = Blueprint("adminTools", __name__, static_folder="static", template_folder="templates")

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:            
            print("You need to login first")
            #return redirect(url_for('login', error='You need to login first'))
            return render_template('sign-in.html', error='You need to login first')    
    return wrap

#We also write a wrapper for admin user(s). It will check with the user is 
# logged in and the usertype is admin and only then it will allow user to
# perform admin functions
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'admin'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as admin user")
            #return redirect(url_for('login', error='You need to login first as admin user'))
            return render_template('sign-in.html', error='You need to login first as admin user')    
    return wrap

#We also write a wrapper for standard user(s). It will check with the usertype is 
#standard and user is logged in, only then it will allow user to perform standard user functions
def standard_user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'standard'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as standard user")
            #return redirect(url_for('login', error='You need to login first as standard user'))
            return render_template('sign-in.html', error='You need to login first as standard user')    
    return wrap


@adminTools.route('/admin/viewbooking')
@login_required
@admin_required
def adminViewBooking():
                print('view all bookings')
                #print(f'EMAIL = {email}')
                print ('Welcome ', session['fullName'])
                conn = hotelDB.getConnection()
                if conn != None:           
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()         	
                    dbcursor.execute('SELECT * FROM reservations;')   
                    print('All bookings extracted successfully')
                    resRow = dbcursor.fetchall()             
                    print(f'RESERVATION = {resRow}')
                    #print(f'RESERVATION 2 = {resRow2}')
                    #print(f'RESERVATION 3 = {resRow3}')
                    conn.commit()
                    dbcursor.close()
                    conn.close()
                    return render_template('adminBooking.html', resData=resRow, userType = session['usertype'], \
                        logged_in=session['logged_in'], fullName=session['fullName'])
                else:
                    print('DB connection Error')
                    return redirect(url_for('userPage'), )


@adminTools.route('/admin/monthlybooking', methods = ['POST', 'GET'])
@login_required
@admin_required
def adminMonthlyBooking():
    if request.method == 'POST':
                reportMonth = request.form['bookingMonth']
                print(f"REPORT MONTH = {reportMonth}")
                conn = hotelDB.getConnection()
                if conn != None:           
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()         	
                    dbcursor.execute('SELECT * FROM reservations WHERE MONTH(checkInDate)=%s;', (reportMonth, ))   
                    print('All bookings extracted successfully')
                    resRow = dbcursor.fetchall()             
                    print(f'RESERVATION = {resRow}')
                    #print(f'RESERVATION 2 = {resRow2}')
                    #print(f'RESERVATION 3 = {resRow3}')
                    conn.commit()
                    dbcursor.close()
                    conn.close()
                    return render_template('adminMonthly.html', resData=resRow, userType = session['usertype'], \
                                logged_in=session['logged_in'], fullName=session['fullName'])
                

                else:
                    print('DB connection Error')
                    flash("Failed to generate monthly report!", 'error')
                    return redirect(url_for('userPage'))  


# Adding hotels
@adminTools.route('/admin/addhotelinput')
@login_required
@admin_required
def addHotelInput():
    return render_template('addHotelInput.html', userType = session['usertype'], \
                                logged_in=session['logged_in'], fullName=session['fullName'])

@adminTools.route('/admin/addsuccess', methods = ['POST', 'GET'])
@login_required
@admin_required
def addSuccess():
    if request.method == 'POST':
        print("POST COMPLETE")
        hotelCity = request.form['hotelCity']
        noofRooms = request.form['noofRooms']
        peakPrice = request.form['peakPrice']
        offpeakPrice = request.form['offpeakPrice']
        print(f"PEAK PRICE = {peakPrice}")
        print(f"OFFPEAK PRICE = {offpeakPrice}")

        if int(peakPrice) > int(offpeakPrice):
            conn = hotelDB.getConnection()
            if conn != None:
                print("MySQL connected!")
                dbcursor = conn.cursor()
                dbcursor.execute('SELECT hotelCity FROM hotels WHERE hotelCity = %s;', (hotelCity, ))
                hotelRow = dbcursor.fetchall()

                if dbcursor.rowcount < 1: # no hotel in the same city
                    dbcursor.execute('INSERT INTO hotels (hotelCity, numberOfRooms, peakPrice, offpeakPrice) \
                                        VALUES (%s, %s, %s, %s)', (hotelCity, noofRooms, peakPrice, offpeakPrice, ))
                    print("Inserted hotel into database successfully!")
                    conn.commit()
                    dbcursor.close()
                    conn.close()

                    flash("Added hotel into database successfully!", 'info')
                    return redirect(url_for('userPage'))
                    
                else:
                    flash("Hotel already exists!")
                    return redirect(url_for('adminTools.addHotelInput'))
            
            else:
                print("DB connection error!")
                flash("Error connecting to database!", 'error')
                return redirect(url_for('adminTools.addHotelInput'))
        
        else:
            print("Off peak price should be lower than peak price!")
            flash("Off-peak price should be lower than peak price!", 'warning')
            return redirect(url_for('adminTools.addHotelInput'))
    
    else:
        print("NO POST")
        flash("Form did not post", 'error')
        return redirect(url_for('adminTools.addHotelInput'))

# View Hotels
@adminTools.route('/admin/viewhotel')
@login_required
@admin_required
def adminViewHotel():
                print('view all hotels')
                #print(f'EMAIL = {email}')
                print ('Welcome ', session['fullName'])
                conn = hotelDB.getConnection()
                if conn != None:           
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()         	
                    dbcursor.execute('SELECT * FROM hotels;')   
                    print('All hotels extracted successfully')
                    hotelRow = dbcursor.fetchall()             
                    print(f'HOTELS = {hotelRow}')
                    #print(f'RESERVATION 2 = {resRow2}')
                    #print(f'RESERVATION 3 = {resRow3}')
                    conn.commit()
                    dbcursor.close()
                    conn.close()
                    return render_template('adminViewHotel.html', hotelData=hotelRow, userType = session['usertype'], \
                        logged_in=session['logged_in'], fullName=session['fullName'])

@adminTools.route('/deletehotel/<deleteHotelCity>', methods=['POST', 'GET'])
@login_required
@admin_required
def deleteHotel(deleteHotelCity):
        if request.method == 'POST':
            print('POST RECEIVED')
            conn = hotelDB.getConnection()
            if conn != None:    #Checking if connection is None         
                print('MySQL Connection is established')
                dbcursor = conn.cursor()
                dbcursor.execute('DELETE FROM hotels WHERE hotelCity = %s', (deleteHotelCity, ))

                conn.commit()
                dbcursor.close()
                conn.close()

                flash(f"{deleteHotelCity} hotel removed from database!", 'info')
                return redirect(url_for('userPage'))

            else:
                print("SQL connection error")
                flash("Error connecting to database!", 'error')
                return redirect(url_for('adminTools.adminViewHotel'))

        else:
            flash("Could not remove at this time!", 'error')
            return redirect(url_for('adminTools.adminViewHotel'))



@adminTools.route('/admin/viewupdatehotel', methods=['POST', 'GET'])
@login_required
@admin_required
def viewUpdateHotel():
                print('view all hotels')
                #print(f'EMAIL = {email}')
                print ('Welcome ', session['fullName'])
                conn = hotelDB.getConnection()
                if conn != None:           
                    print('MySQL Connection is established')                          
                    dbcursor = conn.cursor()         	
                    dbcursor.execute('SELECT * FROM hotels;')   
                    print('All hotels extracted successfully')
                    hotelRow = dbcursor.fetchall()             
                    print(f'HOTELS = {hotelRow}')
                    #print(f'RESERVATION 2 = {resRow2}')
                    #print(f'RESERVATION 3 = {resRow3}')
                    conn.commit()
                    dbcursor.close()
                    conn.close()
                    return render_template('adminViewUpdate.html', hotelData=hotelRow, userType = session['usertype'], \
                        logged_in=session['logged_in'], fullName=session['fullName'])

@adminTools.route('/admin/updatehotelinput/<oldHotelCity>')
@login_required
@admin_required
def updateHotelInput(oldHotelCity):
    flash(f"Input new data for {oldHotelCity} hotel", 'info')
    return render_template('updateHotelInput.html', oldHotelCity=oldHotelCity, userType = session['usertype'], \
                                logged_in=session['logged_in'], fullName=session['fullName'])


@adminTools.route('/admin/updatesuccess/<oldHotelCity>', methods = ['POST', 'GET'])
@login_required
@admin_required
def updateSuccess(oldHotelCity):
    if request.method == 'POST':
        print("POST COMPLETE")
        noofRooms = request.form['noofRooms']
        peakPrice = request.form['peakPrice']
        offpeakPrice = request.form['offpeakPrice']
        #print(f"PEAK PRICE = {peakPrice}")
        #print(f"OFFPEAK PRICE = {offpeakPrice}")


        if int(peakPrice) > int(offpeakPrice):
            conn = hotelDB.getConnection()
            if conn != None:
                print("MySQL connected!")
                dbcursor = conn.cursor()

                dbcursor.execute('UPDATE hotels \
                        SET numberOfRooms = %s, peakPrice = %s, offpeakPrice = %s \
                            WHERE hotelCity = %s;', (noofRooms, peakPrice, offpeakPrice, oldHotelCity, ))
                print("Inserted hotel into database successfully!")
                conn.commit()
                dbcursor.close()
                conn.close()

                flash("Updated hotel successfully!", 'info')
                return redirect(url_for('userPage'))
                    
            
            else:
                print("DB connection error!")
                flash("Error connecting to database!", 'error')
                return redirect(url_for('adminTools.viewUpdateHotel'))
        
        else:
            print("Off peak price should be lower than peak price!")
            flash("Off-peak price should be lower than peak price!", 'warning')
            return redirect(url_for('adminTools.viewUpdateHotel'))
    
    else:
        print("NO POST")
        flash("Form did not post", 'error')
        return redirect(url_for('adminTools.viewUpdateHotel'))







