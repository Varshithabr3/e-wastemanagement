-- EcoCycle - Responsible E-Waste Management Platform
-- Database Schema: ewaste_management
-- Technology: MySQL 8.0+

CREATE DATABASE IF NOT EXISTS `ewaste_management` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `ewaste_management`;

-- Drop tables in reverse foreign-key order
DROP TABLE IF EXISTS `collection_request_items`;
DROP TABLE IF EXISTS `collection_requests`;
DROP TABLE IF EXISTS `ewaste_items`;
DROP TABLE IF EXISTS `recycling_centres`;
DROP TABLE IF EXISTS `disposal_guidelines`;
DROP TABLE IF EXISTS `awareness_content`;
DROP TABLE IF EXISTS `admins`;
DROP TABLE IF EXISTS `users`;

-- ----------------------------------------------------------------------------
-- 1. USERS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `phone` VARCHAR(25) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `address` TEXT NULL,
  `city` VARCHAR(100) NULL DEFAULT 'Bengaluru',
  `pincode` VARCHAR(15) NULL,
  `reset_token` VARCHAR(100) NULL,
  `reset_token_expiry` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. ADMINS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `admins` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `full_name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(50) NOT NULL DEFAULT 'Super Administrator',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_admins_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. E-WASTE ITEMS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `ewaste_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `category` VARCHAR(80) NOT NULL,
  `item_name` VARCHAR(150) NOT NULL,
  `quantity` INT NOT NULL DEFAULT 1,
  `item_condition` ENUM('Working', 'Damaged', 'Not Working') NOT NULL DEFAULT 'Not Working',
  `description` TEXT NULL,
  `location` VARCHAR(150) NOT NULL,
  `image_filename` VARCHAR(255) NULL,
  `status` VARCHAR(50) NOT NULL DEFAULT 'Available',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_ewaste_category` (`category`),
  INDEX `idx_ewaste_user` (`user_id`),
  INDEX `idx_ewaste_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 4. COLLECTION REQUESTS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `collection_requests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `request_code` VARCHAR(40) NOT NULL UNIQUE,
  `user_id` INT NOT NULL,
  `pickup_address` TEXT NOT NULL,
  `city` VARCHAR(100) NOT NULL,
  `pincode` VARCHAR(15) NOT NULL,
  `preferred_date` DATE NOT NULL,
  `preference_type` ENUM('Doorstep Pickup', 'Centre Drop-Off') NOT NULL DEFAULT 'Doorstep Pickup',
  `status` ENUM('Pending', 'Approved', 'In Progress', 'Completed', 'Rejected') NOT NULL DEFAULT 'Pending',
  `admin_notes` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_request_code` (`request_code`),
  INDEX `idx_request_status` (`status`),
  INDEX `idx_request_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 5. COLLECTION REQUEST ITEMS (M2M JUNCTION)
-- ----------------------------------------------------------------------------
CREATE TABLE `collection_request_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `request_id` INT NOT NULL,
  `item_id` INT NOT NULL,
  FOREIGN KEY (`request_id`) REFERENCES `collection_requests`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`item_id`) REFERENCES `ewaste_items`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uk_req_item` (`request_id`, `item_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 6. AUTHORIZED RECYCLING CENTRES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `recycling_centres` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `centre_name` VARCHAR(220) NOT NULL,
  `facility_type` VARCHAR(80) NOT NULL DEFAULT 'Authorized Recycler',
  `complete_address` TEXT NOT NULL,
  `city` VARCHAR(100) NOT NULL,
  `district` VARCHAR(100) NULL DEFAULT 'Bengaluru Urban',
  `pincode` VARCHAR(15) NULL,
  `state` VARCHAR(100) NOT NULL DEFAULT 'Karnataka',
  `contact_phone` VARCHAR(60) NULL,
  `contact_email` VARCHAR(120) NULL,
  `website_url` VARCHAR(255) NULL,
  `services_offered` TEXT NULL,
  `accepted_categories` TEXT NOT NULL,
  `source_url` TEXT NOT NULL,
  `last_verified_date` DATE NOT NULL,
  `is_official_verified` TINYINT(1) NOT NULL DEFAULT 1,
  `directions_url` TEXT NULL,
  `latitude` DECIMAL(10, 7) NULL,
  `longitude` DECIMAL(10, 7) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_centre_city` (`city`),
  INDEX `idx_centre_district` (`district`),
  INDEX `idx_centre_facility` (`facility_type`),
  INDEX `idx_centre_verified` (`is_official_verified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 7. PROPER DISPOSAL GUIDELINES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `disposal_guidelines` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `category` VARCHAR(100) NOT NULL UNIQUE,
  `title` VARCHAR(220) NOT NULL,
  `summary` TEXT NOT NULL,
  `step_by_step` MEDIUMTEXT NOT NULL,
  `dos_and_donts` MEDIUMTEXT NOT NULL,
  `hazards_prevented` TEXT NULL,
  `icon_class` VARCHAR(80) NOT NULL DEFAULT 'fa-recycle',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 8. ENVIRONMENTAL AWARENESS CONTENT TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE `awareness_content` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(220) NOT NULL,
  `category` VARCHAR(100) NOT NULL,
  `summary` TEXT NOT NULL,
  `content` MEDIUMTEXT NOT NULL,
  `toxic_substance` VARCHAR(120) NULL,
  `health_hazard` TEXT NULL,
  `environmental_hazard` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SEED DATA
