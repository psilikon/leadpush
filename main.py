from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import random
import logging
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb
import os
import csv
import time
import requests
from requests.exceptions import Timeout
import re
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from datetime import datetime




app = Flask(__name__)
app.config.from_pyfile('config.py')

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# Intialize MySQL
mysql = MySQL(app)




### - HELPER FUNCTIONS 
## 
#  

# Check file upload extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config.get('ALLOWED_EXTENSIONS')

# Import csv into the master_list table
# insert now() as INSERT_DATETIME
def import_to_table(filename, FLcheck):
	insert_ids = []
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	with open(os.path.join(app.config.get('UPLOAD_FOLDER'), filename)) as csv_file:
		csv_reader = csv.reader(csv_file, dialect='excel')
		
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count += 1
			else:
				try:
					if FLcheck == 'FLORIDA':
						cursor.execute("INSERT INTO master_list (SITUS_COUNTY, APN, ASSESSED_LAND_VALUE, LOT_AREA, LOT_ACREAGE, LAST_SALE_PRICE, OWNER1_FULL_NAME, OWNER1_LASTNAME, OWNER1_FIRSTNAME, MAIL_STREET_ADDR, MAIL_CITY, MAIL_STATE, MAIL_ZIP, LEGAL_DESC, SITUS_STREET_ADDR, SITUS_CITY, SITUS_STATE, SITUS_ZIP, FIRST_NAME, LAST_NAME, PHONE, LINE_TYPE, EMAIL, INSERT_DATETIME, VCL_PUSH_COUNT, SMS_PUSH_COUNT, EMAIL_PUSH_COUNT, VM_PUSH_COUNT, UPLOAD_FILENAME) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),0,0,0,0,%s)", (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[14],row[15],row[16],'FL',row[18],row[19],row[20],row[21],row[22],row[23], filename))

					else:						
						cursor.execute("INSERT INTO master_list (OWNER1_FULL_NAME,OWNER1_FIRSTNAME,OWNER1_LASTNAME,MAIL_STREET_ADDR,MAIL_CITY,MAIL_STATE,MAIL_ZIP,OWNER1_TYPE,SITUS_STREET_ADDR,SITUS_CITY,SITUS_STATE,SITUS_ZIP,SITUS_COUNTY,LEGAL_DESC,APN,LATITUDE,LONGITUDE,SUBDIVISION,LAND_USE,COUNTY_LAND_USE,ZONING,LOT_AREA,LOT_ACREAGE,WATER_TYPE,SEWER_TYPE,FLOOD_ZONE_CODE,ASSESSED_TOTAL_VALUE,ASSESSED_LAND_VALUE,ASSESSED_IMPROV_VALUE,MARKET_VALUE,DELINQ_TAX_VALUE,FIRST_NAME,LAST_NAME,PHONE,LINE_TYPE,EMAIL, INSERT_DATETIME, VCL_PUSH_COUNT, SMS_PUSH_COUNT, EMAIL_PUSH_COUNT, VM_PUSH_COUNT, UPLOAD_FILENAME) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),0,0,0,0,%s)", (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26],row[27],row[28],row[29],row[30],row[31],row[32],row[33],row[34],row[35], filename))

					line_count += 1

				except (MySQLdb.Error, MySQLdb.Warning) as e:
					app.logger.debug(e)
					return None
				cursor.execute("SELECT LAST_INSERT_ID() AS AUTOINC")
				result = cursor.fetchone()
				autoinc = result['AUTOINC']
				insert_ids.append(autoinc)
				app.logger.debug(str(autoinc))
		mysql.connection.commit()

		# record count is line count minus 1 for the header row
		record_count = line_count - 1

		app.logger.info("RECORD INSERT COUNT: ", str(record_count))
		first_id = min(insert_ids)
		last_id = max(insert_ids)
	return str(record_count), str(first_id), str(last_id)

