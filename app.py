"""
Insurance Fraud Ring Detection
Graph-Powered Investigation Platform for SIU Teams

A demonstration of how graph database technology transforms fraud investigation
by revealing hidden network connections that traditional methods miss.
"""

import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from neo4j import GraphDatabase
import time
from datetime import datetime

# Import data generator
from scenario_data_generator import ScenarioDataGenerator

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Fraud Ring Detection | SIU Investigation Platform",
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Improve metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Better expander styling */
    .streamlit-expanderHeader {
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# PERFORMANCE TIMER
# =============================================================================

class PerformanceTimer:
    """Track query performance metrics."""
    
    def __init__(self):
        self.start_time = None
        self.duration_ms = 0
        self.entity_count = 0
        self.relationship_count = 0
        self.exposure = 0.0
    
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        if self.start_time:
            self.duration_ms = round((time.time() - self.start_time) * 1000, 2)
        return self.duration_ms
    
    def set_counts(self, entities, relationships, exposure=0.0):
        self.entity_count = entities
        self.relationship_count = relationships
        self.exposure = exposure

# =============================================================================
# NEO4J CONNECTION
# =============================================================================

@st.cache_resource
def get_neo4j_driver():
    """Establish cached connection to Neo4j database."""
    try:
        uri = st.secrets["neo4j"]["uri"]
        user = st.secrets["neo4j"]["user"]
        password = st.secrets["neo4j"]["password"]
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        return driver
    
    except KeyError:
        st.error("**Configuration Required**: Neo4j credentials not found.")
        st.info("Please configure `.streamlit/secrets.toml` with your Neo4j connection details:")
        st.code("""[neo4j]
uri = "neo4j+s://your-instance.databases.neo4j.io"
user = "neo4j"
password = "your-password"
        """)
        return None
    
    except Exception as e:
        st.error(f"**Connection Failed**: Unable to connect to Neo4j database.")
        st.caption(f"Error details: {e}")
        return None

driver = get_neo4j_driver()
if driver is None:
    st.stop()

# =============================================================================
# VISUAL DESIGN SYSTEM
# =============================================================================

# Entity type colors - professional palette
COLOR_MAP = {
    # Primary entities
    "Claim": "#4A90A4",          # Steel blue
    "Claimant": "#5DADE2",       # Sky blue
    "Witness": "#85C1E9",        # Light blue
    "Adjuster": "#58D68D",       # Green
    "Employee": "#48C9B0",       # Teal
    "Provider": "#AF7AC5",       # Purple
    "Attorney": "#F5B041",       # Amber
    "BodyShop": "#EB984E",       # Orange
    
    # Connector entities
    "Address": "#45B7A0",        # Seafoam
    "Phone": "#5499C7",          # Medium blue
    "Location": "#9B7ED9",       # Lavender
    "Vehicle": "#99A3A4",        # Gray
    "Person": "#AAB7B8",         # Light gray
    
    # Status indicators
    "confirmed_fraud": "#E74C3C", # Red
    "suspicious": "#F39C12",      # Warning orange
    "legitimate": "#27AE60",      # Green
}

# Relationship type labels for display
RELATIONSHIP_LABELS = {
    "FILED_BY": "filed by",
    "TREATED_AT": "treated at",
    "REPRESENTED_BY": "represented by",
    "HANDLED_BY": "handled by",
    "WITNESSED_BY": "witnessed by",
    "REPAIRED_AT": "repaired at",
    "OCCURRED_AT": "occurred at",
    "INVOLVES_VEHICLE": "involves",
    "LIVES_AT": "lives at",
    "HAS_PHONE": "uses phone",
    "LOCATED_AT": "located at",
    "EMPLOYS": "employs",
    "REGISTERED_AGENT": "registered agent",
    "OWNED_BY": "owned by",
    "MARRIED_TO": "married to",
    "FORMER_EMPLOYEE_OF": "formerly at",
}

# =============================================================================
# SCENARIO DEFINITIONS
# =============================================================================

SCENARIOS = {
    1: {
        "title": "Captive Medical Mill",
        "subtitle": "Uncovering a Captive Medical Mill Operation",
        "icon": "⚖️",
        "starting_entity": ("Attorney", "ATT_S1_WEBB", "J. Marcus Webb"),
        "trigger": """
**Initial Flag:**

An adjuster notes an unusual detail: *"Claimant secured legal representation within 2 hours of the reported accident."*

While not unprecedented, this rapid attorney engagement warrants a closer look at the broader pattern.

**Investigation Question:** Is this attorney operating a solicitation network, or simply employing aggressive marketing?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "Starting Point: Attorney Profile",
                "narrative": "Beginning investigation with **Attorney J. Marcus Webb**, flagged for unusually rapid client acquisition patterns.",
                "traditional": "Requesting attorney claim history from IT systems typically requires 2-3 business days.",
                "discovery": None,
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S1_WEBB'})
                    RETURN a
                """
            },
            {
                "depth": 1,
                "title": "Client Portfolio Analysis",
                "narrative": "Expanding to examine all claimants represented by this attorney...",
                "traditional": "Manual file review: approximately 2-3 hours per claimant. For a large portfolio, this represents **140+ hours of investigation time**.",
                "discovery": "**47 claimants retained within 6 months** — representing 8x the typical attorney volume in this market.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S1_WEBB'})
                    OPTIONAL MATCH (a)<-[:REPRESENTED_BY]-(c:Claim)-[:FILED_BY]->(p:Person)
                    RETURN a, c, p
                """
            },
            {
                "depth": 2,
                "title": "Medical Provider Concentration",
                "narrative": "Analyzing treatment facility distribution across the client base...",
                "traditional": "Cross-referencing treatment records across 47 separate claim files would require an additional **20+ hours** of manual work.",
                "discovery": "**41 of 47 claimants (87%)** received treatment at only **two facilities**: Wellness Partners Medical and Peak Recovery Clinic.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S1_WEBB'})
                    OPTIONAL MATCH (a)<-[:REPRESENTED_BY]-(c:Claim)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(claimant:Person)
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
                    RETURN a, c, claimant, prov
                """
            },
            {
                "depth": 3,
                "title": "Business Location Analysis",
                "narrative": "Examining the physical business addresses of these concentrated providers...",
                "traditional": "Secretary of State corporate lookups for each facility — and would an investigator even think to check this?",
                "discovery": "**Both clinics operate from the same address**: 1847 Commerce Boulevard, Suite 200.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S1_WEBB'})
                    OPTIONAL MATCH (a)<-[:REPRESENTED_BY]-(c:Claim)
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
                    OPTIONAL MATCH (prov)-[:LOCATED_AT]->(addr:Address)
                    RETURN a, c, prov, addr
                """
            },
            {
                "depth": 4,
                "title": "Employee Network Mapping",
                "narrative": "Cross-referencing personnel records from **state licensing databases** and **corporate filings** with residential address data...",
                "traditional": "Employee data exists in external public records (licensing boards, corporate filings). Cross-referencing these with residential addresses requires accessing **multiple disconnected systems** — a step rarely taken without prior suspicion.",
                "discovery": "The billing manager at Wellness Partners **shares a residential address** with the patient coordinator at Peak Recovery — indicating a personal relationship between key staff at both clinics.",
                "query": """
                    MATCH (prov:Provider)-[:LOCATED_AT]->(bizAddr:Address {id: 'ADDR_S1_BIZ'})
                    OPTIONAL MATCH (prov)-[:EMPLOYS]->(emp:Person)
                    OPTIONAL MATCH (emp)-[:LIVES_AT]->(homeAddr:Address)
                    RETURN prov, bizAddr, emp, homeAddr
                """
            },
            {
                "depth": 5,
                "title": "Cross-Role Identity Detection",
                "narrative": "Checking whether any employees appear in other capacities within these claims...",
                "traditional": "Systematically checking if clinic staff appear as witnesses? **Virtually impossible without graph technology.**",
                "discovery": "**Maria Santos** (Peak Recovery employee) is listed as **witness on 8 claims** treated at Wellness Partners — a clear cross-role fraud indicator.",
                "query": """
                    MATCH (maria:Person {id: 'P_S1_MARIA'})
                    OPTIONAL MATCH (maria)<-[:WITNESSED_BY]-(c:Claim)
                    OPTIONAL MATCH (prov:Provider)-[:EMPLOYS]->(maria)
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(treatProv:Provider)
                    RETURN maria, c, prov, treatProv
                """
            },
            {
                "depth": 6,
                "title": "Ownership Structure Revealed",
                "narrative": "Cross-referencing **Secretary of State corporate filings** (registered agent records) with **public marriage records** and attorney bar registration...",
                "traditional": "Corporate registry data is public but rarely cross-referenced with claims. Connecting a provider's registered agent to an attorney's spouse requires querying **three separate public record systems** — a path no investigator would pursue without graph-enabled discovery.",
                "discovery": "**Linda Webb** (the attorney's spouse per marriage records) serves as **registered agent for both clinics** per corporate filings. This confirms a fully captive medical mill operation with hidden family ownership.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S1_WEBB'})
                    OPTIONAL MATCH (a)-[:MARRIED_TO]->(spouse:Person)
                    OPTIONAL MATCH (prov:Provider)-[:REGISTERED_AGENT]->(spouse)
                    OPTIONAL MATCH (prov)-[:LOCATED_AT]->(addr:Address)
                    RETURN a, spouse, prov, addr
                """
            }
        ],
        "conclusion": {
            "exposure": "$1.2M across 47 claims",
            "traditional_time": "2-3 weeks minimum",
            "graph_time": "Under 5 minutes",
            "key_finding": "Hidden spousal ownership of medical providers — a connection that exists entirely outside claims data systems.",
            "action_items": [
                "Refer complete network to NICB for criminal investigation",
                "Place administrative hold on all 47 pending claims", 
                "Issue subpoenas for clinic ownership and financial records",
                "Expand search for similar patterns among associated attorneys"
            ]
        }
    },
    
    2: {
        "title": "Identity Web",
        "subtitle": "Detecting an Identity Network Through Shared Contact Information",
        "icon": "📱",
        "starting_entity": ("Phone", "PH_S2_MAIN", "555-847-2931"),
        "trigger": """
**Initial Flag:**

ISO database returns a match: a phone number on a recent claim appears on an unrelated claim from 4 months prior. Different claimant names.

The adjuster's initial assessment: *"Likely a data entry error or shared family contact."*

**Investigation Question:** Is this a clerical anomaly, or evidence of something more significant?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "Starting Point: Phone Number Alert",
                "narrative": "ISO system flagged phone number **555-847-2931** appearing on claims with different claimant names.",
                "traditional": "ISO provides a match on 2 claims. Investigation typically ends here unless obvious fraud indicators are present.",
                "discovery": None,
                "query": """
                    MATCH (ph:Phone {number: '555-847-2931'})
                    RETURN ph
                """
            },
            {
                "depth": 1,
                "title": "Phone Number Usage Analysis",
                "narrative": "Examining all individuals associated with this phone number across our data...",
                "traditional": "Finding additional phone matches would require separate database queries with no guarantee of name consistency.",
                "discovery": "**5 distinct individuals** have used this phone number — ISO only surfaced 2 of them.",
                "query": """
                    MATCH (ph:Phone {number: '555-847-2931'})
                    OPTIONAL MATCH (ph)<-[:HAS_PHONE]-(p:Person)
                    RETURN ph, p
                """
            },
            {
                "depth": 2,
                "title": "Residential Address Mapping",
                "narrative": "Analyzing residential addresses for all five individuals connected to this phone...",
                "traditional": "Running separate address queries for each person across different systems. Each query represents a different access request.",
                "discovery": "**3 of 5 individuals** share the same residential address: 847 Oak Street, Apartment 4B. The remaining 2 (Marcus and Tanya Williams) live at separate addresses.",
                "query": """
                    MATCH (ph:Phone {number: '555-847-2931'})<-[:HAS_PHONE]-(p:Person)
                    OPTIONAL MATCH (p)-[:LIVES_AT]->(addr:Address)
                    RETURN ph, p, addr
                """
            },
            {
                "depth": 3,
                "title": "Address-Based Network Expansion",
                "narrative": "Expanding the search to identify **all individuals** at the shared address, including those using different contact information...",
                "traditional": "Cross-referencing address databases with claimant records across multiple systems would require **hours of manual work** and would miss connections through alternate phone numbers.",
                "discovery": "**2 additional individuals** (Lisa and Tyrell Morgan) reside at 847 Oak Street using a **different phone number** (555-847-2932). **Total network: 7 people across 2 phone numbers.**",
                "query": """
                    MATCH (ph1:Phone {number: '555-847-2931'})<-[:HAS_PHONE]-(p1:Person)
                    OPTIONAL MATCH (p1)-[:LIVES_AT]->(addr1:Address)
                    WITH collect(DISTINCT p1) as phone1_people, collect(DISTINCT addr1) as addrs
                    MATCH (addr:Address {id: 'ADDR_S2_OAK'})<-[:LIVES_AT]-(p2:Person)
                    OPTIONAL MATCH (p2)-[:HAS_PHONE]->(ph2:Phone)
                    WITH phone1_people, p2, ph2, addr
                    UNWIND phone1_people as p1
                    OPTIONAL MATCH (p1)-[:LIVES_AT]->(addr1:Address)
                    OPTIONAL MATCH (p1)-[:HAS_PHONE]->(ph1:Phone)
                    RETURN p1, addr1, ph1, p2, ph2, addr
                """
            },
            {
                "depth": 4,
                "title": "Complete Claims Analysis",
                "narrative": "Mapping all claims filed by individuals in this identity network...",
                "traditional": "Manually cross-referencing 7 individuals across all claims databases. **This level of comprehensive investigation would never occur** based on a single ISO phone match.",
                "discovery": "**7 claims totaling $215,000** — all filed within a **45-day window**. Every individual in the network has filed a claim. This is coordinated fraud activity.",
                "query": """
                    MATCH (ph:Phone)<-[:HAS_PHONE]-(p:Person)-[:LIVES_AT]->(addr:Address)
                    WHERE ph.number IN ['555-847-2931', '555-847-2932']
                    OPTIONAL MATCH (c:Claim)-[:FILED_BY]->(p)
                    RETURN ph, p, addr, c
                    UNION
                    MATCH (ph:Phone {number: '555-847-2931'})<-[:HAS_PHONE]-(p:Person)
                    WHERE NOT (p)-[:LIVES_AT]->(:Address {id: 'ADDR_S2_OAK'})
                    OPTIONAL MATCH (p)-[:LIVES_AT]->(addr:Address)
                    OPTIONAL MATCH (c:Claim)-[:FILED_BY]->(p)
                    RETURN ph, p, addr, c
                """
            }
        ],
        "conclusion": {
            "exposure": "$215,000 across 7 claims",
            "traditional_time": "ISO shows 2 claims; remaining 5 would be missed entirely",
            "graph_time": "90 seconds to full network mapping",
            "key_finding": "Network expansion from 2 ISO hits to 7 connected individuals filing 7 claims. Graph reveals connections through **both shared phones and shared addresses** — patterns impossible to discover through linear queries.",
            "action_items": [
                "Deny all 7 claims pending fraud investigation",
                "Refer to NICB for identity fraud prosecution",
                "Flag both phone numbers (555-847-2931, 555-847-2932) for future claim monitoring",
                "Investigate property records for 847 Oak Street, Apt 4B"
            ]
        }
    },
    
    3: {
        "title": "Provider Distinction",
        "subtitle": "Distinguishing Fraud Networks from High-Volume Legitimate Providers",
        "icon": "📊",
        "starting_entity": ("Provider", "PROV_S3_SUNRISE", "Sunrise Wellness Clinic"),
        "trigger": """
**Initial Flag:**

Quarterly provider audit identifies two facilities with elevated billing patterns:

| Provider | Claims | Billing vs. Peer Average |
|----------|--------|--------------------------|
| Sunrise Wellness Clinic | 28 | +38% |
| City General ER | 32 | +42% |

Both flagged. Limited SIU resources available for investigation.

**Investigation Question:** Which provider warrants full investigation, and which may be a false positive?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "Starting Point: Provider Audit Flag",
                "narrative": "Beginning with **Sunrise Wellness Clinic**, flagged for billing 38% above peer average.",
                "traditional": "Billing analysis provides a single metric without network context. Prioritization is often arbitrary.",
                "discovery": None,
                "query": """
                    MATCH (p:Provider {id: 'PROV_S3_SUNRISE'})
                    RETURN p
                """
            },
            {
                "depth": 1,
                "title": "Patient Network Analysis",
                "narrative": "Examining the patient population treated at Sunrise Wellness...",
                "traditional": "Pulling 28 individual claim files for manual review: approximately **14 hours** of investigation time.",
                "discovery": "28 claimants treated at this facility over a 6-month period.",
                "query": """
                    MATCH (prov:Provider {id: 'PROV_S3_SUNRISE'})
                    OPTIONAL MATCH (c:Claim)-[:TREATED_AT]->(prov)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN prov, c, p
                """
            },
            {
                "depth": 2,
                "title": "Legal Representation Analysis",
                "narrative": "Analyzing attorney distribution across Sunrise patients...",
                "traditional": "Manually tallying attorney representation from individual claim files.",
                "discovery": "**23 of 28 patients (82%)** are represented by a single attorney: Roberto Vega. This concentration is highly anomalous.",
                "query": """
                    MATCH (prov:Provider {id: 'PROV_S3_SUNRISE'})<-[:TREATED_AT]-(c:Claim)
                    OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN prov, c, a, p
                """
            },
            {
                "depth": 3,
                "title": "Attorney Referral Pattern",
                "narrative": "Examining where Attorney Vega refers his other clients for treatment...",
                "traditional": "Querying all of Vega's cases and cross-referencing provider selections would require **another full day** of work.",
                "discovery": "Vega refers clients to **only 2 providers**: Sunrise Wellness and Peak Recovery Center. This is an **exclusive referral pipeline**.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S3_VEGA'})<-[:REPRESENTED_BY]-(c:Claim)
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN a, c, prov, p
                """
            },
            {
                "depth": 4,
                "title": "Cross-Provider Connection Detection",
                "narrative": "Searching for **shared identifiers** and **common participants** between patients at both clinics...",
                "traditional": "Comparing patient contact information and witness lists between providers? **No investigator would systematically perform this cross-provider analysis.**",
                "discovery": "**7 claimants share a phone number** (555-991-8847) across both clinics. Additionally, **Carmen Reyes** appears as witness on claims at **both facilities** — a strong indicator of a professional witness.",
                "query": """
                    MATCH (ph:Phone {id: 'PH_S3_SHARED'})<-[:HAS_PHONE]-(p:Person)
                    OPTIONAL MATCH (c:Claim)-[:FILED_BY]->(p)
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
                    WITH ph, p, c, prov
                    OPTIONAL MATCH (c)-[:WITNESSED_BY]->(w:Person)
                    RETURN ph, p, c, prov, w
                    UNION
                    MATCH (carmen:Person {id: 'P_S3_CARMEN'})<-[:WITNESSED_BY]-(c:Claim)
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(claimant:Person)
                    RETURN carmen as w, claimant as p, c, prov, null as ph
                """
            },
            {
                "depth": 5,
                "title": "Comparison: City General ER",
                "narrative": "Now analyzing the second flagged provider to determine if it warrants investigation or represents a **false positive**...",
                "traditional": "Same manual review process repeated for the second provider. Most audits would stop after investigating the first facility due to resource constraints.",
                "discovery": "City General ER: **32 claims, 12 different attorneys, zero shared phones or addresses**. The facility's location at the **I-85/Highway 20 junction** (a major accident corridor) explains the elevated volume. **This is a legitimate high-volume provider — no investigation warranted.**",
                "query": """
                    MATCH (prov:Provider {id: 'PROV_S3_CITYGEN'})<-[:TREATED_AT]-(c:Claim)
                    OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    OPTIONAL MATCH (p)-[:HAS_PHONE]->(ph:Phone)
                    OPTIONAL MATCH (c)-[:OCCURRED_AT]->(loc:Location)
                    RETURN prov, c, a, p, ph, loc
                """
            }
        ],
        "conclusion": {
            "exposure": "$400K+ exposure at Sunrise; City General cleared",
            "traditional_time": "Both providers flagged with no clear prioritization criteria",
            "graph_time": "Sunrise confirmed: 2 minutes. City General cleared: 30 seconds.",
            "key_finding": "Graph analysis not only identifies fraud networks — it **rapidly clears legitimate entities**, preventing wasted investigation resources.",
            "action_items": [
                "Initiate full investigation of Sunrise Wellness and Peak Recovery",
                "Close audit flag on City General ER — no further action required",
                "Investigate Attorney Roberto Vega's complete client portfolio",
                "Monitor flagged phone number for future claim activity"
            ]
        }
    },
    
    4: {
        "title": "Network Migration",
        "subtitle": "Detecting Network Migration After Successful Prosecution",
        "icon": "🔄",
        "starting_entity": ("Provider", "PROV_S4_BERNARD", "Dr. Bernard's Auto Injury Center"),
        "trigger": """
**Background:**

Six months ago, SIU successfully prosecuted a staged accident ring involving **Dr. Bernard's Auto Injury Center**:

| Outcome | Result |
|---------|--------|
| Claims Denied | $62,000 |
| Provider Status | License Revoked |
| Case Status | **Closed** ✓ |

**Investigation Question:** Did we dismantle the entire operation, or merely one component?
        """,
        "hops": [
            {
                "depth": 0,
                "title": "Starting Point: Confirmed Fraud Case",
                "narrative": "Reviewing **Dr. Bernard's Auto Injury Center** — confirmed fraud, license revoked, case closed.",
                "traditional": "Case closed. File archived. Investigation resources redirected to new matters.",
                "discovery": None,
                "query": """
                    MATCH (p:Provider {id: 'PROV_S4_BERNARD'})
                    RETURN p
                """
            },
            {
                "depth": 1,
                "title": "Original Case Review",
                "narrative": "The 15 claims from the prosecuted case...",
                "traditional": "These claims are documented in the closed case file. Known fraudulent activity.",
                "discovery": "15 confirmed fraudulent claims. All denied. Case successfully prosecuted. ✓",
                "query": """
                    MATCH (prov:Provider {id: 'PROV_S4_BERNARD'})
                    OPTIONAL MATCH (c:Claim)-[:TREATED_AT]->(prov)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN prov, c, p
                """
            },
            {
                "depth": 2,
                "title": "Legal Representation Analysis",
                "narrative": "Examining the complete legal representation picture for all claimants in the Bernard's case...",
                "traditional": "Case file notation: 'Multiple claimants used same attorney.' No systematic analysis of attorney distribution or follow-up investigation conducted.",
                "discovery": "**12 of 15 claimants (80%)** were represented by **Attorney Michael Chen**. The remaining 3 used different attorneys. Chen was **never sanctioned** despite his clients' confirmed fraud and **remains actively practicing**.",
                "query": """
                    MATCH (prov:Provider {id: 'PROV_S4_BERNARD'})<-[:TREATED_AT]-(c:Claim)
                    OPTIONAL MATCH (c)-[:REPRESENTED_BY]->(a:Attorney)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN prov, c, a, p
                """
            },
            {
                "depth": 3,
                "title": "Attorney's Current Activity",
                "narrative": "Investigating Attorney Chen's activities since the case closure...",
                "traditional": "Checking whether the attorney faced sanctions. He did not. **Case remains closed.**",
                "discovery": "Chen has acquired **34 new clients** since Dr. Bernard's was shut down. His practice continues unimpeded.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S4_CHEN'})<-[:REPRESENTED_BY]-(c:Claim)
                    WHERE c.is_fraud = false
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN a, c, p
                """
            },
            {
                "depth": 4,
                "title": "New Treatment Facility Pattern",
                "narrative": "Analyzing where Chen's new clients are receiving treatment...",
                "traditional": "Pulling 34 individual claim files to check treatment providers. **Resource-prohibitive for a 'closed' case.**",
                "discovery": "**28 of 34 clients (82%)** are treated at **Rapid Recovery Med** — a facility that opened 2 months after Dr. Bernard's license was revoked.",
                "query": """
                    MATCH (a:Attorney {id: 'ATT_S4_CHEN'})<-[:REPRESENTED_BY]-(c:Claim)
                    WHERE c.is_fraud = false
                    OPTIONAL MATCH (c)-[:TREATED_AT]->(prov:Provider)
                    OPTIONAL MATCH (c)-[:FILED_BY]->(p:Person)
                    RETURN a, c, prov, p
                """
            },
            {
                "depth": 5,
                "title": "Ownership Investigation",
                "narrative": "Examining corporate records for Rapid Recovery Med...",
                "traditional": "Corporate registry research on a new provider connected to a closed case? **This investigation would never be initiated.**",
                "discovery": "Rapid Recovery is owned by **Dr. Patricia Simmons** — a **former employee of Dr. Bernard's**. The fraud network migrated, not ended.",
                "query": """
                    MATCH (rapid:Provider {id: 'PROV_S4_RAPID'})
                    OPTIONAL MATCH (rapid)-[:OWNED_BY]->(owner:Person)
                    OPTIONAL MATCH (owner)-[:FORMER_EMPLOYEE_OF]->(bernard:Provider)
                    OPTIONAL MATCH (rapid)-[:EMPLOYS]->(emp:Person)
                    RETURN rapid, owner, bernard, emp
                """
            }
        ],
        "conclusion": {
            "exposure": "Original case: $62K saved. Active network exposure: $280K+",
            "traditional_time": "Case closed. Network continues operations undetected.",
            "graph_time": "Network migration detected in under 2 minutes",
            "key_finding": "Fraud networks adapt and migrate. Graph technology reveals **persistent connection points** (Chen) that link old and new operations.",
            "action_items": [
                "Open immediate investigation on Rapid Recovery Med",
                "Issue subpoenas for Attorney Michael Chen's complete case files",
                "Flag all 34 active claimants for expedited review",
                "Conduct background investigation on Dr. Patricia Simmons",
                "Update case status to 'Network Active — Ongoing Investigation'"
            ]
        }
    }
}

