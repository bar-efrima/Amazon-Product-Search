# Amazon-Product-Search
Welcome to my Amazon scraping project. 
To run the project, please execute the following command: "uvicorn --Server:app --

# it's important to note that web scraping is intended for educational purposes only. It is crucial to review the terms of service and policies of each website to ensure scraping is permitted and to understand the guidelines for using their information.

# Project Description:

This project involved creating a web application (website) that displays item prices from various Amazon websites.

The website was built using Python with the FastAPI framework.

The client side of the application was developed using plain HTML, JavaScript, and the fetch() API.

For the backend, a local file database (SQLite) was used to store user data and other necessary information. The site supports only one user, and there is no user authentication or individual data storage. All users share the same data.

Upon opening the root page, users are presented with a search page containing a text box and a SEARCH button. They can enter an item to search for on Amazon.com. The application then scrapes the Amazon.com search page and displays the top 10 results in a table with "Name" and "Image" columns.

After selecting an item from the search results, users are shown a table with the price of the selected item from different Amazon sites. This information is obtained through scraping. To minimize waiting time, the scraping requests are executed in parallel.

All prices are displayed in USD, and the price values are clickable links that open the specific product page in a new tab.

To improve matching of items across different Amazon websites, the ASIN (Amazon Standard Identification Number) from the Amazon.com product page is used to search for the same item on other websites. If a similar ASIN cannot be found, the item name from Amazon.com is used instead.

If a similar item cannot be found on a specific Amazon website, the string "Not found" is displayed under the price column.

Users have access to their past searches through a "My past searches" link.

If a user performs more than 10 searches in a single day, an error message is displayed: "Daily searches cap reached. Consider upgrading to the premium service to search for more items