# Divide record amount evenly among the selected sales agents
def chunks(num, div):
	return ([num // div + (1 if x < num % div else 0)  for x in range (div)])    

#
## 
### END HELPER FUNCTIONS 



### - ROUTES 
##
#

# LOGOUT
@app.route('/logout')
def logout():
	# Remove session data, this will log the user out
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	# Redirect to login page
	return redirect(url_for('login'))	


# FORM SUBMIT Process the data in the uploaded file when upload button is submitted
@app.route('/process_data_import', methods=['POST','GET'])
def process_data_import():
	# Check if user is loggedin
	if 'loggedin' in session:
		# We need all the account info for the user so we can display it on the profile page
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()

		if request.method == 'POST':
			app.logger.debug('Upload folder: \n')
			app.logger.debug(app.config.get('UPLOAD_FOLDER'))
			# check if the post request has the file part
			if 'file_upload' not in request.files:
				flash("No file part")
				return redirect(url_for('data_import'))
			file = request.files['file_upload']
			# If the user does not select a file, the browser submits an
			# empty file without a filename.
			if file.filename == '':
				flash("No selected file")
				return redirect(url_for('data_import'))
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config.get('UPLOAD_FOLDER'), filename))

				# set variable to differentiate import file schema
				FLcheck = request.form['FLcheck'] 

				rows_imported, first_id, last_id = import_to_table(filename, FLcheck)
				flash("Rows imported : "+rows_imported)
				flash("First master_id : "+str(first_id))
				flash("Last master_id : "+str(last_id))
				return render_template('import_report.html')
			flash("File type not allowed")
			return redirect(url_for('data_import'))
	return redirect(url_for('login'))
#
##
### - END ROUTES



### - VIEWS
##
#

# VIEW - Index 
@app.route('/', methods=['GET', 'POST'])
def login():
	# Output message if something goes wrong...
	msg = ''
	# Check if "username" and "password" POST requests exist (user submitted form)
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		# Create variables for easy access
		username = request.form['username']
		password = request.form['password']
		# Check if account exists using MySQL
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
		# Fetch one record and return result
		account = cursor.fetchone()
		# If account exists in accounts table in out database
		if account:
			# Create session data, we can access this data in other routes
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			# Redirect to home page
			return redirect(url_for('home'))
		else:
			# Account doesnt exist or username/password incorrect
			msg = 'Incorrect username/password!'
	# Show the login form with message (if any)
	return render_template('index.html', msg=msg)


# VIEW - Home
@app.route('/home')
def home():
	# Check if user is loggedin
	if 'loggedin' in session:
		# User is loggedin show them the home page
		return render_template('home.html', username=session['username'])
	# User is not loggedin redirect to login page
	return redirect(url_for('login'))	


# VIEW - Present Dataset inventory view
@app.route('/dataset_inventory')
def dataset_inventory():
	# Check if user is loggedin
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()
		# Show the profile page with account info
		return render_template('dataset_inventory.html')
	# User is not loggedin redirect to login page
	return redirect(url_for('login'))


# VIEW - Present the file upload view
@app.route('/data_import')
def data_import():
	# Check if user is loggedin
	if 'loggedin' in session:
		# We need all the account info for the user so we can display it on the profile page
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()
		# Show the profile page with account info
		return render_template('data_import.html', account=account)
	# User is not loggedin redirect to login page
	return redirect(url_for('login'))	


# VIEW - Dataset creation menu
@app.route('/create_dataset', methods=['POST','GET'])
def create_dataset():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()	
		return render_template('create_dataset.html')
	return redirect(url_for('login'))	
	

# VIEW - API endpoints
@app.route('/api_endpoints', methods=['POST','GET'])
def api_endpoints():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()
		return render_template('api_endpoints.html')
	return redirect(url_for('login'))		
	

#
##
### - END VIEWS



### - AJAX ROUTES
##
#