# =============================================================================
# GRAPH VISUALIZATION
# =============================================================================

def get_node_label(labels):
    """Determine most specific label for display."""
    priority = ["Claimant", "Witness", "Adjuster", "Employee", "Provider", 
                "Attorney", "BodyShop", "Address", "Phone", "Location", "Claim", "Person"]
    for p in priority:
        if p in labels:
            return p
    return labels[0] if labels else "Unknown"


def format_currency(amount):
    """Format number as currency."""
    if amount:
        return f"${amount:,.2f}"
    return "N/A"


def create_graph_visualization(records, root_id=None, entity_filters=None):
    """
    Create rich graph visualization with enhanced tooltips and edge styling.
    
    Args:
        records: Neo4j query results
        root_id: ID of the starting/root entity
        entity_filters: Set of entity types to include (None = all)
    """
    nodes = {}
    edges = []
    node_id_map = {}  # Map element_id to our custom id
    
    for record in records:
        for key, value in record.items():
            if value is None:
                continue
            
            # Handle nodes
            if hasattr(value, 'labels'):
                element_id = value.element_id
                if element_id in nodes:
                    continue
                
                labels = list(value.labels)
                props = dict(value)
                
                label = get_node_label(labels)
                
                # Apply entity filter if specified
                if entity_filters and label not in entity_filters:
                    continue
                
                node_id = props.get('id', str(element_id))
                node_id_map[element_id] = node_id
                
                name = props.get('name', props.get('number', props.get('street', node_id)))
                
                # Determine visual properties
                color = COLOR_MAP.get(label, "#AAB7B8")
                size = 28
                border_width = 2
                
                # Fraud highlighting
                if props.get('is_fraud'):
                    color = COLOR_MAP['confirmed_fraud']
                    size = 42
                    border_width = 4
                
                # Root node highlighting
                is_root = (root_id and node_id == root_id)
                if is_root:
                    size = 48
                    border_width = 4
                
                # Build rich tooltip
                tooltip_lines = [
                    f"━━━ {label.upper()} ━━━",
                    f"📌 {name}"
                ]
                
                if label == "Claim":
                    if props.get('claim_amount'):
                        tooltip_lines.append(f"💰 Amount: {format_currency(props['claim_amount'])}")
                    if props.get('claim_date'):
                        tooltip_lines.append(f"📅 Date: {props['claim_date']}")
                    if props.get('status'):
                        tooltip_lines.append(f"📋 Status: {props['status']}")
                    if props.get('incident_type'):
                        tooltip_lines.append(f"🚗 Type: {props['incident_type']}")
                
                elif label == "Provider":
                    if props.get('license'):
                        tooltip_lines.append(f"🏥 License: {props['license']}")
                    if props.get('status'):
                        tooltip_lines.append(f"📋 Status: {props['status']}")
                    if props.get('opened_date'):
                        tooltip_lines.append(f"📅 Opened: {props['opened_date']}")
                
                elif label == "Attorney":
                    if props.get('bar_number'):
                        tooltip_lines.append(f"⚖️ Bar: {props['bar_number']}")
                
                elif label == "Phone":
                    tooltip_lines.append(f"📱 {props.get('number', 'N/A')}")
                
                elif label == "Address":
                    addr_parts = [props.get('street', '')]
                    if props.get('unit'):
                        addr_parts.append(props['unit'])
                    if props.get('city'):
                        addr_parts.append(f"{props['city']}, {props.get('state', '')}")
                    tooltip_lines.append(f"🏠 {', '.join(filter(None, addr_parts))}")
                    if props.get('type'):
                        tooltip_lines.append(f"📍 Type: {props['type']}")
                
                elif label in ["Claimant", "Witness", "Employee", "Person"]:
                    if props.get('role'):
                        tooltip_lines.append(f"👤 Role: {props['role']}")
                    if props.get('job_title'):
                        tooltip_lines.append(f"💼 Title: {props['job_title']}")
                
                # Fraud indicator
                if props.get('is_fraud'):
                    tooltip_lines.extend([
                        "",
                        "🚨 CONFIRMED FRAUD",
                        f"Type: {props.get('fraud_type', 'Unknown')}"
                    ])
                
                # ID reference
                tooltip_lines.extend(["", f"ID: {node_id}"])
                
                nodes[element_id] = Node(
                    id=str(element_id),
                    label=name[:25] + "..." if len(str(name)) > 25 else str(name),
                    size=size,
                    color=color,
                    title="\n".join(tooltip_lines),
                    shape="star" if is_root else "dot",
                    borderWidth=border_width,
                    borderWidthSelected=border_width + 2,
                    font={"size": 12, "color": "#FFFFFF", "strokeWidth": 2, "strokeColor": "#000000"}
                )
    
    # Second pass for relationships (from records with source, r, target structure)
    edge_set = set()
    for record in records:
        record_dict = dict(record)
        if 'r' in record_dict and record_dict['r'] is not None:
            rel = record_dict['r']
            source_node = record_dict.get('source')
            target_node = record_dict.get('target')
            if source_node and target_node and source_node.element_id in nodes and target_node.element_id in nodes:
                source = str(source_node.element_id)
                target = str(target_node.element_id)
                edge_key = f"{source}-{target}"
                reverse_key = f"{target}-{source}"
                
                if edge_key not in edge_set and reverse_key not in edge_set:
                    edge_set.add(edge_key)
                    rel_type = rel.type if hasattr(rel, 'type') else "CONNECTED"
                    rel_label = RELATIONSHIP_LABELS.get(rel_type, rel_type.replace("_", " ").title())
                    
                    edges.append(Edge(
                        source=source,
                        target=target,
                        title=f"🔗 {rel_label}",
                        color="#B0B0B0",
                        width=2,
                        smooth={"type": "continuous"},
                        arrows={"to": {"enabled": True, "scaleFactor": 0.5}},
                        hoverWidth=3,
                        selectionWidth=3
                    ))
    
    return list(nodes.values()), edges


