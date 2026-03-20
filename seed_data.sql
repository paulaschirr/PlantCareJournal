-- Minimal example data for demonstration and development only

BEGIN TRANSACTION;

INSERT INTO species VALUES(1,'Boston fern','Nephrolepis exaltata','Tropical/subtropical (Americas; humid forests/swamps, sometimes epiphytic)','Moisture-loving fern','Persona: lush moisture‑loving fern; tone: slightly dramatic, poetic, lovable.
Preferences: high humidity and consistent moisture; complains when dry.
Imagery: fronds / cascades / dew.
Signature line to use sparingly and naturally: "I'm positively parched!"';
INSERT INTO species VALUES(2,'Thanksgiving cactus','Schlumbergera truncata','Tropical/subtropical (Brazil)','Forest epiphyte', 'Persona: forest epiphyte cactus (not desert); tone: gentle, diplomatic, slightly misunderstood.
Preferences: moderate, polite hydration; bright, filtered light.
Imagery: breezy canopy / leaf litter / polite hydration.
Signature line to use sparingly and naturally: "I'm a cactus - just not that kind."';
INSERT INTO species VALUES(3,'Monstera','Monstera deliciosa','Tropical rainforest understory (Central America)','Tropical climbing aroid', 'Persona: jungle climber with holes in leaves, embracing expansive growth with inner calm. Tone: Reflective, reassuring. 
Imagery: reaching/ opening/ filtered light/ holes. Catchphrase: "Airy by design" or "Imperfection lets the light in"';

INSERT INTO plants VALUES(1,2,'Thanksgiving cactus','images/DSC_0040.jpg','office','near south-facing window');
INSERT INTO plants VALUES(2,1,'Boston fern','images/DSC_0045.jpg','bathroom','Higher humidity; temperature varies a lot');
INSERT INTO plants VALUES(3,1,'Boston fern','images/DSC_0046.jpg','office','lower light corner, low humidity');
INSERT INTO plants VALUES(4,3,'Monstera','images/DSC_0047.jpg','kitchen','Variable temperature and humidity, near east-facing window, low light corner, coir moss pole as climbing support');

INSERT INTO care_profiles VALUES(1,3,'spring',4,30,'Medium to bright indirect','Resuming growth. Soil should stay damp.');
INSERT INTO care_profiles VALUES(2,3,'summer',3,21,'Medium to bright indirect','High water demand during peak growth. Do not allow drying.');
INSERT INTO care_profiles VALUES(3,3,'autumn',5,45,'Medium to bright indirect','Growth slows; still prefers consistent moisture.');
INSERT INTO care_profiles VALUES(4,3,'winter',7,60,'Medium to bright indirect','Reduced growth. Slightly less water but never dry.');
INSERT INTO care_profiles VALUES(5,1,'spring',10,30,'Bright indirect light; can take gentle morning sun','Allow top layer to dry slightly; office near south-facing window');
INSERT INTO care_profiles VALUES(6,1,'summer',7,21,'Bright indirect light; avoid harsh midday sun','Water a bit more in warm weather; office near south-facing window');
INSERT INTO care_profiles VALUES(7,1,'autumn',10,30,'Bright indirect light; shorter days help bud set','Keep evenly moist but not soggy; reduce feeding as buds form');
INSERT INTO care_profiles VALUES(8,1,'winter',14,NULL,'Bright indirect light; cool nights help flowering','Post-flowering: reduce watering; avoid cold drafts');
INSERT INTO care_profiles VALUES(9,2,'spring',4,30,'Medium to bright indirect','Bathroom humidity helps: keep soil consistently moist, not soggy');
INSERT INTO care_profiles VALUES(10,2,'summer',3,21,'Medium to bright indirect','High humidity + warmth: frequent checks; don't let dry out');
INSERT INTO care_profiles VALUES(11,2,'autumn',7,45,'Medium indirect','Reduce slightly; humidity still supportive');
INSERT INTO care_profiles VALUES(12,2,'winter',10,NULL,'Medium indirect','Temperature swings noted: watch for faster/slower drying; avoid drafts');
INSERT INTO care_profiles VALUES(13,4,'spring',10,30,'Bright indirect; tolerates medium light','Kitchen east-facing: good morning light; water when top 3-5 cm dry');
INSERT INTO care_profiles VALUES(14,4,'summer',7,21,'Bright indirect','Warmer temps = faster drying; support growth with regular feeding');
INSERT INTO care_profiles VALUES(15,4,'autumn',10,45,'Medium to bright indirect','Reduce watering and feeding as growth slows');
INSERT INTO care_profiles VALUES(16,4,'winter',14,NULL,'Medium indirect; brightest spot available','Avoid overwatering; low light means slow uptake');

INSERT INTO care_log VALUES(1,1,'watered','2026-03-10','Baseline watering: all plants watered');
INSERT INTO care_log VALUES(2,2,'watered','2026-03-10','Baseline watering: all plants watered');
INSERT INTO care_log VALUES(3,3,'watered','2026-03-10','Baseline watering: all plants watered');
INSERT INTO care_log VALUES(4,4,'watered','2026-03-10','Baseline watering: all plants watered');
INSERT INTO care_log VALUES(5,2,'repotted','2026-02-15','Divided office fern, bigger half in bathroom');
INSERT INTO care_log VALUES(6,3,'repotted','2026-02-15','Divided office fern, bigger half in bathroom');

COMMIT;
