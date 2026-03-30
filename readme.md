# 🧠 Automated Grievance Categorization & Routing System

## (Clean MVP Architecture – Hackathon Ready)

---

# 🎯 Objective

Build an AI-powered system that:

* Classifies complaints into categories
* Detects urgency (High / Medium / Low)
* Routes to the correct department
* Identifies recurring issues
* Displays insights via a dashboard
* Supports multilingual input

---

# 🧩 SYSTEM ARCHITECTURE (HIGH LEVEL)

```
User Input (Web UI)
        ↓
[Language Detection + Translation Layer]
        ↓
[DistilBERT Model]
        ↓
[Category Output]
        ↓
[Urgency Detection Module]
        ↓
[Rule-Based Routing Engine]
        ↓
[Database Storage (Neon PostgreSQL)]
        ↓
[Dashboard (Next.js)]
```

---

# ⚙️ TECH STACK

Frontend:

* Next.js (Vercel)

Backend:

* FastAPI (Render)

Database:

* Neon PostgreSQL

AI Model:

* distilbert-base-uncased

Other:

* Translation (Google Translate API or lightweight library)

---

# 🔄 END-TO-END FLOW (STEP BY STEP)

## 1. User Input

* User submits complaint via web form
* Input can be in any language

Example:

```
"Hostel la water problem iruku"
```

---

## 2. Language Processing

* Detect language
* If not English → translate to English

```
Tamil → English
"Water problem in hostel"
```

---

## 3. Classification (DistilBERT)

* Model predicts category

Example Output:

```
Category: "Hostel"
```

---

## 4. Urgency Detection

### Hybrid Approach:

#### A. Model-based (optional)

* Predict urgency label

#### B. Keyword-based (mandatory fallback)

```
if "urgent" or "immediately":
    HIGH
elif "soon":
    MEDIUM
else:
    LOW
```

---

## 5. Routing Logic (Rule-Based)

```
if category == "Hostel":
    department = "Hostel Office"

elif category == "Fees":
    department = "Accounts"

elif category == "IT":
    department = "IT Support"
```

---

## 6. Database Storage

Store:

* complaint_text
* translated_text
* category
* urgency
* department
* timestamp

---

## 7. Dashboard (Admin View)

Display:

* Total complaints
* Complaints per category
* High priority complaints
* Repeated complaints

---

## 8. Trend Detection (Simple Logic)

```
GROUP BY complaint_text or category
COUNT occurrences
```

→ Identify repeated issues (no ML needed)

---

# 🧠 CORE MODULES

## 1. Translation Layer

* Converts multilingual input → English
* Keeps system lightweight

---

## 2. NLP Model (DistilBERT)

* Handles classification
* Pre-trained or lightly fine-tuned

---

## 3. Urgency Engine

* Hybrid (model + keyword rules)

---

## 4. Routing Engine

* Simple if-else mapping
* Fast and reliable

---

## 5. Database Layer

* Stores all processed complaints
* Enables analytics

---

## 6. Dashboard Layer

* Visual insights for admin
* Helps identify bottlenecks

---

# 🚀 FLOW OF CONTROL (DETAILED)

```
START
 ↓
User submits complaint
 ↓
Check language
 ↓
Translate if needed
 ↓
Send to DistilBERT
 ↓
Get category
 ↓
Detect urgency
 ↓
Apply routing rules
 ↓
Store in database
 ↓
Update dashboard
 ↓
END
```

---

# ⚠️ DESIGN PRINCIPLES (VERY IMPORTANT)

* Keep everything lightweight
* Avoid unnecessary APIs
* Prioritize working demo over complexity
* Modular design → easy to extend later

---

# ❌ EXCLUDED FEATURES (FOR MVP)

These are intentionally removed:

* RAG (ChromaDB, embeddings)
* Voice input
* WhatsApp integration
* Firebase notifications
* mBERT / heavy multilingual models
* SLA-based escalation systems
* Advanced ML analytics

---

# 🔌 EXTENSIBILITY (FOR FUTURE)

Your team can later add:

* RAG-based response system
* Auto-escalation workflows
* Omnichannel input (WhatsApp, voice)
* Notification systems
* Advanced analytics (ML-based pattern detection)

---

# 🏁 FINAL SUMMARY

This system:

* Fully satisfies problem requirements
* Is lightweight and hackathon-ready
* Can be built within time constraints
* Is easily extendable for advanced features

---

# 💬 KEY INSIGHT

Focus on:
✔ Accuracy
✔ Speed
✔ Clarity in demo

Not on:
❌ Complexity
❌ Fancy features
❌ Overengineering
