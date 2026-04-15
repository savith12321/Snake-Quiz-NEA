-- =============================================
-- Snake Seed Data — 35 Sri Lankan Snakes
-- Run against: backend/data/data.db
-- Usage: sqlite3 backend/data/data.db < seed_snakes.sql
--
-- Uses INSERT OR IGNORE so it is safe to re-run.
-- Clear the tables first if you want a fresh load:
--   DELETE FROM SnakeImage;
--   DELETE FROM Snake;
-- =============================================

PRAGMA foreign_keys = ON;

-- =============================================
-- Snakes
-- =============================================
INSERT OR IGNORE INTO Snake (snake_id, common_name, scientific_name, venom_level, description) VALUES
( 1,  'Common Cat Snake',           'Boiga trigonata',               'mild',         'Mildly venomous rear-fanged snake, usually non-aggressive. Active at night; often found in trees and shrubs.'),
( 2,  'Ceylon Krait',               'Bungarus ceylonicus',           'high',         'Highly venomous nocturnal krait endemic to Sri Lanka. Neurotoxic venom; bites often occur while the victim is asleep.'),
( 3,  'Spectacled Cobra',           'Naja naja',                     'high',         'Iconic hooded cobra found throughout Sri Lanka. Spreads its hood when threatened and is responsible for many snakebite fatalities.'),
( 4,  'Green Vine Snake',           'Ahaetulla nasuta',              'non-venomous', 'Slender bright-green arboreal snake with a sharply pointed snout. Masters of camouflage among foliage.'),
( 5,  'Russell''s Viper',           'Daboia russelii',               'high',         'One of Sri Lanka''s most dangerous snakes. Heavy-bodied with a distinctive chain pattern. A leading cause of snakebite mortality.'),
( 6,  'Ceylon Trinket Snake',       'Coelognathus helena',           'non-venomous', 'Large non-venomous constrictor active at night. Frequently found near human settlements where it hunts rodents.'),
( 7,  'Common Sand Boa',            'Eryx conicus',                  'non-venomous', 'Stout burrowing snake with a short blunt tail. Inhabits dry sandy areas and is completely harmless to humans.'),
( 8,  'Starred Bronzeback',         'Dendrelaphis punctulatus',      'non-venomous', 'Slender fast-moving diurnal snake with iridescent bronze scales. Commonly seen in gardens and forest edges.'),
( 9,  'Common Wolf Snake',          'Lycodon aulicus',               'mild',         'Small nocturnal snake frequently found inside homes. Its mild venom is not dangerous to humans; feeds mainly on lizards.'),
(10,  'Hump-nosed Pit Viper',       'Hypnale hypnale',               'mild',         'Small venomous pit viper with a distinctive upturned snout. One of the most common causes of snakebite in Sri Lanka.'),
(11,  'Sri Lanka Green Pit Viper',  'Trimeresurus trigonocephalus',  'high',         'Vivid green arboreal pit viper endemic to Sri Lanka. Possesses heat-sensing pits and potent hemotoxic venom.'),
(12,  'Checkered Keelback',         'Fowlea piscator',               'non-venomous', 'Semi-aquatic snake abundant near ponds, streams and paddy fields. Feeds primarily on fish and frogs.'),
(13,  'Indian Python',              'Python molurus',                'non-venomous', 'Large constrictor reaching over 4 metres. Found in forests and grasslands near water; a protected species in Sri Lanka.'),
(14,  'Sri Lanka Pipe Snake',       'Cylindrophis maculatus',        'non-venomous', 'Small burrowing snake endemic to Sri Lanka. Mimics venomous species by curling its tail to display the bright red underside.'),
(15,  'Banded Racer',               'Argyrogena fasciolata',         'non-venomous', 'Fast-moving diurnal snake with distinct dark body bands. Common in dry scrub zones and agricultural land.'),
(16,  'Indian Cobra',               'Naja naja naja',                'high',         'Widespread subspecies of the spectacled cobra. Highly venomous with potent neurotoxic and cytotoxic venom.'),
(17,  'Ceylon Fer-de-Lance',        'Trimeresurus erythrurus',       'high',         'Reddish-brown pit viper found in the wet zone. Arboreal and nocturnal with haemotoxic venom.'),
(18,  'Oriental Rat Snake',         'Ptyas mucosa',                  'non-venomous', 'One of the largest snakes in Sri Lanka, reaching 3 metres. An aggressive but harmless species that controls rodent populations.'),
(19,  'Sri Lanka Flying Snake',     'Chrysopelea taprobanica',       'mild',         'Endemic gliding snake that can flatten its body and undulate between trees. Mild rear-fanged venom harmless to humans.'),
(20,  'Common Krait',               'Bungarus caeruleus',            'high',         'One of the most venomous snakes in Asia. Nocturnal and docile by day but highly dangerous at night; neurotoxic venom.'),
(21,  'Slender Coral Snake',        'Calliophis melanurus',          'high',         'Secretive burrowing elapid with bright red tail. Rarely seen but possesses potent venom affecting the nervous system.'),
(22,  'Large-scaled Pit Viper',     'Trimeresurus macrolepis',       'high',         'Rare arboreal pit viper found in higher elevations. Green colouration provides excellent camouflage in montane vegetation.'),
(23,  'Sri Lanka Worm Snake',       'Indotyphlops braminus',         'non-venomous', 'Tiny blind burrowing snake often mistaken for an earthworm. The only known all-female (parthenogenetic) snake species.'),
(24,  'Painted Bronzeback',         'Dendrelaphis pictus',           'non-venomous', 'Slender arboreal snake with striking blue and orange flanks visible when the neck is flattened during threat displays.'),
(25,  'Olive Keelback',             'Atretium schistosum',           'non-venomous', 'Semi-aquatic keelback found along streams and wetlands. Olive-green above with a yellowish belly.'),
(26,  'Indian Egg-Eating Snake',    'Elachistodon westermanni',      'non-venomous', 'Specialist feeder that swallows whole bird eggs and regurgitates the crushed shell. Rarely encountered.'),
(27,  'Sri Lanka Kukri Snake',      'Oligodon calamarius',           'non-venomous', 'Small secretive snake named for its curved kukri-shaped rear teeth used to slit open reptile eggs.'),
(28,  'Reticulated Python',         'Malayopython reticulatus',      'non-venomous', 'World''s longest snake by length. Occasionally recorded in Sri Lanka. A powerful constrictor with an intricate net-like pattern.'),
(29,  'Forsten''s Cat Snake',       'Boiga forsteni',                'mild',         'Large nocturnal rear-fanged snake found in forested areas. Feeds on lizards and frogs; rarely bites humans.'),
(30,  'Sri Lanka Shieldtail',       'Uropeltis melanogaster',        'non-venomous', 'Endemic burrowing snake with a shielded tail tip. Lives underground in moist soil in the hill country.'),
(31,  'Buff-striped Keelback',      'Amphiesma stolatum',            'non-venomous', 'Small attractively patterned keelback with pale body stripes. Common in grasslands and cultivated areas.'),
(32,  'Ceylon Coachwhip',           'Ahaetulla pulverulenta',        'mild',         'Dusky-coloured vine snake relative with a pointed snout and horizontal pupils. Hunts lizards and frogs in low vegetation.'),
(33,  'Sri Lanka Tree Boa',         'Corallus hortulanus',           'non-venomous', 'Slender arboreal boa recorded in Sri Lankan forests. Nocturnal hunter with heat-sensitive labial pits.'),
(34,  'Common Smooth Snake',        'Coronella austriaca',           'non-venomous', 'Slim secretive snake with smooth scales. A constrictor that feeds on lizards and small rodents; rarely seen.'),
(35,  'Sri Lanka Palm Viper',       'Craspedocephalus trigonocephalus','high',       'Endemic arboreal pit viper closely related to the green pit viper. Often found coiled in palm and banana foliage.');

