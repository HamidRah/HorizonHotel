
# Hamidur Rahman: 20009146
import email
from pyexpat.errors import messages
from flask import Flask, render_template, request, session, make_response, url_for, redirect, flash
from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps
import hotelDB, mysql.connector
from datetime import datetime, date, time, timedelta
from dateutil.parser import parse
from adminTools import adminTools

app = Flask(__name__)   #instatntiating flask app
app.secret_key = 'Secret Key'
app.register_blueprint(adminTools, url_prefix="")

date_format = "%Y-%m-%d"

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


# / is what the url ends with e.g. /index would mean url ends with /index
@app.route('/')
@app.route('/index')         #Decorator / route
def home():
	conn = hotelDB.getConnection()
	if conn != None:    #Checking if connection is None         
		print('MySQL Connection is established')                          
		dbcursor = conn.cursor()    #Creating cursor object            
		dbcursor.execute('SELECT DISTINCT hotelCity FROM hotels;')   		           
		cityRows = dbcursor.fetchall()  #grab all data
		dbcursor.execute('SELECT DISTINCT roomType FROM roomtypes;')   		           
		roomRows = dbcursor.fetchall()                                  
		dbcursor.close()              
		conn.close() #Connection must be closed
		cities = []				#list of all cities where hotels can be booked
		for city in cityRows:		#as we used fetchall we must clean the data(remove punctuation)
			city = str(city).strip("(")
			city = str(city).strip(")")
			city = str(city).strip(",")
			city = str(city).strip("'")
			cities.append(city)
    
		roomTypes = []				#list of all cities where hotels can be booked
		for roomType in roomRows:		#as we used fetchall we must clean the data(remove punctuation)
			roomType = str(roomType).strip("(")
			roomType = str(roomType).strip(")")
			roomType = str(roomType).strip(",")
			roomType = str(roomType).strip("'")
			roomTypes.append(roomType)

        
		return render_template('index.html', hotelCitylist=cities, roomTypelist=roomTypes)
	else:
		print('DB connection Error')
		return 'DB Connection Error'


@app.route('/index/user')
def mainpage():
	conn = hotelDB.getConnection()
	if conn != None:    #Checking if connection is None         
		print('MySQL Connection is established')                          
		dbcursor = conn.cursor()    #Creating cursor object            
		dbcursor.execute('SELECT DISTINCT hotelCity FROM hotels;')   		           
		cityRows = dbcursor.fetchall()  #grab all data
		dbcursor.execute('SELECT DISTINCT roomType FROM roomtypes;')   		           
		roomRows = dbcursor.fetchall()                                  
		dbcursor.close()              
		conn.close() #Connection must be closed
		cities = []				#list of all cities where hotels can be booked
		for city in cityRows:		#as we used fetchall we must clean the data(remove punctuation)
			city = str(city).strip("(")
			city = str(city).strip(")")
			city = str(city).strip(",")
			city = str(city).strip("'")
			cities.append(city)
    
		roomTypes = []				#list of all cities where hotels can be booked
		for roomType in roomRows:		#as we used fetchall we must clean the data(remove punctuation)
			roomType = str(roomType).strip("(")
			roomType = str(roomType).strip(")")
			roomType = str(roomType).strip(",")
			roomType = str(roomType).strip("'")
			roomTypes.append(roomType)

        
		return render_template('accountIndex.html', hotelCitylist=cities, roomTypelist=roomTypes, fullName=session['fullName'], userType = session['usertype'], \
			logged_in=session['logged_in'], email=session['email'])
	else:
		print('DB connection Error')
		return 'DB Connection Error'


