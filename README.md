# **Property Maintenance Platform \- Backend**

This is the FastAPI backend for a property maintenance platform MVP. The platform is designed with three core user roles: homeowners, contractors, and city officials. The initial development focuses on building out the homeowner role's features.

## **Technologies Used**

* **Backend:** Python with FastAPI  
* **Database:** MongoDB Atlas  
* **Authentication:** Auth0  
* **Hosting:** Render (for the MVP)

## **Project Structure**

The project is organized to be modular and scalable, with separate directories for API endpoints, database models, and core configurations.

/fastapi-backend  
|-- app/  
|   |-- main.py              \# Main application entry point  
|   |-- api/  
|   |   |-- endpoints/  
|   |   |   |-- homeowner.py   \# API routes for homeowner-specific actions  
|   |   |-- deps.py            \# Authentication and dependency functions  
|   |-- core/  
|   |   |-- config.py          \# Application settings and environment variables  
|   |-- db/  
|   |   |-- mongodb.py         \# MongoDB connection setup  
|   |-- models/  
|   |   |-- maintenance.py     \# Pydantic models for maintenance requests  
|   |   |-- user.py            \# Pydantic models for user data  
|-- .env                     \# Local environment variables  
|-- requirements.txt         \# Python dependencies  
|-- README.md

## **Getting Started**

### **1\. Clone the Repository**

git clone \<your-repository-url\>  
cd fastapi-backend

### **2\. Set Up Your Environment**

You need to create a local .env file to store your credentials. This file is ignored by Git to protect sensitive information.

* Create the file: touch .env  
* Copy the contents from .env.example below and fill in your details:

### **.env.example**

\# MongoDB Atlas  
MONGO\_CONNECTION\_STRING="mongodb+srv://\<username\>:\<password\>@\<cluster\_name\>.mongodb.net/?retryWrites=true\&w=majority"  
DB\_NAME="property\_maintenance\_db"

\# Auth0 API  
AUTH0\_DOMAIN="YOUR\_AUTH0\_DOMAIN.auth0.com"  
AUTH0\_API\_AUDIENCE="YOUR\_API\_IDENTIFIER"  
AUTH0\_ALGORITHMS="RS256"

### **3\. Install Dependencies**

pip install \-r requirements.txt

### **4\. Run the Application**

uvicorn app.main:app \--reload

The API will now be running on http://127.0.0.1:8000. The \--reload flag will automatically restart the server when you make code changes.

## **Current Progress**

* **Project Structure:** A scalable file structure has been implemented.  
* **Dependencies:** All necessary Python packages are installed.  
* **Configuration:** The .env file is set up to handle all sensitive credentials and API keys.