-- =============================================
-- SnakeImage
-- Assumes image files extracted to:
--   C:\Users\isavi\Documents\python\snake quiz\backend\data\images\
-- and the SnakeImage table is empty (IDs start at 1).
-- =============================================
INSERT OR IGNORE INTO SnakeImage (snake_id, file_path, is_primary, uploaded_at) VALUES
( 1,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\1.png',  1, '2026-01-01 00:00:00'),
( 2,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\2.png',  1, '2026-01-01 00:00:00'),
( 3,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\3.png',  1, '2026-01-01 00:00:00'),
( 4,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\4.png',  1, '2026-01-01 00:00:00'),
( 5,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\5.png',  1, '2026-01-01 00:00:00'),
( 6,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\6.png',  1, '2026-01-01 00:00:00'),
( 7,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\7.png',  1, '2026-01-01 00:00:00'),
( 8,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\8.png',  1, '2026-01-01 00:00:00'),
( 9,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\9.png',  1, '2026-01-01 00:00:00'),
(10,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\10.png', 1, '2026-01-01 00:00:00'),
(11,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\11.png', 1, '2026-01-01 00:00:00'),
(12,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\12.png', 1, '2026-01-01 00:00:00'),
(13,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\13.png', 1, '2026-01-01 00:00:00'),
(14,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\14.png', 1, '2026-01-01 00:00:00'),
(15,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\15.png', 1, '2026-01-01 00:00:00'),
(16,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\16.png', 1, '2026-01-01 00:00:00'),
(17,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\17.png', 1, '2026-01-01 00:00:00'),
(18,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\18.png', 1, '2026-01-01 00:00:00'),
(19,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\19.png', 1, '2026-01-01 00:00:00'),
(20,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\20.png', 1, '2026-01-01 00:00:00'),
(21,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\21.png', 1, '2026-01-01 00:00:00'),
(22,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\22.png', 1, '2026-01-01 00:00:00'),
(23,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\23.png', 1, '2026-01-01 00:00:00'),
(24,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\24.png', 1, '2026-01-01 00:00:00'),
(25,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\25.png', 1, '2026-01-01 00:00:00'),
(26,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\26.png', 1, '2026-01-01 00:00:00'),
(27,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\27.png', 1, '2026-01-01 00:00:00'),
(28,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\28.png', 1, '2026-01-01 00:00:00'),
(29,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\29.png', 1, '2026-01-01 00:00:00'),
(30,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\30.png', 1, '2026-01-01 00:00:00'),
(31,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\31.png', 1, '2026-01-01 00:00:00'),
(32,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\32.png', 1, '2026-01-01 00:00:00'),
(33,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\33.png', 1, '2026-01-01 00:00:00'),
(34,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\34.png', 1, '2026-01-01 00:00:00'),
(35,  'C:\Users\isavi\Documents\python\snake quiz\backend\data\images\35.png', 1, '2026-01-01 00:00:00');