def get_graph_config(width=1000, height=500, physics_enabled=True):
    """Configure graph visualization settings."""
    return Config(
        width=width,
        height=height,
        directed=True,
        physics={
            "enabled": physics_enabled,
            "stabilization": {"enabled": True, "iterations": 150, "fit": True},
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -60,
                "centralGravity": 0.015,
                "springLength": 120,
                "springConstant": 0.08,
                "avoidOverlap": 0.5
            }
        },
        interaction={
            "hover": True,
            "tooltipDelay": 50,
            "zoomView": True,
            "dragView": True,
            "dragNodes": True,
            "hideEdgesOnDrag": False,
            "hideEdgesOnZoom": False
        },
        edges={
            "color": {"inherit": False, "color": "#B0B0B0", "highlight": "#FFFFFF", "hover": "#FFFFFF"},
            "smooth": {"enabled": True, "type": "continuous"},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
            "hoverWidth": 2,
            "selectionWidth": 2
        },
        nodes={
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "font": {"size": 12, "color": "#FFFFFF"}
        }
    )

# =============================================================================
# DATA QUERIES
# =============================================================================

def run_scenario_query(query):
    """Execute scenario-specific Cypher query."""
    with driver.session() as session:
        result = session.run(query)
        return list(result)


def get_relationships_between_nodes(node_ids):
    """Fetch all relationships between a set of nodes."""
    if not node_ids:
        return []
    with driver.session() as session:
        result = session.run("""
            MATCH (a)-[r]->(b)
            WHERE a.id IN $ids AND b.id IN $ids
            RETURN a as source, r, b as target
        """, ids=list(node_ids))
        return list(result)