# AJAX - Populate dataTable on inventory page
@app.route('/populate_dataTables', methods=['POST'])
def populate_dataTables():
	if 'loggedin' in session:
		resp = {}
		
		draw = request.form['draw']
		row = request.form['start']
		rows_per_page = request.form['length']
		column_index = request.form['order[0][column]']
		column_name = request.form['columns[0][data]']
		column_sort_order = request.form['order[0][dir]']
		#search_value = request.form['search[value]']
		dataset = request.form['dataset']	
		
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT APN, SITUS_STATE, SITUS_COUNTY, LOT_ACREAGE, PHONE, LINE_TYPE, EMAIL, UPLOAD_FILENAME FROM master_list ml JOIN "+dataset+" dstable ON ml.MASTER_ID = dstable.MASTER_ID")
		results = cursor.fetchall()
		#app.logger.debug(results)
		resp['iTotalRecords'] = len(results)
		resp['draw'] = draw
		resp['aaData'] = results
		

		#return(jsonify(resp['data']))
		return(jsonify(resp))
	return redirect(url_for('login'))	


# AJAX route to populate counties based on state
@app.route('/get_county_list', methods=['POST'])
def get_county_list():
	if 'loggedin' in session:
		# We need all the account info for the user so we can display it on the profile page
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()
		json_data = request.json
		state = json_data['state_filter']
		
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		
		try:
			cursor.execute('SELECT DISTINCT(SITUS_COUNTY) FROM master_list WHERE SITUS_STATE = %s', (state,))
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			app.logger.info(e)
			return None
		
		result = cursor.fetchall()
		data = jsonify(result)
		return(data)
	return redirect(url_for('login'))


# AJAX ON Document Ready (create_dataset view)
@app.route('/get_state_list', methods=['POST'])
def get_state_list():
	if 'loggedin' in session:
		# We need all the account info for the user so we can display it on the profile page
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
		account = cursor.fetchone()
		
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

		try:
			cursor.execute('SELECT DISTINCT(SITUS_STATE) FROM master_list')
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			app.logger.info(e)
			return None

		result = cursor.fetchall()
		data = jsonify(result)
		return(data)
	return("Jank")	


# AJAX for calculate button. Show 'WRITE' button if call is successfull
@app.route('/filter_query', methods=['POST'])
def filter_query():
	if 'loggedin' in session:
		# We need all the account info for the user so we can display it on the profile page
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		response = {}
		json_data = request.json
		app.logger.debug(json_data)

		

		# Filter SQL fragement to concat to
		filter_sql_query = """SELECT MASTER_ID FROM master_list WHERE MASTER_ID != 0 """
		json_data = request.json

		if 'filename_filter' in json_data:
			filter_sql_query += "AND UPLOAD_FILENAME = '%s' " % (json_data['filename_filter'])
		if 'state_filter' in json_data:
			filter_sql_query += "AND UPPER(SITUS_STATE) = '%s' " % (json_data['state_filter'])
		if 'county_filter' in json_data:
			filter_sql_query += "AND UPPER(SITUS_COUNTY) = '%s' " % (json_data['county_filter'])
		if 'linetype_filter' in json_data:
			filter_sql_query += "AND UPPER(LINE_TYPE) = '%s' " % (json_data['linetype_filter'])
		if 'phone_filter' in json_data and json_data['phone_filter'] == 'POPULATED':	
			filter_sql_query += "AND LENGTH(PHONE) = 10 "
		if 'phone_filter' in json_data and json_data['phone_filter'] == 'EMPTY':				
			filter_sql_query += "AND LENGTH(PHONE) != 10 "
		if 'lot_acreage_filter_min' in json_data and 'lot_acreage_filter_max' not in json_data:
			filter_sql_query += "AND LOT_ACREAGE >= %s " % (json_data['lot_acreage_filter_min'])
		if 'lot_acreage_filter_max' in json_data and 'lot_acreage_filter_min' not in json_data:
			filter_sql_query += "AND LOT_ACREAGE <= %s " % (json_data['lot_acreage_filter_max'])
		if 'lot_acreage_filter_min' in json_data and 'lot_acreage_filter_max' in json_data:			
			filter_sql_query += "AND LOT_ACREAGE >= %s AND LOT_ACREAGE <= %s " % (json_data['lot_acreage_filter_min'], json_data['lot_acreage_filter_max'])
		if 'dialer_api_count' in json_data:
			filter_sql_query += "AND VCL_PUSH_COUNT = %s " % (json_data['dialer_api_count'])
		if 'email_api_count' in json_data:
			filter_sql_query += "AND EMAIL_PUSH_COUNT = %s " % (json_data['email_api_count'])
		if 'sms_api_count' in json_data:
			filter_sql_query += "AND SMS_PUSH_COUNT = %s " % (json_data['sms_api_count'])
		if 'vm_api_count' in json_data:
			filter_sql_query += "AND VM_PUSH_COUNT = %s " % (json_data['vm_api_count'])

		filter_sql_query += "ORDER BY RAND() LIMIT %s" % (json_data['record_quantity'])
		
		app.logger.debug("Query: "+filter_sql_query+"\n")
		
		try:
			cursor.execute(filter_sql_query)
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			app.logger.info("Error: \n")
			app.logger.info(e)
			return None
		
		else:
			result = cursor.fetchall()
			response['RESULTS'] = result
			app.logger.debug(result)
			app.logger.debug("Rows matching query: "+ str(len(result)))
			response['ROW_COUNT'] = len(result)
			response['QUERY'] = filter_sql_query
			return(jsonify(response))
	return("Jank")	


