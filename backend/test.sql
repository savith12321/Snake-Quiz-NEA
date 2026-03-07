-- ======================
-- Regions
-- ======================
INSERT INTO Region (name) VALUES ('Western Province');
INSERT INTO Region (name) VALUES ('Central Province');
INSERT INTO Region (name) VALUES ('Southern Province');

-- ======================
-- Features
-- ======================
INSERT INTO Feature (name, description) VALUES ('Hood present', 'Hood expands when threatened');
INSERT INTO Feature (name, description) VALUES ('Triangular head', 'Head is distinctly triangular');
INSERT INTO Feature (name, description) VALUES ('Bands on body', 'Body has colored bands');
INSERT INTO Feature (name, description) VALUES ('Round pupils', 'Eyes have round pupils');
INSERT INTO Feature (name, description) VALUES ('Pit organ', 'Heat-sensing pit between eyes and nostrils');
INSERT INTO Feature (name, description) VALUES ('Keel scales', 'Scales on body are ridged');
INSERT INTO Feature (name, description) VALUES ('Tail color different', 'Tail has distinct color from body');

-- ======================
-- Snakes
-- ======================
INSERT INTO Snake (common_name, scientific_name, venom_level, description) VALUES 
('Common Cat Snake', 'Boiga trigonata', 'mild', 'Mildly venomous, usually non-aggressive'),
('Ceylon Krait', 'Bungarus ceylonicus', 'high', 'Highly venomous, nocturnal'),
('Spectacled Cobra', 'Naja naja', 'high', 'Venomous, hooded, found throughout Sri Lanka'),
('Green Vine Snake', 'Ahaetulla nasuta', 'non-venomous', 'Non-venomous, arboreal, thin green body'),
("Russell's Viper", 'Daboia russelii', 'high', 'Highly venomous, terrestrial'),
('Ceylon Trinket Snake', 'Coelognathus helena', 'non-venomous', 'Non-venomous, active at night'),
('Common Sand Boa', 'Eryx conicus', 'non-venomous', 'Non-venomous, burrowing snake'),
('Starred Bronzeback', 'Dendrelaphis punctulatus', 'non-venomous', 'Non-venomous, diurnal'),
('Common Wolf Snake', 'Lycodon aulicus', 'mild', 'Mild venom, rarely dangerous to humans'),
('Hump-nosed Pit Viper', 'Hypnale hypnale', 'mild', 'Venomous, small viper');

-- ======================
-- SnakeFeature (weights 1-5)
-- ======================
-- Hood present
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (2,1,5);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (3,1,5);

-- Triangular head
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (2,2,5);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (5,2,5);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (10,2,4);

-- Bands on body
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (1,3,3);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (5,3,4);

-- Round pupils
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (4,4,5);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (6,4,5);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (7,4,5);

-- Pit organ
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (5,5,5);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (10,5,5);

-- Keel scales
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (7,6,4);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (8,6,3);

-- Tail color different
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (1,7,2);
INSERT INTO SnakeFeature (snake_id, feature_id, weight) VALUES (8,7,2);

-- ======================
-- SnakeRegion
-- ======================
-- Western Province
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (1,1);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (3,1);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (4,1);

-- Central Province
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (2,2);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (5,2);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (6,2);

-- Southern Province
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (7,3);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (8,3);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (9,3);
INSERT INTO SnakeRegion (snake_id, region_id) VALUES (10,3);

-- ======================
-- Users
-- ======================
INSERT INTO User (username, password_hash, created_at) VALUES ('alice', 'dummyhash1', '2026-01-02 10:00:00');
INSERT INTO User (username, password_hash, created_at) VALUES ('bob', 'dummyhash2', '2026-01-02 11:00:00');

-- ======================
-- Attempts
-- ======================
INSERT INTO Attempt (user_id, snake_id, correct, timestamp) VALUES (1,1,1,'2026-01-02 10:15:00');
INSERT INTO Attempt (user_id, snake_id, correct, timestamp) VALUES (1,3,0,'2026-01-02 10:20:00');
INSERT INTO Attempt (user_id, snake_id, correct, timestamp) VALUES (2,4,1,'2026-01-02 11:10:00');
INSERT INTO Attempt (user_id, snake_id, correct, timestamp) VALUES (2,5,0,'2026-01-02 11:20:00');