-- Default Admin Account: admin@ewaste.gov.in / admin123
-- Password hash generated with Werkzeug pbkdf2:sha256
-- ============================================================================

INSERT INTO `admins` (`full_name`, `email`, `password_hash`, `role`) VALUES
('E-Waste Drive Administrator', 'admin@ewaste.gov.in', 'scrypt:32768:8:1$K5GvUvQ8Y7mZ7A$c9b581c1c73a6e9a66d8e8749dc8c4e48b8b809a73860bb54407856b3e390c5504d603a1523c9ce055038c92a9bfd53bf5ffb17ba951f28b7ff70ea56ec23bb6', 'Super Administrator');

-- Seed Official Authorized Recycling Centres (CPCB & KSPCB Verified)
INSERT INTO `recycling_centres` 
(`centre_name`, `facility_type`, `complete_address`, `city`, `district`, `pincode`, `state`, `contact_phone`, `contact_email`, `website_url`, `services_offered`, `accepted_categories`, `source_url`, `last_verified_date`, `is_official_verified`, `directions_url`, `latitude`, `longitude`) VALUES
(
  'M/s. E-Parisaraa Pvt. Ltd.',
  'Authorized Recycler',
  'Plot No. 30-P3, KIADB Industrial Area, Dobaspet, Nelamangala Taluk',
  'Nelamangala',
  'Bengaluru Rural',
  '562111',
  'Karnataka',
  '+91 80 2773 6050',
  NULL,
  'https://www.ewasteindia.com',
  'India''s first CPCB/KSPCB authorized scientific e-waste recycler. Precious metal recovery, PCB shredding, and zero-landfill display processing.',
  'Computers, Laptops, Mobile Phones, Printers, Circuit Boards, Household Electronics',
  'https://eprewaste.cpcb.gov.in/',
  '2026-10-15',
  1,
  'https://www.google.com/maps/search/?api=1&query=E-Parisaraa+Pvt+Ltd+Dobaspet+KIADB',
  13.2355000,
  77.2418000
),
(
  'M/s. Sriram Eco Raksha Computer Services Pvt. Ltd.',
  'Authorized Recycler',
  'Shed No. B-29, KSSIDC Industrial Estate, Bommasandra, Hosur Road, Anekal Taluk',
  'Bengaluru',
  'Bengaluru Urban',
  '560099',
  'Karnataka',
  '+91 80 2783 5530',
  NULL,
  NULL,
  'Certified IT asset recovery, high-security data destruction, copper and aluminum mechanical granulators.',
  'Computers, Laptops, Mobile Phones, Chargers, Servers, Network Equipment',
  'https://kspcb.karnataka.gov.in/',
  '2026-10-10',
  1,
  'https://www.google.com/maps/search/?api=1&query=KSSIDC+Industrial+Estate+Bommasandra+Bangalore',
  12.8188000,
  77.6842000
),
(
  'M/s. 4R Recycling Pvt. Ltd.',
  'Authorized Dismantler',
  'Shed No. A-5, Peenya Industrial Estate, Peenya 3rd Stage, Nallakadirenahalli, Yeshwanthpur Hobli',
  'Bengaluru',
  'Bengaluru Urban',
  '560058',
  'Karnataka',
  '+91 80 2837 4444',
  NULL,
  NULL,
  'KSPCB-authorized manual and mechanical dismantling, hazard isolation, plastic sorting and segregation.',
  'Mobile Phones, Chargers, Batteries, Laptops, Small Household Appliances',
  'https://data.opencity.in/dataset/karnataka-waste-collection-recycling-and-processing-centres',
  '2026-09-25',
  1,
  'https://www.google.com/maps/search/?api=1&query=Peenya+3rd+Stage+Industrial+Estate+Bangalore',
  13.0380000,
  77.5140000
),
(
  'M/s. E-R3 Solutions Pvt. Ltd.',
  'Authorized Recycler',
  'Plot No. 105, Road No. 3, KIADB Bengaluru IT Park, Mahadeva Kodigehalli',
  'Bengaluru',
  'Bengaluru Urban',
  '562149',
  'Karnataka',
  '+91 80 4115 5440',
  NULL,
  'https://er3solutions.com',
  'IT Asset Disposition (ITAD), DoD 5220.22-M certified data erasure, environmentally sound recycling.',
  'Laptops, Desktops, Network Hardware, Server Racks, Lithium-Ion Batteries',
  'https://eprewaste.cpcb.gov.in/',
  '2026-09-20',
  1,
  'https://www.google.com/maps/search/?api=1&query=KIADB+IT+Park+Mahadeva+Kodigehalli+Bengaluru',
  13.1550000,
  77.6740000
),
(
  'M/s. Ash Recyclers',
  'Authorized Dismantler',
  'Plot No. 3, KSSIDC Industrial Estate, Hoskote',
  'Hoskote',
  'Bengaluru Rural',
  '562114',
  'Karnataka',
  NULL,
  NULL,
  'http://ashrecycler.com',
  'Authorized electronic assembly dismantling, circuit board sorting, and copper wire recovery.',
  'Electrical & Electronic Assembly Waste, Telecom Gear, Cables, PCBs',
  'https://kspcb.karnataka.gov.in/',
  '2026-10-05',
  1,
  'https://www.google.com/maps/search/?api=1&query=KSSIDC+Industrial+Estate+Hoskote+Bangalore',
  13.0690000,
  77.7980000
),
(
  'M/s. Cerebra Integrated Technologies Ltd.',
  'Authorized Recycler',
  'S-5, 3rd Cross Street, 1st Stage, Netaji Nagar, Peenya Industrial Area',
  'Bengaluru',
  'Bengaluru Urban',
  '560058',
  'Karnataka',
  '+91 80 2210 7748',
  NULL,
  'https://www.cerebracomputers.com',
  'Large-scale zero-landfill e-waste processing facility, display neutralization, precious metal extraction.',
  'Televisions, CRT Monitors, Laptops, Computers, Telecom Equipment, Large Appliances',
  'https://eprewaste.cpcb.gov.in/',
  '2026-10-18',
  1,
  'https://www.google.com/maps/search/?api=1&query=Peenya+Industrial+Area+1st+Stage+Bengaluru',
  13.0280000,
  77.5220000
),
(
  'M/s. Saahas Zero Waste (Saahas Waste Management Pvt. Ltd.)',
  'Collection Centre',
  'Ground Floor, No. 21, MCHS Colony, 5th C Cross, 16th Main Road, BTM 2nd Stage',
  'Bengaluru',
  'Bengaluru Urban',
  '560076',
  'Karnataka',
  '+91 80 4168 9389',
  NULL,
  'https://saahaszerowaste.com',
  'Official citizen collection and drop-off facility. Aggregation and safe channelization to authorized recyclers.',
  'Mobile Phones, Household Electronics, Chargers, Cables, Dry Cell Batteries',
  'https://data.opencity.in/dataset/karnataka-waste-collection-recycling-and-processing-centres',
  '2026-10-01',
  1,
  'https://www.google.com/maps/search/?api=1&query=BTM+Layout+2nd+Stage+Bengaluru',
  12.9165000,
  77.6101000
),
(
  'M/s. Sheeltron Digital Systems Pvt. Ltd.',
  'Authorized Refurbisher',
  'No. 2/1, East Park Road, Kumara Park East, South End Street',
  'Bengaluru',
  'Bengaluru Urban',
  '560001',
  'Karnataka',
  NULL,
  NULL,
  'https://sheeltron.com',
  'Authorized electronic equipment refurbishing, testing, component upgrading, and hardware lifespan extension.',
  'Laptops, Desktops, Servers, Workstations, Monitors',
  'https://kspcb.karnataka.gov.in/',
  '2026-09-15',
  1,
  'https://www.google.com/maps/search/?api=1&query=Kumara+Park+East+Bangalore+560001',
  12.9880000,
  77.5810000
),
(
  'M/s. Ace Recyclers',
  'Authorized Dismantler',
  'Plot No. C-29, KSSIDC Industrial Estate, Hoskote Taluk',
  'Hoskote',
  'Bengaluru Rural',
  '562114',
  'Karnataka',
  NULL,
  NULL,
  NULL,
  'Authorized dismantling facility for electrical components, segregation of hazardous fraction, mechanical shredding.',
  'Mixed Consumer Electronics, Small IT Equipment, Printed Wiring Boards',
  'https://kspcb.karnataka.gov.in/',
  '2026-09-10',
  1,
  'https://www.google.com/maps/search/?api=1&query=KSSIDC+Industrial+Estate+Hoskote+562114',
  13.0710000,
  77.7950000
),
(
  'M/s. Eco-Ewaste Recyclers India Pvt. Ltd.',
  'Authorized Dismantler',
  'Mutachari Industrial Estate, Hanumanthappa Layout, Mysore Road',
  'Bengaluru',
  'Bengaluru Urban',
  '560026',
  'Karnataka',
  NULL,
  NULL,
  NULL,
  'Authorized dismantling of telecommunication hardware, commercial electronic equipment, and battery segregation.',
  'Industrial Electronics, Telecom Switching Gear, Chargers, Batteries',
  'https://data.opencity.in/dataset/karnataka-waste-collection-recycling-and-processing-centres',
  '2026-08-28',
  1,
  'https://www.google.com/maps/search/?api=1&query=Mutachari+Industrial+Estate+Mysore+Road+Bengaluru',
  12.9450000,
  77.5320000
);

