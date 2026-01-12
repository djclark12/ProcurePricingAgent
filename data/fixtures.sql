-- Fixtures for HEXPOL Procurement and Pricing Demo
-- Run via: python -m data.seed
-- Industrial manufacturing focus: rubber/polymer compounds, MRO, packaging, plus some office items

-- =============================================================================
-- ITEMS / SKUs
-- =============================================================================

CREATE TABLE items (
    sku TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL
);

INSERT INTO items (sku, name, category, description) VALUES
-- Raw Materials & Compounds
('RM-EPDM-70', 'EPDM Rubber Compound 70 Shore A', 'Raw Materials', 'Ethylene propylene diene monomer rubber, 70 durometer, 25kg bales'),
('RM-EPDM-50', 'EPDM Rubber Compound 50 Shore A', 'Raw Materials', 'Soft EPDM for sealing applications, 50 durometer, 25kg bales'),
('RM-NBR-60', 'NBR Rubber Compound 60 Shore A', 'Raw Materials', 'Nitrile butadiene rubber, oil-resistant, 60 durometer, 25kg bales'),
('RM-NBR-80', 'NBR Rubber Compound 80 Shore A', 'Raw Materials', 'Hard nitrile rubber for industrial gaskets, 80 durometer, 25kg bales'),
('RM-SBR-65', 'SBR Rubber Compound 65 Shore A', 'Raw Materials', 'Styrene-butadiene rubber, general purpose, 25kg bales'),
('RM-SILICONE-50', 'Silicone Rubber Compound 50 Shore A', 'Raw Materials', 'High-temp silicone rubber, food-grade, 10kg boxes'),
('RM-SILICONE-70', 'Silicone Rubber Compound 70 Shore A', 'Raw Materials', 'Medical-grade silicone, 70 durometer, 10kg boxes'),
('RM-FKM-75', 'Viton FKM Compound 75 Shore A', 'Raw Materials', 'Fluoroelastomer for extreme chemical/heat resistance, 5kg boxes'),
('RM-CB-N550', 'Carbon Black N550', 'Raw Materials', 'Reinforcing carbon black, 20kg bags, FEF grade'),
('RM-CB-N330', 'Carbon Black N330', 'Raw Materials', 'High abrasion furnace black, 20kg bags, HAF grade'),
('RM-ZNO-ACTIV', 'Zinc Oxide Activator', 'Raw Materials', 'Vulcanization activator, 25kg bags, 99.5% purity'),
('RM-SULFUR-OT', 'Sulfur Oil Treated', 'Raw Materials', 'Oil-treated sulfur for vulcanization, 25kg bags'),
('RM-STEARIC', 'Stearic Acid', 'Raw Materials', 'Processing aid and activator, 25kg bags, triple pressed'),
('RM-PLASTICIZER', 'DOP Plasticizer', 'Raw Materials', 'Dioctyl phthalate plasticizer, 200L drums'),
('RM-ANTIOXI-TMQ', 'Antioxidant TMQ', 'Raw Materials', 'Polymerized 2,2,4-trimethyl-1,2-dihydroquinoline, 25kg bags'),
-- MRO & Equipment
('MRO-BLADE-DIE', 'Die Cutting Blade Set', 'MRO', 'Precision die cutting blades for rubber sheet, set of 12'),
('MRO-SEAL-HYD', 'Hydraulic Cylinder Seal Kit', 'MRO', 'Complete seal kit for 100mm hydraulic cylinders, Viton'),
('MRO-SEAL-PUMP', 'Pump Seal Kit', 'MRO', 'Mechanical seal kit for chemical transfer pumps'),
('MRO-BELT-CONV', 'Conveyor Belt Section 2m', 'MRO', 'Heavy-duty rubber conveyor belt, 600mm width, 2m length'),
('MRO-BELT-V', 'V-Belt Industrial B68', 'MRO', 'Industrial V-belt, B68 profile, for mixer drives'),
('MRO-FILTER-HYD', 'Hydraulic Oil Filter Element', 'MRO', '10 micron filter element for press hydraulic systems'),
('MRO-FILTER-AIR', 'Compressed Air Filter', 'MRO', 'Coalescing filter for plant air system, 0.01 micron'),
('MRO-BEARING-6205', 'Ball Bearing 6205-2RS', 'MRO', 'Sealed ball bearing, 25x52x15mm, for mixer shafts'),
('MRO-BEARING-6310', 'Ball Bearing 6310-2RS', 'MRO', 'Heavy-duty sealed bearing, 50x110x27mm, for calenders'),
('MRO-PUMP-DOSING', 'Chemical Dosing Pump', 'MRO', 'Diaphragm dosing pump, 0-50 L/hr, chemical resistant'),
('MRO-VALVE-SOL', 'Solenoid Valve 1/2"', 'MRO', '2-way solenoid valve, 24VDC, stainless steel'),
('MRO-SENSOR-TEMP', 'Temperature Sensor PT100', 'MRO', 'RTD temperature sensor, -50 to 250°C, 4-wire'),
('MRO-MOTOR-1HP', 'Electric Motor 1HP', 'MRO', '3-phase induction motor, 1HP, 1750 RPM, TEFC'),
('MRO-COUPLING-JAW', 'Jaw Coupling Set', 'MRO', 'Flexible jaw coupling, size L100, with spider'),
-- Packaging
('PKG-PALLET-EUR', 'EUR Pallet', 'Packaging', 'Standard EUR pallet 1200x800mm, heat-treated, ISPM-15'),
('PKG-PALLET-US', 'US Standard Pallet', 'Packaging', 'GMA pallet 48x40 inches, heat-treated'),
('PKG-FILM-STRETCH', 'Stretch Wrap Film 500mm', 'Packaging', 'Machine-grade stretch film, 500mm x 1500m, 23 micron'),
('PKG-FILM-SHRINK', 'Shrink Wrap Film', 'Packaging', 'POF shrink film, 19 micron, 500mm x 1000m'),
('PKG-BOX-GAYLORD', 'Gaylord Box Heavy Duty', 'Packaging', 'Triple-wall corrugated, 48x40x36 inches, 1100 lb capacity'),
('PKG-BOX-EXPORT', 'Export Crate Wooden', 'Packaging', 'ISPM-15 certified wooden crate, 120x80x80cm'),
('PKG-BAG-POLY-25', 'Poly Bag 25kg Capacity', 'Packaging', 'Heavy-duty polyethylene bag for compound bales, 25kg rated'),
('PKG-BAG-VALVE', 'Valve Bag 25kg', 'Packaging', 'Multi-wall paper valve bag for powder products, 25kg'),
('PKG-DESICCANT-500', 'Desiccant Pack 500g', 'Packaging', 'Silica gel desiccant for moisture-sensitive shipments'),
('PKG-TAPE-STRAP', 'Strapping Tape 16mm', 'Packaging', 'Polypropylene strapping, 16mm x 2000m, 200kg break strength'),
('PKG-LABEL-HAZMAT', 'Hazmat Labels Class 9', 'Packaging', 'DOT hazmat labels, Class 9 miscellaneous, 100/roll'),
-- Safety & PPE
('PPE-GLOVE-CHEM', 'Chemical Resistant Gloves', 'Safety', 'Nitrile/neoprene blend, 15 mil, 12-pack'),
('PPE-GLOVE-HEAT', 'Heat Resistant Gloves', 'Safety', 'Kevlar/carbon fiber, rated to 500°F, pair'),
('PPE-GLOVE-CUT', 'Cut Resistant Gloves', 'Safety', 'ANSI A4 cut rating, polyurethane palm, 12-pack'),
('PPE-RESP-N95', 'N95 Respirator Masks', 'Safety', 'NIOSH-approved N95, box of 20, carbon dust rated'),
('PPE-RESP-HALF', 'Half-Face Respirator', 'Safety', 'Reusable half-face respirator with P100 cartridges'),
('PPE-GOGGLES-SPLASH', 'Splash-Proof Safety Goggles', 'Safety', 'Indirect vent, anti-fog, chemical splash rated'),
('PPE-SHIELD-FACE', 'Face Shield with Headgear', 'Safety', 'Full face shield, anti-fog, adjustable headgear'),
('PPE-APRON-CHEM', 'Chemical Resistant Apron', 'Safety', 'PVC-coated polyester, 35x45 inches'),
('PPE-BOOT-STEEL', 'Steel Toe Rubber Boots', 'Safety', 'Chemical resistant, steel toe, size range 7-13'),
('PPE-EARPLUGS', 'Foam Ear Plugs', 'Safety', 'NRR 32dB, disposable foam, 200 pair box'),
-- Office & IT
('OFF-LAPTOP-IND', 'Industrial Laptop Rugged', 'Office', 'Rugged laptop for plant floor, IP65, 14" display'),
('OFF-LAPTOP-STD', 'Business Laptop Standard', 'Office', 'Standard business laptop, 15.6" display, i7 processor'),
('OFF-PRINTER-LBL', 'Industrial Label Printer', 'Office', 'Thermal transfer label printer, 300 DPI, Ethernet'),
('OFF-PRINTER-MFP', 'Multifunction Printer', 'Office', 'Color laser MFP, 30 ppm, scan/copy/fax'),
('OFF-CHAIR-ERGO', 'Ergonomic Office Chair', 'Office', 'Adjustable ergonomic chair with lumbar support'),
('OFF-DESK-SIT', 'Sit-Stand Desk', 'Office', 'Electric height-adjustable desk, 60x30 inches'),
('OFF-MONITOR-27', 'Monitor 27 inch', 'Office', '27" 4K IPS monitor, USB-C hub, adjustable stand'),
('OFF-SCANNER-DOC', 'Document Scanner', 'Office', 'High-speed document scanner, 50 ppm, duplex');


