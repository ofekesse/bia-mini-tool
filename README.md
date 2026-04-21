# GRC BIA Prioritization Mini-Tool

**Goal:** A simple CLI tool that processes Business Impact Analysis (BIA) data, provides dynamic prioritization, and leverages Google Gemini AI to suggest security controls and challenge the sorting logic.

## 🚀 How to Run the Project

1. **Clone the repository and navigate to the folder.**
2. **Set up a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux
   # or `venv\Scripts\activate` on Windows
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up the AI API Key:**
   -Create a .env file in the root directory and add your Google Gemini API key:
   GOOGLE_API_KEY=your_api_key_here
5. **Run the Engine:**
   ```bash
   python main.py
   The script will prompt you to select an Excel file from the directory.
   ```

## 🧠 My Approach - Prioritization Logic & Algorithm

The prioritization engine calculates the recovery order to minimize financial, reputational, and operational damage. The baseline Priority (High/Medium/Low) is primarily driven by the Process Status.

To handle edge cases where multiple systems share the same Priority level, the script applies a sequential tie-breaking algorithm:

RTO (Ascending): Systems with the shortest target recovery time are prioritized first to halt escalating damages.

MAO (Ascending): If RTO is identical, the system with the shortest Maximum Acceptable Outage takes precedence, as it sits closer to the threshold of irreversible business failure.

RPO (Ascending): Data loss (RPO) is evaluated next. While crucial, in an Ad-Tech environment, immediate availability (downtime) often poses a more immediate existential threat than minimal historical data loss.

Time-Critical Flag: Finally, processes containing any documented Time-Critical constraints receive a boolean weight boost, acknowledging their potential volatility during specific business cycles.

## 🤖 AI Usage (Task 2)

I integrated the Google GenAI SDK (Gemini 2.5 Flash) directly into the Python script to act as a "Devil's Advocate" and GRC Consultant.

📜 **The Prompt used:**
As a Senior GRC Expert, review the following BIA (Business Impact Analysis) data from Teads (an Ad-Tech company, Omnichannel, with a global presence).
My internal prioritization engine sorted these processes mathematically based on: Status -> RTO -> MAO -> RPO -> Time-Critical.
However, I need you to act as a critical "Devil's Advocate". Do NOT just agree with the math.

Data: {sorted_data.to_dict(orient='records')}

Based on your industry experience in Ad-Tech:

1. Are any of these systems misclassified in their initial 'Process Status' or 'RTO'? (e.g., Should a system labeled 'Important' actually be 'Critical'?).
2. Explicitly "Suggest a recovery priority" for these processes. If you were the CISO, would you manually override my engine's final sorting order? If yes, explicitly state your proposed order (1 to 4) and justify the business reasons for the override.

PART 2: PROCESS ANALYSIS & CONTROLS
For each process in the list, please provide:

1. A short summary of the business impact if it fails.
2. One specific security CONTROL (Preventive, Detective, or Corrective) that could mitigate the risk.
3. A detailed explanation of why this control is effective for this specific process, considering its RTO, MAO, RPO, and Time-Critical status.

# 💡 **AI Output** - based on all important processes

# AI-Generated GRC Insights:

PART 1: RECOVERY PRIORITY ASSESSMENT & DEVIL'S ADVOCATE

My Assessment:
While your internal engine's mathematical logic (Status -> RTO -> MAO -> RPO -> Time-Critical) is structurally sound and follows standard BIA methodology, as a GRC Devil's Advocate in the Ad-Tech space, I disagree with the final sorting order.

Relying purely on numeric RTO values misses the broader operational context during a crisis.

My Proposed CISO Override Order:

1. Internal Communications (Slack / Email) (Engine Ranked: 4)

2. CRM & Sales Pipeline (Salesforce) (Engine Ranked: 2)

3. Billing & Invoicing System (Engine Ranked: 1)

4. Data Warehouse & Analytics (BigQuery) (Engine Ranked: 3)

Justification for the Override:

Internal Comms to Priority 1: Your engine placed Internal Comms last due to a 48-hour RTO. However, during a major disaster, you cannot coordinate the recovery of the other systems without a communication channel. IT and GRC teams need Slack/Email immediately to manage the incident. It must be the first system restored.

CRM over Billing: In Ad-Tech, especially at the End of Quarter (Time-Critical constraint), losing the ability to close deals is a permanent revenue loss. Delayed billing (invoices) only causes a temporary cash flow delay, but the money isn't lost. Therefore, CRM takes precedence over Billing.

PART 2: PROCESS ANALYSIS & CONTROLS

1. Billing & Invoicing System

Business Impact: Delayed cash flow, inability to process client payments at the end of the month, and potential damage to vendor/client trust.

Security Control (Preventive): Multi-Region Database Replication with Automated Failover.

Explanation: To meet the strict 12-hour RTO and 1-hour RPO, cross-region replication ensures that if the primary payment gateway or database goes down, the system can failover to a secondary region with near-zero data loss, protecting the billing cycle.

2. CRM & Sales Pipeline (Salesforce)

Business Impact: Inability to close pending deals, loss of client contract data, and halted sales operations during critical End-of-Quarter periods, leading to direct revenue loss.

Security Control (Corrective): Automated Third-Party SaaS Backup (e.g., OwnBackup).

Explanation: Relying solely on Salesforce's native recycle bin is risky. A dedicated SaaS backup ensures that even if mass data corruption occurs, the 4-hour RPO and 24-hour RTO can be easily met by restoring a clean, isolated snapshot of the sales pipeline.

3. Data Warehouse & Analytics (BigQuery)

Business Impact: Campaign managers lose real-time optimization insights. Ads will still serve, but performance tuning halts, potentially degrading ROI for advertisers over time.

Security Control (Corrective): Infrastructure as Code (IaC) Recovery Scripts.

Explanation: Since this process has no time-critical constraints and a generous 48-hour MAO, the most cost-effective control is having tested IaC scripts (e.g., Terraform). If the data warehouse gets corrupted, engineers can quickly spin up a fresh instance and re-ingest raw data within the 24-hour RTO.

4. Internal Communications (Slack / Email)

Business Impact: Total paralysis of company-wide coordination, preventing IT and GRC teams from communicating during an incident recovery.

Security Control (Preventive): Out-of-Band (OOB) Emergency Communication Channel.

Explanation: Since Slack/Email is a SaaS dependency, Teads cannot completely control its uptime. Establishing a pre-approved, encrypted OOB channel (like an enterprise WhatsApp group or Signal) mitigates the 48-hour RTO by ensuring business continuity and incident response coordination can happen immediately, even if the main system is down.

⚖️ **AI Agreement / Disagreement**
I partially agree with the AI's assessment. I agree that CRM should outrank Billing, as permanently losing new deals is more damaging than a temporary delay in cash flow. However, I strongly disagree with elevating Internal Communications to Priority 1. In today's hyper-connected era, IT and GRC teams can easily coordinate using out-of-band alternatives (like WhatsApp or personal phones) to bridge the gap during the RTO window. Therefore, core revenue-generating systems must remain the absolute top priority, keeping Internal Comms at Priority 4.
