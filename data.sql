-- Create the table
CREATE TABLE maxinfo (
    id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100)
);

-- Insert 5 different people
INSERT INTO maxinfo (id, first_name, last_name, email) VALUES
(1, 'Alice', 'Johnson', 'alice.johnson@example.com'),
(2, 'Bob', 'Smith', 'bob.smith@example.com'),
(3, 'Carol', 'Davis', 'carol.davis@example.com'),
(4, 'David', 'Lee', 'david.lee@example.com'),
(5, 'Eva', 'Martinez', 'eva.martinez@example.com');
