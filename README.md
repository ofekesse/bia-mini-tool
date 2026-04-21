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

💡 **AI Output**

⚖️ **AI Agreement / Disagreement**