def get_database_stats():
    """Retrieve database statistics for admin dashboard."""
    with driver.session() as session:
        stats = {}
        
        result = session.run("MATCH (n) RETURN count(n) as count").single()
        stats['total_nodes'] = result['count'] if result else 0
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()
        stats['total_relationships'] = result['count'] if result else 0
        
        result = session.run("MATCH (c:Claim) RETURN count(c) as count").single()
        stats['claims'] = result['count'] if result else 0
        
        result = session.run("MATCH (c:Claim {is_fraud: true}) RETURN count(c) as count").single()
        stats['fraud_claims'] = result['count'] if result else 0
        
        return stats


def get_entity_types():
    """Get all entity types present in database."""
    with driver.session() as session:
        result = session.run("CALL db.labels()")
        return sorted([r[0] for r in result])


def get_entities_by_type(entity_type):
    """Get all entities of a specific type."""
    with driver.session() as session:
        result = session.run(f"""
            MATCH (n:{entity_type})
            RETURN n.id AS id, n.name AS name, n.number as number, n.street as street
            ORDER BY n.name, n.number
            LIMIT 500
        """)
        entities = []
        for r in result:
            display = r['name'] or r['number'] or r['street'] or r['id']
            entities.append((r['id'], display))
        return entities


def get_neighborhood(entity_type, entity_id, hops, entity_filters=None):
    """
    Get neighborhood of an entity with optional type filtering.
    
    Returns both nodes and relationship information.
    """
    with driver.session() as session:
        query = f"""
            MATCH path = (root:{entity_type} {{id: $entity_id}})-[*1..{hops}]-(connected)
            UNWIND nodes(path) as n
            RETURN DISTINCT n
        """
        result = session.run(query, entity_id=entity_id)
        return list(result)