-- =============================================================================
-- VENDORS
-- =============================================================================

CREATE TABLE vendors (
    vendor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region TEXT NOT NULL,
    rating REAL NOT NULL,
    reliability_score REAL NOT NULL,
    typical_lead_time_days INTEGER NOT NULL
);

INSERT INTO vendors (vendor_id, name, region, rating, reliability_score, typical_lead_time_days) VALUES
-- Primary Raw Material Suppliers
('VND-LANXESS', 'LANXESS Rubber Compounds', 'Global', 4.7, 94.0, 21),
('VND-KUMHO', 'Kumho Petrochemical', 'APAC', 4.3, 88.0, 28),
('VND-CABOT', 'Cabot Corporation', 'US-East', 4.5, 91.0, 14),
('VND-BRENNTAG', 'Brenntag Specialties', 'Global', 4.2, 87.0, 18),
('VND-EUROIND', 'EuroIndustrial GmbH', 'EU', 4.1, 85.0, 24),
-- Additional Chemical Suppliers
('VND-ARKEMA', 'Arkema Performance Materials', 'EU', 4.4, 90.0, 22),
('VND-SABIC', 'SABIC Polymers', 'APAC', 4.2, 86.0, 30),
('VND-SINOPEC', 'Sinopec Chemical', 'APAC', 3.9, 82.0, 35),
-- MRO Distributors (ship nationwide)
('VND-GRAINGER', 'Grainger Industrial', 'Global', 4.6, 93.0, 5),
('VND-MCMASTER', 'McMaster-Carr', 'Global', 4.8, 96.0, 3),
('VND-MOTION', 'Motion Industries', 'Global', 4.5, 92.0, 4),
('VND-FASTENAL', 'Fastenal Company', 'Global', 4.4, 91.0, 3),
-- Packaging Suppliers (ship nationwide)
('VND-ULINE', 'Uline Packaging', 'Global', 4.4, 90.0, 4),
('VND-INTPAPER', 'International Paper', 'Global', 4.3, 89.0, 7),
('VND-MONDI', 'Mondi Packaging', 'EU', 4.2, 87.0, 14),
-- Safety/PPE Suppliers (ship nationwide)
('VND-3M', '3M Safety Products', 'Global', 4.7, 95.0, 5),
('VND-HONEYWELL', 'Honeywell Safety', 'Global', 4.6, 93.0, 6);


-- =============================================================================
-- PRICE LISTS (vendor pricing for items)
-- =============================================================================

CREATE TABLE price_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id TEXT NOT NULL,
    item_sku TEXT NOT NULL,
    base_price REAL NOT NULL,
    moq INTEGER NOT NULL DEFAULT 1,
    volume_discount_threshold INTEGER NOT NULL DEFAULT 100,
    volume_discount_pct REAL NOT NULL DEFAULT 5.0,
    rush_surcharge_pct REAL NOT NULL DEFAULT 15.0,
    lead_time_days INTEGER NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (item_sku) REFERENCES items(sku)
);

-- Raw Materials (prices per kg or per unit as indicated)
INSERT INTO price_lists (vendor_id, item_sku, base_price, moq, volume_discount_threshold, volume_discount_pct, rush_surcharge_pct, lead_time_days) VALUES
('VND-LANXESS', 'RM-EPDM-70', 4.85, 500, 5000, 8.0, 15.0, 21),
('VND-KUMHO', 'RM-EPDM-70', 4.45, 1000, 10000, 10.0, 20.0, 28),
('VND-EUROIND', 'RM-EPDM-70', 4.65, 500, 5000, 7.0, 18.0, 24),
('VND-ARKEMA', 'RM-EPDM-70', 4.75, 750, 7500, 8.0, 16.0, 22),
('VND-LANXESS', 'RM-EPDM-50', 5.10, 500, 5000, 8.0, 15.0, 21),
('VND-KUMHO', 'RM-EPDM-50', 4.70, 1000, 10000, 10.0, 20.0, 28),
('VND-EUROIND', 'RM-EPDM-50', 4.90, 500, 5000, 7.0, 18.0, 24),
('VND-LANXESS', 'RM-NBR-60', 5.20, 500, 5000, 8.0, 15.0, 21),
('VND-KUMHO', 'RM-NBR-60', 4.80, 1000, 10000, 10.0, 20.0, 28),
('VND-ARKEMA', 'RM-NBR-60', 5.05, 750, 7500, 9.0, 17.0, 22),
('VND-LANXESS', 'RM-NBR-80', 5.85, 500, 5000, 8.0, 15.0, 21),
('VND-KUMHO', 'RM-NBR-80', 5.40, 1000, 10000, 10.0, 20.0, 28),
('VND-LANXESS', 'RM-SBR-65', 2.95, 1000, 10000, 10.0, 12.0, 18),
('VND-KUMHO', 'RM-SBR-65', 2.65, 2000, 20000, 12.0, 18.0, 28),
('VND-SINOPEC', 'RM-SBR-65', 2.35, 5000, 50000, 15.0, 25.0, 35),
('VND-LANXESS', 'RM-SILICONE-50', 18.50, 100, 1000, 6.0, 20.0, 24),
('VND-EUROIND', 'RM-SILICONE-50', 17.80, 200, 2000, 8.0, 22.0, 28),
('VND-ARKEMA', 'RM-SILICONE-50', 18.20, 150, 1500, 7.0, 20.0, 22),
('VND-LANXESS', 'RM-SILICONE-70', 19.80, 100, 1000, 6.0, 20.0, 24),
('VND-EUROIND', 'RM-SILICONE-70', 19.20, 200, 2000, 8.0, 22.0, 28),
('VND-LANXESS', 'RM-FKM-75', 85.00, 25, 250, 5.0, 25.0, 28),
('VND-ARKEMA', 'RM-FKM-75', 82.50, 50, 500, 6.0, 22.0, 24),
('VND-CABOT', 'RM-CB-N550', 1.45, 1000, 20000, 12.0, 10.0, 14),
('VND-BRENNTAG', 'RM-CB-N550', 1.52, 500, 10000, 10.0, 12.0, 18),
('VND-CABOT', 'RM-CB-N330', 1.55, 1000, 20000, 12.0, 10.0, 14),
('VND-BRENNTAG', 'RM-CB-N330', 1.62, 500, 10000, 10.0, 12.0, 18),
('VND-BRENNTAG', 'RM-ZNO-ACTIV', 2.85, 500, 5000, 8.0, 10.0, 14),
('VND-CABOT', 'RM-ZNO-ACTIV', 2.95, 250, 2500, 6.0, 12.0, 12),
('VND-BRENNTAG', 'RM-SULFUR-OT', 1.25, 500, 5000, 10.0, 8.0, 14),
('VND-CABOT', 'RM-SULFUR-OT', 1.32, 250, 2500, 8.0, 10.0, 12),
('VND-BRENNTAG', 'RM-STEARIC', 1.85, 500, 5000, 8.0, 8.0, 14),
('VND-CABOT', 'RM-STEARIC', 1.92, 250, 2500, 6.0, 10.0, 12),
('VND-BRENNTAG', 'RM-PLASTICIZER', 420.00, 5, 50, 6.0, 12.0, 18),
('VND-ARKEMA', 'RM-PLASTICIZER', 405.00, 10, 100, 8.0, 15.0, 22),
('VND-BRENNTAG', 'RM-ANTIOXI-TMQ', 12.50, 100, 1000, 8.0, 12.0, 18),
('VND-ARKEMA', 'RM-ANTIOXI-TMQ', 12.00, 150, 1500, 10.0, 15.0, 22);

