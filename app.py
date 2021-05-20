from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify
from datetime import datetime
import razorpay
from cs50 import SQL


# # Instantiate Flask object named app
app = Flask(__name__)

# # Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Creates a connection to the database
db = SQL ( "sqlite:///data.db" )

@app.route("/")
def index():
    items = db.execute("SELECT * FROM items ORDER BY name ASC")
    itemsLen = len(items)
    # Initialize variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name having user_id=:uid",uid=session["uid"])
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        items = db.execute("SELECT * FROM items ORDER BY name ASC")
        itemsLen = len(items)
        return render_template ("index.html", shoppingCart=shoppingCart, items=items, shopLen=shopLen, itemsLen=itemsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ( "index.html", items=items, shoppingCart=shoppingCart, itemsLen=itemsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/buy/")
def buy():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected item
        id = int(request.args.get('id'))
        # Select info of selected item from database
        goods = db.execute("SELECT * FROM items WHERE id = :id", id=id)
        # Extract values from selected item record
        # Check if item is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        name = goods[0]["name"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected item into shopping cart
        db.execute("INSERT INTO cart (user_id,id, qty, name, image, price, subTotal) VALUES (:uid,:id, :qty, :name, :image, :price, :subTotal)",uid=session["uid"], id=id, qty=qty, name=name, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name having user_id=:uid",uid=session["uid"])
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Select all items for home page view
        items = db.execute("SELECT * FROM items ORDER BY name ASC")
        itemsLen = len(items)
        # Go back to home page
        return redirect("/")


@app.route("/update/")
def update():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        # Store id of the selected item
        id = int(request.args.get('id'))
        db.execute("DELETE FROM cart WHERE id = :id AND user_id=:uid", id=id, uid=session["uid"])
        # Select info of selected item from database
        goods = db.execute("SELECT * FROM items WHERE id = :id", id=id)
        # Extract values from selected item record
        # Check if item is on sale to determine price
        if(goods[0]["onSale"] == 1):
            price = goods[0]["onSalePrice"]
        else:
            price = goods[0]["price"]
        name = goods[0]["name"]
        image = goods[0]["image"]
        subTotal = qty * price
        # Insert selected item into shopping cart
        db.execute("INSERT INTO cart (user_id,id, qty, name, image, price, subTotal) VALUES (:uid,:id, :qty, :name, :image, :price, :subTotal)",uid=session["uid"], id=id, qty=qty, name=name, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name having user_id=:uid",uid=session["uid"])
        shopLen = len(shoppingCart)
        # Rebuild shopping cart
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Go back to cart page
        return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/filter/")
def filter():
    if request.args.get('category'):
        query = request.args.get('category')
        items = db.execute("SELECT * FROM items WHERE category = :query ORDER BY name ASC", query=query )
    itemsLen = len(items)
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        # Rebuild shopping cart
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name HAVING user_id=:uid",uid = session["uid"])
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        # Render filtered view
        return render_template ("index.html", shoppingCart=shoppingCart, items=items, shopLen=shopLen, itemsLen=itemsLen, total=total, totItems=totItems, display=display, session=session )
    # Render filtered view
    return render_template ( "index.html", items=items, shoppingCart=shoppingCart, itemsLen=itemsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)

@app.route("/search/")
def search():
    search_string=request.args.get("search_string")
    items = db.execute("SELECT * FROM items where name like '%"+search_string+"%' ORDER BY name ASC")
    itemsLen = len(items)
    # Initialize variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name having user_id=:uid",uid=session["uid"])
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template ("index.html", shoppingCart=shoppingCart, items=items, shopLen=shopLen, itemsLen=itemsLen, total=total, totItems=totItems, display=display, session=session )
    return render_template ( "index.html", items=items, shoppingCart=shoppingCart, itemsLen=itemsLen, shopLen=shopLen, total=total, totItems=totItems, display=display)

@app.route("/proceed-checkout/")
def proceedcheckout():
    # Redirect to home page

    return render_template("checkout.html")

@app.route("/checkout/")
def checkout():
    address=""
    addresshtml=""
    fields=["name","address1","address2","city","state","country","phno","email"]
    for field in fields:
        field_value = request.args.get(field)
        if field_value:
            address = address + "\n" + field_value
            addresshtml = addresshtml + " " + field_value
    session["address"] = address
    ##To-Do##
    ##add payment details
    shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name HAVING user_id=:uid",uid = session["uid"])
    shopLen = len(shoppingCart)
    total=0
    totItems=0
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    
    client = razorpay.Client(auth=("rzp_test_p2nZZCAVVqlm7E", "hyChRwi9mNN3G2HXMDEwOSpn"))

    rows=db.execute("SELECT qty, price from cart where user_id=:uid",uid=session['uid'])
    #user= User.objects.filter_by(id=id).first()
    
    print("rows //////",rows)
    amount=0
    for row in rows:
        amount+=row['price']*row['qty']
    
    payment= client.order.create({'amount': int(amount*100) ,'currency': 'INR', 'payment_capture': '1'})



    return render_template("payment.html", address=addresshtml, shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, payment = payment)


@app.route("/remove/", methods=["GET"])
def remove():
    # Get the id of item selected to be removed
    out = int(request.args.get("id"))
    # Remove item from shopping cart
    db.execute("DELETE from cart WHERE id=:id AND user_id=:uid", id=out,uid=session["uid"])
    # Initialize shopping cart variables
    totItems, total, display = 0, 0, 0
    # Rebuild shopping cart
    shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name HAVING user_id=:uid",uid = session["uid"])
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    # Turn on "remove success" flag
    display = 1
    # Render shopping cart
    return render_template ("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session )


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    # Render log in page
    return render_template("new.html")


@app.route("/logged/", methods=["POST"] )
def logged():
    # Get log in info from log in form
    user = request.form["username"].lower()
    pwd = request.form["password"]
    #pwd = str(sha1(request.form["password"].encode('utf-8')).hexdigest())
    # Make sure form input is not blank and re-render log in page if blank
    if user == "" or pwd == "":
        return render_template ( "login.html" )
    # Find out if info in form matches a record in user database
    query = "SELECT * FROM users WHERE username = :user AND password = :pwd"
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
    return render_template ( "login.html", msg="Wrong username or password." )


@app.route("/history/")
def history():
    # Initialize shopping cart variables
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all items ever bought by current user
    myitems = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myitemsLen = len(myitems)
    # Render table with shopping history of current user
    return render_template("history.html", show=0, shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myitems=myitems, myitemsLen=myitemsLen)


@app.route("/logout/")
def logout():
    # clear shopping cart
    db.execute("DELETE from cart where user_id=:uid",uid=session["uid"])
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register/", methods=["POST"] )
def registration():
    # Get info from form
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    # See if username already in the database
    rows = db.execute( "SELECT * FROM users WHERE username = :username ", username = username )
    # If username already exists, alert user
    if len( rows ) > 0:
        return render_template ( "new.html", msg="Username already exists!" )
    # If new user, upload his/her info into the users database
    new = db.execute ( "INSERT INTO users (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
                    username=username, password=password, fname=fname, lname=lname, email=email )
    # Render login template
    return render_template ( "login.html" )


@app.route("/cart/")
def cart():
    if 'user' in session:
        # Clear shopping cart variables
        totItems, total, display = 0, 0, 0
        # Grab info currently in database
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM cart GROUP BY name HAVING user_id=:uid",uid=session["uid"])
        # Get variable values
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    # Render shopping cart
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session)


@app.route("/success/",methods=["POST","GET"])
def success():
    order = db.execute("SELECT * from cart where user_id=:uid",uid=session["uid"])
    # Update purchase history of current customer
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, name, image, quantity,address, status) VALUES(:uid, :id, :name, :image, :quantity,:address,:status)",\
             uid=session["uid"], id=item["id"], name=item["name"], image=item["image"], quantity=item["qty"], address=session["address"], status="Not Delivered" )
    # Clear shopping cart
    db.execute("DELETE from cart where user_id=:uid",uid=session["uid"])

    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    # Retrieve all items ever bought by current user
    myitems = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myitemsLen = len(myitems)

    return render_template("history.html",show=1,shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems, display=display, session=session, myitems=myitems, myitemsLen=myitemsLen)





#For admin operations
@app.route("/admin/")
def admin():
    admins=db.execute("SELECT * FROM admins")
    for admin in admins:
        if admin["id"] == session["uid"]:
            return render_template("admin_index.html")
    
    return "You are not an admin"

    
@app.route("/admin/itemadd/")
def itemadd():
    return render_template("itemadd.html")

@app.route("/admin/item/add/", methods=["GET","POST"])
def add_item():
    isadmin=False
    admins=db.execute("SELECT * FROM admins")
    for admin in admins:
        if admin["id"] == session["uid"]:
            isadmin=True
            
    if not isadmin:
        return "You are not an admin"


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


@app.route("/admin/deleteitem/")
def itemdelete():
    return render_template("deleteitem.html")

@app.route("/admin/item/delete/", methods=["GET","POST"])
def delete_item():
    isadmin=False
    admins=db.execute("SELECT * FROM admins")
    for admin in admins:
        if admin["id"] == session["uid"]:
            isadmin=True
    
    if not isadmin:
        return "You are not an admin"

    
    item_id = request.args.get('id')
    db.execute("DELETE FROM items WHERE id = :id", id = item_id)
    return "done"

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
		render_template("login.html",msg="login with a super user account")
	else:  
		db.execute("INSERT INTO admins (id,username, password, superuser, name, addedby) VALUES (:id,:uname,:pwd,:su,:name,:addedby)",\
				uname=username,pwd=password,superuser=superuser,name=name,addedby=addedby,id=id)