def verify_scenarios():
    """Verify scenario data integrity and return results."""
    results = []
    
    with driver.session() as session:
        # Scenario 1: Webb
        result = session.run("""
            MATCH (a:Attorney {name: 'J. Marcus Webb'})<-[:REPRESENTED_BY]-(c:Claim)
            RETURN count(c) as count
        """).single()
        count = result['count'] if result else 0
        results.append({
            "scenario": "1: Captive Medical Mill",
            "check": "Webb client count",
            "expected": 47,
            "actual": count,
            "status": "✅" if count == 47 else "❌"
        })
        
        # Scenario 2: Phone
        result = session.run("""
            MATCH (ph:Phone {number: '555-847-2931'})<-[:HAS_PHONE]-(p:Person)
            RETURN count(p) as count
        """).single()
        count = result['count'] if result else 0
        results.append({
            "scenario": "2: Identity Web",
            "check": "Shared phone users",
            "expected": 5,
            "actual": count,
            "status": "✅" if count == 5 else "❌"
        })
        
        # Scenario 3a: Sunrise
        result = session.run("""
            MATCH (p:Provider {name: 'Sunrise Wellness Clinic'})<-[:TREATED_AT]-(c:Claim)
            RETURN count(c) as count
        """).single()
        count = result['count'] if result else 0
        results.append({
            "scenario": "3: The Audit (Fraud)",
            "check": "Sunrise claim count",
            "expected": 28,
            "actual": count,
            "status": "✅" if count == 28 else "❌"
        })
        
        # Scenario 3b: City General
        result = session.run("""
            MATCH (p:Provider {name: 'City General Emergency Room'})<-[:TREATED_AT]-(c:Claim)
            RETURN count(c) as count
        """).single()
        count = result['count'] if result else 0
        results.append({
            "scenario": "3: The Audit (Legitimate)",
            "check": "City General claim count",
            "expected": 32,
            "actual": count,
            "status": "✅" if count == 32 else "❌"
        })
        
        # Scenario 4: Bernard's fraud flag
        result = session.run("""
            MATCH (p:Provider {name: "Dr. Bernard's Auto Injury Center"})
            RETURN p.is_fraud as is_fraud
        """).single()
        is_fraud = result['is_fraud'] if result else False
        results.append({
            "scenario": "4: The Closed Case",
            "check": "Bernard's fraud flag",
            "expected": "True",
            "actual": str(is_fraud),
            "status": "✅" if is_fraud else "❌"
        })
        
        # Scenario 4: Chen active clients
        result = session.run("""
            MATCH (a:Attorney {name: 'Michael Chen'})<-[:REPRESENTED_BY]-(c:Claim)
            WHERE c.is_fraud = false
            RETURN count(c) as count
        """).single()
        count = result['count'] if result else 0
        results.append({
            "scenario": "4: The Closed Case",
            "check": "Chen active clients",
            "expected": 34,
            "actual": count,
            "status": "✅" if count == 34 else "❌"
        })
    
    return results