# AJAX for calculate button BY IDS. Show 'WRITE' button if call is successfull
@app.route('/filter_query_by_ids', methods=['POST'])
def filter_query_by_ids():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		json_data = request.json

		response = {}

		# Filter SQL 
		filter_sql_query = "SELECT MASTER_ID FROM master_list WHERE MASTER_ID >= %s AND MASTER_ID <= %s" % (json_data['START'], json_data['END'])
		
		try:
			cursor.execute(filter_sql_query)
			result = cursor.fetchall()
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			app.logger.info(e)
			return None
		
		
		response['RESULTS'] = result
		response['ROW_COUNT'] = len(result)
		response['QUERY'] = filter_sql_query
		return(jsonify(response))
	return("Jank")		


#AJAX to create dataset DS_epoch
@app.route('/write_dataset', methods=['POST'])
def write_dataset():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		response = {}
		json_data = request.json
		app.logger.debug(json_data)
		
		IDs = json_data['MASTER_IDS']
		SQL_QUERY = json_data['QUERY']
		DS_ROWCOUNT = json_data['ROW_COUNT']
		table_name = 'DS_'+str(int(time.time()) )
		
		try:
			cursor.execute("CREATE TABLE "+table_name+" (MASTER_ID VARCHAR(50) DEFAULT NULL COLLATE 'utf8mb4_general_ci')")
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			app.logger.info(e)
		try:
			cursor.execute("INSERT IGNORE INTO DATASETS (DATASET_ID, SQL_QUERY, ROW_COUNT) VALUES (%s, %s, %s)", (str(table_name), str(SQL_QUERY), str(DS_ROWCOUNT) )
				)
		except (MySQLdb.Error, MySQLdb.Warning) as e:
			app.logger.info(e)			
		for i in IDs:
			try:
				cursor.execute("INSERT IGNORE INTO "+table_name+" (MASTER_ID) VALUES ("+str(i['MASTER_ID'])+")")
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				app.logger.info(e)

		mysql.connection.commit()
		response['DATASET'] = table_name
		return(jsonify(response))
	return("JANK")


#AJAX to return all DS tables
@app.route('/get_datasets', methods=['POST'])
def get_datasets():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT DATASET_ID FROM DATASETS")
		results = cursor.fetchall()
		return(jsonify(results))
	return("JANK")		


#AJAX to get distinct imported filenames
@app.route('/get_imported_filenames', methods=['POST'])
def get_imported_filenames():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT UPLOAD_FILENAME, MAX(INSERT_DATETIME) AS UPLOAD_DATETIME FROM master_list GROUP BY UPLOAD_FILENAME")
		results = cursor.fetchall()
		return(jsonify(results))
	return("JANK")


#AJAX get dataset details
@app.route('/get_dataset_details', methods=['POST'])
def get_dataset_details():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		json_data = request.json
		ds = json_data['dataset']

		results = {}

		cursor.execute("SELECT DATASET_ID, CREATION_DATE, ROW_COUNT, SQL_QUERY FROM DATASETS WHERE DATASET_ID = %s", [ds])
		ds_res = cursor.fetchone()
		
		results['CREATION_DATE'] = ds_res['CREATION_DATE']
		results['DATASET_ID'] = ds_res['DATASET_ID']
		results['ROW_COUNT'] = ds_res['ROW_COUNT'] 
		results['SQL_QUERY'] = ds_res['SQL_QUERY']
		return(jsonify(results))
	return("JANK")			


