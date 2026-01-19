# Insurance Fraud Ring Detection Platform
## User Guide for SIU Investigators & Business Stakeholders

**Version:** 1.0  
**Last Updated:** January 2025

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [The Graph Advantage](#2-the-graph-advantage)
3. [Application Pages](#3-application-pages)
   - [Scenario Walkthrough](#31-scenario-walkthrough)
   - [Network Exploration](#32-network-exploration)
   - [Administration](#33-administration)
4. [Investigation Scenarios](#4-investigation-scenarios)
   - [Scenario 1: The Two-Hour Attorney](#scenario-1-the-two-hour-attorney)
   - [Scenario 2: The Typo That Wasn't](#scenario-2-the-typo-that-wasnt)
   - [Scenario 3: The Audit That Went Deeper](#scenario-3-the-audit-that-went-deeper)
   - [Scenario 4: The Case We Thought Was Closed](#scenario-4-the-case-we-thought-was-closed)
5. [Data Model Reference](#5-data-model-reference)
   - [Entity Types](#51-entity-types)
   - [Relationship Types](#52-relationship-types)
   - [Schema Diagram](#53-schema-diagram)
6. [Graph Controls & Navigation](#6-graph-controls--navigation)
7. [Interpreting Results](#7-interpreting-results)
8. [Glossary](#8-glossary)

---

## 1. Executive Overview

### Purpose

This platform demonstrates how **graph database technology** transforms insurance fraud investigation by revealing hidden network connections that traditional SQL databases and spreadsheet-based methods cannot efficiently detect.

### Target Users

- Special Investigations Unit (SIU) leadership
- Claims operations directors
- Fraud analysts and investigators
- Technology decision-makers evaluating graph database investments

### Core Value Proposition

| Traditional Investigation | Graph-Powered Investigation |
|---------------------------|----------------------------|
| Query what you already know to ask | Discover what you didn't know to look for |
| Linear, single-claim focus | Network-wide visibility |
| Days/weeks to map connections | Minutes to visualize full networks |
| Manual cross-referencing | Automatic relationship traversal |
| Hidden patterns remain hidden | Lateral connections surface automatically |

---

## 2. The Graph Advantage

### What Makes Graph Different?

In traditional relational databases, data lives in separate tables. Finding connections requires:
- Knowing which tables to join
- Writing complex queries for each connection type
- Multiple round-trips for multi-hop relationships
- Prior knowledge of what you're looking for

**Graph databases store relationships as first-class citizens.** This means:
- Connections are pre-computed and instant to traverse
- Multi-hop queries (friend-of-friend-of-friend) execute in milliseconds
- Pattern discovery happens naturally through exploration
- You can find connections you didn't know to look for

### The "Impossible Without Graph" Test

Each scenario in this platform includes at least one discovery that meets these criteria:

1. **Spans multiple entity types** — The connection crosses from person → address → phone → role
2. **Lateral, not linear** — Discovery happens across providers or across organizational boundaries
3. **Requires unknowable queries** — An investigator would need to know the question before asking it

---

## 3. Application Pages

### 3.1 Scenario Walkthrough

**Purpose:** Guided demonstration of fraud network discovery through four curated investigation scenarios.

#### Layout

| Left Panel | Right Panel |
|------------|-------------|
| Navigation controls | Network visualization |
| Step narrative | Performance metrics |
| Key findings | Interactive graph |
| Traditional vs. Graph comparison | |

#### Components

**Scenario Selector**
- Dropdown menu to choose from four pre-built scenarios
- Reset button to return to Step 1

**Investigation Trigger**
- Expandable panel showing the initial flag that prompted investigation
- Describes what an adjuster or analyst would see in their daily workflow
- Automatically expanded on Step 1, collapsed thereafter

**Step Navigation**
- Progress bar showing current position in the investigation
- Previous/Next buttons to move through discovery steps
- Each step reveals additional network connections

**Current Analysis**
- Blue info box describing what the current step examines
- Written from the investigator's perspective

**Key Finding**
- Green success box highlighting the discovery made at this step
- Only appears when a significant finding is revealed

**Traditional Investigation Method**
- Expandable panel (collapsed by default)
- Describes how this same discovery would occur using traditional methods
- Emphasizes time requirements and practical limitations

**Investigation Summary**
- Appears only on the final step
- Shows total exposure identified
- Compares traditional vs. graph investigation time
- Lists recommended follow-up actions

**Network Visualization**
- Interactive graph showing entities and relationships
- Updates with each step to show expanding network
- Root entity displayed as a star shape
- Fraud-confirmed entities shown in red

---

### 3.2 Network Exploration

**Purpose:** Free-form investigation of any entity in the database, enabling ad-hoc analysis beyond pre-built scenarios.

#### Components

**Entity Selection**
| Control | Description |
|---------|-------------|
| Entity Type | Dropdown to select category (Attorney, Provider, Phone, etc.) |
| Select Entity | Dropdown showing all entities of selected type |
| Depth | Number of relationship hops to traverse (1-5) |

**Entity Type Filters**
- Checkbox grid to show/hide specific entity types in visualization
- All checked by default
- Root entity type is disabled (cannot be excluded) with tooltip explanation
- Allows focusing on specific connection patterns

**Explore Network Button**
- Triggers the graph query and visualization
- Shows loading spinner during query execution

**Results Display**
- Performance metrics: Query time, entity count, connection count, fraud flags
- Full interactive graph visualization
- Same interaction controls as Scenario Walkthrough

---

### 3.3 Administration

**Purpose:** Database management, data generation, and system verification.

#### Components

**Database Status**
- Real-time statistics showing:
  - Total nodes (entities) in database
  - Total relationships (connections)
  - Number of claims
  - Confirmed fraud cases
- Refresh button to update statistics

**Generate Scenario Data**
- One-click generation of complete demo dataset
- Warning: Clears all existing data before generation
- Creates:
  - ~150 legitimate background claims
  - All four fraud scenarios with specific data patterns
  - Supporting entities (providers, attorneys, addresses, phones)
- Shows generation summary upon completion

**Data Verification**
- Runs integrity checks on all four scenarios
- Displays pass/fail status for each check:
  - Scenario 1: Webb client count (expected: 47)
  - Scenario 2: Shared phone users (expected: 5)
  - Scenario 3: Sunrise claims (expected: 28), City General claims (expected: 32)
  - Scenario 4: Bernard's fraud flag, Chen active clients (expected: 34)

**Clear Database**
- Removes all data from the database
- Requires confirmation checkbox before proceeding
- Use with caution — action cannot be undone

---

## 4. Investigation Scenarios

### Scenario 1: The Two-Hour Attorney

#### The Trigger
An adjuster notes that a claimant secured legal representation within 2 hours of reporting an accident. While not unprecedented, this rapid engagement warrants investigation.

#### Investigation Question
Is this attorney operating a solicitation network, or simply employing aggressive marketing?

#### Network Discovery Path

| Step | Discovery | Significance |
|------|-----------|--------------|
| 1 | Attorney J. Marcus Webb identified | Starting point |
| 2 | 47 claimants in 6 months | 8x typical attorney volume |
| 3 | 41 of 47 (87%) treated at 2 clinics | Extreme provider concentration |
| 4 | Both clinics share same business address | Co-location suggests coordination |
| 5 | Billing manager & patient coordinator share home address | Personal relationship between clinic employees |
| 6 | Employee appears as witness on 8 claims | Cross-role fraud indicator |
| 7 | Attorney's wife is registered agent for both clinics | Hidden ownership revealed |

#### What Traditional Methods Would Miss
- The spousal ownership connection exists in corporate registry data, not claims systems
- Employee home address sharing requires HR data cross-reference
- Cross-role witness detection requires systematic comparison across all claims
- **Estimated traditional investigation time: 2-3 weeks**

#### Business Impact
- **Exposure Identified:** $1.2M across 47 claims
- **Graph Investigation Time:** Under 5 minutes
- **Key Insight:** Hidden ownership via spouse as registered agent — a connection that exists entirely outside claims data systems

---

### Scenario 2: The Typo That Wasn't

#### The Trigger
ISO database returns a phone number match: the same number appears on two claims with different claimant names. The adjuster assumes it's a data entry error or shared family contact.

#### Investigation Question
Is this a clerical anomaly, or evidence of coordinated fraud?

#### Network Discovery Path

| Step | Discovery | Significance |
|------|-----------|--------------|
| 1 | Phone 555-847-2931 flagged by ISO | Starting point |
| 2 | 5 different people used this phone | ISO only showed 2 |
| 3 | 3 of 5 share same apartment address | Identity clustering |
| 4 | 2 additional people at same address with different phone | Network expansion to 7 people |
| 5 | 6 claims totaling $185,000 in 45-day window | Coordinated filing pattern |

#### What Traditional Methods Would Miss
- ISO match shows 2 claims; remaining 4 would never be flagged
- Phone → address → different phone → more people requires multiple system queries
- **You cannot query for connections you don't know exist**

#### Business Impact
- **Exposure Identified:** $185,000 across 6 claims
- **Traditional Result:** Investigate 2 claims, miss 4
- **Graph Investigation Time:** 60 seconds
- **Key Insight:** Scope expansion from 2 ISO hits to 7 connected individuals

---

### Scenario 3: The Audit That Went Deeper

#### The Trigger
Quarterly provider audit flags two facilities with elevated billing:
- Sunrise Wellness Clinic: 28 claims, 38% above peer average
- City General ER: 32 claims, 42% above peer average

Both are flagged. Limited SIU resources require prioritization.

#### Investigation Question
Which provider warrants full investigation? Which is a false positive?

#### Network Discovery Path — Sunrise Wellness (FRAUD)

| Step | Discovery | Significance |
|------|-----------|--------------|
| 1 | Sunrise Wellness flagged for high billing | Starting point |
| 2 | 28 claimants treated at facility | Volume baseline |
| 3 | 23 of 28 (82%) represented by same attorney | Extreme concentration |
| 4 | Attorney refers to only 2 providers | Exclusive referral pipeline |
| 5 | 7 claimants share phone across both clinics | Cross-provider identity link |
| 6 | Same witness appears at both facilities | Professional witness indicator |

#### Network Discovery Path — City General ER (LEGITIMATE)

| Step | Discovery | Significance |
|------|-----------|--------------|
| 1 | City General flagged for high billing | Comparison case |
| 2 | 32 claimants treated | Similar volume to Sunrise |
| 3 | 12 different attorneys (none >15%) | Normal distribution |
| 4 | Zero shared phones or addresses | No identity clustering |
| 5 | Location: Major highway junction | High-traffic explains volume |

#### What Traditional Methods Would Miss
- Both providers flagged identically by billing metrics
- Without network analysis, prioritization is arbitrary
- Cross-provider phone sharing would never be discovered
- **False positive investigation wastes ~40 hours**

#### Business Impact
- **Sunrise Exposure:** $400K+ (confirmed fraud network)
- **City General:** Cleared in 30 seconds (legitimate high-volume ER)
- **Key Insight:** Graph analysis both identifies fraud AND rapidly clears legitimate entities

---

### Scenario 4: The Case We Thought Was Closed

#### The Trigger
Six months ago, SIU successfully prosecuted Dr. Bernard's Auto Injury Center:
- $62,000 in claims denied
- Provider license revoked
- Case status: **Closed**

#### Investigation Question
Did we dismantle the entire operation, or merely one component?

#### Network Discovery Path

| Step | Discovery | Significance |
|------|-----------|--------------|
| 1 | Dr. Bernard's marked as confirmed fraud | Closed case |
| 2 | 15 claims in original case | Known scope |
| 3 | 12 of 15 (80%) represented by Attorney Michael Chen | Key connection point |
| 4 | Chen has 34 NEW clients since closure | Network still active |
| 5 | 28 of 34 treated at Rapid Recovery Med | New treatment facility |
| 6 | Rapid Recovery opened 2 months after Bernard's shutdown | Timing correlation |
| 7 | Rapid Recovery owned by Dr. Patricia Simmons — former Bernard's employee | Network migration confirmed |

#### What Traditional Methods Would Miss
- Case closed = file archived = no ongoing monitoring
- Attorney connection noted but not investigated
- New provider opened by former employee never linked to closed case
- **Network adapted and continued operations undetected**

#### Business Impact
- **Original Case Savings:** $62,000
- **Active Network Exposure:** $280,000+
- **Key Insight:** Fraud networks don't disappear — they migrate. Graph reveals persistent links (Chen) connecting old and new operations.

---

## 5. Data Model Reference

### 5.1 Entity Types

| Entity | Description | Key Attributes | Visual Color |
|--------|-------------|----------------|--------------|
| **Claim** | Insurance claim record | Amount, date, status, incident type, fraud flag | Steel Blue |
| **Claimant** | Person who filed the claim | Name, SSN, role | Sky Blue |
| **Witness** | Person who witnessed the incident | Name, role | Light Blue |
| **Adjuster** | Insurance employee handling the claim | Name, employee ID | Green |
| **Employee** | Staff at provider/attorney office | Name, job title | Teal |
| **Provider** | Medical treatment facility | Name, license, status, opened date | Purple |
| **Attorney** | Legal representative | Name, bar number | Amber |
| **BodyShop** | Vehicle repair facility | Name, license | Orange |
| **Address** | Physical location (residential or business) | Street, unit, city, state, type | Seafoam |
| **Phone** | Contact phone number | Number | Medium Blue |
| **Location** | Accident location | Name, coordinates, type | Lavender |
| **Vehicle** | Vehicle involved in claim | VIN, make, model, plate | Gray |

#### Special Indicators

| Indicator | Meaning | Visual |
|-----------|---------|--------|
| Confirmed Fraud | Entity has `is_fraud: true` | Red color, larger size |
| Root Entity | Starting point of investigation | Star shape |

---

### 5.2 Relationship Types

#### Claim Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `FILED_BY` | Claim | Claimant | Who submitted the claim |
| `TREATED_AT` | Claim | Provider | Where medical treatment occurred |
| `REPRESENTED_BY` | Claim | Attorney | Legal representation |
| `HANDLED_BY` | Claim | Adjuster | Insurance employee assigned |
| `WITNESSED_BY` | Claim | Witness | Who observed the incident |
| `REPAIRED_AT` | Claim | BodyShop | Where vehicle was repaired |
| `OCCURRED_AT` | Claim | Location | Where accident happened |
| `INVOLVES_VEHICLE` | Claim | Vehicle | Vehicle in the incident |

#### Person → Identifier Relationships (Key for Fraud Detection)

| Relationship | From | To | Fraud Detection Value |
|--------------|------|-----|----------------------|
| `LIVES_AT` | Person | Address | Detects identity clusters, ghost passengers |
| `HAS_PHONE` | Person | Phone | Reveals shared identity networks |
| `WORKS_AT` | Person | Address | Links employees to business locations |

#### Organization Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `LOCATED_AT` | Provider/Attorney | Address | Business location |
| `EMPLOYS` | Provider/Attorney | Employee | Staff relationships |
| `REGISTERED_AGENT` | Provider | Person | Corporate registration (ownership indicator) |
| `OWNED_BY` | Provider | Person | Direct ownership |

#### Special Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| `MARRIED_TO` | Person | Person | Spousal relationship |
| `FORMER_EMPLOYEE_OF` | Person | Provider | Previous employment (migration indicator) |

---

### 5.3 Schema Diagram

```
                                    ┌─────────────┐
                                    │   Vehicle   │
                                    └──────▲──────┘
                                           │ INVOLVES_VEHICLE
                                           │
┌──────────────┐                    ┌──────┴──────┐                    ┌─────────────┐
│   Location   │◄───OCCURRED_AT─────│    Claim    │────TREATED_AT─────►│  Provider   │
└──────────────┘                    └──────┬──────┘                    └──────┬──────┘
                                           │                                  │
                    ┌──────────────────────┼──────────────────────┐          │
                    │                      │                      │          │
                    ▼                      ▼                      ▼          │
             ┌──────────┐           ┌──────────┐           ┌──────────┐     │
             │ Claimant │           │ Attorney │           │  Witness │     │
             └────┬─────┘           └──────────┘           └──────────┘     │
                  │                                                          │
                  │                                                          │
        ┌─────────┴─────────┐                                    ┌──────────┴──────────┐
        │                   │                                    │                     │
        ▼                   ▼                                    ▼                     ▼
   ┌─────────┐        ┌─────────┐                          ┌──────────┐         ┌──────────┐
   │ Address │        │  Phone  │                          │ Employee │         │ Address  │
   └─────────┘        └─────────┘                          └──────────┘         │(Business)│
        ▲                   ▲                                    │              └──────────┘
        │                   │                                    │
        │                   │                                    ▼
        │                   │                              ┌──────────┐
        └───────────────────┴──────────────────────────────│ Address  │
                    Multiple people sharing                │  (Home)  │
                    = Fraud indicator                      └──────────┘
```

#### Key Fraud Patterns Detected by Schema

| Pattern | Entities Involved | Detection Method |
|---------|-------------------|------------------|
| Identity Ring | Multiple Claimants → Same Phone/Address | Shared identifier clustering |
| Captive Medical Mill | Attorney → Provider → Registered Agent | Ownership traversal |
| Cross-Role Fraud | Employee ↔ Witness | Same person, multiple roles |
| Network Migration | Former Employee → New Provider | Employment history links |
| Referral Pipeline | Attorney → Limited Providers | Relationship concentration |

---

## 6. Graph Controls & Navigation

### Mouse Controls

| Action | Result |
|--------|--------|
| **Scroll wheel** | Zoom in/out |
| **Click + drag background** | Pan the view |
| **Click + drag node** | Reposition entity |
| **Hover over node** | Display entity details tooltip |
| **Hover over edge** | Display relationship type |
| **Click node** | Select entity (highlights connections) |

### Understanding the Visualization

#### Node Appearance

| Visual | Meaning |
|--------|---------|
| **Star shape** | Root entity (investigation starting point) |
| **Dot shape** | Standard entity |
| **Large red node** | Confirmed fraud |
| **Node color** | Entity type (see legend in sidebar) |
| **Node size** | Relative importance/fraud status |

#### Edge Appearance

| Visual | Meaning |
|--------|---------|
| **Arrow direction** | Relationship direction (from → to) |
| **Gray color** | Standard relationship |
| **Highlighted on hover** | Active relationship |

---

## 7. Interpreting Results

### Red Flags to Watch For

| Indicator | What It Means | Severity |
|-----------|---------------|----------|
| High attorney concentration (>50%) | Possible solicitation/referral scheme | High |
| Shared phone across claimants | Identity ring indicator | High |
| Shared address (non-family) | Staged accident ring | High |
| Employee appearing as witness | Cross-role fraud | Critical |
| Provider ownership by attorney family | Captive medical mill | Critical |
| New provider opened after prosecution | Network migration | High |
| Claims clustered in short time window | Coordinated filing | Medium-High |

### False Positive Indicators

| Indicator | Legitimate Explanation |
|-----------|------------------------|
| Shared address (2 people) | Married couple, family members |
| High provider volume | ER near accident-prone location |
| Multiple claims, same attorney | Large personal injury firm |
| Same witness on 2 claims | Legitimate bystander at same location |

### Recommended Investigation Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Attorney client concentration | >70% to single provider | Full investigation |
| Phone sharing | >2 unrelated claimants | Identity verification |
| Address sharing | >3 claimants | Site inspection |
| Provider referral concentration | >60% from single attorney | Provider audit |
| Witness appearances | >3 claims | Background check |

---

## 8. Glossary

| Term | Definition |
|------|------------|
| **Captive Medical Mill** | Medical facility secretly owned/controlled by attorneys who refer their clients there for inflated treatment billing |
| **Cross-Role Fraud** | Single individual appearing in multiple roles (e.g., clinic employee also listed as independent witness) |
| **Entity** | Any node in the graph: person, organization, claim, or identifier |
| **Ghost Passenger** | Fictitious person added to accident claim who wasn't actually present |
| **Graph Traversal** | Following relationships from one entity to connected entities |
| **Hop** | One step along a relationship in the graph (2 hops = entity → relationship → entity → relationship → entity) |
| **Identity Ring** | Group of individuals sharing contact information to file coordinated fraudulent claims |
| **ISO** | Insurance Services Office — industry database for cross-carrier claim matching |
| **Network Migration** | Fraud operation relocating to new entities after prosecution while maintaining key connections |
| **NICB** | National Insurance Crime Bureau — industry organization for fraud investigation referrals |
| **Node** | Visual representation of an entity in the graph |
| **Referral Pipeline** | Arrangement where attorneys exclusively refer clients to specific providers (often for kickbacks) |
| **Relationship** | Connection between two entities (e.g., TREATED_AT, REPRESENTED_BY) |
| **Root Entity** | Starting point of a graph investigation |
| **SIU** | Special Investigations Unit — insurance company fraud investigation team |
| **Staged Accident** | Deliberately caused or fabricated accident for insurance fraud |

---

## Document Information

**Prepared for:** SIU Leadership and Business Stakeholders  
**Platform Version:** 1.0  
**Document Version:** 1.0  
**Classification:** Internal Use

---

*For technical documentation, deployment guides, or API integration details, please refer to the Technical Implementation Guide.*