-- MRO Items
INSERT INTO price_lists (vendor_id, item_sku, base_price, moq, volume_discount_threshold, volume_discount_pct, rush_surcharge_pct, lead_time_days) VALUES
('VND-MCMASTER', 'MRO-BLADE-DIE', 285.00, 1, 10, 8.0, 25.0, 3),
('VND-GRAINGER', 'MRO-BLADE-DIE', 295.00, 1, 10, 6.0, 20.0, 5),
('VND-MOTION', 'MRO-BLADE-DIE', 290.00, 2, 20, 7.0, 22.0, 4),
('VND-MCMASTER', 'MRO-SEAL-HYD', 145.00, 1, 20, 10.0, 30.0, 2),
('VND-GRAINGER', 'MRO-SEAL-HYD', 152.00, 1, 15, 8.0, 25.0, 4),
('VND-MOTION', 'MRO-SEAL-HYD', 148.00, 2, 25, 9.0, 28.0, 3),
('VND-MCMASTER', 'MRO-SEAL-PUMP', 210.00, 1, 15, 8.0, 25.0, 3),
('VND-GRAINGER', 'MRO-SEAL-PUMP', 225.00, 1, 10, 6.0, 20.0, 5),
('VND-MOTION', 'MRO-SEAL-PUMP', 218.00, 2, 20, 7.0, 22.0, 4),
('VND-GRAINGER', 'MRO-BELT-CONV', 420.00, 1, 5, 5.0, 18.0, 7),
('VND-EUROIND', 'MRO-BELT-CONV', 395.00, 2, 10, 7.0, 22.0, 21),
('VND-MOTION', 'MRO-BELT-CONV', 410.00, 1, 8, 6.0, 20.0, 6),
('VND-MCMASTER', 'MRO-BELT-V', 18.50, 5, 50, 12.0, 15.0, 2),
('VND-GRAINGER', 'MRO-BELT-V', 20.00, 5, 50, 10.0, 12.0, 4),
('VND-FASTENAL', 'MRO-BELT-V', 19.25, 10, 100, 15.0, 10.0, 3),
('VND-MCMASTER', 'MRO-FILTER-HYD', 38.50, 5, 50, 12.0, 15.0, 2),
('VND-GRAINGER', 'MRO-FILTER-HYD', 42.00, 5, 50, 10.0, 12.0, 4),
('VND-MOTION', 'MRO-FILTER-HYD', 40.00, 10, 100, 14.0, 10.0, 3),
('VND-MCMASTER', 'MRO-FILTER-AIR', 68.00, 3, 30, 10.0, 18.0, 2),
('VND-GRAINGER', 'MRO-FILTER-AIR', 72.00, 2, 20, 8.0, 15.0, 4),
('VND-MCMASTER', 'MRO-BEARING-6205', 12.80, 10, 100, 15.0, 10.0, 2),
('VND-GRAINGER', 'MRO-BEARING-6205', 14.20, 5, 50, 12.0, 8.0, 3),
('VND-MOTION', 'MRO-BEARING-6205', 13.50, 10, 100, 14.0, 10.0, 2),
('VND-MCMASTER', 'MRO-BEARING-6310', 28.50, 5, 50, 12.0, 12.0, 2),
('VND-GRAINGER', 'MRO-BEARING-6310', 31.00, 5, 50, 10.0, 10.0, 3),
('VND-MOTION', 'MRO-BEARING-6310', 29.80, 10, 100, 14.0, 10.0, 2),
('VND-GRAINGER', 'MRO-PUMP-DOSING', 1850.00, 1, 3, 5.0, 20.0, 10),
('VND-EUROIND', 'MRO-PUMP-DOSING', 1720.00, 1, 5, 6.0, 25.0, 18),
('VND-MOTION', 'MRO-PUMP-DOSING', 1780.00, 1, 3, 5.0, 22.0, 8),
('VND-MCMASTER', 'MRO-VALVE-SOL', 85.00, 5, 50, 10.0, 15.0, 2),
('VND-GRAINGER', 'MRO-VALVE-SOL', 92.00, 5, 50, 8.0, 12.0, 4),
('VND-FASTENAL', 'MRO-VALVE-SOL', 88.00, 10, 100, 12.0, 10.0, 3),
('VND-MCMASTER', 'MRO-SENSOR-TEMP', 45.00, 5, 50, 10.0, 12.0, 2),
('VND-GRAINGER', 'MRO-SENSOR-TEMP', 48.50, 5, 50, 8.0, 10.0, 4),
('VND-GRAINGER', 'MRO-MOTOR-1HP', 285.00, 1, 10, 6.0, 18.0, 7),
('VND-MOTION', 'MRO-MOTOR-1HP', 275.00, 1, 10, 8.0, 20.0, 5),
('VND-MCMASTER', 'MRO-COUPLING-JAW', 42.00, 5, 50, 12.0, 10.0, 2),
('VND-GRAINGER', 'MRO-COUPLING-JAW', 46.00, 5, 50, 10.0, 8.0, 4);

-- Packaging
INSERT INTO price_lists (vendor_id, item_sku, base_price, moq, volume_discount_threshold, volume_discount_pct, rush_surcharge_pct, lead_time_days) VALUES
('VND-ULINE', 'PKG-PALLET-EUR', 18.50, 20, 200, 12.0, 8.0, 4),
('VND-GRAINGER', 'PKG-PALLET-EUR', 21.00, 10, 100, 8.0, 10.0, 5),
('VND-INTPAPER', 'PKG-PALLET-EUR', 19.50, 25, 250, 10.0, 8.0, 7),
('VND-ULINE', 'PKG-PALLET-US', 16.50, 20, 200, 12.0, 8.0, 4),
('VND-INTPAPER', 'PKG-PALLET-US', 17.50, 25, 250, 10.0, 8.0, 7),
('VND-ULINE', 'PKG-FILM-STRETCH', 42.00, 10, 100, 15.0, 5.0, 3),
('VND-GRAINGER', 'PKG-FILM-STRETCH', 45.50, 5, 50, 10.0, 8.0, 4),
('VND-MONDI', 'PKG-FILM-STRETCH', 44.00, 15, 150, 12.0, 10.0, 14),
('VND-ULINE', 'PKG-FILM-SHRINK', 48.00, 10, 100, 15.0, 5.0, 3),
('VND-MONDI', 'PKG-FILM-SHRINK', 50.00, 15, 150, 12.0, 10.0, 14),
('VND-ULINE', 'PKG-BOX-GAYLORD', 28.50, 10, 100, 12.0, 10.0, 4),
('VND-GRAINGER', 'PKG-BOX-GAYLORD', 31.00, 5, 50, 8.0, 12.0, 5),
('VND-INTPAPER', 'PKG-BOX-GAYLORD', 29.50, 15, 150, 10.0, 10.0, 7),
('VND-ULINE', 'PKG-BOX-EXPORT', 125.00, 5, 50, 8.0, 15.0, 6),
('VND-INTPAPER', 'PKG-BOX-EXPORT', 135.00, 5, 50, 6.0, 12.0, 8),
('VND-MONDI', 'PKG-BOX-EXPORT', 118.00, 10, 100, 10.0, 18.0, 14),
('VND-ULINE', 'PKG-BAG-POLY-25', 0.85, 500, 5000, 18.0, 5.0, 3),
('VND-GRAINGER', 'PKG-BAG-POLY-25', 0.92, 250, 2500, 12.0, 8.0, 4),
('VND-MONDI', 'PKG-BAG-POLY-25', 0.88, 1000, 10000, 20.0, 10.0, 14),
('VND-ULINE', 'PKG-BAG-VALVE', 1.45, 500, 5000, 15.0, 5.0, 3),
('VND-INTPAPER', 'PKG-BAG-VALVE', 1.52, 500, 5000, 12.0, 8.0, 7),
('VND-ULINE', 'PKG-DESICCANT-500', 2.40, 50, 500, 15.0, 5.0, 3),
('VND-MCMASTER', 'PKG-DESICCANT-500', 2.65, 25, 250, 10.0, 8.0, 2),
('VND-ULINE', 'PKG-TAPE-STRAP', 85.00, 5, 50, 12.0, 8.0, 3),
('VND-GRAINGER', 'PKG-TAPE-STRAP', 92.00, 5, 50, 10.0, 10.0, 4),
('VND-ULINE', 'PKG-LABEL-HAZMAT', 45.00, 10, 100, 10.0, 5.0, 3),
('VND-GRAINGER', 'PKG-LABEL-HAZMAT', 48.00, 5, 50, 8.0, 8.0, 4);

-- Safety & PPE
INSERT INTO price_lists (vendor_id, item_sku, base_price, moq, volume_discount_threshold, volume_discount_pct, rush_surcharge_pct, lead_time_days) VALUES
('VND-GRAINGER', 'PPE-GLOVE-CHEM', 24.50, 10, 100, 12.0, 8.0, 4),
('VND-MCMASTER', 'PPE-GLOVE-CHEM', 22.80, 10, 100, 10.0, 10.0, 3),
('VND-ULINE', 'PPE-GLOVE-CHEM', 23.50, 20, 200, 15.0, 5.0, 4),
('VND-3M', 'PPE-GLOVE-CHEM', 21.50, 20, 200, 12.0, 8.0, 5),
('VND-HONEYWELL', 'PPE-GLOVE-CHEM', 22.00, 20, 200, 14.0, 6.0, 6),
('VND-GRAINGER', 'PPE-GLOVE-HEAT', 48.00, 5, 50, 10.0, 12.0, 4),
('VND-MCMASTER', 'PPE-GLOVE-HEAT', 45.00, 5, 50, 8.0, 15.0, 3),
('VND-3M', 'PPE-GLOVE-HEAT', 42.50, 10, 100, 12.0, 10.0, 5),
('VND-GRAINGER', 'PPE-GLOVE-CUT', 32.00, 10, 100, 12.0, 8.0, 4),
('VND-MCMASTER', 'PPE-GLOVE-CUT', 30.00, 10, 100, 10.0, 10.0, 3),
('VND-HONEYWELL', 'PPE-GLOVE-CUT', 29.00, 20, 200, 14.0, 6.0, 6),
('VND-GRAINGER', 'PPE-RESP-N95', 28.00, 5, 50, 10.0, 12.0, 3),
('VND-MCMASTER', 'PPE-RESP-N95', 26.50, 5, 50, 8.0, 15.0, 2),
('VND-3M', 'PPE-RESP-N95', 24.00, 10, 100, 12.0, 10.0, 5),
('VND-GRAINGER', 'PPE-RESP-HALF', 85.00, 2, 20, 8.0, 15.0, 4),
('VND-3M', 'PPE-RESP-HALF', 78.00, 5, 50, 10.0, 12.0, 5),
('VND-HONEYWELL', 'PPE-RESP-HALF', 82.00, 5, 50, 10.0, 12.0, 6),
('VND-GRAINGER', 'PPE-GOGGLES-SPLASH', 8.50, 20, 200, 15.0, 8.0, 4),
('VND-MCMASTER', 'PPE-GOGGLES-SPLASH', 7.80, 10, 100, 12.0, 10.0, 3),
('VND-3M', 'PPE-GOGGLES-SPLASH', 7.20, 25, 250, 18.0, 6.0, 5),
('VND-GRAINGER', 'PPE-SHIELD-FACE', 15.00, 10, 100, 12.0, 10.0, 4),
('VND-3M', 'PPE-SHIELD-FACE', 13.50, 20, 200, 15.0, 8.0, 5),
('VND-HONEYWELL', 'PPE-SHIELD-FACE', 14.00, 15, 150, 14.0, 8.0, 6),
('VND-GRAINGER', 'PPE-APRON-CHEM', 28.00, 10, 100, 10.0, 12.0, 4),
('VND-ULINE', 'PPE-APRON-CHEM', 25.50, 20, 200, 14.0, 8.0, 4),
('VND-GRAINGER', 'PPE-BOOT-STEEL', 85.00, 5, 50, 8.0, 15.0, 5),
('VND-MCMASTER', 'PPE-BOOT-STEEL', 82.00, 5, 50, 8.0, 18.0, 4),
('VND-HONEYWELL', 'PPE-BOOT-STEEL', 78.00, 10, 100, 10.0, 12.0, 6),
('VND-GRAINGER', 'PPE-EARPLUGS', 35.00, 5, 50, 15.0, 5.0, 3),
('VND-3M', 'PPE-EARPLUGS', 32.00, 10, 100, 18.0, 5.0, 5),
('VND-ULINE', 'PPE-EARPLUGS', 33.50, 10, 100, 16.0, 5.0, 4);

