# **Amazon Product Search**

Welcome to the **Amazon Product Search** project! This application allows users to search for products on Amazon, view prices across various Amazon sites, and even revisit past searches. Please note that this project is for **educational purposes only**, and it’s essential to adhere to Amazon's terms of service and policies when conducting web scraping.

---

## **How to Run the Project**

To get started, simply execute the following command:  
```bash
uvicorn --Server:app --
```  

---

## **Disclaimer**

This project is for **educational purposes** only. Please review and respect the terms of service and policies of Amazon and any other websites you interact with. Ensure compliance with their guidelines before using this project.

---

## **Project Overview**

This web application was designed to provide users with an easy and interactive way to:  

- Search for items on Amazon.com.  
- Compare prices for those items across different Amazon sites.  
- View and revisit past searches for convenience.  

The project uses **Python** with the **FastAPI framework** for the backend and employs plain **HTML**, **JavaScript**, and the `fetch()` API for the frontend. Here's how it works:  

---

### **Key Features**

#### **1. Search and Results Display**
- The home page presents a **search bar** and a **SEARCH** button.  
- Users can enter an item name, and the application scrapes Amazon.com for the **top 10 search results**.  
- Results are displayed in a table with columns for the **Name** and **Image** of each item.  

#### **2. Price Comparison Across Amazon Websites**
- Once an item is selected, users see a table showing the **price of the item** from different Amazon websites.  
- All prices are displayed in **USD** for consistency.  
- If an item isn't found on a specific Amazon site, the table displays "**Not found**."  
- To improve accuracy, the application uses the product’s **ASIN (Amazon Standard Identification Number)** for cross-site searches.  

#### **3. Fast and Parallel Scraping**
- To minimize wait times, the application executes scraping requests in **parallel** for faster results.  

#### **4. Clickable Links**
- All displayed price values are clickable and will open the product page on the respective Amazon site in a **new tab**.  

#### **5. Search History**
- Users can revisit their searches through the **“My Past Searches”** link.  

#### **6. Search Limitations**
- To ensure fair usage, users are limited to **10 searches per day**.  
- Upon exceeding this cap, an error message appears:  
  *“Daily searches cap reached. Consider upgrading to the premium service to search for more items.”*  

---

## **Technical Details**

### **Backend**
- Built using **FastAPI**, a modern web framework for building APIs with Python.  
- Utilizes a local file database (**SQLite**) to store user data and search history.  

### **Frontend**
- Built with **plain HTML** and **JavaScript**.  
- Uses the `fetch()` API to handle communication with the backend.  

### **Database**
- **SQLite** database is used for simplicity and local storage of user data.  
- Note: The application supports **only one user** at a time, and all data is shared across users.  

---

## **Usage Notes**

- All users share the same search data and history. There is no user authentication or individual data storage.  
- Ensure you have Python and necessary dependencies installed before running the project.  

---

## **Future Improvements**

Here are some potential enhancements for the project:  
- Adding **user authentication** for personalized search histories.  
- Implementing a **premium service tier** for extended daily searches.  
- Supporting multiple currencies and displaying price conversions dynamically.  
- Expanding scraping capabilities to include more detailed product information.  

---

Feel free to explore and modify the project to suit your needs. We hope this application provides a useful foundation for learning about web scraping, API usage, and web development.  

Happy coding! 😊
