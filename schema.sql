-- Database schema for Meal Tracker application
-- Creates the table and initial data for staging

CREATE TABLE IF NOT EXISTS meals (
id INT AUTO_INCREMENT PRIMARY KEY,
description VARCHAR(1000) NOT NULL,
rating VARCHAR(50) NOT NULL
);

-- Indices for better performance
CREATE INDEX idx_meals_rating ON meals(rating);