-- Office
INSERT INTO price_lists (vendor_id, item_sku, base_price, moq, volume_discount_threshold, volume_discount_pct, rush_surcharge_pct, lead_time_days) VALUES
('VND-GRAINGER', 'OFF-LAPTOP-IND', 2450.00, 1, 10, 5.0, 15.0, 10),
('VND-MCMASTER', 'OFF-LAPTOP-IND', 2380.00, 1, 5, 4.0, 18.0, 7),
('VND-GRAINGER', 'OFF-LAPTOP-STD', 1250.00, 1, 20, 8.0, 12.0, 7),
('VND-FASTENAL', 'OFF-LAPTOP-STD', 1180.00, 1, 15, 6.0, 15.0, 5),
('VND-GRAINGER', 'OFF-PRINTER-LBL', 685.00, 1, 5, 6.0, 12.0, 5),
('VND-ULINE', 'OFF-PRINTER-LBL', 650.00, 1, 10, 8.0, 10.0, 4),
('VND-GRAINGER', 'OFF-PRINTER-MFP', 420.00, 1, 10, 8.0, 12.0, 5),
('VND-FASTENAL', 'OFF-PRINTER-MFP', 395.00, 1, 10, 6.0, 15.0, 4),
('VND-GRAINGER', 'OFF-CHAIR-ERGO', 295.00, 5, 50, 10.0, 15.0, 8),
('VND-ULINE', 'OFF-CHAIR-ERGO', 275.00, 10, 100, 12.0, 12.0, 6),
('VND-FASTENAL', 'OFF-CHAIR-ERGO', 285.00, 5, 50, 10.0, 12.0, 5),
('VND-GRAINGER', 'OFF-DESK-SIT', 485.00, 1, 10, 6.0, 18.0, 10),
('VND-ULINE', 'OFF-DESK-SIT', 465.00, 1, 10, 8.0, 15.0, 8),
('VND-GRAINGER', 'OFF-MONITOR-27', 385.00, 1, 10, 8.0, 12.0, 5),
('VND-FASTENAL', 'OFF-MONITOR-27', 365.00, 1, 15, 10.0, 15.0, 4),
('VND-GRAINGER', 'OFF-SCANNER-DOC', 295.00, 1, 5, 5.0, 12.0, 5),
('VND-ULINE', 'OFF-SCANNER-DOC', 280.00, 1, 10, 8.0, 10.0, 4);


-- =============================================================================
-- COST BASIS (for pricing agent - what HEXPOL pays/should pay)
-- =============================================================================

CREATE TABLE cost_basis (
    sku TEXT PRIMARY KEY,
    unit_cost REAL NOT NULL,
    cost_type TEXT NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    last_updated TEXT NOT NULL,
    FOREIGN KEY (sku) REFERENCES items(sku)
);

INSERT INTO cost_basis (sku, unit_cost, cost_type, currency, last_updated) VALUES
-- Raw Materials
('RM-EPDM-70', 4.25, 'last_purchase', 'USD', '2025-12-01'),
('RM-EPDM-50', 4.50, 'last_purchase', 'USD', '2025-12-01'),
('RM-NBR-60', 4.60, 'last_purchase', 'USD', '2025-12-01'),
('RM-NBR-80', 5.20, 'last_purchase', 'USD', '2025-11-20'),
('RM-SBR-65', 2.45, 'last_purchase', 'USD', '2025-11-15'),
('RM-SILICONE-50', 16.20, 'should_cost', 'USD', '2025-12-10'),
('RM-SILICONE-70', 17.80, 'should_cost', 'USD', '2025-12-10'),
('RM-FKM-75', 78.00, 'should_cost', 'USD', '2025-11-25'),
('RM-CB-N550', 1.32, 'average', 'USD', '2025-12-05'),
('RM-CB-N330', 1.42, 'average', 'USD', '2025-12-05'),
('RM-ZNO-ACTIV', 2.65, 'average', 'USD', '2025-12-05'),
('RM-SULFUR-OT', 1.15, 'average', 'USD', '2025-12-05'),
('RM-STEARIC', 1.70, 'average', 'USD', '2025-12-05'),
('RM-PLASTICIZER', 380.00, 'last_purchase', 'USD', '2025-11-20'),
('RM-ANTIOXI-TMQ', 11.20, 'average', 'USD', '2025-12-05'),
-- MRO
('MRO-BLADE-DIE', 245.00, 'last_purchase', 'USD', '2025-11-20'),
('MRO-SEAL-HYD', 125.00, 'should_cost', 'USD', '2025-12-01'),
('MRO-SEAL-PUMP', 185.00, 'should_cost', 'USD', '2025-12-01'),
('MRO-BELT-CONV', 355.00, 'last_purchase', 'USD', '2025-10-15'),
('MRO-BELT-V', 16.50, 'average', 'USD', '2025-12-10'),
('MRO-FILTER-HYD', 32.00, 'average', 'USD', '2025-12-10'),
('MRO-FILTER-AIR', 58.00, 'average', 'USD', '2025-12-10'),
('MRO-BEARING-6205', 10.50, 'average', 'USD', '2025-12-10'),
('MRO-BEARING-6310', 25.00, 'average', 'USD', '2025-12-10'),
('MRO-PUMP-DOSING', 1580.00, 'should_cost', 'USD', '2025-11-01'),
('MRO-VALVE-SOL', 75.00, 'average', 'USD', '2025-12-10'),
('MRO-SENSOR-TEMP', 40.00, 'average', 'USD', '2025-12-10'),
('MRO-MOTOR-1HP', 250.00, 'should_cost', 'USD', '2025-11-15'),
('MRO-COUPLING-JAW', 38.00, 'average', 'USD', '2025-12-10'),
-- Packaging
('PKG-PALLET-EUR', 15.80, 'average', 'USD', '2025-12-15'),
('PKG-PALLET-US', 14.50, 'average', 'USD', '2025-12-15'),
('PKG-FILM-STRETCH', 36.00, 'last_purchase', 'USD', '2025-12-10'),
('PKG-FILM-SHRINK', 42.00, 'last_purchase', 'USD', '2025-12-10'),
('PKG-BOX-GAYLORD', 24.00, 'average', 'USD', '2025-12-01'),
('PKG-BOX-EXPORT', 108.00, 'should_cost', 'USD', '2025-11-20'),
('PKG-BAG-POLY-25', 0.72, 'last_purchase', 'USD', '2025-12-15'),
('PKG-BAG-VALVE', 1.32, 'average', 'USD', '2025-12-10'),
('PKG-DESICCANT-500', 2.10, 'average', 'USD', '2025-12-10'),
('PKG-TAPE-STRAP', 75.00, 'average', 'USD', '2025-12-10'),
('PKG-LABEL-HAZMAT', 38.00, 'average', 'USD', '2025-12-10'),
-- Safety
('PPE-GLOVE-CHEM', 19.50, 'average', 'USD', '2025-12-15'),
('PPE-GLOVE-HEAT', 38.00, 'average', 'USD', '2025-12-10'),
('PPE-GLOVE-CUT', 26.00, 'average', 'USD', '2025-12-10'),
('PPE-RESP-N95', 22.00, 'average', 'USD', '2025-12-15'),
('PPE-RESP-HALF', 68.00, 'should_cost', 'USD', '2025-12-01'),
('PPE-GOGGLES-SPLASH', 6.50, 'average', 'USD', '2025-12-10'),
('PPE-SHIELD-FACE', 11.50, 'average', 'USD', '2025-12-10'),
('PPE-APRON-CHEM', 22.00, 'average', 'USD', '2025-12-10'),
('PPE-BOOT-STEEL', 68.00, 'average', 'USD', '2025-12-05'),
('PPE-EARPLUGS', 28.00, 'average', 'USD', '2025-12-10'),
-- Office
('OFF-LAPTOP-IND', 2150.00, 'last_purchase', 'USD', '2025-11-01'),
('OFF-LAPTOP-STD', 1050.00, 'last_purchase', 'USD', '2025-11-15'),
('OFF-PRINTER-LBL', 580.00, 'should_cost', 'USD', '2025-12-01'),
('OFF-PRINTER-MFP', 350.00, 'average', 'USD', '2025-12-05'),
('OFF-CHAIR-ERGO', 245.00, 'average', 'USD', '2025-12-10'),
('OFF-DESK-SIT', 420.00, 'should_cost', 'USD', '2025-11-20'),
('OFF-MONITOR-27', 320.00, 'average', 'USD', '2025-12-10'),
('OFF-SCANNER-DOC', 250.00, 'average', 'USD', '2025-12-05');