### - EXTERNAL APIs (VICIDIAL)
##
#

# VICIDIAL API
@app.route('/push_to_vicidial', methods=['POST'])
def push_to_vicidial():
	if 'loggedin' in session:
		route_response = {}
		json_data = request.json
		ds = json_data['dataset']
		ds_split = ds.split("_")
		list_id = ds_split[1]
		list_name = ds
		vicidial_duplicate_check = "DUPLIST"

		app.logger.debug("json_data: \n")
		app.logger.debug(json_data)

		### - Create Vicidial List using Vicidial NON-AGENT API
		post_url_query = app.config.get('VICIDIAL_API_URL')+"?source=%s&user=%s&pass=%s&function=add_list&list_id=%s&list_name=%s&campaign_id=%s" % (app.config.get('VICIDIAL_API_SOURCE'), app.config.get('VICIDIAL_API_USER'), app.config.get('VICIDIAL_API_PASS'), list_id, list_name, app.config.get('VICIDIAL_API_CAMPAIGN'))
		payload = {}
		headers = {}

		try:
			response = requests.request("POST", post_url_query, headers=headers, data=payload, timeout=120)
		except Timeout:
			app.logger.info("VICIDIAL API TIMEOUT!")
			return None
		
		vicidial_api_res = response.text
		app.logger.info(vicidial_api_res)

		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT MASTER_ID FROM "+ds)
		master_ids = [item['MASTER_ID'] for item in cur.fetchall()]

		cur.execute("SELECT MASTER_ID, SUBSTRING(PHONE,1,3) AS AREACODE, OWNER1_FIRSTNAME AS first_name, OWNER1_LASTNAME AS last_name, SITUS_STATE AS state, SITUS_COUNTY AS vendor_lead_code, LOT_ACREAGE AS title, PHONE AS phone_number, LEGAL_DESC AS comments FROM master_list WHERE MASTER_ID IN %s AND LENGTH(PHONE) = 10", [master_ids])
		results = cur.fetchall()
		
		error_count = 0
		success_count = 0
		vcl_lead_id = "none"
		for result in results:
			master_id = result['MASTER_ID']
			first_name = result['first_name']
			last_name = result['last_name']
			state = result['state']
			vendor_lead_code =  result['vendor_lead_code']
			title = result['title']
			phone_number = result['phone_number']
			comments = re.sub(r'[^a-zA-Z0-9 ]','',result['comments'])

			post_url_query = app.config.get('VICIDIAL_API_URL')+"?source=%s&user=%s&pass=%s&function=add_lead&list_id=%s&duplicate_check=%s&first_name=%s&last_name=%s&state=%s&vendor_lead_code=%s&title=%s&phone_number=%s&comments=%s" % (app.config.get('VICIDIAL_API_SOURCE'), app.config.get('VICIDIAL_API_USER'), app.config.get('VICIDIAL_API_PASS'), list_id, vicidial_duplicate_check, first_name, last_name, state, vendor_lead_code, title, phone_number, comments)
			app.logger.debug(post_url_query)			
			payload = {}
			headers = {}

			try:
				response = requests.request("POST", post_url_query, headers=headers, data=payload, timeout=120)
			except Timeout:
				app.logger.info("VICIDIAL API TIMEOUT!")
				return None
			
			api_resp = response.text.split(":")
			
			if api_resp[0] == 'ERROR':
				error_count += 1	
			if api_resp[0] == 'SUCCESS':
				resp_details = api_resp[1].split("|")
				vcl_lead_id = resp_details[-3]
				success_count += 1
			app.logger.debug("Vicidial API [ Success: %s, Error: %s, %s, VCL LEAD_ID: %s]" % (str(success_count), str(error_count), api_resp, str(vcl_lead_id)))
			sql = "UPDATE master_list SET VCL_PUSH_COUNT = VCL_PUSH_COUNT + 1, VCL_LEADID = '"+str(vcl_lead_id)+"', VCL_PUSH_TIME = now() WHERE MASTER_ID = "+str(master_id)+";"

			try:
				cur.execute(sql)
				mysql.connection.commit()
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				app.logger.debug(e)
				return None

		route_response['SUCCESS'] = str(success_count)
		route_response['ERROR'] = str(error_count)
		route_response['MSG'] = "COMPLETE"
		return(jsonify(route_response))
	return("YOU AINT COOL.")


