import webapp2
import cgi
import jinja2
import os
import string
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))


#global varables



class BlogDB(db.Model):
    blogTitle = db.StringProperty()
    blogBody = db.StringProperty(multiline=True)
    created = db.DateTimeProperty(auto_now_add = True)






class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")


class Index(Handler):



    def get(self):

        # render the confirmation message
        t = jinja_env.get_template("frontpage.html")
        content = t.render()
        self.response.write(content)

class NewPost(Handler):




    def get(self,blogBody="",blogTitle="",error=""):   

        # render the confirmation message
        t = jinja_env.get_template("NewPost.html")
        content = t.render(blogTitle = blogTitle, blogBody=blogBody, error = error)
        self.response.write(content)

    def post(self):

      blogTitle= self.request.get("blogTitle")
      blogBody= self.request.get("blogBody")
      error =""
      blogTitleEscaped = cgi.escape(blogTitle, quote=True)
      blogBodyEscaped = cgi.escape(blogBody, quote=True)


# if the user typed nothing at all, redirect and yell at them
      if (blogBodyEscaped == ""):
          error = "Please write the body"
          self.get(blogBodyEscaped,blogTitleEscaped,error)
          #self.redirect("/?error=" + cgi.escape(error))
      # construct a blog entry
      elif (blogTitleEscaped == ""):
          error = "Please write the title"
          self.get(blogBodyEscaped,blogTitleEscaped,error)
      else: 

        blogBodyEscaped = blogBodyEscaped.replace("\n", "<br />") #because we want to convert line endings into breaks, to display nicely.
        #write to database
        blogPost = BlogDB(blogTitle = blogTitleEscaped, blogBody = blogBodyEscaped)			
        blogPost.put()


        #write to screen
        t = jinja_env.get_template("NewPost-confirmation.html")
        content = t.render(blogTitle = blogTitleEscaped, blogPost = blogBodyEscaped, error = error)      
        self.response.write(content)


class Blog(Handler):


    def get(self):


      page = self.request.get("page")
       
      if page == "":
        page = 1
      if not str(page).isdigit() :
          self.redirect("/?error=")
      #this currently does not work, alwasys returns true  
   

      #we start with page 1, because if it is =1 jinga won't display the elemit

      

      offset = str((int(page)-1) * 5)

      #build the page numbers for forward and back
      nextpage = int(page) + 1
      previous = int(page) - 1
      
     

      t = jinja_env.get_template("blog.html")


      blogEntries = db.GqlQuery("SELECT * FROM BlogDB ORDER BY created DESC LIMIT "+ offset+",5")

      #if less than 5 entries were displayed, don't display next
      #previous is not shown if page = 0, this is by jinja design


      count = 0
      for titles in blogEntries:
        count += 1
      if count != 5:
        nextpage = ""

      content = t.render(blogEntries = blogEntries, nextpage=nextpage, previous=previous)

      self.response.write(content)


class ViewPostHandler(Handler):
      def get(self,id):

        blogEntrie = BlogDB.get_by_id(int(id))
        t = jinja_env.get_template("singleblog.html")
        content = t.render(blogEntrie = blogEntrie)
        self.response.write(content)



app = webapp2.WSGIApplication([
    ('/', Index),
    ('/NewPost', NewPost),
    ('/Blog', Blog),
    webapp2.Route('/Blog/<id:\d+>', ViewPostHandler)
], debug=True)
