# bia-mini-tool

Goal: Simple tool that processes BIA data and provides basic prioritization

My Approach - Prioritization Logic & Algorithm:
The prioritization engine calculates the recovery order to minimize financial, reputational, and operational damage. The baseline Priority (High/Medium/Low) is primarily driven by the Process Status.
To handle edge cases where multiple systems share the same Priority level, the script applies a sequential tie-breaking algorithm:

RTO (Ascending): Systems with the shortest target recovery time are prioritized first to halt escalating damages.

MAO (Ascending): If RTO is identical, the system with the shortest Maximum Acceptable Outage takes precedence, as it sits closer to the threshold of irreversible business failure.

RPO (Ascending): Data loss (RPO) is evaluated next. While crucial, in an Ad-Tech environment, immediate availability (downtime) often poses a more immediate existential threat than minimal historical data loss.

Time-Critical Flag: Finally, processes containing any documented Time-Critical constraints receive a boolean weight boost, acknowledging their potential volatility during specific business cycles.