# =============================================================================
# PAGE: SCENARIO WALKTHROUGH
# =============================================================================

def render_scenario_walkthrough():
    """Render the primary scenario walkthrough interface."""
    
    st.title("🎯 Fraud Network Investigation")
    
    # Initialize session state
    if 'current_scenario' not in st.session_state:
        st.session_state.current_scenario = 1
    if 'current_hop' not in st.session_state:
        st.session_state.current_hop = 0
    
    # Scenario selector - prominent placement
    scenario_options = {
        1: "⚖️ Scenario 1: Captive Medical Mill",
        2: "📱 Scenario 2: Identity Web", 
        3: "📊 Scenario 3: Provider Distinction",
        4: "🔄 Scenario 4: Network Migration"
    }
    
    col_select, col_reset = st.columns([4, 1])
    
    with col_select:
        selected = st.selectbox(
            "Select Investigation Scenario",
            options=list(scenario_options.keys()),
            format_func=lambda x: scenario_options[x],
            index=st.session_state.current_scenario - 1,
            label_visibility="collapsed"
        )
    
    with col_reset:
        if st.button("↩️ Reset", use_container_width=True):
            st.session_state.current_hop = 0
            st.rerun()
    
    # Handle scenario change
    if selected != st.session_state.current_scenario:
        st.session_state.current_scenario = selected
        st.session_state.current_hop = 0
        st.rerun()
    
    scenario = SCENARIOS[selected]
    max_hop = len(scenario['hops']) - 1
    current_hop = st.session_state.current_hop
    hop = scenario['hops'][current_hop]
    
    # Scenario header
    st.markdown(f"### {scenario['icon']} {scenario['title']}")
    st.caption(scenario['subtitle'])
    
    # Trigger panel (collapsed after step 0)
    with st.expander("📋 Investigation Trigger", expanded=(current_hop == 0)):
        st.markdown(scenario['trigger'])
    
    st.divider()
    
    # Main layout: Controls + Info on left, Graph on right
    col_left, col_right = st.columns([2, 3])
    
    with col_left:
        # Navigation controls
        st.markdown(f"**Step {current_hop + 1} of {max_hop + 1}:** {hop['title']}")
        
        # Progress bar
        st.progress((current_hop + 1) / (max_hop + 1))
        
        # Navigation buttons
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button("← Previous", disabled=(current_hop == 0), use_container_width=True):
                st.session_state.current_hop -= 1
                st.rerun()
        with nav_col2:
            if current_hop < max_hop:
                if st.button("Next →", use_container_width=True, type="primary"):
                    st.session_state.current_hop += 1
                    st.rerun()
            else:
                st.button("✓ Complete", disabled=True, use_container_width=True)
        
        st.markdown("")
        
        # Current step narrative
        st.markdown("**Current Analysis:**")
        st.info(hop['narrative'])
        
        # Discovery highlight
        if hop['discovery']:
            st.success(f"**Key Finding:** {hop['discovery']}")
        
        # Comparison panels
        st.markdown("")
        
        with st.expander("🐌 Traditional Investigation Method", expanded=False):
            st.markdown(hop['traditional'])
        
        # Conclusion panel (final step only)
        if current_hop == max_hop:
            st.markdown("---")
            st.markdown("### 📊 Investigation Summary")
            
            conclusion = scenario['conclusion']
            
            st.metric("Total Exposure Identified", conclusion['exposure'])
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.metric("Traditional Time", conclusion['traditional_time'])
            with col_t2:
                st.metric("Graph Time", conclusion['graph_time'])
            
            st.warning(f"**Key Insight:** {conclusion['key_finding']}")
            
            with st.expander("📋 Recommended Actions", expanded=True):
                for i, action in enumerate(conclusion['action_items'], 1):
                    st.markdown(f"{i}. {action}")
    
    with col_right:
        # Graph visualization
        st.markdown("**Network Visualization**")
        
        timer = PerformanceTimer()
        timer.start()
        
        try:
            records = run_scenario_query(hop['query'])
            
            # Extract node IDs and fetch relationships
            node_ids = set()
            for record in records:
                for key, value in dict(record).items():
                    if value and hasattr(value, 'labels'):
                        props = dict(value)
                        if props.get('id'):
                            node_ids.add(props['id'])
            
            rel_records = get_relationships_between_nodes(node_ids)
            timer.stop()
            
            if records:
                # Combine node records with relationship records
                nodes, edges = create_graph_visualization(rel_records + records, scenario['starting_entity'][1])
                timer.set_counts(len(nodes), len(edges))
                
                # Compact metrics row
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Query", f"{timer.duration_ms}ms")
                with m2:
                    st.metric("Entities", len(nodes))
                with m3:
                    st.metric("Connections", len(edges))
                
                # Render graph
                config = get_graph_config(width=650, height=450)
                agraph(nodes, edges, config)
                
            else:
                st.warning("No data available. Please generate demo data in the Admin panel.")
        
        except Exception as e:
            st.error(f"Query error: {str(e)[:100]}")