# register page
@app.route('/register/', methods=['POST', 'GET'])
def register():
		error = ''
		print('Register start')
		try:
			if request.method == "POST":       
				fullName = request.form['fullName']
				email = request.form['email']
				password = request.form['password']                      
				if fullName != None and email != None and password != None:           
					conn = hotelDB.getConnection()
					if conn != None:    #Checking if connection is None           
						if conn.is_connected(): #Checking if connection is established
							print('MySQL Connection is established')                          
							dbcursor = conn.cursor()    #Creating cursor object 
							#here we should check if email already exists                                                           
							password = sha256_crypt.hash((str(password)))           
							verify_EmailQuery = "SELECT * FROM users WHERE email = %s;"
							dbcursor.execute(verify_EmailQuery,(email,))
							rows = dbcursor.fetchall()           
							if dbcursor.rowcount > 0:   #this means there is a user with same email
								print('email already taken, please choose another')
								error = "User name already taken, please choose another"
								return render_template("register.html", error=error)    
							else:   #this means we can add new user             
								dbcursor.execute("INSERT INTO users (fullName, email, \
									passwordHash) VALUES (%s, %s, %s)", (fullName, email, password))                
								conn.commit()  #saves data in database              
								print("Thanks for registering!")
								dbcursor.close()
								conn.close()
								gc.collect()                        
								session['logged_in'] = True     #session variables
								session['email'] = email
								session['usertype'] = 'standard'   #default all users are standard
								session['fullName'] = fullName
								flash("Registered successfully!", 'info')
								flash("Only your full name and email will be stored. Password is hashed and never stored", 'info')
								return redirect(url_for('mainpage'))

						else:                        
							print('Connection error')
							return 'DB Connection Error'
					else:                    
						print('Connection error')
						return 'DB Connection Error'
				else:                
					print('empty parameters')
					return render_template("register.html", error=error)
			else:            
				return render_template("register.html", error=error)        
		except Exception as e:                
			return render_template("register.html", error=e)    

	

@app.route('/signin', methods=['POST', 'GET'])
def signin():
		form={}
		try:	
			if request.method == "POST":            
				email = request.form['email']
				password = request.form['password']            
				form = request.form
				print('login start')
				
				if email != None and password != None:  #check if un or pw is none          
					conn = hotelDB.getConnection()
					if conn != None:    #Checking if connection is None                    
						if conn.is_connected(): #Checking if connection is established                        
							print('MySQL Connection is established')                          
							dbcursor = conn.cursor()    #Creating cursor object                                                 
							dbcursor.execute("SELECT passwordHash, userType, fullName FROM users WHERE email = %s;", (email,))                                                
							data = dbcursor.fetchone()
							print(data[0])
							print(data[1])
							print(data[2])
							dbcursor.close()
							conn.close()
							if dbcursor.rowcount < 1: #this mean no user exists                         
								flash("Email/Password does not exist!", 'error')
								return render_template("sign-in.html")
							else:                            
								#data = dbcursor.fetchone()[0] #extracting password   
								# verify passoword hash and password received from user                                                             
								if sha256_crypt.verify(request.form['password'], str(data[0])):                                
									session['logged_in'] = True     #set session variables
									session['email'] = request.form['email']
									session['usertype'] = str(data[1])
									session['fullName'] = str(data[2])                          
									print("You are now logged in")
									flash("Logged in successfully!", 'info')
									flash("Only your full name and email will be stored. Password is hashed and never stored", 'info')                                
									return redirect(url_for('mainpage'))
								else:
									flash("Invalid credentials!", 'error')                               
						gc.collect()
						print('login start')
						return render_template("sign-in.html", form=form)
		except Exception as e:                
			flash(f"Error: Invalid Credentials!", 'error')
			return render_template("sign-in.html", form=form)   
		
		return render_template("sign-in.html", form=form)

@app.route("/logout")
@login_required
def logout():    
		session.clear()    #clears session variables
		print("You have been logged out!")
		gc.collect()
		flash("Logged out successfuly!", 'info')
		return redirect(url_for('home'))


@app.route('/usersettings')
@login_required
def userPage():
			print('fetchrecords')
			userType = session['usertype']
			print(f'USER TYPE = {userType}')
			#records from database can be derived
			#user login can be checked..
			print ('Welcome ', session['fullName'])
			return render_template('userPage.html', \
				fullName=session['fullName'], userType = session['usertype'], \
				logged_in=session['logged_in'])

