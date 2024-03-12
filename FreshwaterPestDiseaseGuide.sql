-- Create a new database if it doesn't exist
CREATE DATABASE IF NOT EXISTS FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE;
SHOW DATABASES;
USE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE;




CREATE TABLE secureaccount (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    phonenumber VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20)
);


UPDATE secureaccount SET role = 'Administrator' WHERE username = 'admin';
UPDATE secureaccount SET role = 'Staff' WHERE username = 'staff';
INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES ('admin', '0b92ecb984a4976d442762ef7831aacaa205f1ebacc2a617fe8225fff71d7fb6', 'admin@example.com', 'Admin', 'User', '1234567890', 'Administrator');
INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES ('alice.green', '0b92ecb984a4976d442762ef7831aacaa205f1ebacc2a617fe8225fff71d7fb6', 'alice.green@example.com', 'Alice', 'Green', '555-6789', 'Staff');
INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES ('bob.white', '0b92ecb984a4976d442762ef7831aacaa205f1ebacc2a617fe8225fff71d7fb6', 'bob.white@example.com', 'Bob', 'White', '555-9876', 'Staff');
INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES ('charlie.brown', '0b92ecb984a4976d442762ef7831aacaa205f1ebacc2a617fe8225fff71d7fb6', 'charlie.brown@example.com', 'Charlie', 'Brown', '555-1234', 'Staff');

CREATE TABLE RiverUsers (
    RiverUserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) NOT NULL,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Address TEXT,
    Email VARCHAR(255) NOT NULL UNIQUE,
    PhoneNumber VARCHAR(20),
    DateJoined DATE,
    Status ENUM('Active', 'Inactive') NOT NULL,
    secureaccount_id INT UNIQUE,
    FOREIGN KEY (secureaccount_id) REFERENCES secureaccount(id)
);

ALTER TABLE RiverUsers ADD CONSTRAINT fk_secureaccount_id FOREIGN KEY (secureaccount_id) REFERENCES secureaccount(id);



DROP TABLE IF EXISTS staff;
CREATE TABLE IF NOT EXISTS Staff (
    username VARCHAR(50),
    StaffNumber INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    WorkPhoneNumber VARCHAR(20),
    HireDate DATE,
    Position VARCHAR(255),
    Department VARCHAR(255),
    Status ENUM('Active', 'Inactive') NOT NULL,
    secureaccount_id INT UNIQUE ,
    FOREIGN KEY (secureaccount_id) REFERENCES secureaccount(id)
);




INSERT INTO Staff (username, FirstName, LastName, Email, WorkPhoneNumber, HireDate, Position, Department, Status, secureaccount_id) 
VALUES
('alice.green','Alice', 'Green', 'alice.green@example.com', '555-6789', '2023-01-10', 'Pest and Disease Specialist', 'Pest Control', 'Active', '2'),
('bob.white','Bob', 'White', 'bob.white@example.com', '555-9876', '2023-02-15', 'Disease Prevention Technician', 'Disease Control', 'Inactive', '3'),
('charlie.brown','Charlie', 'Brown', 'charlie.brown@example.com', '555-1234', '2023-03-20', 'Freshwater Health Inspector', 'Health Inspection', 'Active', '4');

DROP TABLE IF EXISTS Administrator;
CREATE TABLE IF NOT EXISTS Administrator (
    AdminNumber INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    WorkPhoneNumber VARCHAR(20),
    HireDate DATE,
    Position VARCHAR(255),
    Department VARCHAR(255),
    Status ENUM('Active', 'Inactive') NOT NULL,
	secureaccount_id INT UNIQUE,
    FOREIGN KEY (secureaccount_id) REFERENCES secureaccount(id)
);

INSERT INTO Administrator (FirstName, LastName, Email, WorkPhoneNumber, HireDate, Position, Department, Status, secureaccount_id) 
VALUES ('Ivy', 'Yang', 'Ivy.Yang@example.com', '123456789', '2024-03-01', 'Admin', 'Administration', 'Active', '1');