# =============================================================================
# PAGE: FREE EXPLORATION
# =============================================================================

def render_free_exploration():
    """Render the free network exploration interface."""
    
    st.title("🔍 Network Exploration")
    st.caption("Investigate any entity's connections across the fraud network database")
    
    # Get available entity types
    entity_types = get_entity_types()
    
    if not entity_types:
        st.warning("Database is empty. Please generate demo data in the Admin panel.")
        return
    
    # Selection controls
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        selected_type = st.selectbox("Entity Type", entity_types, key="explore_type")
    
    with col2:
        entities = get_entities_by_type(selected_type)
        if not entities:
            st.warning(f"No {selected_type} entities found")
            return
        
        selected_entity = st.selectbox(
            "Select Entity",
            entities,
            format_func=lambda x: x[1],
            key="explore_entity"
        )
    
    with col3:
        hops = st.number_input("Depth", 1, 5, 2, key="explore_hops")
    
    # Entity type filters
    st.markdown("**Filter Visible Entity Types:**")
    
    filter_cols = st.columns(6)
    default_filters = {"Claim", "Claimant", "Provider", "Attorney", "Address", "Phone", "Witness", "Employee"}
    
    # Initialize filter state
    if 'entity_filters' not in st.session_state:
        st.session_state.entity_filters = default_filters.copy()
    
    available_filters = ["Claim", "Claimant", "Provider", "Attorney", "Address", "Phone", "Witness", "Employee", "Adjuster", "Location"]
    
    active_filters = set()
    for i, filter_type in enumerate(available_filters):
        with filter_cols[i % 6]:
            if st.checkbox(
                filter_type, 
                value=filter_type in st.session_state.entity_filters,
                key=f"filter_{filter_type}"
            ):
                active_filters.add(filter_type)
    
    st.session_state.entity_filters = active_filters if active_filters else default_filters
    
    # Selected entity display
    st.markdown(f"**Selected:** `{selected_entity[1]}` ({selected_type})")
    
    # Explore button
    if st.button("🔍 Explore Network", type="primary", use_container_width=True):
        timer = PerformanceTimer()
        timer.start()
        
        with st.spinner("Mapping network connections..."):
            records = get_neighborhood(selected_type, selected_entity[0], hops)
            timer.stop()
            
            if records:
                nodes, edges = create_graph_visualization(
                    records, 
                    selected_entity[0],
                    st.session_state.entity_filters
                )
                timer.set_counts(len(nodes), len(edges))
                
                st.session_state.explore_nodes = nodes
                st.session_state.explore_edges = edges
                st.session_state.explore_timer = timer
                st.session_state.explore_entity_name = selected_entity[1]
            else:
                st.warning("No connections found for this entity at the specified depth.")
                st.session_state.explore_nodes = None
    
    # Render stored graph
    if st.session_state.get('explore_nodes'):
        nodes = st.session_state.explore_nodes
        edges = st.session_state.explore_edges
        timer = st.session_state.explore_timer
        
        st.divider()
        
        st.markdown(f"### Network: {st.session_state.explore_entity_name}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Query Time", f"{timer.duration_ms}ms")
        with col2:
            st.metric("Entities", len(nodes))
        with col3:
            st.metric("Connections", len(edges))
        with col4:
            fraud_count = sum(1 for n in nodes if 'CONFIRMED FRAUD' in (n.title or ''))
            st.metric("Fraud Flags", fraud_count)
        
        config = get_graph_config(width=1100, height=550)
        agraph(nodes, edges, config)

