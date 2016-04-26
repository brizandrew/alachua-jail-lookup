# [Alachua County Jail Lookup](http://andrewbriz.pythonanywhere.com/)

#### Description
The Alachua County Jail Lookup is a hybrid flask app and scraper to help keep WUFT up to date on the latest inmates being booked in Alachua County. The app is set to scrape twice a day (at noon and midnight), log any changes such as additions, removals, status updates or bond changes. At the time of the scrape, users who have set up email alerts will be notified of the changes based on their specific preferences. The scraper can also be manually run by admin users. The data is easily accessible in a number of ways on the flask app. The home page features a quick search functions which serves as an all inclusive way of finding data quickly. The advanced search page allows users to apply filters to narrow a search and find only inmates that meet every part of the specific set of criteria. Finally, the changelog is a record of all the changes. In the login page, all users can add filters for their alerts and admins can see and add users.

#### Why I Made It
[The Alachua County Jail Inmate system](http://oldweb.circuit8.org/inmatelist.php) is a bare-bones web page that houses a single table. All inmates are sorted in alphabetical order and there's no way to sort them or do any kind of meaningful analysis. Furthermore, WUFT only receives updates on new inmates if a PIO sends an email. This means that if anyone is arrested that the county does not want them to know about, they will likely not know unless they get a tip. My app aims to change that. 

#### Setup
1. Create virtual environment (optional, but highly recommended).
2. Install all dependencies by using ' $ pip install -r requirements.txt '.
3. Set up [baseDB.sql](baseDB.sql) on your database.
4. Upload the repo files on to a Python host (such as [Python Anywhere](https://www.pythonanywhere.com/)). Alternatively you can host a local server. In that case, add the following lines of code to the end of [ajl.py](ajl.py). `if __name__ == '__main__':` insert a return and tab and then add `app.run()`.
5. Update the data in [dbInfo.py](dbInfo.py) to match the information of your database. If no unix_socket is needed, leave that line as is. You will need to create a Gmail account to use the email alert system. The account username goes in this file as well.
6. You will need to set up the password for the Gmail account as well, but including it in the source files is unsafe. The easiest way to do this is by running [this script](https://gist.github.com/brizandrew/5662cbff0285c98dcbe793533883c3a4) in your bash prompt. You will be prompted for a password, and asked if you would like to save it. Type ` y ` to do so. If you are running this on Python Anywhere you will also need to pip install [keyrings.alt](https://pypi.python.org/pypi/keyrings.alt).
7. Start your server.

#### Dependencies
* [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [PyMySQL](https://github.com/PyMySQL/PyMySQL)
* [Flask](http://flask.pocoo.org/)
* [Flask-WTF](https://flask-wtf.readthedocs.org/en/latest/)
* [Flask-Bootstrap](https://pythonhosted.org/Flask-Bootstrap/)
* [Titlecase](https://pypi.python.org/pypi/titlecase)
* [Yagmail](https://github.com/kootenpv/yagmail)
* [Schedule](https://pypi.python.org/pypi/schedule)

#### Usage Disclaimer
This app is made for in-house usage where a developer is close at hand for any fixing. There is very little error checking or editing without entering the SQL backend. In its current form, the admin page is a useful shortcut for adding new users, but only developers who have access to and know how to use the SQL backend should have admin accounts. Deleting and updating user info is currently not supported for security reasons.

#### About Files
###### [ajl.py](ajl.py)
The main app file takes care of routing users to the correct pages. It also includes all the forms used throughout the app.
###### [db.py](db.py)
This module is a collection of custom functions that use PyMySQL to interact with the SQL database in a number of ways. Some functions read certain data including searchDB (the main searching function) and others write to different tables. It also manages alerts, checking them when new additions are made, and sending emails accordingly.
###### [dbInfo.py](dbInfo.py)
This file holds the data specific to your host database. `charset` should not be changed. Adding a `unix_socket` is optional, but the variable should be left as is if it's not needed.
###### [runScraper.py](runScraper.py)
This script runs the scraper once. It's useful for setting up automation in envioronments where threaded automation isn't allowed like in Python Everywhere.
###### [templates](templates)
This folder holds all the html views that are rendered by [ajl.py](ajl.py).
###### [static/js/main](static/js/main)
This javascript file activates DataTables library on certain tables throughout the app, and it handles special POST requests in the login page to activate Python scripts without leaving the page.
###### [static/css/style](static/css/style)
Specific css styles.