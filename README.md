# [Alachua County Jail Lookup](http://andrewbriz.pythonanywhere.com/)

#### Description
The Alachua County Jail Lookup is a hybrid flask app and scraper to help keep WUFT up to date on the latest inmates being booked in Alachua County. The app is set to scrape twice a day (at noon and midnight), log any changes such as additions, removals, status updates or bond changes. At the time of the scrape, users who have set up email alerts will be notified of the changes based on their specific preferences. The scraper can also be manually run by admin users. The data is easily accessible in a number of ways on the flask app. The home page features a quick search functions which serves as an all inclusive way of finding data quickly. The advanced search page allows users to apply filters to narrow a search and find only inmates that meet every part of the specific set of criteria. Finally, the changelog is a record of all the changes. In the login page, all users can add filters for their alerts and admins can see and add users.

#### Why I Made It
[The Alachua County Jail Inmate system](http://oldweb.circuit8.org/inmatelist.php) is a bare-bones web page that houses a single table. All inmates are sorted in alphabetical order and there's no way to sort them or do any kind of meaningful analysis. Furthermore, WUFT only receives updates on new inmates if a PIO sends an email. This means that if anyone is arrested that the county does not want them to know about, they will likely not know unless they get a tip. My app aims to change that. 

#### Setup
1. Create virtual environment (optional, but highly recommended)
2. Install all dependencies by using ' $ pip install -r requirements.txt '
3. Set up baseDB on your database
4. Upload the repo files on to a Python host (such as [Python Anywhere](https://www.pythonanywhere.com/)). Alternatively you can host a local server. In that case, add the following lines of code to the end of ajl.py: `if __name__ == '__main__':` and `app.run()`
5. Update the data in dbInfo.py to match the information of your database. If no unix_socket is needed, leave that line as is.
6. Start your server

#### Usage Disclaimer
This app is made for in-house usage where a developer is close at hand for any fixing. There is very little error checking or editing without entering the SQL backend. In its current form, the admin page is a useful shortcut for adding new users, but only developers who have access to and know how to use the SQL backend should have admin accounts. Deleting and updating user info is currently not supported for security reasons.