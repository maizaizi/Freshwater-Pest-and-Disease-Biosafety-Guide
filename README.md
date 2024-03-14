#  COMP639 Freshwater Guide Application

## Project Overview
This Flask web application is designed to support the management and viewing of river ecosystem information, with particular emphasis on users, staff, and administrators. It includes features for user authentication, role-based access control, profile management, and CRUD operations for managing river ecosystem data.
## Application Structure
The application follows the MVC (Model-View-Controller) architectural pattern with clear separation of routes (controllers), logic, and templates (views). The model's functionality is implemented via interactions with a MySQL database.All uploaded images are stored in the static/images folder, and the "templates" directory contains HTML files with data provided by the render controller.
### Directory Layout
app.py: The entry point of the application configuring Flask and routes.
connect.py: Defines the database connection parameters.
db.py: Contains the database connection and cursor creation functions.
Blueprints for modularization:
admin_dashboard.py: Admin-specific functionalities such as user and staff management.
staff_dashboard.py: Staff-specific functionalities including guide management and user viewing.
user_dashboard.py: User-specific functionalities like profile management and guide viewing.
### Key Routes and Functionalities:
- 1. General User Dashboard (/user/dashboard):**
Route: /user/dashboard
Functionality: Displays the dashboard with user-specific details and a list of guides related to freshwater ecosystems.
Data Flow: User details and guide entries are retrieved from the database; if the user is not logged in, they are redirected to the login page.
- 2. Admin Dashboard (/admin/dashboard):**
Functionality: Provides administrators with an overview of the application and quick access to manage all aspects, including users, staff, and guide items.
Data Flow: Displays information relevant to administrative tasks, with options for user and guide management.
- 3. Staff Dashboard (/staff/dashboard):**
Functionality: Allows staff members to view user profiles and manage guide entries, providing them with the necessary tools to contribute to the application’s content.
Data Flow: Staff members access information pertinent to their roles, with restricted capabilities compared to administrators.
- 4. Authentication (/login/, /register, /logout):**
Routes: /login/, /register, /logout
Functionality: Handles user registration, login, and logout processes.
Data Flow: Involves checking credentials, registering new users with hashed passwords, and managing session data for authentication.
- 5. Profile Management (/profile, /profile/update, /change_password):**
Routes: /profile, /profile/update, /change_password
Functionality: Enables users to view and edit their profile information and change their passwords.
Data Flow: Information is fetched from and updated in the database, with password changes incorporating hashing for security.
- 6. Guide Item Management (/admin/manage_guide, /admin/add_guide, /admin/edit_guide/<int:item_id>, /admin/delete_guide/<int:item_id>):**
Routes: Specific to guide management, including adding, updating, and deleting guide items.
Functionality: Allows administrators to maintain the content of the guide, ensuring it is comprehensive and up-to-date.
Data Flow: Guide items are created, modified, or removed from the database, reflecting changes in the user interface.
- 7. Guide Viewing (/listfreshwater, /view_item_details/<int:item_id>):**
Routes: For public and user-specific viewing of guide entries.
Functionality: Users can browse a list of freshwater guide entries and view detailed information on each.
Data Flow: Retrieves guide information from the database for display purposes.
- 8. User and Staff Management (/admin/manage_user, /admin/manage_staff, /admin/add_river_user, /admin/add_staff, /admin/edit_river_user/<username>, /admin/edit_staff/<username>, /admin/delete_river_user/<username>, /admin/delete_staff/<username>):**
Routes: Dedicated to the management of user and staff accounts.
Functionality: Includes creating, updating, and deleting accounts, with additional capabilities for admins such as viewing all user and staff profiles.
Data Flow: Manipulates user and staff data within the database, with updates reflecting immediately in the application.

## Assumptions and Design Decisions
### Assumptions
- Session Management by Users: It is assumed that users will responsibly manage their sessions by logging out when necessary. This ensures security and integrity of user-specific data.
- Target User Group: The application is primarily targeted towards individuals who have an understanding of biosecurity concerns related to freshwater ecosystems. This includes environmental scientists, researchers, biosecurity personnel, and educated enthusiasts.
- MySQL Schema Effectiveness: It is assumed that the provided MySQL database schema is well-designed and structured to efficiently meet the data storage and retrieval needs of the application. This includes proper normalization, indexing, and relationship definition among various data entities.
### Design Decisions
- Flask's Built-in Session Management: The decision to use Flask's built-in session management was made for its ease of use and seamless integration within the Flask ecosystem. This enables secure and straightforward management of user sessions, facilitating features such as login, logout, and session persistence.
- Password Hashing with Flask-Hashing: For enhanced security, Flask-Hashing is employed to hash user passwords. This ensures that passwords are not stored in plain text in the database, thereby protecting user information from potential security breaches.
- Role-Based Access Control (RBAC): The application implements role-based access control to manage different levels of user permissions and access rights. This allows for a clear separation of functionalities among different user roles, such as administrators, staff, and general users, ensuring that users can only access information and functionalities appropriate to their roles.
- Template Inheritance: The use of template inheritance in the application's design promotes consistency and maintainability. By employing a base template, repetitive structures such as headers, footers, and navigation bars are defined in one place and inherited by other templates, making the UI consistent across different parts of the application and easier to maintain.
- RESTful Principles for Routes and Methods: The application's routes and methods are designed following RESTful principles, providing clarity and standardization to the requests and responses between the client and server. This approach simplifies the API structure, making it intuitive and easy to understand, which is beneficial for development, documentation, and future scalability.
- These assumptions and design decisions form the foundational principles guiding the development and operation of your Flask web application, ensuring it serves its intended purpose effectively while providing a secure, user-friendly, and maintainable platform.





