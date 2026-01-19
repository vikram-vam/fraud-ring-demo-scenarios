# 🔍 Insurance Fraud Ring Detection Demo

A scenario-driven demonstration of Graph Database technology for insurance fraud investigation, targeting SIU (Special Investigations Unit) stakeholders in P&C Auto Insurance.

## 🎯 Demo Objectives

This demo showcases how **Graph DB enables discoveries that are impossible with traditional SQL/Excel approaches**:

1. **Lateral connections** across entity types (person ↔ address ↔ phone ↔ role)
2. **Network-wide visibility** vs. single-claim investigation
3. **Hidden relationships** (ownership, employment, identity sharing)
4. **False positive reduction** by quickly clearing legitimate high-volume entities

## 📋 Scenarios

### 1. The Two-Hour Attorney
Attorney with 47 clients → 87% treated at 2 clinics → Same business address → Wife is registered agent for both → **Captive medical mill**

### 2. The Typo That Wasn't  
ISO flags 2 claims sharing phone → Graph reveals 5 users → 3 share address → 2 more at same address with different phone → **7-person identity ring, $185K exposure**

### 3. The Audit That Went Deeper
Two providers flagged for high billing → Graph shows Sunrise has 82% referral concentration + shared phones → City General has normal distribution → **One fraud, one legitimate (false positive avoided)**

### 4. The Case We Thought Was Closed
Confirmed fraud provider → Attorney represented 80% → Attorney now has 34 new clients → 82% at new clinic → Owner was former employee → **Network migrated, not ended**

## 🚀 Quick Start

### 1. Set up Neo4j

Create a free [Neo4j AuraDB](https://neo4j.com/cloud/aura/) instance or use local Neo4j.

### 2. Configure Secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your Neo4j credentials
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

### 5. Generate Demo Data

1. Navigate to **⚙️ Admin** panel
2. Click **🎯 Generate All Scenario Data**
3. Go to **🎯 Scenario Walkthrough** to start the demo

## 📁 Project Structure

```
fraud-ring-demo/
├── app.py                      # Main Streamlit application
├── scenario_data_generator.py  # Data generation for all scenarios
├── requirements.txt            # Python dependencies
├── .streamlit/
│   ├── config.toml            # Streamlit theme/config
│   └── secrets.toml.example   # Template for Neo4j credentials
└── README.md                   # This file
```

## 🎨 UI Features

- **Hop-by-hop walkthrough** with Traditional vs Graph comparison
- **Interactive network visualization** with drag/zoom
- **Performance metrics** (query time, entity counts)
- **Color-coded entities** (blue=people, purple=providers, orange=attorneys, red=fraud)
- **Free exploration mode** for ad-hoc investigation

## 📊 Data Schema

### Nodes
- `Claim` - Insurance claims
- `Person` (`:Claimant`, `:Witness`, `:Adjuster`, `:Employee`)
- `Provider` - Medical providers
- `Attorney` - Legal representation
- `Address` - Residential and business addresses
- `Phone` - Phone numbers (key for identity detection)
- `Location` - Accident locations

### Key Relationships
- `(Claim)-[:FILED_BY]->(Person:Claimant)`
- `(Claim)-[:TREATED_AT]->(Provider)`
- `(Claim)-[:REPRESENTED_BY]->(Attorney)`
- `(Person)-[:LIVES_AT]->(Address)` ← **Enables identity clustering**
- `(Person)-[:HAS_PHONE]->(Phone)` ← **Enables identity detection**
- `(Provider)-[:REGISTERED_AGENT]->(Person)` ← **Exposes hidden ownership**

## 🎯 Demo Tips

1. **Start with Scenario 1** - Most comprehensive, shows hidden ownership
2. **Use the "Traditional vs Graph" panels** - Key for ROI messaging
3. **Highlight the "impossible" moments** - Where would you even think to query this?
4. **End with Scenario 3's false positive** - Shows graph saves time both ways
5. **Let stakeholders drive Free Exploration** - "What else would you want to check?"

## 📝 License

MIT License - Use freely for demonstrations and proof-of-concepts.