# SIMPLETEXTING API
@app.route('/create_sms_lists', methods=['POST'])
def create_sms_lists():
	if 'loggedin' in session:
		agents_contacts_dict = {}
		sms_campaign_names = [] #list for the list names and campaign names that are created in simpletexting
		json_data = request.json
		app.logger.debug("json_data: \n")
		app.logger.debug(json_data)
		UPLOAD_FILENAME = 'NO_FILENAME'
		route_response = {}
		ds = json_data['ds']
		part_of_day = json_data['part_of_day']
		sms_agents_count = len(json_data['sms_agents'])
		row_count = json_data['row_count']
		agents = json_data['sms_agents']
		chunks_amount_list = chunks(row_count, sms_agents_count)

		agents_amount_dictionary = dict(zip(agents, chunks_amount_list))
		app.logger.debug("agents_amount_dictionary: \n")
		app.logger.debug(agents_amount_dictionary)
		
		
		#Assign MASTER IDs to lists
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		
		#get filename
		cursor.execute("SELECT UPLOAD_FILENAME FROM master_list WHERE MASTER_ID IN (SELECT MASTER_ID FROM "+ds+") LIMIT 1");
		res = cursor.fetchone()
		UPLOAD_FILENAME = res['UPLOAD_FILENAME']

		cursor.execute("DROP TABLE IF EXISTS used_master_ids")
		cursor.execute("CREATE TABLE used_master_ids LIKE TEMP_TEMP")
		for key, value in agents_amount_dictionary.items():
			agents_contacts_dict[key] = []
			cursor.execute("SELECT MASTER_ID FROM "+ds+" WHERE MASTER_ID NOT IN (SELECT * FROM used_master_ids) ORDER BY RAND() LIMIT "+str(value))
			results = cursor.fetchall()
			contact_list = []
			for temp_id in results:
				temp_master_id = temp_id['MASTER_ID']
				cursor.execute("INSERT INTO used_master_ids (MASTER_ID) VALUES ("+str(temp_master_id)+") ")
				mysql.connection.commit()
				contact_list.append(temp_master_id)
			agents_contacts_dict[key] = contact_list
		
		app.logger.debug("agents_contacts_dict: \n")
		app.logger.debug(agents_contacts_dict)

		#establish date data for list naming
		now = datetime.now()
		date_now_suffix = now.strftime("%Y-%m-%d_%H%M")

		#Create the lists on simple texting		
		for agent_sms_phone in agents_contacts_dict:
			payload = json.dumps({
  				"name": agent_sms_phone+"_"+date_now_suffix
			})
			
			headers = {
  				'Content-Type': 'application/json',
  				'Authorization': app.config.get('SIMPLETEXTING_TOKEN')
			}

			response = requests.request("POST", app.config.get('SIMPLETEXTING_URL')+"contact-lists", headers=headers, data=payload, timeout=120)
			app.logger.info(response.text)
			sms_campaign_names.append(agent_sms_phone+"_"+date_now_suffix)
		#end simple texting list creation

		route_response['LISTS_MSG'] = "Created lists..."

		#create the contacts and associate them with the lists created above
		for agent_sms_phone in agents_contacts_dict:					
			for id in agents_contacts_dict[agent_sms_phone]:
				list_id = agent_sms_phone+"_"+date_now_suffix
				cursor.execute("SELECT OWNER1_LASTNAME, OWNER1_FIRSTNAME, FIRST_NAME, LAST_NAME, PHONE, SITUS_COUNTY, SITUS_STATE, APN, ASSESSED_LAND_VALUE, ASSESSED_TOTAL_VALUE, LEGAL_DESC, LOT_ACREAGE, MARKET_VALUE, LAST_SALE_PRICE, SITUS_STREET_ADDR, SITUS_STATE, DELINQ_TAX_VALUE FROM master_list WHERE MASTER_ID = %s", [id])
				result = cursor.fetchone()
				
				if result['SITUS_STATE'] == "FL":
					payload = json.dumps({
						"upsert": "false",
						"listsReplacement": "false",
						"contactPhone": result['PHONE'],
						"firstName": result['OWNER1_FIRSTNAME'],
						"lastName": result['OWNER1_LASTNAME'],
						"customFields" : { 
							"County": result['SITUS_COUNTY'],
							"Address": result['SITUS_STREET_ADDR'],
							"Parcel ID": result['APN'],
							"Assessed Value" : result['ASSESSED_LAND_VALUE'],
							"Legal": result['LEGAL_DESC'],
							"Site State": result['SITUS_STATE'],
							"Acres/SQ FT": result['LOT_ACREAGE'],
							"County": result['SITUS_COUNTY'],
							"Last Sale": result['LAST_SALE_PRICE']
						},
						"listIds": [list_id]
					})
				else:
					payload = json.dumps({
						"upsert": "false",
						"listsReplacement": "false",
						"contactPhone": result['PHONE'],
						"firstName": result['FIRST_NAME'],
						"lastName": result['LAST_NAME'],
						"customFields" : { 
							"County": result['SITUS_COUNTY'],
							"Address": result['SITUS_STREET_ADDR'],
							"Parcel ID": result['APN'],
							"Assessed Value" : result['ASSESSED_TOTAL_VALUE'],
							"Legal": result['LEGAL_DESC'],
							"Acres/SQ FT": result['LOT_ACREAGE'],
							"County": result['SITUS_COUNTY'],
							"Site State": result['SITUS_STATE'],
							"Taxes Owed": result['DELINQ_TAX_VALUE'],
							"Market Value": result['MARKET_VALUE']
						},
						"listIds": [list_id]
					})

				headers = {
  				'Content-Type': 'application/json',
  				'Authorization': app.config.get('SIMPLETEXTING_TOKEN')
				}

				response = requests.request("POST", app.config.get('SIMPLETEXTING_URL')+"contacts", headers=headers, data=payload, timeout=120)
				app.logger.debug(response.text)				

				try:
					cursor.execute("UPDATE master_list SET SMS_PUSH_COUNT = SMS_PUSH_COUNT + 1, SMS_PUSH_TIME = now() WHERE MASTER_ID = "+str(id))
					#cursor.execute("UPDATE master_list SET SMS_PUSH_TIME = now() WHERE MASTER_ID = "+str(id))
					mysql.connection.commit()
					pass
				except (MySQLdb.Error, MySQLdb.Warning) as e:
					app.logger.debug(e)
					return None
		
		app.logger.debug("sms_campaign_names: \n")
		app.logger.debug(sms_campaign_names)

		templates_dict = {}
		cursor.execute("SELECT template_msg FROM simpletexting_templates WHERE part_of_day = %s", [part_of_day]) 
		templates_res = cursor.fetchall()

		row_count = 0
		for row in templates_res:
			templates_dict[row_count] = row
			row_count += 1

					
		#before random key selection the templates dictionary is pristine
		app.logger.debug("templates_dict: \n")
		app.logger.debug(templates_dict)				

		### TEST DATASET DS_1656036316  4 records
		for campaign_id in sms_campaign_names:
			campaign_title = campaign_id+"_"+UPLOAD_FILENAME
			app.logger.debug("Campaign Title: "+campaign_title+"\n")

			
			rand_templates_item = random.choice(list(templates_dict))
			#app.logger.debug("Template Index: \n")
			#app.logger.debug(str(rand_templates_item))
			msg = templates_dict[rand_templates_item]['template_msg']
			#app.logger.debug("Template msg: \n")
			#app.logger.debug(msg)

			#after random selection and removal of template by key
			del templates_dict[rand_templates_item]
			#app.logger.debug("templates_dict after key deletion: \n")
			#app.logger.debug(templates_dict)				
						
			accountPhone = campaign_id[0:10]

			campaign_payload = json.dumps({
			  "title": campaign_title,
			  "listIds": [
			    campaign_id
			  ],
			  "accountPhone": accountPhone,
			  "customFieldsMaxLength": {
				"County": "25",
				"Site State": "15"
			  },
			  "messageTemplate": {
			    "mode": "SINGLE_SMS_STRICTLY",
			    "text": msg,
			    "unsubscribeText": "",
			    "fallbackText": "Hi, my name is Robert. Are you interested in selling your land?",
			    "fallbackUnsubscribeText": "",
			    "mediaItems": [ ]
			  }
			})
			
			headers = {
  				'Content-Type': 'application/json',
  				'Authorization': app.config.get('SIMPLETEXTING_TOKEN')
			}

			
			app.logger.debug("campaign_payload: \n")
			app.logger.debug(campaign_payload)

			response = requests.request("POST", app.config.get('SIMPLETEXTING_URL')+"campaigns", headers=headers, data=campaign_payload, timeout=120)
			app.logger.debug("API response text: \n")				
			app.logger.debug(response.text+"\n")				
			
			
		route_response['CAMPAIGN_MSG'] = "Created campaigns and started sending..."
		route_response['CONTACTS_MSG'] = "Added contacts to lists..."
		return(jsonify(route_response))
	return("JANK")		