-- =============================================================================
-- COMPETITOR PRICES (for pricing agent - market intelligence)
-- =============================================================================

CREATE TABLE competitor_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL,
    competitor_name TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    source TEXT NOT NULL,
    observed_date TEXT NOT NULL,
    FOREIGN KEY (sku) REFERENCES items(sku)
);

INSERT INTO competitor_prices (sku, competitor_name, price, currency, source, observed_date) VALUES
-- EPDM Rubber (key compound - track competitor pricing closely)
('RM-EPDM-70', 'Trelleborg', 5.85, 'USD', 'quote', '2025-12-18'),
('RM-EPDM-70', 'Freudenberg', 5.95, 'USD', 'catalog', '2025-12-15'),
('RM-EPDM-70', 'Parker Hannifin', 5.75, 'USD', 'distributor', '2025-12-20'),
('RM-EPDM-70', 'NOK Corporation', 5.45, 'USD', 'quote', '2025-12-12'),
('RM-EPDM-50', 'Trelleborg', 6.20, 'USD', 'quote', '2025-12-18'),
('RM-EPDM-50', 'Freudenberg', 6.35, 'USD', 'catalog', '2025-12-15'),
-- NBR Rubber
('RM-NBR-60', 'Trelleborg', 6.40, 'USD', 'quote', '2025-12-18'),
('RM-NBR-60', 'Freudenberg', 6.55, 'USD', 'catalog', '2025-12-15'),
('RM-NBR-60', 'SKF Sealing', 6.25, 'USD', 'distributor', '2025-12-20'),
('RM-NBR-80', 'Trelleborg', 7.20, 'USD', 'quote', '2025-12-18'),
('RM-NBR-80', 'Parker Hannifin', 7.05, 'USD', 'catalog', '2025-12-15'),
-- Silicone Rubber
('RM-SILICONE-50', 'Momentive', 22.50, 'USD', 'quote', '2025-12-18'),
('RM-SILICONE-50', 'Wacker', 23.00, 'USD', 'catalog', '2025-12-15'),
('RM-SILICONE-50', 'Dow Corning', 21.80, 'USD', 'distributor', '2025-12-20'),
('RM-SILICONE-70', 'Momentive', 24.50, 'USD', 'quote', '2025-12-18'),
('RM-SILICONE-70', 'Wacker', 25.00, 'USD', 'catalog', '2025-12-15'),
-- Viton FKM (high-value specialty)
('RM-FKM-75', 'DuPont', 105.00, 'USD', 'catalog', '2025-12-20'),
('RM-FKM-75', 'Solvay', 102.00, 'USD', 'quote', '2025-12-18'),
('RM-FKM-75', 'Daikin', 98.00, 'USD', 'distributor', '2025-12-15'),
-- Carbon Black
('RM-CB-N550', 'Orion Engineered Carbons', 1.68, 'USD', 'market_report', '2025-12-20'),
('RM-CB-N550', 'Birla Carbon', 1.72, 'USD', 'quote', '2025-12-15'),
('RM-CB-N550', 'Continental Carbon', 1.65, 'USD', 'catalog', '2025-12-18'),
('RM-CB-N330', 'Orion Engineered Carbons', 1.78, 'USD', 'market_report', '2025-12-20'),
('RM-CB-N330', 'Birla Carbon', 1.82, 'USD', 'quote', '2025-12-15'),
-- Hydraulic Seals (aftermarket pricing)
('MRO-SEAL-HYD', 'SKF', 185.00, 'USD', 'catalog', '2025-12-20'),
('MRO-SEAL-HYD', 'Parker', 192.00, 'USD', 'distributor', '2025-12-18'),
('MRO-SEAL-HYD', 'Trelleborg', 178.00, 'USD', 'quote', '2025-12-15'),
('MRO-SEAL-PUMP', 'Flowserve', 285.00, 'USD', 'catalog', '2025-12-20'),
('MRO-SEAL-PUMP', 'John Crane', 295.00, 'USD', 'distributor', '2025-12-18'),
-- Bearings
('MRO-BEARING-6205', 'SKF', 18.50, 'USD', 'catalog', '2025-12-20'),
('MRO-BEARING-6205', 'NSK', 17.80, 'USD', 'distributor', '2025-12-18'),
('MRO-BEARING-6205', 'Timken', 19.00, 'USD', 'quote', '2025-12-15'),
('MRO-BEARING-6310', 'SKF', 42.00, 'USD', 'catalog', '2025-12-20'),
('MRO-BEARING-6310', 'NSK', 40.50, 'USD', 'distributor', '2025-12-18'),
-- EUR Pallets (commodity - track for resale)
('PKG-PALLET-EUR', 'CHEP Rental', 22.50, 'USD', 'contract', '2025-12-01'),
('PKG-PALLET-EUR', 'PECO Pallet', 21.00, 'USD', 'catalog', '2025-12-15'),
('PKG-PALLET-EUR', 'Brambles', 23.00, 'USD', 'quote', '2025-12-10'),
-- Safety/PPE
('PPE-GLOVE-CHEM', 'Ansell', 28.00, 'USD', 'catalog', '2025-12-20'),
('PPE-GLOVE-CHEM', 'Showa', 26.50, 'USD', 'distributor', '2025-12-18'),
('PPE-RESP-N95', '3M (competitor)', 32.00, 'USD', 'catalog', '2025-12-20'),
('PPE-RESP-N95', 'Moldex', 29.00, 'USD', 'distributor', '2025-12-18'),
('PPE-RESP-HALF', '3M (competitor)', 95.00, 'USD', 'catalog', '2025-12-20'),
('PPE-RESP-HALF', 'MSA Safety', 98.00, 'USD', 'distributor', '2025-12-18');


-- =============================================================================
-- DEMAND NOTES (signals for pricing decisions)
-- =============================================================================

CREATE TABLE demand_notes (
    sku TEXT PRIMARY KEY,
    signal TEXT NOT NULL,
    notes TEXT,
    last_updated TEXT NOT NULL,
    FOREIGN KEY (sku) REFERENCES items(sku)
);

INSERT INTO demand_notes (sku, signal, notes, last_updated) VALUES
-- Raw Materials
('RM-EPDM-70', 'high demand', 'Automotive sealing orders up 20% YoY, EV battery gasket demand surge', '2025-12-20'),
('RM-EPDM-50', 'high demand', 'Soft sealing applications growing in HVAC sector', '2025-12-18'),
('RM-NBR-60', 'high demand', 'Oil & gas sector recovery driving hydraulic seal demand', '2025-12-18'),
('RM-NBR-80', 'normal', 'Industrial gasket demand steady', '2025-12-15'),
('RM-SBR-65', 'normal', 'Steady conveyor belt replacement cycle', '2025-12-15'),
('RM-SILICONE-50', 'high demand', 'Medical device and food processing applications growing', '2025-12-20'),
('RM-SILICONE-70', 'high demand', 'Medical-grade applications surge post-pandemic', '2025-12-20'),
('RM-FKM-75', 'high demand', 'Aerospace and chemical processing orders strong', '2025-12-18'),
('RM-CB-N550', 'normal', 'Stable reinforcement filler consumption', '2025-12-10'),
('RM-CB-N330', 'normal', 'Consistent tire and belt production', '2025-12-10'),
('RM-ZNO-ACTIV', 'normal', 'Consistent vulcanization demand', '2025-12-10'),
('RM-SULFUR-OT', 'normal', 'Steady curing agent consumption', '2025-12-10'),
('RM-STEARIC', 'normal', 'Processing aid demand stable', '2025-12-10'),
('RM-PLASTICIZER', 'slow-moving', 'Some customers switching to bio-based alternatives', '2025-12-05'),
('RM-ANTIOXI-TMQ', 'normal', 'Consistent additive consumption', '2025-12-10'),
-- MRO
('MRO-BLADE-DIE', 'normal', 'Regular replacement cycle', '2025-12-15'),
('MRO-SEAL-HYD', 'high demand', 'Plant maintenance backlog being addressed', '2025-12-18'),
('MRO-SEAL-PUMP', 'normal', 'Scheduled maintenance cycle', '2025-12-15'),
('MRO-BELT-CONV', 'slow-moving', 'Recent belt replacements completed, low near-term need', '2025-12-10'),
('MRO-BELT-V', 'normal', 'Mixer drive maintenance steady', '2025-12-15'),
('MRO-FILTER-HYD', 'high demand', 'Quarterly PM cycle approaching', '2025-12-20'),
('MRO-FILTER-AIR', 'normal', 'Routine air system maintenance', '2025-12-15'),
('MRO-BEARING-6205', 'normal', 'Steady mixer maintenance', '2025-12-15'),
('MRO-BEARING-6310', 'normal', 'Calender maintenance on schedule', '2025-12-15'),
('MRO-PUMP-DOSING', 'slow-moving', 'Capital expense freeze, deferrals expected', '2025-12-01'),
('MRO-VALVE-SOL', 'normal', 'Process automation steady', '2025-12-15'),
('MRO-SENSOR-TEMP', 'high demand', 'Process monitoring upgrades underway', '2025-12-18'),
('MRO-MOTOR-1HP', 'slow-moving', 'No motor replacements planned', '2025-12-10'),
('MRO-COUPLING-JAW', 'normal', 'Drive system maintenance cycle', '2025-12-15'),
-- Packaging
('PKG-PALLET-EUR', 'high demand', 'Q1 shipment surge for European automotive customers', '2025-12-20'),
('PKG-PALLET-US', 'normal', 'Domestic shipments steady', '2025-12-15'),
('PKG-FILM-STRETCH', 'normal', 'Consistent wrapping consumption', '2025-12-15'),
('PKG-FILM-SHRINK', 'normal', 'Bundling operations steady', '2025-12-15'),
('PKG-BOX-GAYLORD', 'normal', 'Stable bulk shipping needs', '2025-12-10'),
('PKG-BOX-EXPORT', 'high demand', 'Export orders to Asia increasing', '2025-12-18'),
('PKG-BAG-POLY-25', 'high demand', 'Compound bale shipments increasing', '2025-12-18'),
('PKG-BAG-VALVE', 'normal', 'Powder product packaging steady', '2025-12-15'),
('PKG-DESICCANT-500', 'normal', 'Moisture control consistent', '2025-12-15'),
('PKG-TAPE-STRAP', 'normal', 'Pallet securing steady', '2025-12-15'),
('PKG-LABEL-HAZMAT', 'normal', 'Regulated shipments consistent', '2025-12-15'),
-- Safety
('PPE-GLOVE-CHEM', 'high demand', 'Safety stock increase mandated', '2025-12-18'),
('PPE-GLOVE-HEAT', 'normal', 'Hot process PPE consumption steady', '2025-12-15'),
('PPE-GLOVE-CUT', 'normal', 'Cutting operations PPE steady', '2025-12-15'),
('PPE-RESP-N95', 'normal', 'Carbon dust protection needs steady', '2025-12-15'),
('PPE-RESP-HALF', 'slow-moving', 'Full inventory from recent purchase', '2025-12-10'),
('PPE-GOGGLES-SPLASH', 'normal', 'Chemical handling PPE consistent', '2025-12-15'),
('PPE-SHIELD-FACE', 'normal', 'Face protection steady', '2025-12-15'),
('PPE-APRON-CHEM', 'normal', 'Chemical protection steady', '2025-12-15'),
('PPE-BOOT-STEEL', 'slow-moving', 'Recent safety footwear refresh completed', '2025-12-05'),
('PPE-EARPLUGS', 'high demand', 'Mixer area hearing protection usage up', '2025-12-18'),
-- Office
('OFF-LAPTOP-IND', 'slow-moving', 'IT refresh completed last quarter', '2025-12-01'),
('OFF-LAPTOP-STD', 'normal', 'Office equipment rotation cycle', '2025-12-15'),
('OFF-PRINTER-LBL', 'normal', 'Steady label printing for QC/shipping', '2025-12-15'),
('OFF-PRINTER-MFP', 'slow-moving', 'Recent MFP upgrade completed', '2025-12-05'),
('OFF-CHAIR-ERGO', 'normal', 'Office furniture replacement cycle', '2025-12-15'),
('OFF-DESK-SIT', 'high demand', 'Ergonomic workplace initiative', '2025-12-18'),
('OFF-MONITOR-27', 'normal', 'Display refresh cycle', '2025-12-15'),
('OFF-SCANNER-DOC', 'slow-moving', 'Document digitization complete', '2025-12-05');


