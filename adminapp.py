from cs50 import SQL
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify, url_for
from datetime import datetime

app = Flask(__name__)

db = SQL ( "sqlite:///data.db" )

@app.route("/")
def index():
	return "add product:<a href=%s>Add Item</a>"%url_for('add_item')

@app.route("/admin/add-admin/")
def add_admin():
	username=request.form["username"].lower()
	pwd = request.form["password"]
	superuser = request.form["superuser"]
	name = request.form["name"]
	addedby = session['user']
	id = request.form["id"]
	superusers = db.execute("SELECT * FROM admins WHERE username = :addedby AND superuser = 1",addedby)
	if len(superusers)==0:
		render_template("adminlogin.html",msg="login with a super user account")
	else:  
		db.execute("INSERT INTO admins (id,username, password, superuser, name, addedby) VALUES (:id,:uname,:pwd,:su,:name,:addedby)",\
				uname=username,pwd=password,superuser=superuser,name=name,addedby=addedby,id=id)

@app.route("/admin/logged/")
def logged():
    # Get log in info from log in form
    user = request.form["username"].lower()
    pwd = request.form["password"]
    # Make sure form input is not blank and re-render log in page if blank
    if user == "" or pwd == "":
        return render_template ( "adminlogin.html", msg="Wrong username or password." )
    # Find out if info in form matches a record in user database
    query = "SELECT * FROM admin WHERE username = :user AND password = :pwd"
    rows = db.execute ( query, user=user, pwd=pwd )

    # If username and password match a record in database, set session variables
    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now( )
        session['uid'] = rows[0]["id"]
    # Redirect to Home Page
    if 'user' in session:
        return redirect ( "/" )
    # If username is not in the database return the log in page
    return render_template ( "adminlogin.html", msg="Wrong username or password." )


@app.route("/admin/item/add/")
def add_item():
	item_id=request.args.get('id')
	name=request.args.get('name')
	price=request.args.get('price')
	category=request.args.get('category')
	quantity=request.args.get('quantity')
	image=request.args.get('image_path')
	onSale=request.args.get('onSale')
	onSalePrice=request.args.get('onSalePrice')
	description=request.args.get('description')
	

	db.execute("""INSERT INTO items (id,name,price,image,onSale,onSalePrice,category,quantity,description) 
		VALUES (:id,:name,:price,:image,:onSale,:onSalePrice,:category,:quantity,:description) """,\
		id=item_id, name=name, price=price, category=category, quantity=quantity, image=image, onSale=onSale, onSalePrice=onSalePrice,description = description)

	return "done:add the image also"
	##TO-DO##
	#add image to the images directory

@app.route("/admin/item/update_quantity/")
def	update_quantity():
	item_id=request.args.get('id')
	new_quantity=request.args.get('new_quantity')
	db.execute("UPDATE items SET quantity = :new_quantity where id = :id",\
							new_quantity = new_quantity, id = item_id)

@app.route("/adin/item/delete/")
def delete_item():
	item_id = request.args.get('id')
	
	##TO-DO##
	#Delete the image from the folder

	db.execute("DELETE FROM items WHERE id = :id", id = item_id)
	return "done"