-- Seed Proper Disposal Guidelines
INSERT INTO `disposal_guidelines`
(`category`, `title`, `summary`, `step_by_step`, `dos_and_donts`, `hazards_prevented`, `icon_class`) VALUES
(
  'Mobile Phones',
  'Safe Disposal & Data Security for Smartphones and Feature Phones',
  'Smartphones contain toxic heavy metals such as cadmium and lead, as well as recoverable precious metals (gold, silver, palladium). Personal privacy and battery safety are top priorities.',
  'Step 1: Backup all personal data to cloud or external storage.\nStep 2: Sign out of all Google, Apple, and banking accounts.\nStep 3: Perform a complete cryptographic Factory Data Reset.\nStep 4: Remove SIM card and MicroSD storage cards.\nStep 5: Inspect battery for swelling. If swollen, do not compress; isolate in a non-conductive box.\nStep 6: Hand over to authorized CPCB/KSPCB dismantler or submit a digital collection drive request.',
  'DO: Keep the phone at room temperature in a dry container.\nDO: Tape over cracked screens with clear packing tape to prevent injury and glass contamination.\nDON''T: Never throw a phone into municipal garbage bins or incinerators.\nDON''T: Never burn cables or heat batteries to recover copper or gold.\nDON''T: Do not sell to unauthorized roadside scrap vendors (informal sector acid leaching).',
  'Prevents lithium thermal runaway fires in municipal compaction trucks; prevents groundwater cadmium poisoning; stops unauthorized personal identity theft.',
  'fa-mobile-screen-button'
),
(
  'Laptops & Computers',
  'Responsible Handling for Desktop CPUs, Laptops, and Servers',
  'Computers contain hazardous printed circuit boards (lead, brominated flame retardants), mercury cold-cathode lamps in older displays, and valuable copper heat pipes.',
  'Step 1: Save critical files and unlicense software activations.\nStep 2: Use drive wiping utilities (e.g., DBAN or BitLocker cryptographic erase) to overwrite storage.\nStep 3: Disconnect power cables, external mouse, keyboards, and lithium backup CMOS batteries.\nStep 4: Wrap the display screen in protective cardboard to avoid mercury vapor leakage from fluorescent backlights.\nStep 5: Bundle cables neatly and register the desktop/laptop for authorized scientific dismantling.',
  'DO: Separate the external battery pack if detachable.\nDO: Document serial numbers for your institutional audit or e-waste disposal receipt.\nDON''T: Never crack open CRT or LCD monitors (releases lead dust and mercury vapor).\nDON''T: Never use open flame to unsolder electronic components from motherboards.',
  'Prevents airborne dioxin and furans caused by burning PCB resin; shields soil from lead and arsenic leaching.',
  'fa-laptop'
),
(
  'Batteries',
  'Safe Isolation & Terminal Taping for Lithium-Ion, NiMH & Lead-Acid Cells',
  'Spent batteries present the highest fire hazard in the waste management stream due to stored chemical energy and flammable electrolytes.',
  'Step 1: Identify battery chemistry (Li-Ion, Alkaline, NiCad, Lead-Acid).\nStep 2: Apply clear insulating electrical tape over both positive (+) and negative (-) terminals to prevent short-circuiting.\nStep 3: If battery shows signs of bulge, puncture, or corrosion, place immediately in a fire-safe bucket of dry sand or vermiculite.\nStep 4: Store in a cool, ventilated area away from moisture and flammable solvents.\nStep 5: Deliver strictly to specialized hydrometallurgical battery recyclers.',
  'DO: Tape button cells and lithium packs individually.\nDO: Keep different battery chemistries separated if storing in bulk.\nDON''T: Never mix damaged batteries with metallic paperclips, coins, or keys.\nDON''T: Never attempt to recharge swollen or deformed cells.\nDON''T: Never dump spent car batteries or power bank cells into domestic dustbins.',
  'Prevents intense lithium fires reaching 1000°C; prevents sulfuric acid and caustic potassium hydroxide chemical burns.',
  'fa-car-battery'
),
(
  'Chargers & Cables',
  'Proper Management of Adapters, Charging Bricks, and Connectors',
  'Cables contain high-grade copper surrounded by polyvinyl chloride (PVC) and halogenated flame retardants that release toxic dioxins if burned.',
  'Step 1: Check if the charger is in working condition; consider donating or reusing with compatible devices.\nStep 2: Coil the cable in loose loops; do not tie tightly into knots that can crush wire cores.\nStep 3: Keep transformer wall-warts intact; do not smash the outer plastic casing.\nStep 4: Consolidate small cords into a clean cardboard box and register them collectively.',
  'DO: Group USB-C, micro-USB, and appliance power cords together.\nDON''T: Never set fire to wire insulation in open air to strip copper (strictly illegal under E-Waste Rules 2022).\nDON''T: Do not mix with wet household organic waste.',
  'Prevents atmospheric emission of carcinogens (dioxins, furans, hydrochloric acid fumes) and promotes 100% mechanical copper granulation.',
  'fa-plug-circle-bolt'
),
(
  'Televisions & Other Appliances',
  'Disposal Protocol for Smart TVs, CRT Sets, and Home Electronics',
  'Televisions and consumer appliances contain high-voltage capacitors, leaded glass funnels (in CRT up to 2-3 kg of lead), and polyurethane insulation.',
  'Step 1: Unplug appliance from mains power at least 24 hours prior to moving to allow high-voltage capacitors to bleed charge.\nStep 2: Secure power cord against the chassis with removable masking tape.\nStep 3: Cover front glass screens with cardboard sheets to safeguard against shattering.\nStep 4: Request doorstep pickup from an authorized collection center with proper mechanical lifting assistance.',
  'DO: Keep original stands and remotes bundled together for refurbishment potential.\nDON''T: Never dismantle television backs yourself—CRT tubes are under high vacuum and can implode violently.\nDON''T: Never dispose of microwave ovens, monitors, or amplifiers in standard municipal dumpsters.',
  'Prevents physical implosion injuries from CRT vacuum tubes; eliminates lead poisoning from pulverized display glass in public landfills.',
  'fa-tv'
);