@app.route('/selectbooking', methods=['POST', 'GET'])
@login_required
def selectBooking():
	if request.method == 'POST':
		#print('Select booking initiated')
		hotelCity = request.form['hotelCitylist']
		#arrivalcity = request.form['arrivalslist']
		checkin = request.form['checkin']
		checkout = request.form['checkout']
		adults = request.form['adult']
		children = request.form['children']
		roomType = request.form['roomTypelist']
		noofguests = int(adults) + int(children)				
		noofDays = datetime.strptime(checkout, date_format) - datetime.strptime(checkin, date_format)		
		lookupdata = [hotelCity, checkin, checkout, noofguests, noofDays.days, roomType, session['email']]		
		conn = hotelDB.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object            
			dbcursor.execute('SELECT * FROM hotels WHERE hotelCity = %s;', (hotelCity, ))   
			#	print('SELECT statement executed successfully.')             
			hotelsRows = dbcursor.fetchall()
			dbcursor.execute('SELECT * FROM roomtypes WHERE roomType = %s;', (roomType, ))
			roomtypeRow = dbcursor.fetchall()
			datarows=[]
			#print('RoomType = ', roomtypeRow)

			for roomtypeData in roomtypeRow:	
				percentofRooms = roomtypeData[1]
				pricePercentage = roomtypeData[2]
				maxPeople = roomtypeData[3]
			
			for hotelsData in hotelsRows:
				noofRooms = hotelsData[1]
				peakPrice = hotelsData[2]
				offpeakPrice = hotelsData[3]


			#print(peakPrice)
			# converting dates to datetime format
			checkinDatetime = parse(checkin)
			checkoutDatetime = parse(checkout)
			todayDatetime = datetime.today()
			timeDelta = checkinDatetime - todayDatetime
			#print(checkinDatetime.month)
			#print(noofDays.days)
			#Now here you can apply business logic. For demo purposes I'll keep it simple
			for bookingData in hotelsRows:
				data = list(bookingData)
				# can only book upto 3 months in advance
				if timeDelta.days <= 90:
					# Cannot exceed max capacity
					if noofguests <= maxPeople:
						# Must have more than 1 room left
						if (percentofRooms) * (noofRooms) > 0:
							# check if between April and September for peak prices
							if ((checkinDatetime.month) and (checkoutDatetime.month) >= 4) and ((checkinDatetime.month) and (checkoutDatetime.month) <= 9):
								# check if booked between 80 and 90 days
								if (timeDelta.days >= 80) and (timeDelta.days <= 90):
									# check for double and another guest and charge 10% of standard room price
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (peakPrice * pricePercentage * noofguests * noofDays.days * 0.8) + (peakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  peakPrice * pricePercentage * noofguests * noofDays.days * 0.8
										data.append(totalPrice)
										datarows.append(data)
								
								elif (timeDelta.days >= 60) and (timeDelta.days <= 79):
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (peakPrice * pricePercentage * noofguests * noofDays.days * 0.9) + (peakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  peakPrice * pricePercentage * noofguests * noofDays.days * 0.9
										data.append(totalPrice)
										datarows.append(data)
								
								elif (timeDelta.days >= 45) and (timeDelta.days <= 59):
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (peakPrice * pricePercentage * noofguests * noofDays.days * 0.95) + (peakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  peakPrice * pricePercentage * noofguests * noofDays.days * 0.95
										data.append(totalPrice)
										datarows.append(data)
								
								else:
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (peakPrice * pricePercentage * noofguests * noofDays.days) + (peakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  peakPrice * pricePercentage * noofguests * noofDays.days
										data.append(totalPrice)
										datarows.append(data)
							
							# off peak prices
							else:
								# check if booked between 80 and 90 days
								if (timeDelta.days >= 80) and (timeDelta.days <= 90):
									# check for double and another guest and charge 10% of standard room price
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (offpeakPrice * pricePercentage * noofguests * noofDays.days * 0.8) + (offpeakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)										
									else:
										totalPrice =  offpeakPrice * pricePercentage * noofguests * noofDays.days * 0.8
										data.append(totalPrice)
										datarows.append(data)

								elif (timeDelta.days >= 60) and (timeDelta.days <= 79):
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (offpeakPrice * pricePercentage * noofguests * noofDays.days * 0.9) + (offpeakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  offpeakPrice * pricePercentage * noofguests * noofDays.days * 0.9
										data.append(totalPrice)
										datarows.append(data)

								elif (timeDelta.days >= 45) and (timeDelta.days <= 59):
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (offpeakPrice * pricePercentage * noofguests * noofDays.days * 0.95) + (offpeakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  offpeakPrice * pricePercentage * noofguests * noofDays.days * 0.95	
										data.append(totalPrice)
										datarows.append(data)
								else:
									if (roomType == 'Double') and noofguests == 2:
										totalPrice = (offpeakPrice * pricePercentage * noofguests * noofDays.days) + (offpeakPrice * 0.1)
										data.append(totalPrice)
										datarows.append(data)
									else:
										totalPrice =  offpeakPrice * pricePercentage * noofguests * noofDays.days
										data.append(totalPrice)
										datarows.append(data)

								
						else:
							flash(f'No more {roomType} rooms from {hotelCity}!', 'error')
							return redirect(url_for('mainpage'))
					
					else:
						flash(f'Number of guests exceeds {roomType} room maximum capacity!', 'error')
						return redirect(url_for('mainpage'))
				
				else:
					flash('Can only book upto 3 months in advance!', 'error')
					return redirect(url_for('mainpage'))
			
			print(f'Total price is {totalPrice}')
			#print(f'Time delta ')
			lookupdata.append(int(noofRooms * percentofRooms))
			lookupdata.append(totalPrice)
			print(datarows)
			print(lookupdata)
			dbcursor.close()              
			conn.close() #Connection must be closed			
			return render_template('selectBooking.html', resultset=datarows, lookupdata=lookupdata)
		else:
			print('DB connection Error')
			return redirect(url_for('mainpage'))
	else:
		return redirect(url_for('mainpage'))

@app.route('/confirmbooking', methods=['POST', 'GET'])
@login_required
def confirmBooking():
	if request.method == 'POST':
		email = request.form['email']
		hotelCity = request.form['hotelCity']
		roomType = request.form['roomType']
		checkin = request.form['checkin']
		checkout = request.form['checkout']
		totalPrice = request.form['totalPrice']
		noofGuests = request.form['noofGuests']

		conn = hotelDB.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object     	
			dbcursor.execute('SELECT numberofRooms FROM hotels WHERE hotelCity = %s;', (hotelCity, ))
			noofRoomsrow = dbcursor.fetchone()
			
			for noofRooms in noofRoomsrow:		
				noofRooms = str(noofRooms).strip("(")

			updateNoofRooms = int(noofRooms) - 1
			print(f'NUMBER OF ROOMS = {updateNoofRooms}')
			
			dbcursor.close()
			conn.close()

		resData = [email, hotelCity, roomType, checkin, checkout, totalPrice, noofGuests]
		
		#Now we need to save booking data in DB
		conn = hotelDB.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object     	
			dbcursor.execute('INSERT INTO reservations (email, hotelCity, roomType, checkInDate, checkOutDate, totalPrice, numberofPeople) VALUES \
				(%s, %s, %s, %s, %s, %s, %s);', (email, hotelCity, roomType, checkin, checkout, totalPrice, noofGuests))   
			print('Booking statement executed successfully.') 
			dbcursor.execute('UPDATE hotels SET numberofRooms = numberofRooms-1 WHERE hotelCity = %s;', (hotelCity, ))            
			conn.commit()	
			
			#As res id is autogenerated so we can get it by running following SELECT
			dbcursor.execute('SELECT LAST_INSERT_ID();')			
			rows = dbcursor.fetchone()			
			resID = rows[0]
			resData.append(resID)

			dbcursor.execute('UPDATE hotels SET numberofRooms = numberofRooms-1 WHERE hotelCity = %s;', (hotelCity, ))
			print('Rooms updated successfully!')
			dbcursor.close()              
			conn.close()
			flash('Reservation successful!', 'info')
			return redirect(url_for('mainpage'))
		else:
			print('DB connection Error')
			return redirect(url_for('mainpage'))

@app.route('/viewbooking')
@login_required
def viewBooking():
			print('view Booking')
			userType = session['usertype']
			email = session['email']
			print(f'EMAIL = {email}')
			#records from database can be derived
			#user login can be checked..
			print ('Welcome ', session['fullName'])
			conn = hotelDB.getConnection()
			if conn != None:    #Checking if connection is None         
				print('MySQL Connection is established')                          
				dbcursor = conn.cursor()    #Creating cursor object     	
				dbcursor.execute('SELECT * FROM reservations WHERE email = %s;', (email, ))   
				print('Reservation extraction executed successfully.')
				resRow = dbcursor.fetchall()             
				print(f'RESERVATION = {resRow}')
				#print(f'RESERVATION 2 = {resRow2}')
				#print(f'RESERVATION 3 = {resRow3}')
			
				return render_template('userBooking.html', resData=resRow, userType = session['usertype'], \
					logged_in=session['logged_in'], fullName=session['fullName'])
			else:
				print('DB connection Error')
				return redirect(url_for('userPage'))

@app.route('/cancelbooking/<cancelResID>', methods=['POST', 'GET'])
@login_required
def cancelBooking(cancelResID):
	if request.method == 'POST':
		userType=session['usertype']
		print('POST RECEIVED')
		conn = hotelDB.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object     	
			dbcursor.execute('SELECT * FROM reservations WHERE reservationID = %s;', (cancelResID, ))
			cancelResRow = dbcursor.fetchall()

			for resItem in cancelResRow:
				checkin = resItem[4]
				totalPrice = resItem[6]
			#print(f'BOOKING DATE = {checkin}')
			todayDate = date.today()
			timeDelta = checkin - todayDate
			print(f'TIME DELTA = {timeDelta.days}')

			if timeDelta.days > 60:
				cancelPrice = 0
			
			elif (timeDelta.days >= 30) and (timeDelta.days <= 60):
				cancelPrice = totalPrice * 0.5

			else:
				cancelPrice = totalPrice
			conn.commit()
			dbcursor.close()
			conn.close() 	           	
		return render_template('cancelBooking.html', resID=cancelResID, cancelPrice=cancelPrice, userType=session['usertype'])
	else:
		print('DB connection Error')
	flash('Delete not possible at the moment!', 'error')
	return redirect(url_for('viewBooking'))

@app.route('/confirmcancel/<cancelResID>', methods=['POST', 'GET'])
@login_required
def confirmCancel(cancelResID):
	if request.method == 'POST':
		print('POST RECEIVED')
		conn = hotelDB.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()
			
			dbcursor.execute('SELECT hotelCity FROM reservations WHERE reservationID = %s;', (cancelResID, ))
			hotelCityrow = dbcursor.fetchone()
			for hotelItem in hotelCityrow:
				hotelCity = str(hotelItem)

			dbcursor.execute('DELETE FROM reservations WHERE reservationID = %s;', (cancelResID, ))
    	
			print(f'CANCELLED HOTEL = {hotelCity}')
			dbcursor.execute('UPDATE hotels SET numberofRooms = numberofRooms+1 WHERE hotelCity = %s;', (hotelCity, ))
			
			conn.commit()
			dbcursor.close()
			conn.close() 
			print('Removal executed successfully.')
				           	
		flash(f'Reservation {cancelResID} cancelled successfully!', 'info')
		return redirect(url_for('viewBooking'))
	else:
		print('DB connection Error')
		flash('Delete not possible at the moment!', 'error')
		return redirect(url_for('viewBooking'))


@app.route('/changepassword')
@login_required
def updatePwdInput():
    flash(f"Enter current and new password", 'info')
    return render_template('updatePasswordInput.html', userType = session['usertype'], \
                                logged_in=session['logged_in'], fullName=session['fullName'])

@app.route('/updatepwdsuccess', methods=['POST', 'GET'])
@login_required
def updatePwdSucess():
	if request.method == 'POST':
		print("POST received")
		inputOldPwd = request.form['oldpwd']
		newPwd = request.form['newpwd']
		email = session['email']

		conn = hotelDB.getConnection()
		if conn != None:
			print("MySQL connected!")
			dbcursor = conn.cursor()
			dbcursor.execute('SELECT passwordHash FROM users WHERE email = %s;', (email, ))
			oldPwd = dbcursor.fetchone()		
			oldPwd = str(oldPwd).strip("(")
			oldPwd = str(oldPwd).strip(")")
			oldPwd = str(oldPwd).strip(",")
			oldPwd = str(oldPwd).strip("'")
			#print(f"OLD PASSWORD HASH = {oldPwd}")

			if sha256_crypt.verify(inputOldPwd, oldPwd):
				newPwd = sha256_crypt.hash((str(newPwd)))
				dbcursor.execute('UPDATE users SET passwordHash = %s WHERE email = %s;', (newPwd, email,))

				conn.commit()
				dbcursor.close()
				conn.close()

				print("Password updated successfully!")
				flash(f"Password for {email} updated sucessfully", 'info')			
				return redirect(url_for('userPage'))

			
			else:
				flash("Invalid Current Password!", 'error')
				return redirect(url_for('updatePwdInput'))

		
		else:
			print("MySQL connection failed!")
			flash("Could not connect to database!", 'error')
			return redirect(url_for('userPage'))

	
	else:
		print("NO POST")
		flash("Cannot update password at this time", 'error')
		return redirect(url_for('userPage'))




#if __name__ == '__main__':   
#   app.run(debug = True)
if __name__ == '__main__':    
    for i in range(13000, 18000):
      try:
         # debug mode allows changes to be made while app is still running, only recommended while website is in development
         app.run(debug = True, port = i)
         break
      except OSError as e:
         print("Port {i} not available".format(i))