-- This file sets up the staging environment with test data
-- Make sure new staging site does not have old data
DELETE FROM meals;

-- Insert test data
INSERT INTO meals (description, rating) VALUES 
('Grilled chicken with vegetables', 'Pretty Good'),
('Just mushrooms', 'Nasty'),
('Fajita, cheese, and bean tacos', 'DELICIOUS');

-- Make sure data was inserted
SELECT COUNT(*) as total_meals FROM meals;
SELECT * FROM meals ORDER BY rating;