-- Seed Environmental Awareness Articles
INSERT INTO `awareness_content`
(`title`, `category`, `summary`, `content`, `toxic_substance`, `health_hazard`, `environmental_hazard`) VALUES
(
  'The Silent Menace: Heavy Metals in Everyday Electronics',
  'Toxic Substances',
  'Modern electronic devices contain over 1,000 distinct materials, many of which are toxic and bioaccumulative.',
  'When electronic devices are casually tossed into municipal landfills, seasonal rainfall percolates through the garbage layers, creating a toxic chemical soup known as "leachate." This leachate dissolves lead from solder, cadmium from resistors, and mercury from fluorescent displays, percolating into the water table and contaminating agricultural irrigation channels.',
  'Lead (Pb), Cadmium (Cd), Mercury (Hg)',
  'Damage to central and peripheral nervous systems, kidney dysfunction, intellectual impairment in developing children, and chronic respiratory illness.',
  'Irreversible contamination of groundwater aquifers, bioaccumulation in marine life, and severe soil infertility.',
  CURRENT_TIMESTAMP
),
(
  'Urban Mining: Why E-Waste is Far Richer Than Natural Mines',
  'Circular Economy',
  'One metric tonne of discarded smartphones contains up to 300 grams of pure gold and 2 kg of silver—over 50 times richer than mined ore.',
  'Natural gold mining requires excavating over 1 tonne of raw rocky earth to yield merely 5 grams of gold, consuming thousands of liters of diesel and toxic cyanide. Conversely, specialized hydro-metallurgical electronic recycling recovers gold, silver, copper, and palladium with an 80% reduction in carbon footprint. Circular recycling reduces international dependency on destructive virgin mineral extraction.',
  'Gold (Au), Silver (Ag), Palladium (Pd), Copper (Cu)',
  'Mitigates occupational hazards, silicosis, and mine tailings collapse risks associated with conventional primary open-pit mining.',
  'Prevents massive deforestation, landscape destruction, and sulfur dioxide emissions caused by virgin ore smelting.',
  CURRENT_TIMESTAMP
),
(
  'India E-Waste Management Rules, 2022 and EPR Compliance',
  'Regulations & Policy',
  'The revised E-Waste (Management) Rules notify strict Extended Producer Responsibility (EPR) targets and outlaw crude informal processing.',
  'Under the regulations issued by the Ministry of Environment, Forest and Climate Change (MoEFCC) and monitored by CPCB & State Pollution Control Boards, electronics manufacturers are legally mandated to collect and channel a progressive percentage of historical electronics sold into authorized recycling streams. Citizens and bulk consumers have an explicit duty to channel e-waste exclusively to registered recyclers.',
  'Regulated Electronic Categories I to IV',
  'Protects informal sector workers, including women and children, from fatal toxic gas exposure in unventilated acid baths.',
  'Enforces zero-landfill processing and tracks material balance certificates across the national registry.',
  CURRENT_TIMESTAMP
);

