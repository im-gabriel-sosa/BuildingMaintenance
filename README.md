# **Property Maintenance Platform \- Backend**

This is the FastAPI backend for a property maintenance platform MVP. The platform is designed with three core user roles: homeowners, contractors, and city officials. The initial development focuses on building out the homeowner role's features.

## **Technologies Used**

* **Backend:** Python with FastAPI & Gunicorn  
* **Database:** MongoDB Atlas  
* **Authentication:** Auth0  
* **Hosting:** Render (for the MVP)

## **Project Structure**

The project is organized to be modular and scalable, with separate directories for API endpoints, database models, and core configurations.

/fastapi-backend  
|-- app/  
|   |-- main.py             \# Main application entry point  
|   |-- api/  
|   |   |-- endpoints/  
|   |   |   |-- homeowner.py  \# API routes for homeowner-specific actions  
|   |   |-- deps.py             \# Authentication and dependency functions  
|   |   |-- utils.py            \# Pydantic utility helpers (e.g., for ObjectId)  
|   |-- core/  
|   |   |-- config.py           \# Application settings and environment variables  
|   |-- db/  
|   |   |-- mongodb.py          \# MongoDB connection setup  
|   |-- models/  
|   |   |-- maintenance.py      \# Pydantic models for maintenance requests  
|-- .env                    \# Local environment variables  
|-- .gitignore              \# Files and folders to ignore in Git  
|-- requirements.txt        \# Python dependencies  
|-- README.md

## **Getting Started**

### **1\. Clone the Repository**

Bash  
git clone \<your-repository-url\>  
cd fastapi-backend

### **2\. Set Up Your Environment**

You need to create a local `.env` file to store your credentials. This file is ignored by Git to protect sensitive information.

* Create the file: `touch .env`  
* Copy the contents from `.env.example` below and fill in your details:

#### **.env.example**

Code snippet  
\# MongoDB Atlas  
MONGO\_CONNECTION\_STRING="mongodb+srv://\<username\>:\<password\>@\<cluster\_name\>.mongodb.net/?retryWrites=true\&w=majority"  
DB\_NAME="property\_maintenance\_db"

\# Auth0 API  
AUTH0\_DOMAIN="YOUR\_AUTH0\_DOMAIN.auth0.com"  
AUTH0\_API\_AUDIENCE="YOUR\_API\_IDENTIFIER"  
AUTH0\_ALGORITHMS="RS256"

### **3\. Install Dependencies**

Bash  
\# It's recommended to use a virtual environment  
python \-m venv .venv  
source .venv/bin/activate

pip install \-r requirements.txt

### **4\. Run the Application**

For local development:

Bash  
uvicorn app.main:app \--reload

The API will now be running on `http://127.0.0.1:8000`. The `--reload` flag will automatically restart the server when you make code changes.

For production, use `gunicorn`:

Bash  
gunicorn \-w 4 \-k uvicorn.workers.UvicornWorker app.main:app

## **API Endpoints**

All homeowner endpoints are prefixed with `/homeowner` and require a valid JWT with the `homeowner` role.

### **Maintenance Requests**

* **`GET /requests`**  
  * **Description:** Retrieves a list of all maintenance requests submitted by the authenticated homeowner.  
  * **Response:** A list of `MaintenanceRequestOut` objects.  
* **`POST /requests`**  
  * **Description:** Creates a new maintenance request.  
  * **Body:** A `MaintenanceRequest` object.  
  * **Response:** The newly created `MaintenanceRequestOut` object.

## **Features Implemented**

* **Database Integration:** Established a robust, asynchronous connection to a MongoDB Atlas cluster.  
* **Secure Authentication:** Integrated Auth0 for user authentication. The system validates JWTs based on signature, issuer, and audience.  
* **Role-Based Access Control (RBAC):** Endpoints are protected, requiring users to have a specific role (e.g., "homeowner") present in their JWT claims.  
* **Pydantic Data Modeling:** Implemented detailed Pydantic models for data validation, serialization, and handling of MongoDB's special `ObjectId` type.  
* **Homeowner API:** Built the core API endpoints for homeowners to create (`POST`) and view (`GET`) their maintenance requests.  
* **Production-Ready Server:** Added `gunicorn` to the project dependencies for production deployment.

