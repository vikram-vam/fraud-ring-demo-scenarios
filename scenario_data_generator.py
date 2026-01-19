"""
Scenario-Driven Data Generator for Insurance Fraud Ring Detection Demo

Generates:
1. Background legitimate data (~150 claims)
2. Four curated fraud scenarios with specific data requirements
3. One false positive contrast (City General ER)

All scenario data is isolated to prevent cross-contamination.

Scenarios:
1. "The Two-Hour Attorney" - Captive medical mill with hidden ownership
2. "The Typo That Wasn't" - Identity web via shared phone/address
3. "The Audit That Went Deeper" - Provider billing anomaly + false positive contrast
4. "The Case We Thought Was Closed" - Network migration after prosecution
"""

import random
from datetime import datetime, timedelta
from neo4j import GraphDatabase
import streamlit as st


class ScenarioDataGenerator:
    """
    Generates curated demo data for fraud ring detection scenarios.
    
    Design Principles:
    - Each scenario uses DEDICATED entities (no cross-contamination)
    - Background data has ZERO shared phones/addresses (except realistic 5% couples)
    - Scenario signals are CLEAR outliers vs background
    """
    
    def __init__(self):
        """Initialize generator with Neo4j connection from Streamlit secrets."""
        try:
            neo4j_uri = st.secrets["neo4j"]["uri"]
            neo4j_user = st.secrets["neo4j"]["user"]
            neo4j_password = st.secrets["neo4j"]["password"]
        except Exception as e:
            raise ConnectionError(f"Failed to load Neo4j secrets: {e}")

        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        # Global counters for unique IDs
        self.claim_counter = 0
        self.person_counter = 0
        self.provider_counter = 0
        self.attorney_counter = 0
        self.bodyshop_counter = 0
        self.adjuster_counter = 0
        self.address_counter = 0
        self.phone_counter = 0
        self.location_counter = 0
        self.vehicle_counter = 0
        
        # Pools for reuse
        self.adjuster_pool = []
        self.background_providers = []
        self.background_attorneys = []
        self.background_locations = []
        self.background_bodyshops = []
        
        # Track what's been used (for isolation verification)
        self.used_phones = set()
        self.used_addresses = set()
        
        # Generation stats
        self.stats = {
            'background_claims': 0,
            'scenario_1_claims': 0,
            'scenario_2_claims': 0,
            'scenario_3a_claims': 0,
            'scenario_3b_claims': 0,
            'scenario_4_claims': 0
        }

    def close(self):
        """Close Neo4j connection."""
        self.driver.close()

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def clear_database(self):
        """Clear all existing data."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✓ Database cleared")

    def create_indexes(self):
        """Create indexes for better query performance."""
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX claim_id IF NOT EXISTS FOR (c:Claim) ON (c.id)",
                "CREATE INDEX person_id IF NOT EXISTS FOR (p:Person) ON (p.id)",
                "CREATE INDEX provider_id IF NOT EXISTS FOR (p:Provider) ON (p.id)",
                "CREATE INDEX attorney_id IF NOT EXISTS FOR (a:Attorney) ON (a.id)",
                "CREATE INDEX bodyshop_id IF NOT EXISTS FOR (b:BodyShop) ON (b.id)",
                "CREATE INDEX address_id IF NOT EXISTS FOR (a:Address) ON (a.id)",
                "CREATE INDEX phone_id IF NOT EXISTS FOR (p:Phone) ON (p.id)",
                "CREATE INDEX phone_number IF NOT EXISTS FOR (p:Phone) ON (p.number)",
                "CREATE INDEX location_id IF NOT EXISTS FOR (l:Location) ON (l.id)",
            ]
            for idx in indexes:
                try:
                    session.run(idx)
                except Exception:
                    pass
            print("✓ Indexes created")

    def generate_name(self):
        """Generate random person name."""
        first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
            "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
            "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
            "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon"
        ]
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
            "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright",
            "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Campbell", "Mitchell",
            "Roberts", "Carter", "Phillips", "Evans", "Turner", "Torres", "Parker", "Collins"
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def generate_date(self, days_ago_start=365, days_ago_end=0):
        """Generate random date within range."""
        start = datetime.now() - timedelta(days=days_ago_start)
        end = datetime.now() - timedelta(days=days_ago_end)
        delta = end - start
        random_days = random.randint(0, max(1, delta.days))
        return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

    def generate_phone(self, prefix="555"):
        """Generate unique phone number."""
        phone = f"{prefix}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        while phone in self.used_phones:
            phone = f"{prefix}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        self.used_phones.add(phone)
        return phone

    def generate_ssn(self):
        """Generate random SSN."""
        return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

    def generate_street_address(self):
        """Generate random street address."""
        numbers = random.randint(100, 9999)
        streets = [
            "Main Street", "Oak Avenue", "Maple Drive", "Cedar Lane", "Pine Road",
            "Elm Street", "Washington Boulevard", "Park Avenue", "Lake Drive", "River Road",
            "Highland Avenue", "Forest Drive", "Valley Road", "Spring Street", "Church Street",
            "Mill Road", "School Street", "North Street", "South Avenue", "West Drive"
        ]
        return f"{numbers} {random.choice(streets)}"

    def generate_city_state(self):
        """Generate random city/state."""
        locations = [
            ("Atlanta", "GA", "30301"), ("Birmingham", "AL", "35201"),
            ("Charlotte", "NC", "28201"), ("Nashville", "TN", "37201"),
            ("Jacksonville", "FL", "32099"), ("Memphis", "TN", "38101"),
            ("Richmond", "VA", "23218"), ("Columbia", "SC", "29201")
        ]
        return random.choice(locations)

    # =========================================================================
    # POOL CREATION
    # =========================================================================
    
    def create_adjuster_pool(self, count=15):
        """Create a pool of adjusters to be assigned to claims."""
        print(f"\nCreating pool of {count} adjusters...")
        
        with self.driver.session() as session:
            for i in range(count):
                adjuster_id = f"ADJ_{self.adjuster_counter:05d}"
                adjuster_name = self.generate_name()
                employee_id = f"EMP-{random.randint(10000, 99999)}"
                
                session.run("""
                    CREATE (a:Person:Adjuster {
                        id: $id,
                        name: $name,
                        employee_id: $employee_id,
                        role: 'Adjuster'
                    })
                """, id=adjuster_id, name=adjuster_name, employee_id=employee_id)
                
                self.adjuster_pool.append(adjuster_id)
                self.adjuster_counter += 1
        
        print(f"✓ Created {count} adjusters")

    def create_background_providers(self, count=15):
        """Create background medical providers (legitimate)."""
        print(f"\nCreating {count} background providers...")
        
        provider_names = [
            "Community Health Center", "Family Medical Associates", "Metro Urgent Care",
            "Riverside Medical Group", "Valley Health Clinic", "Lakeside Medical",
            "Central Care Physicians", "Eastside Health Partners", "Westview Medical",
            "Northpoint Healthcare", "Southside Medical Center", "Heritage Health",
            "Cornerstone Medical", "Gateway Health Services", "Precision Medical Group"
        ]
        
        with self.driver.session() as session:
            for i in range(count):
                provider_id = f"PROV_BG_{self.provider_counter:05d}"
                name = provider_names[i % len(provider_names)]
                if i >= len(provider_names):
                    name = f"{name} {i // len(provider_names) + 1}"
                
                # Create provider with address
                city, state, zip_code = self.generate_city_state()
                address_id = f"ADDR_{self.address_counter:05d}"
                self.address_counter += 1
                
                session.run("""
                    CREATE (p:Provider {
                        id: $provider_id,
                        name: $name,
                        license: $license,
                        opened_date: $opened_date,
                        status: 'Active'
                    })
                    CREATE (a:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Business'
                    })
                    CREATE (p)-[:LOCATED_AT]->(a)
                """,
                    provider_id=provider_id,
                    name=name,
                    license=f"MED-{random.randint(100000, 999999)}",
                    opened_date=self.generate_date(1500, 365),
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code
                )
                
                self.background_providers.append(provider_id)
                self.provider_counter += 1
        
        print(f"✓ Created {count} background providers")

    def create_background_attorneys(self, count=12):
        """Create background attorneys (legitimate volume)."""
        print(f"\nCreating {count} background attorneys...")
        
        with self.driver.session() as session:
            for i in range(count):
                attorney_id = f"ATT_BG_{self.attorney_counter:05d}"
                attorney_name = f"{self.generate_name()}, Esq."
                
                session.run("""
                    CREATE (a:Attorney {
                        id: $id,
                        name: $name,
                        bar_number: $bar_number
                    })
                """,
                    id=attorney_id,
                    name=attorney_name,
                    bar_number=f"BAR-{random.randint(100000, 999999)}"
                )
                
                self.background_attorneys.append(attorney_id)
                self.attorney_counter += 1
        
        print(f"✓ Created {count} background attorneys")

    def create_background_bodyshops(self, count=8):
        """Create background body shops."""
        print(f"\nCreating {count} background body shops...")
        
        shop_names = [
            "Expert Auto Body", "Premier Collision Center", "Quality Auto Repair",
            "Elite Body Works", "Precision Collision", "Master Auto Body",
            "Champion Collision", "Superior Auto Repair"
        ]
        
        with self.driver.session() as session:
            for i in range(count):
                bodyshop_id = f"BS_BG_{self.bodyshop_counter:05d}"
                name = shop_names[i % len(shop_names)]
                
                session.run("""
                    CREATE (b:BodyShop {
                        id: $id,
                        name: $name,
                        license: $license
                    })
                """,
                    id=bodyshop_id,
                    name=name,
                    license=f"BS-{random.randint(10000, 99999)}"
                )
                
                self.background_bodyshops.append(bodyshop_id)
                self.bodyshop_counter += 1
        
        print(f"✓ Created {count} background body shops")

    def create_background_locations(self, count=20):
        """Create accident locations (intersections, highways)."""
        print(f"\nCreating {count} accident locations...")
        
        location_templates = [
            ("I-85 Exit {}", "Highway"),
            ("Highway 20 Mile {}", "Highway"),
            ("{} & Main Street", "Intersection"),
            ("{} & Oak Avenue", "Intersection"),
            ("Highway 78 Exit {}", "Highway"),
            ("I-20 Mile Marker {}", "Highway"),
            ("{} Street & {} Avenue", "Intersection"),
            ("Route {} Junction", "Highway")
        ]
        
        with self.driver.session() as session:
            for i in range(count):
                location_id = f"LOC_{self.location_counter:05d}"
                template = random.choice(location_templates)
                
                if template[0].count("{}") == 2:
                    name = template[0].format(random.randint(1, 50), random.randint(1, 20))
                else:
                    name = template[0].format(random.randint(1, 50))
                
                session.run("""
                    CREATE (l:Location {
                        id: $id,
                        name: $name,
                        type: $type,
                        lat: $lat,
                        lng: $lng
                    })
                """,
                    id=location_id,
                    name=name,
                    type=template[1],
                    lat=round(33.5 + random.uniform(-0.5, 0.5), 4),
                    lng=round(-84.4 + random.uniform(-0.5, 0.5), 4)
                )
                
                self.background_locations.append(location_id)
                self.location_counter += 1
        
        print(f"✓ Created {count} accident locations")

    # =========================================================================
    # BACKGROUND LEGITIMATE DATA
    # =========================================================================
    
    def create_legitimate_claims(self, count=150):
        """
        Create legitimate background claims with realistic patterns.
        
        Rules:
        - Each claimant has UNIQUE phone
        - Each claimant has UNIQUE address (except 5% couples)
        - Providers get 3-8 claims each (distributed)
        - Attorneys get 2-6 clients each (30% of claims)
        - No suspicious patterns
        """
        print(f"\nCreating {count} legitimate claims...")
        
        # Track provider/attorney claim counts to stay in bounds
        provider_claims = {p: 0 for p in self.background_providers}
        attorney_claims = {a: 0 for a in self.background_attorneys}
        
        with self.driver.session() as session:
            couples_created = 0
            max_couples = int(count * 0.05)  # 5% are couples
            
            for i in range(count):
                claim_id = f"CLM_BG_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                # Create claimant with unique phone and address
                claimant_id = f"P_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                
                phone_number = self.generate_phone()
                phone_id = f"PH_{self.phone_counter:05d}"
                self.phone_counter += 1
                
                city, state, zip_code = self.generate_city_state()
                address_id = f"ADDR_{self.address_counter:05d}"
                self.address_counter += 1
                
                # Select provider (keep within 3-8 range)
                available_providers = [p for p in self.background_providers if provider_claims[p] < 8]
                if not available_providers:
                    available_providers = self.background_providers
                provider_id = random.choice(available_providers)
                provider_claims[provider_id] += 1
                
                # Select adjuster
                adjuster_id = random.choice(self.adjuster_pool)
                
                # Select location
                location_id = random.choice(self.background_locations)
                
                # Claim details
                claim_amount = round(random.uniform(2000, 25000), 2)
                claim_date = self.generate_date(365, 0)
                incident_types = ["Rear-End Collision", "Side Impact", "Parking Lot Incident", 
                                 "Multi-Vehicle Accident", "Single Vehicle Accident"]
                incident_type = random.choice(incident_types)
                
                # Create the claim network
                session.run("""
                    // Create claim
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: $claim_name,
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: $incident_type,
                        status: 'Closed',
                        is_fraud: false
                    })
                    
                    // Create claimant
                    CREATE (p:Person:Claimant {
                        id: $claimant_id,
                        name: $claimant_name,
                        ssn: $ssn,
                        role: 'Claimant'
                    })
                    
                    // Create phone
                    CREATE (ph:Phone {
                        id: $phone_id,
                        number: $phone_number
                    })
                    
                    // Create address
                    CREATE (addr:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential'
                    })
                    
                    // Connect claimant to phone/address
                    CREATE (p)-[:HAS_PHONE]->(ph)
                    CREATE (p)-[:LIVES_AT]->(addr)
                    
                    // Connect claim
                    CREATE (c)-[:FILED_BY]->(p)
                    
                    // Connect to provider
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    
                    // Connect to adjuster
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    
                    // Connect to location
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    claim_name=f"Auto Claim - {incident_type}",
                    amount=claim_amount,
                    claim_date=claim_date,
                    incident_type=incident_type,
                    claimant_id=claimant_id,
                    claimant_name=claimant_name,
                    ssn=self.generate_ssn(),
                    phone_id=phone_id,
                    phone_number=phone_number,
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code,
                    provider_id=provider_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
                
                # 30% chance of attorney (distributed across attorneys)
                if random.random() < 0.30:
                    available_attorneys = [a for a in self.background_attorneys if attorney_claims[a] < 6]
                    if not available_attorneys:
                        available_attorneys = self.background_attorneys
                    attorney_id = random.choice(available_attorneys)
                    attorney_claims[attorney_id] += 1
                    
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (a:Attorney {id: $attorney_id})
                        CREATE (c)-[:REPRESENTED_BY]->(a)
                    """, claim_id=claim_id, attorney_id=attorney_id)
                
                # 40% chance of body shop
                if random.random() < 0.40:
                    bodyshop_id = random.choice(self.background_bodyshops)
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (b:BodyShop {id: $bodyshop_id})
                        CREATE (c)-[:REPAIRED_AT]->(b)
                    """, claim_id=claim_id, bodyshop_id=bodyshop_id)
                
                # 60% chance of witness
                if random.random() < 0.60:
                    witness_id = f"P_{self.person_counter:05d}"
                    witness_name = self.generate_name()
                    self.person_counter += 1
                    
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        CREATE (w:Person:Witness {
                            id: $witness_id,
                            name: $witness_name,
                            role: 'Witness'
                        })
                        CREATE (c)-[:WITNESSED_BY]->(w)
                    """, claim_id=claim_id, witness_id=witness_id, witness_name=witness_name)
        
        self.stats['background_claims'] = count
        print(f"✓ Created {count} legitimate claims")

    # =========================================================================
    # SCENARIO 1: THE TWO-HOUR ATTORNEY
    # =========================================================================
    
    def create_scenario_1_two_hour_attorney(self):
        """
        Creates the "Two-Hour Attorney" fraud ring.
        
        Structure:
        - Attorney J. Marcus Webb (47 clients)
        - 2 clinics: Wellness Partners Medical + Peak Recovery Clinic
        - Both clinics share business address (1847 Commerce Blvd)
        - Linda Webb (wife) = registered agent for both clinics
        - Maria Santos = paralegal at Webb's firm + patient coordinator at Peak + witness on 8 claims
        - James Rivera = billing manager at Wellness + lives with Maria
        """
        print("\n" + "="*60)
        print("SCENARIO 1: The Two-Hour Attorney")
        print("="*60)
        
        with self.driver.session() as session:
            # === CREATE ATTORNEY: J. Marcus Webb ===
            webb_id = "ATT_S1_WEBB"
            session.run("""
                CREATE (a:Attorney {
                    id: $id,
                    name: 'J. Marcus Webb',
                    bar_number: 'BAR-789456',
                    scenario: 'scenario_1'
                })
            """, id=webb_id)
            print("  ✓ Created Attorney: J. Marcus Webb")
            
            # === CREATE LINDA WEBB (Wife/Registered Agent) ===
            linda_id = "P_S1_LINDA"
            session.run("""
                CREATE (p:Person:Employee {
                    id: $id,
                    name: 'Linda Webb',
                    role: 'Registered Agent',
                    job_title: 'Registered Agent',
                    scenario: 'scenario_1'
                })
            """, id=linda_id)
            
            # Marriage relationship
            session.run("""
                MATCH (a:Attorney {id: 'ATT_S1_WEBB'})
                MATCH (p:Person {id: 'P_S1_LINDA'})
                CREATE (a)-[:MARRIED_TO]->(p)
            """)
            print("  ✓ Created Linda Webb (wife, registered agent)")
            
            # === CREATE SHARED BUSINESS ADDRESS ===
            biz_address_id = "ADDR_S1_BIZ"
            session.run("""
                CREATE (a:Address {
                    id: $id,
                    street: '1847 Commerce Boulevard',
                    unit: 'Suite 200',
                    city: 'Atlanta',
                    state: 'GA',
                    zip: '30309',
                    type: 'Business',
                    scenario: 'scenario_1'
                })
            """, id=biz_address_id)
            
            # === CREATE TWO CLINICS ===
            wellness_id = "PROV_S1_WELLNESS"
            peak_id = "PROV_S1_PEAK"
            
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: 'Wellness Partners Medical',
                    license: 'MED-S1-001',
                    opened_date: '2024-01-15',
                    status: 'Active',
                    scenario: 'scenario_1'
                })
                WITH p
                MATCH (a:Address {id: 'ADDR_S1_BIZ'})
                CREATE (p)-[:LOCATED_AT]->(a)
                WITH p
                MATCH (linda:Person {id: 'P_S1_LINDA'})
                CREATE (p)-[:REGISTERED_AGENT]->(linda)
            """, id=wellness_id)
            
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: 'Peak Recovery Clinic',
                    license: 'MED-S1-002',
                    opened_date: '2024-04-01',
                    status: 'Active',
                    scenario: 'scenario_1'
                })
                WITH p
                MATCH (a:Address {id: 'ADDR_S1_BIZ'})
                CREATE (p)-[:LOCATED_AT]->(a)
                WITH p
                MATCH (linda:Person {id: 'P_S1_LINDA'})
                CREATE (p)-[:REGISTERED_AGENT]->(linda)
            """, id=peak_id)
            print("  ✓ Created 2 clinics at shared address with Linda as registered agent")
            
            # === CREATE EMPLOYEES WITH SHARED HOME ADDRESS ===
            home_address_id = "ADDR_S1_HOME"
            session.run("""
                CREATE (a:Address {
                    id: $id,
                    street: '445 Maple Street',
                    unit: 'Apt 12',
                    city: 'Atlanta',
                    state: 'GA',
                    zip: '30312',
                    type: 'Residential',
                    scenario: 'scenario_1'
                })
            """, id=home_address_id)
            
            # James Rivera - Billing Manager at Wellness
            james_id = "P_S1_JAMES"
            session.run("""
                CREATE (p:Person:Employee {
                    id: $id,
                    name: 'James Rivera',
                    role: 'Employee',
                    job_title: 'Billing Manager',
                    scenario: 'scenario_1'
                })
                WITH p
                MATCH (addr:Address {id: 'ADDR_S1_HOME'})
                CREATE (p)-[:LIVES_AT]->(addr)
                WITH p
                MATCH (prov:Provider {id: 'PROV_S1_WELLNESS'})
                CREATE (prov)-[:EMPLOYS]->(p)
            """, id=james_id)
            
            # Maria Santos - Patient Coordinator at Peak + Paralegal at Webb's
            maria_id = "P_S1_MARIA"
            session.run("""
                CREATE (p:Person:Employee:Witness {
                    id: $id,
                    name: 'Maria Santos',
                    role: 'Employee',
                    job_title: 'Patient Coordinator / Paralegal',
                    scenario: 'scenario_1'
                })
                WITH p
                MATCH (addr:Address {id: 'ADDR_S1_HOME'})
                CREATE (p)-[:LIVES_AT]->(addr)
                WITH p
                MATCH (prov:Provider {id: 'PROV_S1_PEAK'})
                CREATE (prov)-[:EMPLOYS]->(p)
                WITH p
                MATCH (att:Attorney {id: 'ATT_S1_WEBB'})
                CREATE (att)-[:EMPLOYS]->(p)
            """, id=maria_id)
            print("  ✓ Created employees: James (billing) + Maria (coordinator/paralegal) at shared home")
            
            # === CREATE 47 CLAIMANTS WITH CLAIMS ===
            print("  Creating 47 claims for Webb's network...")
            
            claims_at_wellness = 0
            claims_at_peak = 0
            maria_witness_count = 0
            
            for i in range(47):
                claim_id = f"CLM_S1_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                claimant_id = f"P_S1_CLM_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                
                # Create unique phone/address for each claimant
                phone_id = f"PH_S1_{self.phone_counter:05d}"
                phone_number = self.generate_phone("555")
                self.phone_counter += 1
                
                address_id = f"ADDR_S1_CLM_{self.address_counter:05d}"
                city, state, zip_code = self.generate_city_state()
                self.address_counter += 1
                
                # Distribute between clinics (41 go to either clinic)
                if i < 41:
                    if claims_at_wellness < 22:
                        provider_id = wellness_id
                        claims_at_wellness += 1
                    else:
                        provider_id = peak_id
                        claims_at_peak += 1
                else:
                    # 6 go to background providers (slight variety)
                    provider_id = random.choice(self.background_providers)
                
                adjuster_id = random.choice(self.adjuster_pool)
                location_id = random.choice(self.background_locations)
                
                # Higher claim amounts (mill behavior)
                claim_amount = round(random.uniform(15000, 45000), 2)
                claim_date = self.generate_date(180, 0)
                
                session.run("""
                    // Create claim
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: 'Auto Claim - Soft Tissue Injury',
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: 'Rear-End Collision',
                        status: 'Open',
                        is_fraud: false,
                        scenario: 'scenario_1'
                    })
                    
                    // Create claimant
                    CREATE (p:Person:Claimant {
                        id: $claimant_id,
                        name: $claimant_name,
                        ssn: $ssn,
                        role: 'Claimant',
                        scenario: 'scenario_1'
                    })
                    
                    // Create phone and address
                    CREATE (ph:Phone {id: $phone_id, number: $phone_number})
                    CREATE (addr:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential'
                    })
                    
                    CREATE (p)-[:HAS_PHONE]->(ph)
                    CREATE (p)-[:LIVES_AT]->(addr)
                    CREATE (c)-[:FILED_BY]->(p)
                    
                    // Connect to Webb
                    WITH c
                    MATCH (att:Attorney {id: 'ATT_S1_WEBB'})
                    CREATE (c)-[:REPRESENTED_BY]->(att)
                    
                    // Connect to provider
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    
                    // Connect to adjuster
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    
                    // Connect to location
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    amount=claim_amount,
                    claim_date=claim_date,
                    claimant_id=claimant_id,
                    claimant_name=claimant_name,
                    ssn=self.generate_ssn(),
                    phone_id=phone_id,
                    phone_number=phone_number,
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code,
                    provider_id=provider_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
                
                # First 8 claims at Wellness get Maria as witness (cross-role fraud)
                if i < 8:
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (m:Person {id: 'P_S1_MARIA'})
                        CREATE (c)-[:WITNESSED_BY]->(m)
                    """, claim_id=claim_id)
                    maria_witness_count += 1
            
            self.stats['scenario_1_claims'] = 47
            print(f"  ✓ Created 47 claims (41 at Webb's clinics, 8 with Maria as witness)")
            print(f"    - Wellness Partners: {claims_at_wellness} claims")
            print(f"    - Peak Recovery: {claims_at_peak} claims")
            print(f"    - Maria Santos witness appearances: {maria_witness_count}")

    # =========================================================================
    # SCENARIO 2: THE TYPO THAT WASN'T
    # =========================================================================
    
    def create_scenario_2_identity_web(self):
        """
        Creates the "Identity Web" fraud ring.
        
        Structure:
        - 7 claimants total
        - Phone 555-847-2931 shared by 5 claimants
        - Phone 555-847-2932 shared by 2 claimants
        - Address "847 Oak Street, Apt 4B" shared by 5 claimants
        - 6 claims totaling ~$185,000
        - All within 45-day window
        """
        print("\n" + "="*60)
        print("SCENARIO 2: The Typo That Wasn't (Identity Web)")
        print("="*60)
        
        with self.driver.session() as session:
            # === CREATE SHARED PHONES ===
            phone1_id = "PH_S2_MAIN"
            phone1_number = "555-847-2931"
            phone2_id = "PH_S2_ALT"
            phone2_number = "555-847-2932"
            
            session.run("""
                CREATE (p1:Phone {id: $id1, number: $num1, scenario: 'scenario_2'})
                CREATE (p2:Phone {id: $id2, number: $num2, scenario: 'scenario_2'})
            """, id1=phone1_id, num1=phone1_number, id2=phone2_id, num2=phone2_number)
            
            self.used_phones.add(phone1_number)
            self.used_phones.add(phone2_number)
            print(f"  ✓ Created shared phones: {phone1_number}, {phone2_number}")
            
            # === CREATE SHARED ADDRESS ===
            shared_address_id = "ADDR_S2_OAK"
            session.run("""
                CREATE (a:Address {
                    id: $id,
                    street: '847 Oak Street',
                    unit: 'Apt 4B',
                    city: 'Atlanta',
                    state: 'GA',
                    zip: '30310',
                    type: 'Residential',
                    scenario: 'scenario_2'
                })
            """, id=shared_address_id)
            print("  ✓ Created shared address: 847 Oak Street, Apt 4B")
            
            # === CREATE 7 CLAIMANTS ===
            # Phone 1 users (5): Marcus, Tanya, Deshawn, Keisha, Andre
            # Phone 2 users (2): Lisa, Tyrell
            # Address users (5): Deshawn, Keisha, Andre, Lisa, Tyrell
            
            claimants = [
                {"name": "Marcus Williams", "phone": phone1_id, "address": None},
                {"name": "Tanya Williams", "phone": phone1_id, "address": None},
                {"name": "Deshawn Brooks", "phone": phone1_id, "address": shared_address_id},
                {"name": "Keisha Brooks", "phone": phone1_id, "address": shared_address_id},
                {"name": "Andre Thompson", "phone": phone1_id, "address": shared_address_id},
                {"name": "Lisa Morgan", "phone": phone2_id, "address": shared_address_id},
                {"name": "Tyrell Morgan", "phone": phone2_id, "address": shared_address_id},
            ]
            
            claimant_ids = []
            
            for i, c in enumerate(claimants):
                claimant_id = f"P_S2_{i:03d}"
                claimant_ids.append(claimant_id)
                
                # Create separate address if not using shared
                if c["address"] is None:
                    addr_id = f"ADDR_S2_{self.address_counter:05d}"
                    city, state, zip_code = self.generate_city_state()
                    self.address_counter += 1
                    
                    session.run("""
                        CREATE (p:Person:Claimant {
                            id: $claimant_id,
                            name: $name,
                            ssn: $ssn,
                            role: 'Claimant',
                            scenario: 'scenario_2'
                        })
                        CREATE (addr:Address {
                            id: $addr_id,
                            street: $street,
                            city: $city,
                            state: $state,
                            zip: $zip,
                            type: 'Residential'
                        })
                        CREATE (p)-[:LIVES_AT]->(addr)
                        WITH p
                        MATCH (ph:Phone {id: $phone_id})
                        CREATE (p)-[:HAS_PHONE]->(ph)
                    """,
                        claimant_id=claimant_id,
                        name=c["name"],
                        ssn=self.generate_ssn(),
                        addr_id=addr_id,
                        street=self.generate_street_address(),
                        city=city,
                        state=state,
                        zip=zip_code,
                        phone_id=c["phone"]
                    )
                else:
                    session.run("""
                        CREATE (p:Person:Claimant {
                            id: $claimant_id,
                            name: $name,
                            ssn: $ssn,
                            role: 'Claimant',
                            scenario: 'scenario_2'
                        })
                        WITH p
                        MATCH (addr:Address {id: $addr_id})
                        CREATE (p)-[:LIVES_AT]->(addr)
                        WITH p
                        MATCH (ph:Phone {id: $phone_id})
                        CREATE (p)-[:HAS_PHONE]->(ph)
                    """,
                        claimant_id=claimant_id,
                        name=c["name"],
                        ssn=self.generate_ssn(),
                        addr_id=c["address"],
                        phone_id=c["phone"]
                    )
            
            print(f"  ✓ Created 7 claimants with shared identifiers")
            
            # === CREATE 6 CLAIMS (totaling ~$185K) ===
            claim_amounts = [32000, 28500, 35000, 31000, 29500, 29000]  # Total: $185,000
            base_date = datetime.now() - timedelta(days=60)
            
            for i in range(6):
                claim_id = f"CLM_S2_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                # Spread across 45-day window
                claim_date = (base_date + timedelta(days=random.randint(0, 45))).strftime("%Y-%m-%d")
                
                # Different claimant for each claim (one claimant has 2 claims)
                if i < 6:
                    claimant_id = claimant_ids[i]
                else:
                    claimant_id = claimant_ids[0]  # Marcus has 2nd claim
                
                provider_id = random.choice(self.background_providers)
                adjuster_id = random.choice(self.adjuster_pool)
                location_id = random.choice(self.background_locations)
                
                session.run("""
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: 'Auto Claim - Rear-End Collision',
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: 'Rear-End Collision',
                        status: 'Open',
                        is_fraud: false,
                        scenario: 'scenario_2'
                    })
                    WITH c
                    MATCH (p:Person {id: $claimant_id})
                    CREATE (c)-[:FILED_BY]->(p)
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    amount=claim_amounts[i],
                    claim_date=claim_date,
                    claimant_id=claimant_id,
                    provider_id=provider_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
            
            self.stats['scenario_2_claims'] = 6
            print(f"  ✓ Created 6 claims totaling ${sum(claim_amounts):,}")

    # =========================================================================
    # SCENARIO 3A: THE AUDIT - SUNRISE WELLNESS (FRAUD)
    # =========================================================================
    
    def create_scenario_3a_sunrise_fraud(self):
        """
        Creates the fraudulent provider network for audit comparison.
        
        Structure:
        - Sunrise Wellness Clinic (28 claims)
        - Peak Recovery Center (15 claims, different from Scenario 1!)
        - Attorney Roberto Vega (82% referral rate to Sunrise)
        - Phone 555-991-8847 shared by 7 claimants across BOTH clinics
        - Carmen Reyes = witness at BOTH clinics (6 claims total)
        """
        print("\n" + "="*60)
        print("SCENARIO 3A: The Audit - Sunrise Wellness (FRAUD)")
        print("="*60)
        
        with self.driver.session() as session:
            # === CREATE ATTORNEY: Roberto Vega ===
            vega_id = "ATT_S3_VEGA"
            session.run("""
                CREATE (a:Attorney {
                    id: $id,
                    name: 'Roberto Vega',
                    bar_number: 'BAR-456123',
                    scenario: 'scenario_3'
                })
            """, id=vega_id)
            print("  ✓ Created Attorney: Roberto Vega")
            
            # === CREATE TWO CLINICS ===
            sunrise_id = "PROV_S3_SUNRISE"
            peak_s3_id = "PROV_S3_PEAK"
            
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: 'Sunrise Wellness Clinic',
                    license: 'MED-S3-001',
                    opened_date: '2024-02-01',
                    status: 'Active',
                    avg_billing_pct_above_peer: 38,
                    scenario: 'scenario_3'
                })
            """, id=sunrise_id)
            
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: 'Peak Recovery Center',
                    license: 'MED-S3-002',
                    opened_date: '2024-05-01',
                    status: 'Active',
                    scenario: 'scenario_3'
                })
            """, id=peak_s3_id)
            print("  ✓ Created 2 clinics: Sunrise Wellness + Peak Recovery")
            
            # === CREATE SHARED PHONE ===
            shared_phone_id = "PH_S3_SHARED"
            shared_phone_number = "555-991-8847"
            session.run("""
                CREATE (p:Phone {id: $id, number: $num, scenario: 'scenario_3'})
            """, id=shared_phone_id, num=shared_phone_number)
            self.used_phones.add(shared_phone_number)
            print(f"  ✓ Created shared phone: {shared_phone_number}")
            
            # === CREATE CARMEN REYES (Cross-clinic witness) ===
            carmen_id = "P_S3_CARMEN"
            session.run("""
                CREATE (p:Person:Witness {
                    id: $id,
                    name: 'Carmen Reyes',
                    role: 'Witness',
                    scenario: 'scenario_3'
                })
            """, id=carmen_id)
            print("  ✓ Created Carmen Reyes (professional witness)")
            
            # === CREATE 28 CLAIMS AT SUNRISE ===
            print("  Creating 28 claims at Sunrise Wellness...")
            
            vega_client_count = 0
            shared_phone_users = 0
            carmen_witness_sunrise = 0
            
            for i in range(28):
                claim_id = f"CLM_S3_SUN_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                claimant_id = f"P_S3_SUN_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                
                # First 7 claimants share the phone
                if shared_phone_users < 4:  # 4 at Sunrise
                    phone_id = shared_phone_id
                    shared_phone_users += 1
                else:
                    phone_id = f"PH_S3_{self.phone_counter:05d}"
                    session.run("""
                        CREATE (p:Phone {id: $id, number: $num})
                    """, id=phone_id, num=self.generate_phone())
                    self.phone_counter += 1
                
                address_id = f"ADDR_S3_{self.address_counter:05d}"
                city, state, zip_code = self.generate_city_state()
                self.address_counter += 1
                
                adjuster_id = random.choice(self.adjuster_pool)
                location_id = random.choice(self.background_locations)
                
                # Higher amounts (billing anomaly)
                claim_amount = round(random.uniform(18000, 42000), 2)
                claim_date = self.generate_date(180, 0)
                
                session.run("""
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: 'Auto Claim - Soft Tissue',
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: 'Rear-End Collision',
                        status: 'Open',
                        is_fraud: false,
                        scenario: 'scenario_3'
                    })
                    
                    CREATE (p:Person:Claimant {
                        id: $claimant_id,
                        name: $claimant_name,
                        ssn: $ssn,
                        role: 'Claimant',
                        scenario: 'scenario_3'
                    })
                    
                    CREATE (addr:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential'
                    })
                    
                    CREATE (p)-[:LIVES_AT]->(addr)
                    CREATE (c)-[:FILED_BY]->(p)
                    
                    WITH c, p
                    MATCH (ph:Phone {id: $phone_id})
                    CREATE (p)-[:HAS_PHONE]->(ph)
                    
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    amount=claim_amount,
                    claim_date=claim_date,
                    claimant_id=claimant_id,
                    claimant_name=claimant_name,
                    ssn=self.generate_ssn(),
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code,
                    phone_id=phone_id,
                    provider_id=sunrise_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
                
                # 23 of 28 (82%) represented by Vega
                if vega_client_count < 23:
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (a:Attorney {id: $vega_id})
                        CREATE (c)-[:REPRESENTED_BY]->(a)
                    """, claim_id=claim_id, vega_id=vega_id)
                    vega_client_count += 1
                
                # First 4 get Carmen as witness
                if carmen_witness_sunrise < 4:
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (w:Person {id: $carmen_id})
                        CREATE (c)-[:WITNESSED_BY]->(w)
                    """, claim_id=claim_id, carmen_id=carmen_id)
                    carmen_witness_sunrise += 1
            
            print(f"  ✓ Created 28 claims at Sunrise (23 with Vega, 4 with Carmen witness)")
            
            # === CREATE 15 CLAIMS AT PEAK (some overlap) ===
            print("  Creating 15 claims at Peak Recovery...")
            
            carmen_witness_peak = 0
            shared_phone_peak = 0
            
            for i in range(15):
                claim_id = f"CLM_S3_PEAK_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                claimant_id = f"P_S3_PEAK_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                
                # 3 more claimants share the phone (total 7 across both clinics)
                if shared_phone_peak < 3:
                    phone_id = shared_phone_id
                    shared_phone_peak += 1
                else:
                    phone_id = f"PH_S3_{self.phone_counter:05d}"
                    session.run("""
                        CREATE (p:Phone {id: $id, number: $num})
                    """, id=phone_id, num=self.generate_phone())
                    self.phone_counter += 1
                
                address_id = f"ADDR_S3_{self.address_counter:05d}"
                city, state, zip_code = self.generate_city_state()
                self.address_counter += 1
                
                adjuster_id = random.choice(self.adjuster_pool)
                location_id = random.choice(self.background_locations)
                
                claim_amount = round(random.uniform(16000, 38000), 2)
                claim_date = self.generate_date(180, 0)
                
                session.run("""
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: 'Auto Claim - Soft Tissue',
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: 'Rear-End Collision',
                        status: 'Open',
                        is_fraud: false,
                        scenario: 'scenario_3'
                    })
                    
                    CREATE (p:Person:Claimant {
                        id: $claimant_id,
                        name: $claimant_name,
                        ssn: $ssn,
                        role: 'Claimant',
                        scenario: 'scenario_3'
                    })
                    
                    CREATE (addr:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential'
                    })
                    
                    CREATE (p)-[:LIVES_AT]->(addr)
                    CREATE (c)-[:FILED_BY]->(p)
                    
                    WITH c, p
                    MATCH (ph:Phone {id: $phone_id})
                    CREATE (p)-[:HAS_PHONE]->(ph)
                    
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    amount=claim_amount,
                    claim_date=claim_date,
                    claimant_id=claimant_id,
                    claimant_name=claimant_name,
                    ssn=self.generate_ssn(),
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code,
                    phone_id=phone_id,
                    provider_id=peak_s3_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
                
                # 12 of 15 also with Vega
                if i < 12:
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (a:Attorney {id: $vega_id})
                        CREATE (c)-[:REPRESENTED_BY]->(a)
                    """, claim_id=claim_id, vega_id=vega_id)
                
                # 2 get Carmen as witness
                if carmen_witness_peak < 2:
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (w:Person {id: $carmen_id})
                        CREATE (c)-[:WITNESSED_BY]->(w)
                    """, claim_id=claim_id, carmen_id=carmen_id)
                    carmen_witness_peak += 1
            
            self.stats['scenario_3a_claims'] = 28 + 15
            print(f"  ✓ Created 15 claims at Peak (12 with Vega, 2 with Carmen witness)")
            print(f"  ✓ Total shared phone users across both clinics: 7")
            print(f"  ✓ Carmen Reyes witness appearances: {carmen_witness_sunrise + carmen_witness_peak}")

    # =========================================================================
    # SCENARIO 3B: THE AUDIT - CITY GENERAL (LEGITIMATE)
    # =========================================================================
    
    def create_scenario_3b_city_general_legitimate(self):
        """
        Creates the legitimate high-volume provider for false positive contrast.
        
        Structure:
        - City General Emergency Room (32 claims)
        - Located at high-traffic accident corridor (I-85/Highway 20)
        - 12 different attorneys (distributed)
        - ALL unique phones and addresses
        - 2 legitimate married couples (shared addresses - marked as such)
        """
        print("\n" + "="*60)
        print("SCENARIO 3B: The Audit - City General (LEGITIMATE)")
        print("="*60)
        
        with self.driver.session() as session:
            # === CREATE CITY GENERAL ER ===
            cg_id = "PROV_S3_CITYGEN"
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: 'City General Emergency Room',
                    license: 'MED-S3-CG001',
                    opened_date: '2015-06-01',
                    status: 'Active',
                    avg_billing_pct_above_peer: 42,
                    legitimate_high_volume: true,
                    scenario: 'scenario_3'
                })
            """, id=cg_id)
            print("  ✓ Created City General Emergency Room")
            
            # === CREATE HIGH-TRAFFIC LOCATION ===
            location_id = "LOC_S3_I85"
            session.run("""
                CREATE (l:Location {
                    id: $id,
                    name: 'I-85 / Highway 20 Junction',
                    type: 'Highway',
                    lat: 33.7490,
                    lng: -84.3880,
                    high_traffic: true,
                    scenario: 'scenario_3'
                })
            """, id=location_id)
            print("  ✓ Created high-traffic accident location")
            
            # === CREATE 32 CLAIMS (all unique) ===
            print("  Creating 32 legitimate claims...")
            
            # Track attorney usage (max 4 clients each for 12 attorneys)
            cg_attorneys = []
            attorney_claims = {}
            
            # Create 12 attorneys for this provider
            for i in range(12):
                att_id = f"ATT_S3_CG_{i:03d}"
                att_name = f"{self.generate_name()}, Esq."
                session.run("""
                    CREATE (a:Attorney {
                        id: $id,
                        name: $name,
                        bar_number: $bar
                    })
                """, id=att_id, name=att_name, bar=f"BAR-CG{random.randint(100000, 999999)}")
                cg_attorneys.append(att_id)
                attorney_claims[att_id] = 0
            
            # 2 married couples (4 people sharing 2 addresses)
            couple_addresses = []
            for c in range(2):
                addr_id = f"ADDR_S3_COUPLE_{c}"
                city, state, zip_code = self.generate_city_state()
                session.run("""
                    CREATE (a:Address {
                        id: $id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential',
                        legitimate_shared: true,
                        relationship: 'Married Couple'
                    })
                """, id=addr_id, street=self.generate_street_address(), 
                   city=city, state=state, zip=zip_code)
                couple_addresses.append(addr_id)
            
            for i in range(32):
                claim_id = f"CLM_S3_CG_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                claimant_id = f"P_S3_CG_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                
                # Unique phone for everyone
                phone_id = f"PH_S3_CG_{self.phone_counter:05d}"
                phone_number = self.generate_phone()
                self.phone_counter += 1
                
                # First 4 claimants are 2 married couples
                if i < 4:
                    address_id = couple_addresses[i // 2]
                    create_address = False
                else:
                    address_id = f"ADDR_S3_CG_{self.address_counter:05d}"
                    create_address = True
                    self.address_counter += 1
                
                adjuster_id = random.choice(self.adjuster_pool)
                
                # Normal claim amounts
                claim_amount = round(random.uniform(3000, 18000), 2)
                claim_date = self.generate_date(365, 0)
                
                if create_address:
                    city, state, zip_code = self.generate_city_state()
                    session.run("""
                        CREATE (c:Claim {
                            id: $claim_id,
                            name: 'Auto Claim - ER Visit',
                            claim_amount: $amount,
                            claim_date: $claim_date,
                            claim_type: 'Auto',
                            incident_type: $incident_type,
                            status: 'Closed',
                            is_fraud: false,
                            scenario: 'scenario_3'
                        })
                        
                        CREATE (p:Person:Claimant {
                            id: $claimant_id,
                            name: $claimant_name,
                            ssn: $ssn,
                            role: 'Claimant',
                            scenario: 'scenario_3'
                        })
                        
                        CREATE (ph:Phone {id: $phone_id, number: $phone_number})
                        
                        CREATE (addr:Address {
                            id: $address_id,
                            street: $street,
                            city: $city,
                            state: $state,
                            zip: $zip,
                            type: 'Residential'
                        })
                        
                        CREATE (p)-[:HAS_PHONE]->(ph)
                        CREATE (p)-[:LIVES_AT]->(addr)
                        CREATE (c)-[:FILED_BY]->(p)
                        
                        WITH c
                        MATCH (prov:Provider {id: $provider_id})
                        CREATE (c)-[:TREATED_AT]->(prov)
                        
                        WITH c
                        MATCH (adj:Person:Adjuster {id: $adjuster_id})
                        CREATE (c)-[:HANDLED_BY]->(adj)
                        
                        WITH c
                        MATCH (loc:Location {id: $location_id})
                        CREATE (c)-[:OCCURRED_AT]->(loc)
                    """,
                        claim_id=claim_id,
                        amount=claim_amount,
                        claim_date=claim_date,
                        incident_type=random.choice(["Rear-End Collision", "Side Impact", "Multi-Vehicle"]),
                        claimant_id=claimant_id,
                        claimant_name=claimant_name,
                        ssn=self.generate_ssn(),
                        phone_id=phone_id,
                        phone_number=phone_number,
                        address_id=address_id,
                        street=self.generate_street_address(),
                        city=city,
                        state=state,
                        zip=zip_code,
                        provider_id=cg_id,
                        adjuster_id=adjuster_id,
                        location_id=location_id
                    )
                else:
                    # Use existing couple address
                    session.run("""
                        CREATE (c:Claim {
                            id: $claim_id,
                            name: 'Auto Claim - ER Visit',
                            claim_amount: $amount,
                            claim_date: $claim_date,
                            claim_type: 'Auto',
                            incident_type: $incident_type,
                            status: 'Closed',
                            is_fraud: false,
                            scenario: 'scenario_3'
                        })
                        
                        CREATE (p:Person:Claimant {
                            id: $claimant_id,
                            name: $claimant_name,
                            ssn: $ssn,
                            role: 'Claimant',
                            scenario: 'scenario_3'
                        })
                        
                        CREATE (ph:Phone {id: $phone_id, number: $phone_number})
                        CREATE (p)-[:HAS_PHONE]->(ph)
                        
                        WITH c, p
                        MATCH (addr:Address {id: $address_id})
                        CREATE (p)-[:LIVES_AT]->(addr)
                        CREATE (c)-[:FILED_BY]->(p)
                        
                        WITH c
                        MATCH (prov:Provider {id: $provider_id})
                        CREATE (c)-[:TREATED_AT]->(prov)
                        
                        WITH c
                        MATCH (adj:Person:Adjuster {id: $adjuster_id})
                        CREATE (c)-[:HANDLED_BY]->(adj)
                        
                        WITH c
                        MATCH (loc:Location {id: $location_id})
                        CREATE (c)-[:OCCURRED_AT]->(loc)
                    """,
                        claim_id=claim_id,
                        amount=claim_amount,
                        claim_date=claim_date,
                        incident_type=random.choice(["Rear-End Collision", "Side Impact", "Multi-Vehicle"]),
                        claimant_id=claimant_id,
                        claimant_name=claimant_name,
                        ssn=self.generate_ssn(),
                        phone_id=phone_id,
                        phone_number=phone_number,
                        address_id=address_id,
                        provider_id=cg_id,
                        adjuster_id=adjuster_id,
                        location_id=location_id
                    )
                
                # Distribute attorneys (40% have attorney, distributed across 12)
                if random.random() < 0.40:
                    available = [a for a in cg_attorneys if attorney_claims[a] < 4]
                    if available:
                        att_id = random.choice(available)
                        attorney_claims[att_id] += 1
                        session.run("""
                            MATCH (c:Claim {id: $claim_id})
                            MATCH (a:Attorney {id: $att_id})
                            CREATE (c)-[:REPRESENTED_BY]->(a)
                        """, claim_id=claim_id, att_id=att_id)
            
            self.stats['scenario_3b_claims'] = 32
            print(f"  ✓ Created 32 legitimate claims at City General")
            print(f"    - All unique phones")
            print(f"    - 2 married couples (4 people sharing 2 addresses - legitimate)")
            print(f"    - 12 different attorneys (no concentration)")

    # =========================================================================
    # SCENARIO 4: THE CASE WE THOUGHT WAS CLOSED
    # =========================================================================
    
    def create_scenario_4_closed_case(self):
        """
        Creates the network migration scenario.
        
        Structure:
        - Dr. Bernard's Auto Injury Center (CONFIRMED FRAUD, license revoked)
          - 15 claims (all is_fraud=true)
          - Closed 6 months ago
        - Attorney Michael Chen (represented 12 of 15 at Bernard's)
        - 34 NEW claimants with Chen (not in Bernard's case)
        - Rapid Recovery Med (28 of 34 treated here)
          - Opened 2 months after Bernard's shutdown
          - Owner: Dr. Patricia Simmons (former Bernard's employee)
        """
        print("\n" + "="*60)
        print("SCENARIO 4: The Case We Thought Was Closed")
        print("="*60)
        
        with self.driver.session() as session:
            # === CREATE DR. BERNARD'S (CONFIRMED FRAUD) ===
            bernard_id = "PROV_S4_BERNARD"
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: "Dr. Bernard's Auto Injury Center",
                    license: 'MED-S4-REVOKED',
                    opened_date: '2020-03-01',
                    closed_date: '2025-07-15',
                    status: 'License Revoked',
                    is_fraud: true,
                    fraud_type: 'Medical Mill - Confirmed',
                    scenario: 'scenario_4'
                })
            """, id=bernard_id)
            print("  ✓ Created Dr. Bernard's (CONFIRMED FRAUD - License Revoked)")
            
            # === CREATE ATTORNEY MICHAEL CHEN ===
            chen_id = "ATT_S4_CHEN"
            session.run("""
                CREATE (a:Attorney {
                    id: $id,
                    name: 'Michael Chen',
                    bar_number: 'BAR-321654',
                    scenario: 'scenario_4'
                })
            """, id=chen_id)
            print("  ✓ Created Attorney: Michael Chen")
            
            # === CREATE 15 CLAIMS AT BERNARD'S (all confirmed fraud) ===
            print("  Creating 15 confirmed fraud claims at Bernard's...")
            
            bernard_claimants = []
            chen_at_bernard = 0
            
            for i in range(15):
                claim_id = f"CLM_S4_BER_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                claimant_id = f"P_S4_BER_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                bernard_claimants.append(claimant_id)
                
                phone_id = f"PH_S4_{self.phone_counter:05d}"
                phone_number = self.generate_phone()
                self.phone_counter += 1
                
                address_id = f"ADDR_S4_{self.address_counter:05d}"
                city, state, zip_code = self.generate_city_state()
                self.address_counter += 1
                
                adjuster_id = random.choice(self.adjuster_pool)
                location_id = random.choice(self.background_locations)
                
                # Claims from 8-14 months ago (before shutdown)
                claim_date = self.generate_date(420, 180)
                claim_amount = round(random.uniform(18000, 40000), 2)
                
                session.run("""
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: 'Auto Claim - FRAUD CONFIRMED',
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: 'Staged Accident',
                        status: 'Denied',
                        is_fraud: true,
                        fraud_type: 'Medical Mill',
                        scenario: 'scenario_4'
                    })
                    
                    CREATE (p:Person:Claimant {
                        id: $claimant_id,
                        name: $claimant_name,
                        ssn: $ssn,
                        role: 'Claimant',
                        is_fraud: true,
                        scenario: 'scenario_4'
                    })
                    
                    CREATE (ph:Phone {id: $phone_id, number: $phone_number})
                    CREATE (addr:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential'
                    })
                    
                    CREATE (p)-[:HAS_PHONE]->(ph)
                    CREATE (p)-[:LIVES_AT]->(addr)
                    CREATE (c)-[:FILED_BY]->(p)
                    
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    amount=claim_amount,
                    claim_date=claim_date,
                    claimant_id=claimant_id,
                    claimant_name=claimant_name,
                    ssn=self.generate_ssn(),
                    phone_id=phone_id,
                    phone_number=phone_number,
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code,
                    provider_id=bernard_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
                
                # 12 of 15 represented by Chen
                if chen_at_bernard < 12:
                    session.run("""
                        MATCH (c:Claim {id: $claim_id})
                        MATCH (a:Attorney {id: $chen_id})
                        CREATE (c)-[:REPRESENTED_BY]->(a)
                    """, claim_id=claim_id, chen_id=chen_id)
                    chen_at_bernard += 1
            
            print(f"  ✓ Created 15 confirmed fraud claims at Bernard's (12 with Chen)")
            
            # === CREATE DR. PATRICIA SIMMONS (Former Bernard's employee, now owns Rapid Recovery) ===
            simmons_id = "P_S4_SIMMONS"
            session.run("""
                CREATE (p:Person:Employee {
                    id: $id,
                    name: 'Dr. Patricia Simmons',
                    role: 'Owner',
                    job_title: 'Medical Director / Owner',
                    scenario: 'scenario_4'
                })
                WITH p
                MATCH (bernard:Provider {id: 'PROV_S4_BERNARD'})
                CREATE (p)-[:FORMER_EMPLOYEE_OF]->(bernard)
            """, id=simmons_id)
            print("  ✓ Created Dr. Patricia Simmons (former Bernard's employee)")
            
            # === CREATE RAPID RECOVERY MED (New fraud outlet) ===
            rapid_id = "PROV_S4_RAPID"
            session.run("""
                CREATE (p:Provider {
                    id: $id,
                    name: 'Rapid Recovery Med',
                    license: 'MED-S4-RAPID001',
                    opened_date: '2025-09-15',
                    status: 'Active',
                    scenario: 'scenario_4'
                })
                WITH p
                MATCH (simmons:Person {id: 'P_S4_SIMMONS'})
                CREATE (p)-[:OWNED_BY]->(simmons)
                CREATE (p)-[:EMPLOYS]->(simmons)
            """, id=rapid_id)
            print("  ✓ Created Rapid Recovery Med (opened 2 months after Bernard's shutdown)")
            
            # === CREATE 34 NEW CLAIMS WITH CHEN ===
            print("  Creating 34 new claims for Chen's pipeline...")
            
            chen_at_rapid = 0
            chen_other = 0
            
            for i in range(34):
                claim_id = f"CLM_S4_NEW_{self.claim_counter:05d}"
                self.claim_counter += 1
                
                claimant_id = f"P_S4_NEW_{self.person_counter:05d}"
                claimant_name = self.generate_name()
                self.person_counter += 1
                
                phone_id = f"PH_S4_{self.phone_counter:05d}"
                phone_number = self.generate_phone()
                self.phone_counter += 1
                
                address_id = f"ADDR_S4_{self.address_counter:05d}"
                city, state, zip_code = self.generate_city_state()
                self.address_counter += 1
                
                adjuster_id = random.choice(self.adjuster_pool)
                location_id = random.choice(self.background_locations)
                
                # 28 go to Rapid Recovery, 6 to background providers
                if chen_at_rapid < 28:
                    provider_id = rapid_id
                    chen_at_rapid += 1
                else:
                    provider_id = random.choice(self.background_providers)
                    chen_other += 1
                
                # Recent claims (last 4 months)
                claim_date = self.generate_date(120, 0)
                claim_amount = round(random.uniform(15000, 38000), 2)
                
                session.run("""
                    CREATE (c:Claim {
                        id: $claim_id,
                        name: 'Auto Claim - Soft Tissue',
                        claim_amount: $amount,
                        claim_date: $claim_date,
                        claim_type: 'Auto',
                        incident_type: 'Rear-End Collision',
                        status: 'Open',
                        is_fraud: false,
                        scenario: 'scenario_4'
                    })
                    
                    CREATE (p:Person:Claimant {
                        id: $claimant_id,
                        name: $claimant_name,
                        ssn: $ssn,
                        role: 'Claimant',
                        scenario: 'scenario_4'
                    })
                    
                    CREATE (ph:Phone {id: $phone_id, number: $phone_number})
                    CREATE (addr:Address {
                        id: $address_id,
                        street: $street,
                        city: $city,
                        state: $state,
                        zip: $zip,
                        type: 'Residential'
                    })
                    
                    CREATE (p)-[:HAS_PHONE]->(ph)
                    CREATE (p)-[:LIVES_AT]->(addr)
                    CREATE (c)-[:FILED_BY]->(p)
                    
                    WITH c
                    MATCH (prov:Provider {id: $provider_id})
                    CREATE (c)-[:TREATED_AT]->(prov)
                    
                    WITH c
                    MATCH (att:Attorney {id: $chen_id})
                    CREATE (c)-[:REPRESENTED_BY]->(att)
                    
                    WITH c
                    MATCH (adj:Person:Adjuster {id: $adjuster_id})
                    CREATE (c)-[:HANDLED_BY]->(adj)
                    
                    WITH c
                    MATCH (loc:Location {id: $location_id})
                    CREATE (c)-[:OCCURRED_AT]->(loc)
                """,
                    claim_id=claim_id,
                    amount=claim_amount,
                    claim_date=claim_date,
                    claimant_id=claimant_id,
                    claimant_name=claimant_name,
                    ssn=self.generate_ssn(),
                    phone_id=phone_id,
                    phone_number=phone_number,
                    address_id=address_id,
                    street=self.generate_street_address(),
                    city=city,
                    state=state,
                    zip=zip_code,
                    provider_id=provider_id,
                    chen_id=chen_id,
                    adjuster_id=adjuster_id,
                    location_id=location_id
                )
            
            self.stats['scenario_4_claims'] = 15 + 34
            print(f"  ✓ Created 34 new claims for Chen (28 at Rapid Recovery, 6 at other providers)")

    # =========================================================================
    # MASTER GENERATION
    # =========================================================================
    
    def generate_all_demo_data(self):
        """
        One-click generation of complete demo dataset.
        
        Order:
        1. Clear database
        2. Create indexes
        3. Create shared pools
        4. Create background data
        5. Create each scenario
        6. Print summary
        """
        print("\n" + "="*70)
        print("  FRAUD RING DETECTION DEMO - DATA GENERATION")
        print("="*70)
        
        # Setup
        self.clear_database()
        self.create_indexes()
        
        # Pools
        self.create_adjuster_pool(count=15)
        self.create_background_providers(count=15)
        self.create_background_attorneys(count=12)
        self.create_background_bodyshops(count=8)
        self.create_background_locations(count=20)
        
        # Background
        self.create_legitimate_claims(count=150)
        
        # Scenarios
        self.create_scenario_1_two_hour_attorney()
        self.create_scenario_2_identity_web()
        self.create_scenario_3a_sunrise_fraud()
        self.create_scenario_3b_city_general_legitimate()
        self.create_scenario_4_closed_case()
        
        # Summary
        self._print_summary()
        
        return self.stats

    def _print_summary(self):
        """Print generation summary."""
        print("\n" + "="*70)
        print("  GENERATION COMPLETE")
        print("="*70)
        
        total_claims = sum(self.stats.values())
        
        print(f"\n📊 Summary:")
        print(f"   Background Claims:        {self.stats['background_claims']}")
        print(f"   Scenario 1 (Webb):        {self.stats['scenario_1_claims']}")
        print(f"   Scenario 2 (Identity):    {self.stats['scenario_2_claims']}")
        print(f"   Scenario 3a (Sunrise):    {self.stats['scenario_3a_claims']}")
        print(f"   Scenario 3b (City Gen):   {self.stats['scenario_3b_claims']}")
        print(f"   Scenario 4 (Bernard's):   {self.stats['scenario_4_claims']}")
        print(f"   ─────────────────────────────────")
        print(f"   TOTAL CLAIMS:             {total_claims}")
        
        print(f"\n🎯 Entry Points for Demo:")
        print(f"   1. Attorney 'J. Marcus Webb' - 47 clients")
        print(f"   2. Phone '555-847-2931' - 5 users")
        print(f"   3. Provider 'Sunrise Wellness Clinic' - 28 claims, 38% above avg")
        print(f"   3. Provider 'City General Emergency Room' - 32 claims (LEGITIMATE)")
        print(f"   4. Provider 'Dr. Bernard's Auto Injury Center' - CONFIRMED FRAUD")

    def verify_scenario_integrity(self):
        """Verify each scenario has expected data."""
        print("\n" + "="*70)
        print("  VERIFYING SCENARIO INTEGRITY")
        print("="*70)
        
        issues = []
        
        with self.driver.session() as session:
            # Scenario 1: Webb should have 47 clients
            result = session.run("""
                MATCH (a:Attorney {name: 'J. Marcus Webb'})<-[:REPRESENTED_BY]-(c:Claim)
                RETURN count(c) as count
            """).single()
            webb_count = result['count'] if result else 0
            if webb_count != 47:
                issues.append(f"Scenario 1: Webb has {webb_count} clients (expected 47)")
            else:
                print(f"  ✓ Scenario 1: Webb has {webb_count} clients")
            
            # Scenario 2: Phone should connect to 5 people
            result = session.run("""
                MATCH (ph:Phone {number: '555-847-2931'})<-[:HAS_PHONE]-(p:Person)
                RETURN count(p) as count
            """).single()
            phone_count = result['count'] if result else 0
            if phone_count != 5:
                issues.append(f"Scenario 2: Phone has {phone_count} users (expected 5)")
            else:
                print(f"  ✓ Scenario 2: Phone 555-847-2931 has {phone_count} users")
            
            # Scenario 3a: Sunrise should have 28 claims
            result = session.run("""
                MATCH (p:Provider {name: 'Sunrise Wellness Clinic'})<-[:TREATED_AT]-(c:Claim)
                RETURN count(c) as count
            """).single()
            sunrise_count = result['count'] if result else 0
            if sunrise_count != 28:
                issues.append(f"Scenario 3a: Sunrise has {sunrise_count} claims (expected 28)")
            else:
                print(f"  ✓ Scenario 3a: Sunrise has {sunrise_count} claims")
            
            # Scenario 3b: City General should have 32 claims
            result = session.run("""
                MATCH (p:Provider {name: 'City General Emergency Room'})<-[:TREATED_AT]-(c:Claim)
                RETURN count(c) as count
            """).single()
            cg_count = result['count'] if result else 0
            if cg_count != 32:
                issues.append(f"Scenario 3b: City General has {cg_count} claims (expected 32)")
            else:
                print(f"  ✓ Scenario 3b: City General has {cg_count} claims")
            
            # Scenario 4: Bernard's should be confirmed fraud
            result = session.run("""
                MATCH (p:Provider {name: "Dr. Bernard's Auto Injury Center"})
                RETURN p.is_fraud as is_fraud
            """).single()
            is_fraud = result['is_fraud'] if result else False
            if not is_fraud:
                issues.append("Scenario 4: Bernard's is not marked as fraud")
            else:
                print(f"  ✓ Scenario 4: Bernard's is marked CONFIRMED FRAUD")
            
            # Scenario 4: Chen should have 34 active (non-fraud) clients
            result = session.run("""
                MATCH (a:Attorney {name: 'Michael Chen'})<-[:REPRESENTED_BY]-(c:Claim)
                WHERE c.is_fraud = false
                RETURN count(c) as count
            """).single()
            chen_active = result['count'] if result else 0
            if chen_active != 34:
                issues.append(f"Scenario 4: Chen has {chen_active} active clients (expected 34)")
            else:
                print(f"  ✓ Scenario 4: Chen has {chen_active} active clients")
        
        if issues:
            print(f"\n⚠️ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print(f"\n✅ All scenarios verified successfully!")
            return True


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    print("This module is designed to run within Streamlit.")
    print("Run: streamlit run app.py")
    print("\nTo test directly, ensure secrets.toml is configured and uncomment below:")
    # 
    # generator = ScenarioDataGenerator()
    # generator.generate_all_demo_data()
    # generator.verify_scenario_integrity()
    # generator.close()