from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

#connect to database!!
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				
				restaurant_list = session.query(Restaurant).all()

				#send results back to client
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				message = ""
				message += "<html><body>"
				message += "<a href = '/restaurants/new'>Create new restaurant here!</a></br></br>"
				for restaurant in restaurant_list:
					message += restaurant.name + "</br>"
					message += "<a href = '/restaurants/%s/edit'>Edit</a></br>" % restaurant.id
					message += "<a href = '/restaurants/%s/delete'>Delete</a></br>" % restaurant.id
					message += "</br></br>"
				message += "</body></html>"
				self.wfile.write(message)
				return
			if self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1> Creating new restaurant... </h1>"
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
            		<input name="restaurantName" type="text" placeholder = "New restaurant name" >
            		<input type="submit" value="Create"> </form>'''
				output += "</body></html>"
				self.wfile.write(output)
				return

			if self.path.endswith("/edit"):

				restaurantID = self.path.split('/')[2]
				print self.path.split('/')
				restaurant = session.query(Restaurant).filter_by(id = restaurantID).one()

				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1> Renaming %s </h1>" % restaurant.name
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>''' % restaurant.id
				output += '''<input name="restaurantName" type="text" placeholder = "%s">''' % restaurant.name
				output += "<input type='submit' value='Rename'> </form>"
				output += "</body></html>"
				self.wfile.write(output)
				print "finished with edit get"
				return

			if self.path.endswith("/delete"):

				restaurantID = self.path.split('/')[2]
				restaurant = session.query(Restaurant).filter_by(id = restaurantID).one()

				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()
				output = ""
				output += "<html><body>"
				output += "<h1> Are you sure you want to delete the restaurant %s? </h1>" % restaurant.name
				output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>''' % restaurant.id
				output += "<input type='submit' value='Delete'> </form>"
				output += "</body></html>"
				self.wfile.write(output)
				return

		except IOError:
			self.send_error(404, "File Not Found: %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('restaurantName')
				
				#add to database
				if messagecontent != []:
					restaurant1 = Restaurant(name= messagecontent[0])
					session.add(restaurant1)
					session.commit()

					self.send_response(301)
					#redirect
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
				return

			if self.path.endswith("/edit"):
				print "ented post edit"
				restaurantID = self.path.split('/')[2]
				print "reached split"
				ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
				if ctype == 'multipart/form-data':
					fields = cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('restaurantName')
				print "finished parsing"
				#modify in database
				restaurant = session.query(Restaurant).filter_by(id= restaurantID).one() #should be only one with this id
				if restaurant != [] and messagecontent != []:
					print "entered if statements"
					restaurant.name = messagecontent[0]
					session.add(restaurant)
					session.commit()

					#now send code and redirect
					self.send_response(301)
					#redirect
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
				return

			if self.path.endswith("/delete"):
				restaurantID = self.path.split('/')[2]
				#modify in database
				restaurant = session.query(Restaurant).filter_by(id= restaurantID).one() #should be only one with this id
				if restaurant != []:
					session.delete(restaurant)
					session.commit()

					#now send code and redirect
					self.send_response(301)
					#redirect
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()
				return
			
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Webserver is running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print " ^C entered, stopping webserver..."
		server.socket.close()

if __name__ == '__main__':
	main()
