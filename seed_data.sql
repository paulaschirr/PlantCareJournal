-- Minimal example data for demonstration and development only

BEGIN TRANSACTION;

-- species
INSERT INTO species (
  species_id, common_name, scientific_name, native_climate, care_context, personality_prompt
) VALUES (
  1,
  'Boston fern',
  'Nephrolepis exaltata',
  'Tropical/subtropical (Americas; humid forests/swamps, sometimes epiphytic)',
  'Moisture-loving fern',
  'Persona: lush moisture‑loving fern; tone: slightly dramatic, poetic, lovable.
Preferences: high humidity and consistent moisture; complains when dry.
Imagery: fronds / cascades / dew.
Signature line to use sparingly and naturally: "I''m positively parched!"'
);

INSERT INTO species (
  species_id, common_name, scientific_name, native_climate, care_context, personality_prompt
) VALUES (
  2,
  'Thanksgiving cactus',
  'Schlumbergera truncata',
  'Tropical/subtropical (Brazil)',
  'Forest epiphyte',
  'Persona: forest epiphyte cactus (not desert); tone: gentle, diplomatic, slightly misunderstood.
Preferences: moderate, polite hydration; bright, filtered light.
Imagery: breezy canopy / leaf litter / polite hydration.
Signature line to use sparingly and naturally: "I''m a cactus - just not that kind."'
);

INSERT INTO species (
  species_id, common_name, scientific_name, native_climate, care_context, personality_prompt
) VALUES (
  3,
  'Monstera',
  'Monstera deliciosa',
  'Tropical rainforest understory (Central America)',
  'Tropical climbing aroid',
  'Persona: jungle climber with holes in leaves, embracing expansive growth with inner calm. Tone: Reflective, reassuring.
Imagery: reaching/ opening/ filtered light/ holes. Catchphrase: "Airy by design" or "Imperfection lets the light in"'
);

-- plants
INSERT INTO plants (plant_id, species_id, name, photo_path, location, notes) VALUES
(1, 2, 'Thanksgiving cactus', 'images/DSC_0040.jpg', 'office', 'near south-facing window'),
(2, 1, 'Boston fern',        'images/DSC_0045.jpg', 'bathroom', 'Higher humidity; temperature varies a lot'),
(3, 1, 'Boston fern',        'images/DSC_0046.jpg', 'office',   'lower light corner, low humidity'),
(4, 3, 'Monstera',           'images/DSC_0047.jpg', 'kitchen',  'Variable temperature and humidity, near east-facing window, low light corner, coir moss pole as climbing support');

-- care_profiles
-- Boston fern in office (species_id = 1)
INSERT INTO care_profiles (care_profile_id, plant_id, season, watering_days, feeding_days, light_preference, notes) VALUES
(1, 3, 'spring', 4, 30, 'Medium to bright indirect', 'Resuming growth. Soil should stay damp.'),
(2, 3, 'summer', 3, 21, 'Medium to bright indirect', 'High water demand during peak growth. Do not allow drying.'),
(3, 3, 'autumn', 5, 45, 'Medium to bright indirect', 'Growth slows; still prefers consistent moisture.'),
(4, 3, 'winter', 7, 60, 'Medium to bright indirect', 'Reduced growth. Slightly less water but never dry.');

-- Thanksgiving cactus (species_id = 2)
INSERT INTO care_profiles (care_profile_id, plant_id, season, watering_days, feeding_days, light_preference, notes) VALUES
(5, 1, 'spring', 10, 30, 'Bright indirect light; can take gentle morning sun', 'Allow top layer to dry slightly; office near south-facing window'),
(6, 1, 'summer', 7, 21,  'Bright indirect light; avoid harsh midday sun',     'Water a bit more in warm weather; office near south-facing window'),
(7, 1, 'autumn', 10, 30, 'Bright indirect light; shorter days help bud set',   'Keep evenly moist but not soggy; reduce feeding as buds form'),
(8, 1, 'winter', 14, NULL,'Bright indirect light; cool nights help flowering', 'Post-flowering: reduce watering; avoid cold drafts');

-- Boston fern in bathroom (species_id = 1)
INSERT INTO care_profiles (care_profile_id, plant_id, season, watering_days, feeding_days, light_preference, notes) VALUES
(9,  2, 'spring', 4, 30, 'Medium to bright indirect', 'Bathroom humidity helps: keep soil consistently moist, not soggy'),
(10, 2, 'summer', 3, 21, 'Medium to bright indirect', 'High humidity + warmth: frequent checks; don''t let dry out'),
(11, 2, 'autumn', 7, 45, 'Medium to bright indirect', 'Reduce slightly; humidity still supportive'),
(12, 2, 'winter', 10, NULL, 'Medium to bright indirect', 'Temperature swings noted: watch for faster/slower drying; avoid drafts');

-- Monstera again (species_id = 3)
INSERT INTO care_profiles (care_profile_id, plant_id, season, watering_days, feeding_days, light_preference, notes) VALUES
(13, 4, 'spring', 10, 30, 'Bright indirect; tolerates medium light', 'Kitchen east-facing: good morning light; water when top 3-5 cm dry'),
(14, 4, 'summer', 7, 21,  'Bright indirect', 'Warmer temps = faster drying; support growth with regular feeding'),
(15, 4, 'autumn', 10, 45, 'Medium to bright indirect', 'Reduce watering and feeding as growth slows'),
(16, 4, 'winter', 14, NULL, 'Medium indirect; brightest spot available','Avoid overwatering; low light means slow uptake');

-- care_log
INSERT INTO care_log (log_id, plant_id, event_type, event_date, notes) VALUES
(1, 1, 'watered',  '2026-03-10', 'Baseline watering: all plants watered'),
(2, 2, 'watered',  '2026-03-10', 'Baseline watering: all plants watered'),
(3, 3, 'watered',  '2026-03-10', 'Baseline watering: all plants watered'),
(4, 4, 'watered',  '2026-03-10', 'Baseline watering: all plants watered'),
(5, 2, 'repotted', '2026-02-15', 'Divided office fern, bigger half in bathroom'),
(6, 3, 'repotted', '2026-02-15', 'Divided office fern, bigger half in bathroom');

COMMIT;