# DROP.CO API
@app.route('/vmdrop_push', methods=['POST'])
def vmdrop_push():
	if 'loggedin' in session:
		route_response = {}
		json_data = request.json
		
		drop_campaign_tokens = app.config.get('DROPCO_TOKENS')
		
		ds = json_data['dataset']		
		drop_campaign = json_data['drop_campaign']
		campaign_token = drop_campaign_tokens[drop_campaign]
		app.logger.debug("Dataset: "+ds+"\n")
		app.logger.debug("Selected Drop Campaign: "+drop_campaign+"\n")
		app.logger.debug("Campaign Token: "+campaign_token+"\n")

		cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cur.execute("SELECT MASTER_ID FROM "+ds)
		master_ids = [item['MASTER_ID'] for item in cur.fetchall()]
		cur.execute("SELECT MASTER_ID, PHONE FROM master_list WHERE MASTER_ID IN %s AND LENGTH(PHONE) = 10", [master_ids])
		results = cur.fetchall()
		success_count = 0
		for i in results:
			app.logger.debug(i)
			url = app.config.get('DROPCO_API_DELIVERY_URL')+"ApiKey="+app.config.get('DROPCO_API_KEY')+"&CampaignToken="+campaign_token+"&PhoneTo="+i['PHONE']

			app.logger.debug("URL: "+url+"\n")
			payload={}
			headers = {}

			try:
				response = requests.request("POST", url, headers=headers, data=payload)
			except:
				return False

			respj = response.json()
			ApiStatusCode = str(respj['ApiStatusCode'])
			ApiStatusMessage = respj['ApiStatusMessage']
			PhoneTo = respj['PhoneTo']
			ActivityToken = respj['ActivityToken']
			app.logger.debug('API Status Code: '+ApiStatusCode+"\n")
			app.logger.debug('API Status Msg: '+ApiStatusMessage+"\n")
			app.logger.debug('API Phone To: '+PhoneTo+"\n")
			app.logger.debug('API Activity Token: '+ActivityToken+"\n")
	
			params_tuple = (ApiStatusCode, ApiStatusMessage, ActivityToken, str(i['MASTER_ID']))
			if ApiStatusCode == '1038':
				success_count = success_count + 1
			try:
				cur.execute("UPDATE master_list SET VM_PUSH_COUNT = VM_PUSH_COUNT + 1, VM_PUSH_TIME = now(), VM_API_CODE = %s, VM_API_STATUS_MSG = %s, VM_API_ACT_TOKEN = %s WHERE MASTER_ID = %s", params_tuple)
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				app.logger.debug(e)
				return False
			mysql.connection.commit()
		route_response['SUCCESS_COUNT'] = success_count
		route_response['STATUS'] = 'COMPLETE'
		return(jsonify(route_response))
	return("NOT AUTHORIZED!")