import sys
import os
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure directory is on path
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, basedir)

from config import Config, SQLALCHEMY_DATABASE_URI, DB_ENGINE_LABEL
from models import (
    Base, User, Admin, EwasteItem, CollectionRequest, 
    RecyclingCentre, DisposalGuideline, AwarenessContent,
    collection_request_items
)

def initialize_database():
    print("=" * 70)
    print("  E-WASTE MANAGEMENT SYSTEM - DATABASE INITIALIZATION")
    print("=" * 70)
    print(f"Connecting to: {DB_ENGINE_LABEL}")
    print(f"URI: {SQLALCHEMY_DATABASE_URI}")

    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    
    # Create all tables if they do not exist
    print("Creating tables if not present...")
    Base.metadata.create_all(engine)
    print("Tables verified/created successfully.")

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Seed Admin
        admin = session.query(Admin).filter_by(email='admin@ewaste.gov.in').first()
        if not admin:
            print("Seeding default Administrator (admin@ewaste.gov.in)...")
            admin = Admin(
                full_name="E-Waste Drive Administrator",
                email="admin@ewaste.gov.in",
                password_hash=generate_password_hash("admin123"),
                role="Super Administrator"
            )
            session.add(admin)
        else:
            print("Admin account already exists.")

        # 2. Seed Recycling Centres (Official CPCB, KSPCB & OpenCity Verified Only - Zero Dummy Records)
        print("Purging any unverified/outdated recycling centres and seeding official verified facilities...")
        session.query(RecyclingCentre).delete()
        
        centres = [
            RecyclingCentre(
                centre_name="M/s. E-Parisaraa Pvt. Ltd.",
                facility_type="Authorized Recycler",
                complete_address="Plot No. 30-P3, KIADB Industrial Area, Dobaspet, Nelamangala Taluk",
                city="Nelamangala",
                district="Bengaluru Rural",
                pincode="562111",
                state="Karnataka",
                contact_phone="+91 80 2773 6050",
                contact_email=None,
                website_url="https://www.ewasteindia.com",
                services_offered="India's first CPCB/KSPCB authorized scientific e-waste recycler. Precious metal recovery, PCB shredding, and zero-landfill display processing.",
                accepted_categories="Computers, Laptops, Mobile Phones, Printers, Circuit Boards, Household Electronics",
                source_url="https://eprewaste.cpcb.gov.in/",
                last_verified_date=date(2026, 10, 15),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=E-Parisaraa+Pvt+Ltd+Dobaspet+KIADB",
                latitude=13.2355000,
                longitude=77.2418000
            ),
            RecyclingCentre(
                centre_name="M/s. Sriram Eco Raksha Computer Services Pvt. Ltd.",
                facility_type="Authorized Recycler",
                complete_address="Shed No. B-29, KSSIDC Industrial Estate, Bommasandra, Hosur Road, Anekal Taluk",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="560099",
                state="Karnataka",
                contact_phone="+91 80 2783 5530",
                contact_email=None,
                website_url=None,
                services_offered="Certified IT asset recovery, high-security data destruction, copper and aluminum mechanical granulators.",
                accepted_categories="Computers, Laptops, Mobile Phones, Chargers, Servers, Network Equipment",
                source_url="https://kspcb.karnataka.gov.in/",
                last_verified_date=date(2026, 10, 10),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=KSSIDC+Industrial+Estate+Bommasandra+Bangalore",
                latitude=12.8188000,
                longitude=77.6842000
            ),
            RecyclingCentre(
                centre_name="M/s. 4R Recycling Pvt. Ltd.",
                facility_type="Authorized Dismantler",
                complete_address="Shed No. A-5, Peenya Industrial Estate, Peenya 3rd Stage, Nallakadirenahalli, Yeshwanthpur Hobli",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="560058",
                state="Karnataka",
                contact_phone="+91 80 2837 4444",
                contact_email=None,
                website_url=None,
                services_offered="KSPCB-authorized manual and mechanical dismantling, hazard isolation, plastic sorting and segregation.",
                accepted_categories="Mobile Phones, Chargers, Batteries, Laptops, Small Household Appliances",
                source_url="https://data.opencity.in/dataset/karnataka-waste-collection-recycling-and-processing-centres",
                last_verified_date=date(2026, 9, 25),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=Peenya+3rd+Stage+Industrial+Estate+Bangalore",
                latitude=13.0380000,
                longitude=77.5140000
            ),
            RecyclingCentre(
                centre_name="M/s. E-R3 Solutions Pvt. Ltd.",
                facility_type="Authorized Recycler",
                complete_address="Plot No. 105, Road No. 3, KIADB Bengaluru IT Park, Mahadeva Kodigehalli",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="562149",
                state="Karnataka",
                contact_phone="+91 80 4115 5440",
                contact_email=None,
                website_url="https://er3solutions.com",
                services_offered="IT Asset Disposition (ITAD), DoD 5220.22-M certified data erasure, environmentally sound recycling.",
                accepted_categories="Laptops, Desktops, Network Hardware, Server Racks, Lithium-Ion Batteries",
                source_url="https://eprewaste.cpcb.gov.in/",
                last_verified_date=date(2026, 9, 20),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=KIADB+IT+Park+Mahadeva+Kodigehalli+Bengaluru",
                latitude=13.1550000,
                longitude=77.6740000
            ),
            RecyclingCentre(
                centre_name="M/s. Ash Recyclers",
                facility_type="Authorized Dismantler",
                complete_address="Plot No. 3, KSSIDC Industrial Estate, Hoskote",
                city="Hoskote",
                district="Bengaluru Rural",
                pincode="562114",
                state="Karnataka",
                contact_phone=None,
                contact_email=None,
                website_url="http://ashrecycler.com",
                services_offered="Authorized electronic assembly dismantling, circuit board sorting, and copper wire recovery.",
                accepted_categories="Electrical & Electronic Assembly Waste, Telecom Gear, Cables, PCBs",
                source_url="https://kspcb.karnataka.gov.in/",
                last_verified_date=date(2026, 10, 5),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=KSSIDC+Industrial+Estate+Hoskote+Bangalore",
                latitude=13.0690000,
                longitude=77.7980000
            ),
            RecyclingCentre(
                centre_name="M/s. Cerebra Integrated Technologies Ltd.",
                facility_type="Authorized Recycler",
                complete_address="S-5, 3rd Cross Street, 1st Stage, Netaji Nagar, Peenya Industrial Area",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="560058",
                state="Karnataka",
                contact_phone="+91 80 2210 7748",
                contact_email=None,
                website_url="https://www.cerebracomputers.com",
                services_offered="Large-scale zero-landfill e-waste processing facility, display neutralization, precious metal extraction.",
                accepted_categories="Televisions, CRT Monitors, Laptops, Computers, Telecom Equipment, Large Appliances",
                source_url="https://eprewaste.cpcb.gov.in/",
                last_verified_date=date(2026, 10, 18),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=Peenya+Industrial+Area+1st+Stage+Bengaluru",
                latitude=13.0280000,
                longitude=77.5220000
            ),
            RecyclingCentre(
                centre_name="M/s. Saahas Zero Waste (Saahas Waste Management Pvt. Ltd.)",
                facility_type="Collection Centre",
                complete_address="Ground Floor, No. 21, MCHS Colony, 5th C Cross, 16th Main Road, BTM 2nd Stage",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="560076",
                state="Karnataka",
                contact_phone="+91 80 4168 9389",
                contact_email=None,
                website_url="https://saahaszerowaste.com",
                services_offered="Official citizen collection and drop-off facility. Aggregation and safe channelization to authorized recyclers.",
                accepted_categories="Mobile Phones, Household Electronics, Chargers, Cables, Dry Cell Batteries",
                source_url="https://data.opencity.in/dataset/karnataka-waste-collection-recycling-and-processing-centres",
                last_verified_date=date(2026, 10, 1),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=BTM+Layout+2nd+Stage+Bengaluru",
                latitude=12.9165000,
                longitude=77.6101000
            ),
            RecyclingCentre(
                centre_name="M/s. Sheeltron Digital Systems Pvt. Ltd.",
                facility_type="Authorized Refurbisher",
                complete_address="No. 2/1, East Park Road, Kumara Park East, South End Street",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="560001",
                state="Karnataka",
                contact_phone=None,
                contact_email=None,
                website_url="https://sheeltron.com",
                services_offered="Authorized electronic equipment refurbishing, testing, component upgrading, and hardware lifespan extension.",
                accepted_categories="Laptops, Desktops, Servers, Workstations, Monitors",
                source_url="https://kspcb.karnataka.gov.in/",
                last_verified_date=date(2026, 9, 15),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=Kumara+Park+East+Bangalore+560001",
                latitude=12.9880000,
                longitude=77.5810000
            ),
            RecyclingCentre(
                centre_name="M/s. Ace Recyclers",
                facility_type="Authorized Dismantler",
                complete_address="Plot No. C-29, KSSIDC Industrial Estate, Hoskote Taluk",
                city="Hoskote",
                district="Bengaluru Rural",
                pincode="562114",
                state="Karnataka",
                contact_phone=None,
                contact_email=None,
                website_url=None,
                services_offered="Authorized dismantling facility for electrical components, segregation of hazardous fraction, mechanical shredding.",
                accepted_categories="Mixed Consumer Electronics, Small IT Equipment, Printed Wiring Boards",
                source_url="https://kspcb.karnataka.gov.in/",
                last_verified_date=date(2026, 9, 10),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=KSSIDC+Industrial+Estate+Hoskote+562114",
                latitude=13.0710000,
                longitude=77.7950000
            ),
            RecyclingCentre(
                centre_name="M/s. Eco-Ewaste Recyclers India Pvt. Ltd.",
                facility_type="Authorized Dismantler",
                complete_address="Mutachari Industrial Estate, Hanumanthappa Layout, Mysore Road",
                city="Bengaluru",
                district="Bengaluru Urban",
                pincode="560026",
                state="Karnataka",
                contact_phone=None,
                contact_email=None,
                website_url=None,
                services_offered="Authorized dismantling of telecommunication hardware, commercial electronic equipment, and battery segregation.",
                accepted_categories="Industrial Electronics, Telecom Switching Gear, Chargers, Batteries",
                source_url="https://data.opencity.in/dataset/karnataka-waste-collection-recycling-and-processing-centres",
                last_verified_date=date(2026, 8, 28),
                is_official_verified=True,
                directions_url="https://www.google.com/maps/search/?api=1&query=Mutachari+Industrial+Estate+Mysore+Road+Bengaluru",
                latitude=12.9450000,
                longitude=77.5320000
            )
        ]
        session.add_all(centres)
        session.commit()
        print(f"Seeded {len(centres)} official verified recycling/collection centres successfully.")

        # 3. Seed Disposal Guidelines
        if session.query(DisposalGuideline).count() == 0:
            print("Seeding Proper Disposal Guidelines...")
            guidelines = [
                DisposalGuideline(
                    category="Mobile Phones",
                    title="Safe Disposal & Data Security for Smartphones and Feature Phones",
                    summary="Smartphones contain toxic heavy metals such as cadmium and lead, as well as recoverable precious metals (gold, silver, palladium). Personal privacy and battery safety are top priorities.",
                    step_by_step=(
                        "Step 1: Backup all personal data to cloud or external storage.\n"
                        "Step 2: Sign out of all Google, Apple, and banking accounts.\n"
                        "Step 3: Perform a complete cryptographic Factory Data Reset.\n"
                        "Step 4: Remove SIM card and MicroSD storage cards.\n"
                        "Step 5: Inspect battery for swelling. If swollen, do not compress; isolate in a non-conductive box.\n"
                        "Step 6: Hand over to authorized CPCB/KSPCB dismantler or submit a digital collection drive request."
                    ),
                    dos_and_donts=(
                        "DO: Keep the phone at room temperature in a dry container.\n"
                        "DO: Tape over cracked screens with clear packing tape to prevent injury and glass contamination.\n"
                        "DON'T: Never throw a phone into municipal garbage bins or incinerators.\n"
                        "DON'T: Never burn cables or heat batteries to recover copper or gold.\n"
                        "DON'T: Do not sell to unauthorized roadside scrap vendors (informal sector acid leaching)."
                    ),
                    hazards_prevented="Prevents lithium thermal runaway fires in municipal compaction trucks; prevents groundwater cadmium poisoning; stops unauthorized personal identity theft.",
                    icon_class="fa-mobile-screen-button"
                ),
                DisposalGuideline(
                    category="Laptops & Computers",
                    title="Responsible Handling for Desktop CPUs, Laptops, and Servers",
                    summary="Computers contain hazardous printed circuit boards (lead, brominated flame retardants), mercury cold-cathode lamps in older displays, and valuable copper heat pipes.",
                    step_by_step=(
                        "Step 1: Save critical files and unlicense software activations.\n"
                        "Step 2: Use drive wiping utilities (e.g., DBAN or BitLocker cryptographic erase) to overwrite storage.\n"
                        "Step 3: Disconnect power cables, external mouse, keyboards, and lithium backup CMOS batteries.\n"
                        "Step 4: Wrap the display screen in protective cardboard to avoid mercury vapor leakage from fluorescent backlights.\n"
                        "Step 5: Bundle cables neatly and register the desktop/laptop for authorized scientific dismantling."
                    ),
                    dos_and_donts=(
                        "DO: Separate the external battery pack if detachable.\n"
                        "DO: Document serial numbers for your institutional audit or e-waste disposal receipt.\n"
                        "DON'T: Never crack open CRT or LCD monitors (releases lead dust and mercury vapor).\n"
                        "DON'T: Never use open flame to unsolder electronic components from motherboards."
                    ),
                    hazards_prevented="Prevents airborne dioxin and furans caused by burning PCB resin; shields soil from lead and arsenic leaching.",
                    icon_class="fa-laptop"
                ),
                DisposalGuideline(
                    category="Batteries",
                    title="Safe Isolation & Terminal Taping for Lithium-Ion, NiMH & Lead-Acid Cells",
                    summary="Spent batteries present the highest fire hazard in the waste management stream due to stored chemical energy and flammable electrolytes.",
                    step_by_step=(
                        "Step 1: Identify battery chemistry (Li-Ion, Alkaline, NiCad, Lead-Acid).\n"
                        "Step 2: Apply clear insulating electrical tape over both positive (+) and negative (-) terminals to prevent short-circuiting.\n"
                        "Step 3: If battery shows signs of bulge, puncture, or corrosion, place immediately in a fire-safe bucket of dry sand or vermiculite.\n"
                        "Step 4: Store in a cool, ventilated area away from moisture and flammable solvents.\n"
                        "Step 5: Deliver strictly to specialized hydrometallurgical battery recyclers."
                    ),
                    dos_and_donts=(
                        "DO: Tape button cells and lithium packs individually.\n"
                        "DO: Keep different battery chemistries separated if storing in bulk.\n"
                        "DON'T: Never mix damaged batteries with metallic paperclips, coins, or keys.\n"
                        "DON'T: Never attempt to recharge swollen or deformed cells.\n"
                        "DON'T: Never dump spent car batteries or power bank cells into domestic dustbins."
                    ),
                    hazards_prevented="Prevents intense lithium fires reaching 1000°C; prevents sulfuric acid and caustic potassium hydroxide chemical burns.",
                    icon_class="fa-car-battery"
                ),
                DisposalGuideline(
                    category="Chargers & Cables",
                    title="Proper Management of Adapters, Charging Bricks, and Connectors",
                    summary="Cables contain high-grade copper surrounded by polyvinyl chloride (PVC) and halogenated flame retardants that release toxic dioxins if burned.",
                    step_by_step=(
                        "Step 1: Check if the charger is in working condition; consider donating or reusing with compatible devices.\n"
                        "Step 2: Coil the cable in loose loops; do not tie tightly into knots that can crush wire cores.\n"
                        "Step 3: Keep transformer wall-warts intact; do not smash the outer plastic casing.\n"
                        "Step 4: Consolidate small cords into a clean cardboard box and register them collectively."
                    ),
                    dos_and_donts=(
                        "DO: Group USB-C, micro-USB, and appliance power cords together.\n"
                        "DON'T: Never set fire to wire insulation in open air to strip copper (strictly illegal under E-Waste Rules 2022).\n"
                        "DON'T: Do not mix with wet household organic waste."
                    ),
                    hazards_prevented="Prevents atmospheric emission of carcinogens (dioxins, furans, hydrochloric acid fumes) and promotes 100% mechanical copper granulation.",
                    icon_class="fa-plug-circle-bolt"
                ),
                DisposalGuideline(
                    category="Televisions & Other Electronics",
                    title="Disposal Protocol for Smart TVs, CRT Sets, and Home Electronics",
                    summary="Televisions and consumer appliances contain high-voltage capacitors, leaded glass funnels (in CRT up to 2-3 kg of lead), and polyurethane insulation.",
                    step_by_step=(
                        "Step 1: Unplug appliance from mains power at least 24 hours prior to moving to allow high-voltage capacitors to bleed charge.\n"
                        "Step 2: Secure power cord against the chassis with removable masking tape.\n"
                        "Step 3: Cover front glass screens with cardboard sheets to safeguard against shattering.\n"
                        "Step 4: Request doorstep pickup from an authorized collection center with proper mechanical lifting assistance."
                    ),
                    dos_and_donts=(
                        "DO: Keep original stands and remotes bundled together for refurbishment potential.\n"
                        "DON'T: Never dismantle television backs yourself—CRT tubes are under high vacuum and can implode violently.\n"
                        "DON'T: Never dispose of microwave ovens, monitors, or amplifiers in standard municipal dumpsters."
                    ),
                    hazards_prevented="Prevents physical implosion injuries from CRT vacuum tubes; eliminates lead poisoning from pulverized display glass in public landfills.",
                    icon_class="fa-tv"
                )
            ]
            session.add_all(guidelines)

        # 4. Seed Environmental Awareness Content
        if session.query(AwarenessContent).count() == 0:
            print("Seeding Environmental Awareness Content...")
            articles = [
                AwarenessContent(
                    title="The Silent Menace: Heavy Metals in Everyday Electronics",
                    category="Toxic Substances & Health",
                    summary="Modern electronic devices contain over 1,000 distinct materials, many of which are toxic and bioaccumulative.",
                    content=(
                        "When electronic devices are casually tossed into municipal landfills, seasonal rainfall percolates through "
                        "the garbage layers, creating a toxic chemical soup known as 'leachate.' This leachate dissolves lead from solder, "
                        "cadmium from resistors, and mercury from fluorescent displays, percolating into the water table and contaminating "
                        "agricultural irrigation channels."
                    ),
                    toxic_substance="Lead (Pb), Cadmium (Cd), Mercury (Hg)",
                    health_hazard="Damage to central and peripheral nervous systems, kidney dysfunction, intellectual impairment in developing children, and chronic respiratory illness.",
                    environmental_hazard="Irreversible contamination of groundwater aquifers, bioaccumulation in marine life, and severe soil infertility."
                ),
                AwarenessContent(
                    title="Urban Mining: Why E-Waste is Far Richer Than Natural Mines",
                    category="Circular Economy & Resource Recovery",
                    summary="One metric tonne of discarded smartphones contains up to 300 grams of pure gold and 2 kg of silver—over 50 times richer than mined ore.",
                    content=(
                        "Natural gold mining requires excavating over 1 tonne of raw rocky earth to yield merely 5 grams of gold, consuming thousands of "
                        "liters of diesel and toxic cyanide. Conversely, specialized hydro-metallurgical electronic recycling recovers gold, silver, "
                        "copper, and palladium with an 80% reduction in carbon footprint. Circular recycling reduces international dependency on destructive virgin mineral extraction."
                    ),
                    toxic_substance="Gold (Au), Silver (Ag), Palladium (Pd), Copper (Cu)",
                    health_hazard="Mitigates occupational hazards, silicosis, and mine tailings collapse risks associated with conventional primary open-pit mining.",
                    environmental_hazard="Prevents massive deforestation, landscape destruction, and sulfur dioxide emissions caused by virgin ore smelting."
                ),
                AwarenessContent(
                    title="India E-Waste Management Rules, 2022 and EPR Compliance",
                    category="Environmental Regulations & Policy",
                    summary="The revised E-Waste (Management) Rules notify strict Extended Producer Responsibility (EPR) targets and outlaw crude informal processing.",
                    content=(
                        "Under the regulations issued by the Ministry of Environment, Forest and Climate Change (MoEFCC) and monitored by CPCB & State "
                        "Pollution Control Boards, electronics manufacturers are legally mandated to collect and channel a progressive percentage of historical "
                        "electronics sold into authorized recycling streams. Citizens and bulk consumers have an explicit duty to channel e-waste exclusively to registered recyclers."
                    ),
                    toxic_substance="Regulated Electronic Categories I to IV",
                    health_hazard="Protects informal sector workers, including women and children, from fatal toxic gas exposure in unventilated acid baths.",
                    environmental_hazard="Enforces zero-landfill processing and tracks material balance certificates across the national registry."
                )
            ]
            session.add_all(articles)

        # 5. Seed Demonstration User, Items, and Requests (for immediate rich experience)
        demo_user = session.query(User).filter_by(email='student@college.edu').first()
        if not demo_user:
            print("Seeding sample User (student@college.edu)...")
            demo_user = User(
                full_name="Citizen User",
                email="student@college.edu",
                phone="+91 98451 22334",
                password_hash=generate_password_hash("student123"),
                address="42, 5th Main, Green Glen Layout, Bellandur",
                city="Bengaluru",
                pincode="560103"
            )
            session.add(demo_user)
            session.flush()

            # Seed sample e-waste items
            item1 = EwasteItem(
                user_id=demo_user.id,
                category="Mobile Phones",
                item_name="Samsung Galaxy J7 Prime (Defective Battery)",
                quantity=1,
                item_condition="Damaged",
                description="Phone boots but battery swollen. Screen glass has slight corner crack.",
                location="Bengaluru",
                status="In Request"
            )
            item2 = EwasteItem(
                user_id=demo_user.id,
                category="Laptops",
                item_name="Dell Inspiron 15R (Motherboard Failure)",
                quantity=1,
                item_condition="Not Working",
                description="Power surge fried motherboard. Hard disk removed, RAM intact.",
                location="Bengaluru",
                status="In Request"
            )
            item3 = EwasteItem(
                user_id=demo_user.id,
                category="Batteries",
                item_name="Assorted Li-ion 18650 Powerbank Cells",
                quantity=6,
                item_condition="Not Working",
                description="Terminals taped with insulation tape as per safety instructions.",
                location="Bengaluru",
                status="In Request"
            )
            item4 = EwasteItem(
                user_id=demo_user.id,
                category="Chargers",
                item_name="Old Micro-USB & Nokia 2mm Pin Adapters",
                quantity=4,
                item_condition="Working",
                description="Working chargers for legacy devices no longer in use.",
                location="Bengaluru",
                status="Available"
            )
            item5 = EwasteItem(
                user_id=demo_user.id,
                category="Televisions",
                item_name="LG 21-inch CRT Color Television",
                quantity=1,
                item_condition="Not Working",
                description="Vintage CRT unit from family home. Unopened back panel.",
                location="Bengaluru",
                status="Collected"
            )
            session.add_all([item1, item2, item3, item4, item5])
            session.flush()

            # Seed sample collection requests
            req1 = CollectionRequest(
                request_code="EWC-202611-B48A",
                user_id=demo_user.id,
                pickup_address="42, 5th Main, Green Glen Layout, Bellandur, Bengaluru",
                city="Bengaluru",
                pincode="560103",
                preferred_date=date.today() + timedelta(days=3),
                preference_type="Doorstep Pickup",
                status="Approved",
                admin_notes="Assigned to CPCB/KSPCB Partner Route B-4. Logistics pickup scheduled."
            )
            req1.items.extend([item1, item2, item3])

            req2 = CollectionRequest(
                request_code="EWC-202610-A91C",
                user_id=demo_user.id,
                pickup_address="42, 5th Main, Green Glen Layout, Bellandur, Bengaluru",
                city="Bengaluru",
                pincode="560103",
                preferred_date=date.today() - timedelta(days=12),
                preference_type="Doorstep Pickup",
                status="Completed",
                admin_notes="Collection completed. Received by authorized recycler. Manifest closed."
            )
            req2.items.append(item5)

            session.add_all([req1, req2])

        session.commit()
        print("Database initialization and initial seeding completed successfully!")
        print("-" * 70)
        print("Default Accounts:")
        print("  Admin : admin@ewaste.gov.in  / admin123")
        print("  User  : student@college.edu   / student123")
        print("-" * 70)
    except Exception as e:
        session.rollback()
        print(f"Error during database initialization: {e}")
        raise e
    finally:
        session.close()

if __name__ == '__main__':
    initialize_database()

