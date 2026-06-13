
USE foodredistribution;

CREATE TABLE organizations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200),
    type VARCHAR(50),
    latitude DOUBLE,
    longitude DOUBLE,
    fulladdress TEXT,
    phone VARCHAR(20),
    google_maps_url TEXT
);