# =============================================================================
# PAGE: ADMIN
# =============================================================================

def render_admin():
    """Render the administration panel."""
    
    st.title("⚙️ Administration")
    st.caption("Database management and scenario data generation")
    
    # Database Statistics
    st.markdown("### 📊 Database Status")
    
    col_header, col_refresh = st.columns([5, 1])
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_stats"):
            st.rerun()
    
    try:
        stats = get_database_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Nodes", f"{stats['total_nodes']:,}")
        with col2:
            st.metric("Relationships", f"{stats['total_relationships']:,}")
        with col3:
            st.metric("Claims", f"{stats['claims']:,}")
        with col4:
            st.metric("Fraud Cases", f"{stats['fraud_claims']:,}")
        
        if stats['total_nodes'] == 0:
            st.info("📭 Database is empty. Generate scenario data below to begin.")
    
    except Exception as e:
        st.error(f"Unable to retrieve database statistics: {e}")
    
    st.divider()
    
    # Data Generation
    st.markdown("### 🚀 Generate Scenario Data")
    st.warning("⚠️ This operation will **clear all existing data** and generate fresh scenario datasets including background data.")
    
    if st.button("Generate All Scenario Data", type="primary", use_container_width=True):
        progress_container = st.empty()
        status_container = st.empty()
        
        with st.spinner("Initializing data generation..."):
            try:
                generator = ScenarioDataGenerator()
                gen_stats = generator.generate_all_demo_data()
                generator.close()
                
                status_container.success("✅ Scenario data generated successfully!")
                st.balloons()
                
                # Show generation summary
                st.markdown("**Generation Summary:**")
                summary_cols = st.columns(3)
                
                items = list(gen_stats.items())
                for i, (key, value) in enumerate(items):
                    with summary_cols[i % 3]:
                        label = key.replace('_', ' ').title()
                        st.metric(label, f"{value} claims")
                
                st.info("👉 Navigate to **Scenario Walkthrough** to begin the demonstration.")
                
                time.sleep(1.5)
                st.rerun()
                
            except Exception as e:
                st.error(f"Data generation failed: {e}")
    
    st.divider()
    
    # Verification
    st.markdown("### ✅ Data Verification")
    st.caption("Verify that all scenario data was generated correctly")
    
    if st.button("Run Verification Checks", use_container_width=True):
        with st.spinner("Running verification..."):
            try:
                results = verify_scenarios()
                
                # Display as table
                st.markdown("**Verification Results:**")
                
                all_passed = all(r['status'] == '✅' for r in results)
                
                for r in results:
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    with col1:
                        st.text(r['scenario'])
                    with col2:
                        st.text(r['check'])
                    with col3:
                        st.text(f"{r['actual']}/{r['expected']}")
                    with col4:
                        st.text(r['status'])
                
                if all_passed:
                    st.success("All verification checks passed.")
                else:
                    st.warning("Some checks failed. Consider regenerating scenario data.")
                    
            except Exception as e:
                st.error(f"Verification failed: {e}")
    
    st.divider()
    
    # Clear Database
    st.markdown("### 🗑️ Clear Database")
    st.caption("Remove all data from the database")
    
    # Use a form to handle the confirmation properly
    with st.form("clear_form"):
        confirm = st.checkbox("I confirm I want to delete ALL data from the database")
        submitted = st.form_submit_button("Clear All Data", type="secondary")
        
        if submitted:
            if confirm:
                try:
                    with driver.session() as session:
                        session.run("MATCH (n) DETACH DELETE n")
                    st.success("✅ Database cleared successfully.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear database: {e}")
            else:
                st.warning("Please check the confirmation box to proceed.")

# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.title("🔍 Fraud Ring Detection")
st.sidebar.caption("Graph-Powered SIU Investigation Platform")

page = st.sidebar.radio(
    "Navigation",
    ["🎯 Scenario Walkthrough", "🔍 Network Exploration", "⚙️ Administration"],
    label_visibility="collapsed"
)

st.sidebar.divider()

# Legend
st.sidebar.markdown("### Visual Legend")
st.sidebar.markdown("""
**Entity Types:**
- 🔵 Claimants & Witnesses
- 🟢 Adjusters & Employees
- 🟣 Medical Providers
- 🟠 Attorneys
- 🩵 Addresses & Phones

**Indicators:**
- 🔴 Confirmed Fraud
- ⭐ Investigation Starting Point
""")

st.sidebar.divider()

st.sidebar.markdown("### Graph Controls")
st.sidebar.markdown("""
- **Scroll** — Zoom in/out
- **Drag background** — Pan view
- **Drag node** — Reposition
- **Hover** — View details
- **Click** — Select entity
""")

st.sidebar.divider()
st.sidebar.caption("© 2025 SIU Investigation Platform")

# =============================================================================
# MAIN ROUTING
# =============================================================================

if page == "🎯 Scenario Walkthrough":
    render_scenario_walkthrough()
elif page == "🔍 Network Exploration":
    render_free_exploration()
else:
    render_admin()