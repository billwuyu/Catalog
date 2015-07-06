from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

#connect to database!!
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
	return render_template('menu.html', restaurant = restaurant, items = items)


@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods = ['GET', 'POST'])
def newMenuItem(restaurant_id):

	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'],
			course=request.form['course'], restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash("New menu item created!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else: # handle GET request
		return render_template('newmenuitem.html', restaurant_id = restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods = ['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	
	menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if menuItem is None:
		print "No such menu item!"
		return
	
	if request.method == 'POST':
		if request.form["name"]:
			menuItem.name = request.form["name"]
		if request.form["description"]:
			menuItem.description = request.form["description"]
		if request.form["price"]:
			menuItem.price = request.form["price"]
		if request.form["course"]:
			menuItem.course = request.form["course"]
		session.add(menuItem)
		session.commit()
		flash("Menu item edited!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else: # handle GET request
		return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, menuItem = menuItem)



@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):

	menuItem = session.query(MenuItem).filter_by(id = menu_id).one()
	if menuItem is None:
		print "No such menu item!"
		return

	if request.method == 'POST':
		session.delete(menuItem)
		session.commit()
		flash("Menu item deleted!")
		return redirect (url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return render_template('deletemenuitem.html', restaurant_id = restaurant_id, item = menuItem)

# for API endpoints
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	item = session.query(MenuItem).filter_by(id = menu_id).one()
	return jsonify(item.serialize)


if __name__ == "__main__":
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
