#  COMP639-Flask Freshwater Guide Application

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
**General User Dashboard (/user/dashboard):**
Route: /user/dashboard
Functionality: Displays the dashboard with user-specific details and a list of guides related to freshwater ecosystems.
Data Flow: User details and guide entries are retrieved from the database; if the user is not logged in, they are redirected to the login page.
**Admin Dashboard (/admin/dashboard):**
Functionality: Provides administrators with an overview of the application and quick access to manage all aspects, including users, staff, and guide items.
Data Flow: Displays information relevant to administrative tasks, with options for user and guide management.
**Staff Dashboard (/staff/dashboard):**
Functionality: Allows staff members to view user profiles and manage guide entries, providing them with the necessary tools to contribute to the application’s content.
Data Flow: Staff members access information pertinent to their roles, with restricted capabilities compared to administrators.
**Authentication (/login/, /register, /logout):**
Routes: /login/, /register, /logout
Functionality: Handles user registration, login, and logout processes.
Data Flow: Involves checking credentials, registering new users with hashed passwords, and managing session data for authentication.
**Profile Management (/profile, /profile/update, /change_password):**
Routes: /profile, /profile/update, /change_password
Functionality: Enables users to view and edit their profile information and change their passwords.
Data Flow: Information is fetched from and updated in the database, with password changes incorporating hashing for security.
**Guide Item Management (/admin/manage_guide, /admin/add_guide, /admin/edit_guide/<int:item_id>, /admin/delete_guide/<int:item_id>):**
Routes: Specific to guide management, including adding, updating, and deleting guide items.
Functionality: Allows administrators to maintain the content of the guide, ensuring it is comprehensive and up-to-date.
Data Flow: Guide items are created, modified, or removed from the database, reflecting changes in the user interface.
**Guide Viewing (/listfreshwater, /view_item_details/<int:item_id>):**
Routes: For public and user-specific viewing of guide entries.
Functionality: Users can browse a list of freshwater guide entries and view detailed information on each.
Data Flow: Retrieves guide information from the database for display purposes.
**User and Staff Management (/admin/manage_user, /admin/manage_staff, /admin/add_river_user, /admin/add_staff, /admin/edit_river_user/<username>, /admin/edit_staff/<username>, /admin/delete_river_user/<username>, /admin/delete_staff/<username>):**
Routes: Dedicated to the management of user and staff accounts.
Functionality: Includes creating, updating, and deleting accounts, with additional capabilities for admins such as viewing all user and staff profiles.
Data Flow: Manipulates user and staff data within the database, with updates reflecting immediately in the application.