-- Create indexes for common queries
CREATE INDEX idx_price_lists_item ON price_lists(item_sku);
CREATE INDEX idx_price_lists_vendor ON price_lists(vendor_id);
CREATE INDEX idx_competitor_prices_sku ON competitor_prices(sku);


-- =============================================================================
-- PURCHASE HISTORY (for analytics/insights)
-- =============================================================================

CREATE TABLE purchase_history (
    po_id TEXT PRIMARY KEY,
    item_sku TEXT NOT NULL,
    vendor_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_amount REAL NOT NULL,
    order_date TEXT NOT NULL,
    delivery_date TEXT,
    days_late INTEGER DEFAULT 0,
    category TEXT NOT NULL,
    FOREIGN KEY (item_sku) REFERENCES items(sku),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- 12 months of purchase history for analytics
INSERT INTO purchase_history (po_id, item_sku, vendor_id, quantity, unit_price, total_amount, order_date, delivery_date, days_late, category) VALUES
-- Raw Materials purchases (January - June 2025)
('PO-2025-001', 'RM-EPDM-70', 'VND-LANXESS', 5000, 4.65, 23250.00, '2025-01-10', '2025-01-31', 0, 'Raw Materials'),
('PO-2025-002', 'RM-EPDM-70', 'VND-KUMHO', 10000, 4.25, 42500.00, '2025-02-15', '2025-03-15', 0, 'Raw Materials'),
('PO-2025-003', 'RM-NBR-60', 'VND-LANXESS', 3000, 5.10, 15300.00, '2025-01-20', '2025-02-10', 0, 'Raw Materials'),
('PO-2025-004', 'RM-NBR-60', 'VND-KUMHO', 5000, 4.70, 23500.00, '2025-03-05', '2025-04-05', 3, 'Raw Materials'),
('PO-2025-005', 'RM-SBR-65', 'VND-KUMHO', 15000, 2.55, 38250.00, '2025-02-01', '2025-02-28', 0, 'Raw Materials'),
('PO-2025-006', 'RM-CB-N550', 'VND-CABOT', 20000, 1.38, 27600.00, '2025-01-25', '2025-02-08', 0, 'Raw Materials'),
('PO-2025-007', 'RM-CB-N550', 'VND-BRENNTAG', 15000, 1.45, 21750.00, '2025-03-15', '2025-04-03', 1, 'Raw Materials'),
('PO-2025-008', 'RM-SILICONE-50', 'VND-LANXESS', 500, 17.80, 8900.00, '2025-02-10', '2025-03-05', 0, 'Raw Materials'),
('PO-2025-009', 'RM-ZNO-ACTIV', 'VND-BRENNTAG', 3000, 2.75, 8250.00, '2025-01-15', '2025-01-29', 0, 'Raw Materials'),
('PO-2025-010', 'RM-EPDM-50', 'VND-LANXESS', 4000, 4.90, 19600.00, '2025-03-20', '2025-04-10', 0, 'Raw Materials'),
('PO-2025-011', 'RM-NBR-80', 'VND-KUMHO', 3000, 5.30, 15900.00, '2025-04-05', '2025-05-05', 2, 'Raw Materials'),
('PO-2025-012', 'RM-FKM-75', 'VND-ARKEMA', 100, 80.00, 8000.00, '2025-04-15', '2025-05-10', 0, 'Raw Materials'),
('PO-2025-013', 'RM-CB-N330', 'VND-CABOT', 18000, 1.48, 26640.00, '2025-04-20', '2025-05-04', 0, 'Raw Materials'),
('PO-2025-014', 'RM-SULFUR-OT', 'VND-BRENNTAG', 2000, 1.20, 2400.00, '2025-05-01', '2025-05-15', 0, 'Raw Materials'),
('PO-2025-015', 'RM-STEARIC', 'VND-BRENNTAG', 2500, 1.78, 4450.00, '2025-05-10', '2025-05-24', 0, 'Raw Materials'),
('PO-2025-016', 'RM-PLASTICIZER', 'VND-BRENNTAG', 20, 395.00, 7900.00, '2025-05-15', '2025-06-02', 0, 'Raw Materials'),
('PO-2025-017', 'RM-ANTIOXI-TMQ', 'VND-ARKEMA', 500, 11.50, 5750.00, '2025-05-20', '2025-06-12', 0, 'Raw Materials'),
('PO-2025-018', 'RM-SILICONE-70', 'VND-EUROIND', 400, 18.50, 7400.00, '2025-06-01', '2025-06-28', 0, 'Raw Materials'),
-- Raw Materials purchases (July - December 2025)
('PO-2025-019', 'RM-EPDM-70', 'VND-LANXESS', 7500, 4.55, 34125.00, '2025-07-15', '2025-08-05', 0, 'Raw Materials'),
('PO-2025-020', 'RM-EPDM-70', 'VND-KUMHO', 12000, 4.20, 50400.00, '2025-08-20', '2025-09-20', 2, 'Raw Materials'),
('PO-2025-021', 'RM-EPDM-70', 'VND-EUROIND', 6000, 4.45, 26700.00, '2025-10-01', '2025-10-25', 0, 'Raw Materials'),
('PO-2025-022', 'RM-EPDM-70', 'VND-ARKEMA', 8000, 4.50, 36000.00, '2025-11-15', '2025-12-08', 0, 'Raw Materials'),
('PO-2025-023', 'RM-NBR-60', 'VND-LANXESS', 4000, 5.05, 20200.00, '2025-07-20', '2025-08-10', 0, 'Raw Materials'),
('PO-2025-024', 'RM-NBR-60', 'VND-ARKEMA', 5500, 4.85, 26675.00, '2025-09-10', '2025-10-05', 0, 'Raw Materials'),
('PO-2025-025', 'RM-NBR-60', 'VND-LANXESS', 4500, 5.00, 22500.00, '2025-11-10', '2025-12-01', 0, 'Raw Materials'),
('PO-2025-026', 'RM-SBR-65', 'VND-LANXESS', 10000, 2.75, 27500.00, '2025-08-01', '2025-08-20', 0, 'Raw Materials'),
('PO-2025-027', 'RM-SBR-65', 'VND-SINOPEC', 25000, 2.25, 56250.00, '2025-10-15', '2025-11-20', 0, 'Raw Materials'),
('PO-2025-028', 'RM-SILICONE-50', 'VND-EUROIND', 800, 17.20, 13760.00, '2025-09-01', '2025-09-28', 0, 'Raw Materials'),
('PO-2025-029', 'RM-SILICONE-50', 'VND-ARKEMA', 600, 17.50, 10500.00, '2025-11-20', '2025-12-15', 0, 'Raw Materials'),
('PO-2025-030', 'RM-CB-N550', 'VND-CABOT', 25000, 1.35, 33750.00, '2025-08-25', '2025-09-08', 0, 'Raw Materials'),
('PO-2025-031', 'RM-CB-N550', 'VND-CABOT', 22000, 1.32, 29040.00, '2025-11-01', '2025-11-15', 0, 'Raw Materials'),
('PO-2025-032', 'RM-ZNO-ACTIV', 'VND-CABOT', 2500, 2.80, 7000.00, '2025-09-20', '2025-10-01', 0, 'Raw Materials'),
('PO-2025-033', 'RM-EPDM-50', 'VND-KUMHO', 6000, 4.55, 27300.00, '2025-10-05', '2025-11-05', 1, 'Raw Materials'),
('PO-2025-034', 'RM-NBR-80', 'VND-LANXESS', 4000, 5.65, 22600.00, '2025-11-05', '2025-11-26', 0, 'Raw Materials'),
('PO-2025-035', 'RM-FKM-75', 'VND-LANXESS', 150, 82.00, 12300.00, '2025-10-20', '2025-11-18', 0, 'Raw Materials'),
('PO-2025-036', 'RM-CB-N330', 'VND-BRENNTAG', 12000, 1.55, 18600.00, '2025-11-15', '2025-12-03', 0, 'Raw Materials'),
-- MRO purchases (January - June 2025)
('PO-2025-037', 'MRO-BLADE-DIE', 'VND-MCMASTER', 15, 270.00, 4050.00, '2025-01-10', '2025-01-13', 0, 'MRO'),
('PO-2025-038', 'MRO-SEAL-HYD', 'VND-MCMASTER', 40, 138.00, 5520.00, '2025-01-20', '2025-01-22', 0, 'MRO'),
('PO-2025-039', 'MRO-FILTER-HYD', 'VND-MCMASTER', 80, 36.00, 2880.00, '2025-02-05', '2025-02-07', 0, 'MRO'),
('PO-2025-040', 'MRO-BEARING-6205', 'VND-MCMASTER', 150, 11.80, 1770.00, '2025-02-15', '2025-02-17', 0, 'MRO'),
('PO-2025-041', 'MRO-BELT-CONV', 'VND-GRAINGER', 8, 405.00, 3240.00, '2025-03-01', '2025-03-08', 0, 'MRO'),
('PO-2025-042', 'MRO-PUMP-DOSING', 'VND-MOTION', 2, 1720.00, 3440.00, '2025-03-15', '2025-03-23', 0, 'MRO'),
('PO-2025-043', 'MRO-SEAL-PUMP', 'VND-MCMASTER', 25, 200.00, 5000.00, '2025-04-10', '2025-04-13', 0, 'MRO'),
('PO-2025-044', 'MRO-BELT-V', 'VND-FASTENAL', 50, 18.00, 900.00, '2025-04-20', '2025-04-23', 0, 'MRO'),
('PO-2025-045', 'MRO-FILTER-AIR', 'VND-MCMASTER', 30, 65.00, 1950.00, '2025-05-05', '2025-05-07', 0, 'MRO'),
('PO-2025-046', 'MRO-VALVE-SOL', 'VND-GRAINGER', 20, 88.00, 1760.00, '2025-05-15', '2025-05-19', 0, 'MRO'),
('PO-2025-047', 'MRO-SENSOR-TEMP', 'VND-MCMASTER', 40, 43.00, 1720.00, '2025-06-01', '2025-06-03', 0, 'MRO'),
('PO-2025-048', 'MRO-BEARING-6310', 'VND-MOTION', 30, 28.00, 840.00, '2025-06-10', '2025-06-12', 0, 'MRO'),
-- MRO purchases (July - December 2025)
('PO-2025-049', 'MRO-BLADE-DIE', 'VND-GRAINGER', 20, 285.00, 5700.00, '2025-07-10', '2025-07-15', 0, 'MRO'),
('PO-2025-050', 'MRO-BLADE-DIE', 'VND-MOTION', 18, 278.00, 5004.00, '2025-09-25', '2025-09-29', 0, 'MRO'),
('PO-2025-051', 'MRO-BLADE-DIE', 'VND-MCMASTER', 25, 265.00, 6625.00, '2025-11-30', '2025-12-03', 0, 'MRO'),
('PO-2025-052', 'MRO-SEAL-HYD', 'VND-MOTION', 45, 142.00, 6390.00, '2025-08-05', '2025-08-08', 0, 'MRO'),
('PO-2025-053', 'MRO-SEAL-HYD', 'VND-GRAINGER', 30, 148.00, 4440.00, '2025-10-10', '2025-10-14', 0, 'MRO'),
('PO-2025-054', 'MRO-SEAL-HYD', 'VND-MCMASTER', 50, 135.00, 6750.00, '2025-12-01', '2025-12-03', 0, 'MRO'),
('PO-2025-055', 'MRO-BELT-CONV', 'VND-EUROIND', 15, 385.00, 5775.00, '2025-08-20', '2025-09-10', 0, 'MRO'),
('PO-2025-056', 'MRO-BELT-CONV', 'VND-MOTION', 12, 398.00, 4776.00, '2025-10-25', '2025-10-31', 0, 'MRO'),
('PO-2025-057', 'MRO-FILTER-HYD', 'VND-GRAINGER', 100, 40.00, 4000.00, '2025-07-15', '2025-07-19', 0, 'MRO'),
('PO-2025-058', 'MRO-FILTER-HYD', 'VND-MOTION', 120, 38.00, 4560.00, '2025-09-20', '2025-09-23', 0, 'MRO'),
('PO-2025-059', 'MRO-FILTER-HYD', 'VND-MCMASTER', 150, 35.00, 5250.00, '2025-11-25', '2025-11-27', 0, 'MRO'),
('PO-2025-060', 'MRO-BEARING-6205', 'VND-MOTION', 200, 12.50, 2500.00, '2025-08-15', '2025-08-17', 0, 'MRO'),
('PO-2025-061', 'MRO-BEARING-6205', 'VND-GRAINGER', 180, 13.50, 2430.00, '2025-10-30', '2025-11-02', 0, 'MRO'),
('PO-2025-062', 'MRO-BEARING-6310', 'VND-MCMASTER', 40, 27.00, 1080.00, '2025-09-15', '2025-09-17', 0, 'MRO'),
('PO-2025-063', 'MRO-VALVE-SOL', 'VND-FASTENAL', 35, 82.00, 2870.00, '2025-10-05', '2025-10-08', 0, 'MRO'),
('PO-2025-064', 'MRO-MOTOR-1HP', 'VND-MOTION', 3, 265.00, 795.00, '2025-08-25', '2025-08-30', 0, 'MRO'),
('PO-2025-065', 'MRO-COUPLING-JAW', 'VND-MCMASTER', 25, 40.00, 1000.00, '2025-11-10', '2025-11-12', 0, 'MRO'),
-- Packaging purchases (January - June 2025)
('PO-2025-066', 'PKG-PALLET-EUR', 'VND-ULINE', 400, 17.50, 7000.00, '2025-01-15', '2025-01-19', 0, 'Packaging'),
('PO-2025-067', 'PKG-FILM-STRETCH', 'VND-ULINE', 150, 40.00, 6000.00, '2025-01-25', '2025-01-28', 0, 'Packaging'),
('PO-2025-068', 'PKG-BOX-GAYLORD', 'VND-ULINE', 100, 27.00, 2700.00, '2025-02-10', '2025-02-14', 0, 'Packaging'),
('PO-2025-069', 'PKG-BAG-POLY-25', 'VND-ULINE', 8000, 0.78, 6240.00, '2025-02-20', '2025-02-23', 0, 'Packaging'),
('PO-2025-070', 'PKG-PALLET-US', 'VND-INTPAPER', 300, 16.50, 4950.00, '2025-03-05', '2025-03-12', 0, 'Packaging'),
('PO-2025-071', 'PKG-BOX-EXPORT', 'VND-MONDI', 50, 112.00, 5600.00, '2025-03-20', '2025-04-03', 0, 'Packaging'),
('PO-2025-072', 'PKG-DESICCANT-500', 'VND-ULINE', 200, 2.30, 460.00, '2025-04-05', '2025-04-08', 0, 'Packaging'),
('PO-2025-073', 'PKG-BAG-VALVE', 'VND-INTPAPER', 3000, 1.42, 4260.00, '2025-04-15', '2025-04-22', 0, 'Packaging'),
('PO-2025-074', 'PKG-FILM-SHRINK', 'VND-MONDI', 100, 48.00, 4800.00, '2025-05-01', '2025-05-15', 0, 'Packaging'),
('PO-2025-075', 'PKG-TAPE-STRAP', 'VND-ULINE', 30, 82.00, 2460.00, '2025-05-20', '2025-05-23', 0, 'Packaging'),
('PO-2025-076', 'PKG-LABEL-HAZMAT', 'VND-GRAINGER', 50, 46.00, 2300.00, '2025-06-05', '2025-06-09', 0, 'Packaging'),
-- Packaging purchases (July - December 2025)
('PO-2025-077', 'PKG-PALLET-EUR', 'VND-ULINE', 500, 17.00, 8500.00, '2025-07-20', '2025-07-24', 0, 'Packaging'),
('PO-2025-078', 'PKG-PALLET-EUR', 'VND-GRAINGER', 300, 20.00, 6000.00, '2025-09-10', '2025-09-15', 0, 'Packaging'),
('PO-2025-079', 'PKG-PALLET-EUR', 'VND-INTPAPER', 450, 18.50, 8325.00, '2025-11-05', '2025-11-12', 0, 'Packaging'),
('PO-2025-080', 'PKG-FILM-STRETCH', 'VND-ULINE', 200, 39.00, 7800.00, '2025-08-01', '2025-08-04', 0, 'Packaging'),
('PO-2025-081', 'PKG-FILM-STRETCH', 'VND-MONDI', 150, 42.00, 6300.00, '2025-10-15', '2025-10-29', 0, 'Packaging'),
('PO-2025-082', 'PKG-FILM-STRETCH', 'VND-ULINE', 250, 38.00, 9500.00, '2025-12-01', '2025-12-04', 0, 'Packaging'),
('PO-2025-083', 'PKG-BOX-GAYLORD', 'VND-INTPAPER', 120, 28.50, 3420.00, '2025-08-25', '2025-09-01', 0, 'Packaging'),
('PO-2025-084', 'PKG-BOX-GAYLORD', 'VND-GRAINGER', 80, 30.00, 2400.00, '2025-10-20', '2025-10-25', 0, 'Packaging'),
('PO-2025-085', 'PKG-BAG-POLY-25', 'VND-MONDI', 15000, 0.82, 12300.00, '2025-09-05', '2025-09-19', 0, 'Packaging'),
('PO-2025-086', 'PKG-BAG-POLY-25', 'VND-ULINE', 10000, 0.76, 7600.00, '2025-11-10', '2025-11-13', 0, 'Packaging'),
('PO-2025-087', 'PKG-BOX-EXPORT', 'VND-ULINE', 40, 120.00, 4800.00, '2025-09-20', '2025-09-26', 0, 'Packaging'),
('PO-2025-088', 'PKG-BOX-EXPORT', 'VND-INTPAPER', 60, 128.00, 7680.00, '2025-11-25', '2025-12-03', 0, 'Packaging'),
-- Safety/PPE purchases (January - June 2025)
('PO-2025-089', 'PPE-GLOVE-CHEM', 'VND-3M', 150, 20.50, 3075.00, '2025-01-20', '2025-01-25', 0, 'Safety'),
('PO-2025-090', 'PPE-RESP-N95', 'VND-3M', 80, 23.00, 1840.00, '2025-02-05', '2025-02-10', 0, 'Safety'),
('PO-2025-091', 'PPE-GOGGLES-SPLASH', 'VND-3M', 100, 7.00, 700.00, '2025-02-15', '2025-02-20', 0, 'Safety'),
('PO-2025-092', 'PPE-GLOVE-HEAT', 'VND-MCMASTER', 40, 44.00, 1760.00, '2025-03-10', '2025-03-13', 0, 'Safety'),
('PO-2025-093', 'PPE-GLOVE-CUT', 'VND-HONEYWELL', 100, 28.00, 2800.00, '2025-03-25', '2025-03-31', 0, 'Safety'),
('PO-2025-094', 'PPE-RESP-HALF', 'VND-3M', 20, 75.00, 1500.00, '2025-04-05', '2025-04-10', 0, 'Safety'),
('PO-2025-095', 'PPE-SHIELD-FACE', 'VND-HONEYWELL', 50, 13.50, 675.00, '2025-04-20', '2025-04-26', 0, 'Safety'),
('PO-2025-096', 'PPE-APRON-CHEM', 'VND-ULINE', 30, 24.00, 720.00, '2025-05-05', '2025-05-09', 0, 'Safety'),
('PO-2025-097', 'PPE-BOOT-STEEL', 'VND-HONEYWELL', 25, 75.00, 1875.00, '2025-05-15', '2025-05-21', 0, 'Safety'),
('PO-2025-098', 'PPE-EARPLUGS', 'VND-3M', 50, 30.00, 1500.00, '2025-06-01', '2025-06-06', 0, 'Safety'),
-- Safety/PPE purchases (July - December 2025)
('PO-2025-099', 'PPE-GLOVE-CHEM', 'VND-MCMASTER', 200, 21.50, 4300.00, '2025-07-25', '2025-07-28', 0, 'Safety'),
('PO-2025-100', 'PPE-GLOVE-CHEM', 'VND-GRAINGER', 150, 24.00, 3600.00, '2025-09-30', '2025-10-04', 0, 'Safety'),
('PO-2025-101', 'PPE-GLOVE-CHEM', 'VND-HONEYWELL', 250, 21.00, 5250.00, '2025-11-20', '2025-11-26', 0, 'Safety'),
('PO-2025-102', 'PPE-RESP-N95', 'VND-MCMASTER', 100, 25.00, 2500.00, '2025-08-10', '2025-08-12', 0, 'Safety'),
('PO-2025-103', 'PPE-RESP-N95', 'VND-3M', 120, 22.50, 2700.00, '2025-10-25', '2025-10-30', 0, 'Safety'),
('PO-2025-104', 'PPE-GOGGLES-SPLASH', 'VND-MCMASTER', 80, 7.50, 600.00, '2025-09-15', '2025-09-17', 0, 'Safety'),
('PO-2025-105', 'PPE-GLOVE-HEAT', 'VND-3M', 50, 41.00, 2050.00, '2025-10-10', '2025-10-15', 0, 'Safety'),
('PO-2025-106', 'PPE-GLOVE-CUT', 'VND-GRAINGER', 120, 31.00, 3720.00, '2025-11-05', '2025-11-09', 0, 'Safety'),
('PO-2025-107', 'PPE-EARPLUGS', 'VND-ULINE', 80, 32.00, 2560.00, '2025-12-05', '2025-12-09', 0, 'Safety'),
-- Office purchases (throughout 2025)
('PO-2025-108', 'OFF-LAPTOP-IND', 'VND-MCMASTER', 5, 2320.00, 11600.00, '2025-02-01', '2025-02-08', 0, 'Office'),
('PO-2025-109', 'OFF-LAPTOP-STD', 'VND-FASTENAL', 10, 1150.00, 11500.00, '2025-03-15', '2025-03-20', 0, 'Office'),
('PO-2025-110', 'OFF-PRINTER-LBL', 'VND-ULINE', 4, 620.00, 2480.00, '2025-04-10', '2025-04-14', 0, 'Office'),
('PO-2025-111', 'OFF-PRINTER-MFP', 'VND-FASTENAL', 3, 385.00, 1155.00, '2025-05-05', '2025-05-09', 0, 'Office'),
('PO-2025-112', 'OFF-CHAIR-ERGO', 'VND-ULINE', 25, 265.00, 6625.00, '2025-06-01', '2025-06-07', 0, 'Office'),
('PO-2025-113', 'OFF-DESK-SIT', 'VND-ULINE', 8, 455.00, 3640.00, '2025-07-15', '2025-07-23', 0, 'Office'),
('PO-2025-114', 'OFF-MONITOR-27', 'VND-FASTENAL', 15, 355.00, 5325.00, '2025-08-20', '2025-08-24', 0, 'Office'),
('PO-2025-115', 'OFF-SCANNER-DOC', 'VND-ULINE', 2, 275.00, 550.00, '2025-09-10', '2025-09-14', 0, 'Office'),
('PO-2025-116', 'OFF-CHAIR-ERGO', 'VND-GRAINGER', 15, 285.00, 4275.00, '2025-10-05', '2025-10-13', 0, 'Office'),
('PO-2025-117', 'OFF-DESK-SIT', 'VND-GRAINGER', 5, 475.00, 2375.00, '2025-11-15', '2025-11-25', 0, 'Office'),
('PO-2025-118', 'OFF-LAPTOP-IND', 'VND-GRAINGER', 3, 2400.00, 7200.00, '2025-11-20', '2025-11-30', 0, 'Office'),
-- Additional late shipments (for vendor performance analysis)
('PO-2025-119', 'RM-EPDM-70', 'VND-SINOPEC', 20000, 4.05, 81000.00, '2025-06-01', '2025-07-10', 4, 'Raw Materials'),
('PO-2025-120', 'RM-SBR-65', 'VND-SINOPEC', 30000, 2.20, 66000.00, '2025-08-15', '2025-09-25', 5, 'Raw Materials'),
('PO-2025-121', 'MRO-PUMP-DOSING', 'VND-EUROIND', 3, 1680.00, 5040.00, '2025-07-01', '2025-07-25', 3, 'MRO'),
('PO-2025-122', 'PKG-BOX-EXPORT', 'VND-MONDI', 80, 115.00, 9200.00, '2025-08-10', '2025-08-28', 2, 'Packaging'),
('PO-2025-123', 'RM-NBR-60', 'VND-SABIC', 8000, 4.50, 36000.00, '2025-09-01', '2025-10-08', 4, 'Raw Materials'),
('PO-2025-124', 'RM-SILICONE-70', 'VND-SABIC', 600, 18.00, 10800.00, '2025-10-10', '2025-11-15', 3, 'Raw Materials'),
('PO-2025-125', 'MRO-BELT-CONV', 'VND-EUROIND', 10, 380.00, 3800.00, '2025-11-01', '2025-11-28', 4, 'MRO');

-- Index for purchase history queries
CREATE INDEX idx_purchase_history_vendor ON purchase_history(vendor_id);
CREATE INDEX idx_purchase_history_sku ON purchase_history(item_sku);
CREATE INDEX idx_purchase_history_category ON purchase_history(category);
CREATE INDEX idx_purchase_history_date ON purchase_history(order_date);