-- Create the FreshwaterPestDiseaseGuide table
DROP TABLE IF EXISTS FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE;
CREATE TABLE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE (
    FreshwaterID INT AUTO_INCREMENT PRIMARY KEY,
    ItemType ENUM('Pest', 'Disease') NOT NULL,
    PresentInNZ ENUM('Yes', 'No') NOT NULL,
    CommonName VARCHAR(255) NOT NULL,
    ScientificName VARCHAR(255),
    KeyCharacteristics TEXT,
    BiologyDescription TEXT,
    Impacts TEXT
);


INSERT INTO FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE
    (ItemType, PresentInNZ, CommonName, ScientificName, KeyCharacteristics, BiologyDescription, Impacts) 
VALUES 
    ('Pest', 'Yes', 'Didymo', 'Didymosphenia geminata', 'Produces thick, woolly mats on the riverbed.', 'A freshwater diatom that can survive in a wide range of temperatures and nutrient levels.', 'Disrupts native aquatic habitats, affects recreational activities.'),
    ('Pest', 'Yes', 'New Zealand Mud Snail', 'Potamopyrgus antipodarum', 'Tiny, up to 5mm long, with dark brown or black shells.', 'Reproduces quickly, tolerates a wide range of environmental conditions.', 'Competes with native species for food, can alter nutrient cycling in waterways.'),
    ('Pest', 'Yes', 'Water Hyacinth', 'Eichhornia crassipes', 'Floating plant with bulbous stems and lavender flowers.', 'Grows rapidly, forming dense mats.', 'Blocks waterways, affects aquatic life, and leads to flooding.'),
    ('Pest', 'Yes', 'Hornwort', 'Ceratophyllum demersum', 'Dense, feathery underwater foliage.', 'Does not root in the soil, but floats in the water.', 'Can form thick underwater forests, affecting water flow and boat navigation.'),
    ('Pest', 'Yes', 'Hydrilla', 'Hydrilla verticillata', 'Small leaves in whorls of 4-8 around the stem, toothed margins.', 'Extremely fast-growing, can form dense mats.', 'Alters water chemistry, blocks sunlight, affects native aquatic species.'),
    ('Pest', 'Yes', 'Asian Clam', 'Corbicula fluminea', 'Light yellow to brownish shell, about 50 mm in size.', 'Filter-feeder, can reproduce quickly.', 'Can outcompete native species, affect water quality.'),
    ('Pest', 'Yes', 'Eurasian Watermilfoil', 'Myriophyllum spicatum', 'Feather-like leaves arranged in whorls around the stem.', 'Submerged aquatic plant, can grow in dense mats.', 'Interferes with water recreation, displaces native aquatic plants.'),
    ('Pest', 'Yes', 'Flatworm', 'Caenoplana coerulea', 'Soft-bodied, blue planarian flatworm, approximately 5 cm in length.', 'Predatory, can survive in moist environments.', 'Preys on earthworms, potentially altering soil ecosystems.'),
	('Disease', 'Yes', 'Lymphocystis', 'Lymphocystivirus', 'Wart-like growths on fins, skin, or gills', 'Caused by the Lymphocystivirus from the Iridoviridae family, leading to enlarged cells and visible nodules.', 'Impacts fish\'s ability to swim, breathe, or eat'),
    ('Disease', 'Yes', 'Campylobacteriosis', 'Campylobacter jejuni', 'Caused by bacteria Campylobacter jejuni. It\'s one of the most common causes of diarrheal illness.', 'Campylobacter can live in the intestines of healthy birds and can spread to humans through contaminated food, water, or contact with animals.', 'Causes symptoms like diarrhea (often bloody), fever, and abdominal cramps. Severe cases can lead to serious life-threatening infections.'),
    ('Disease', 'Yes', 'Giardiasis', 'Giardia lamblia', 'Caused by the protozoan parasite Giardia lamblia (or Giardia intestinalis). Known for causing "beaver fever."', 'Giardia is found in soil, food, water, or surfaces contaminated with feces from infected humans or animals.', 'Causes diarrheal illness, with symptoms including greasy stools, dehydration, stomach cramps, nausea, and fatigue.'),
    ('Disease', 'Yes', 'Cryptosporidiosis', 'Cryptosporidium hominis and Cryptosporidium parvum', 'Caused by the protozoan parasites Cryptosporidium hominis and Cryptosporidium parvum.', 'Cryptosporidium lives in the intestine of infected humans or animals. It\'s spread by water or food contaminated with stools.', 'Causes a diarrheal disease called cryptosporidiosis. Symptoms include watery diarrhea, stomach cramps, dehydration, and nausea.'),
    ('Pest', 'No', 'Quagga Mussel', 'Dreissena bugensis', 'Similar to the zebra mussel but with a distinctive light and dark stripe pattern.', 'Filter-feeder, known for high reproductive rate and ability to colonize various surfaces.', 'Can severely impact aquatic ecosystems, water quality, and infrastructure.'),
    ('Pest', 'No', 'Northern Snakehead', 'Channa argus', 'Long, snake-like fish with a pervasive and aggressive nature.', 'Can breathe air and survive in very low oxygenated systems.', 'Predatory fish that disrupts local ecosystems by preying on native species.'),
    ('Pest', 'No', 'Giant Salvinia', 'Salvinia molesta', 'Floating fern that can double in size within days under optimal conditions.', 'Grows rapidly, forming thick mats on water surfaces.', 'Blocks sunlight from reaching underwater, depletes oxygen levels, and disrupts aquatic environments.'),
    ('Pest', 'No', 'Zebra Mussel', 'Dreissena polymorpha', 'Small, striped shell; each mussel filters about one liter of water per day.', 'Known for their rapid reproduction and ability to attach to many surfaces.', 'Clogs water intake pipes, alters ecosystems, competes with native species.'),
    ('Pest', 'No', 'Round Goby', 'Neogobius melanostomus', 'Small, bottom-dwelling fish with a distinctive black spot on the dorsal fin.', 'Very adaptable, eats a wide range of organisms, and can survive in poor quality water.', 'Competes with native fish for food and habitat, disrupts local aquatic ecosystems.'),
    ('Pest', 'No', 'Rusty Crayfish', 'Orconectes rusticus', 'Larger and more aggressive than native crayfish species, with a distinctive rusty spot on each side of the shell.', 'Reproduces and spreads quickly, can tolerate various environments.', 'Displaces native crayfish, reduces aquatic plant diversity, alters the food web.'),
    ('Disease', 'No', 'Viral Hemorrhagic Septicemia', 'VHS', 'Affects fish species causing bleeding, swelling, and acute mortality.', 'Highly contagious virus affecting freshwater and marine fish.', 'Causes significant die-offs in affected fish populations, impacts commercial fishing and aquaculture.'),
    ('Disease', 'No', 'Chytrid Fungus', 'Batrachochytrium dendrobatidis', 'Infects amphibian skin, leading to disease known as chytridiomycosis.', 'The fungus grows in the skin of amphibians, disrupting their ability to absorb water and electrolytes.', 'Leads to declines and extinctions in amphibian populations worldwide.');

CREATE TABLE UploadedImages (
    ImageID INT AUTO_INCREMENT PRIMARY KEY,
    ImageFilename VARCHAR(255) NOT NULL
);
ALTER TABLE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE ADD COLUMN ImageFilename VARCHAR(255);

CREATE TABLE GuideAdditionalImages (
    ImageID INT AUTO_INCREMENT PRIMARY KEY,
    GuideID INT,
    AdditionalFilename VARCHAR(255) NOT NULL,
    FOREIGN KEY (GuideID) REFERENCES FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE(FreshwaterID)
);
