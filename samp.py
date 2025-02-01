import pandas as pd
from datetime import datetime

# -------------------------------
# Define our firefighting resources
# -------------------------------
# Each resource type is defined by its name, deployment time (in minutes),
# operational cost per deployment, and total units available.
resource_specs = {
    "Smoke Jumpers": {"deployment_minutes": 30, "operational_cost": 5000, "count": 5},
    "Fire Engines": {"deployment_minutes": 60, "operational_cost": 2000, "count": 10},
    "Helicopters": {"deployment_minutes": 45, "operational_cost": 8000, "count": 3},
    "Tanker Planes": {"deployment_minutes": 120, "operational_cost": 15000, "count": 2},
    "Ground Crews": {"deployment_minutes": 90, "operational_cost": 3000, "count": 8}
}

# Damage costs for missed responses (if no resource is available)
damage_costs = {
    "low": 50000,
    "medium": 100000,
    "high": 200000
}

# -------------------------------
# Create a pool of resource units (non-reusable)
# -------------------------------
# Each unit is represented as a dictionary.
resource_pool = []
for r_type, spec in resource_specs.items():
    for _ in range(spec["count"]):
        resource_pool.append({
            "resource_type": r_type,
            "deployment_minutes": spec["deployment_minutes"],
            "operational_cost": spec["operational_cost"]
        })

# -------------------------------
# Heuristic for selecting a resource for a given event
# -------------------------------
def select_resource(available_resources, severity):
    """
    Given a list of available resource units and the event severity,
    select one unit based on a severity-dependent heuristic.
    
    For high severity: choose the fastest (smallest deployment_minutes) unit.
    For low severity: choose the cheapest unit.
    For medium severity: choose based on a weighted score that combines deployment_minutes
        and operational_cost.
    """
    if severity == "high":
        available_resources.sort(key=lambda r: (r["deployment_minutes"], r["operational_cost"]))
        return available_resources[0]
    elif severity == "low":
        available_resources.sort(key=lambda r: (r["operational_cost"], r["deployment_minutes"]))
        return available_resources[0]
    elif severity == "medium":
        factor = 50  # factor to convert minutes to an equivalent cost
        available_resources.sort(key=lambda r: (r["operational_cost"] + factor * r["deployment_minutes"]))
        return available_resources[0]
    else:
        available_resources.sort(key=lambda r: (r["operational_cost"], r["deployment_minutes"]))
        return available_resources[0]

# -------------------------------
# Simulation of resource deployment (non-reusable units) with logging
# and with an intentional miss policy for the first few low-severity events.
# -------------------------------
def simulate_deployment(df_events, allowed_low_misses=4):
    """
    Given a dataframe of wildfire events (with columns: timestamp, fire_start_time, location, severity),
    simulate resource assignment. Each resource is used only once.
    
    Policy change: For low severity events, intentionally "miss" (i.e. do not assign a resource)
    for the first `allowed_low_misses` occurrences, even if a resource is available.
    
    Returns a summary report and a list of incident logs.
    """
    # Convert timestamp columns to datetime objects
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'])
    df_events['fire_start_time'] = pd.to_datetime(df_events['fire_start_time'])
    
    # Sort events by report time; if same time, then high severity events first.
    severity_order = {"high": 0, "medium": 1, "low": 2}
    df_events.sort_values(
        by=["timestamp", "severity"],
        key=lambda col: col.map(severity_order) if col.name == "severity" else col,
        inplace=True
    )
    
    total_operational_cost = 0
    total_damage_cost = 0
    addressed_count = 0
    missed_count = 0

    # Counters per severity:
    addressed_by_severity = {"low": 0, "medium": 0, "high": 0}
    missed_by_severity = {"low": 0, "medium": 0, "high": 0}
    
    # Policy: keep track of how many low severity events have been intentionally missed.
    low_missed_count = 0
    
    # Create a copy of the resource pool
    available_resources = resource_pool.copy()
    
    # List to log each incident
    incident_logs = []
    
    # Process each event one by one
    for idx, event in df_events.iterrows():
        severity = event['severity'].lower()  # ensure lower-case
        event_time = event['timestamp']
        location = event.get('location', 'Unknown')
        
        log_entry = {
            "event_index": idx,
            "timestamp": event_time,
            "severity": severity,
            "location": location,
            "action": None,  # Will be updated below
            "resource": None,  # The unit assigned (if any)
            "operational_cost": 0
        }
        
        # --- Intentional miss policy for low severity events ---
        if severity == "low" and low_missed_count < allowed_low_misses:
            low_missed_count += 1
            missed_count += 1
            total_damage_cost += damage_costs.get(severity, 0)
            missed_by_severity[severity] += 1
            log_entry["action"] = f"Missed (allowed low miss #{low_missed_count})"
            incident_logs.append(log_entry)
            continue
        
        # Normal processing: assign a resource if available
        if not available_resources:
            # No resource available; mark as missed response
            missed_count += 1
            total_damage_cost += damage_costs.get(severity, 0)
            missed_by_severity[severity] += 1
            log_entry["action"] = "Missed (no resources)"
        else:
            # Select a resource unit using the severity-dependent heuristic
            selected = select_resource(available_resources, severity)
            available_resources.remove(selected)  # Non-reusable: remove from pool
            total_operational_cost += selected["operational_cost"]
            addressed_count += 1
            addressed_by_severity[severity] += 1
            log_entry["action"] = "Assigned"
            log_entry["resource"] = selected["resource_type"]
            log_entry["operational_cost"] = selected["operational_cost"]
        
        incident_logs.append(log_entry)
    
    # Prepare the summary report dictionary
    report = {
        "Number of fires addressed": addressed_count,
        "Number of fires delayed (missed responses)": missed_count,
        "Total operational costs": total_operational_cost,
        "Estimated damage costs from delayed responses": total_damage_cost,
        "Fire severity report": {
            "addressed": addressed_by_severity,
            "missed": missed_by_severity
        }
    }
    
    return report, incident_logs

# -------------------------------
# Function to print incident details
# -------------------------------
def print_incident_report(incident_logs):
    """
    Given a list of incident logs, print details for each event.
    """
    print("\n----- Detailed Incident Report -----")
    for log in incident_logs:
        event_info = (f"Event {log['event_index']} | Time: {log['timestamp']} | "
                      f"Severity: {log['severity'].capitalize()} | Location: {log['location']}")
        if log["action"].startswith("Assigned"):
            unit_info = f"--> Assigned Unit: {log['resource']} (Cost: ${log['operational_cost']})"
        else:
            unit_info = f"--> {log['action']}"
        print(f"{event_info} {unit_info}")

# -------------------------------
# Main execution block
# -------------------------------
if __name__ == "__main__":
    # Read the wildfire data CSV for the current wildfire season (2024)
    # Ensure the CSV file has columns: timestamp, fire_start_time, location, severity.
    try:
        df_wildfire = pd.read_csv("current_wildfiredata.csv")
    except Exception as e:
        print("Error reading the CSV file:", e)
        exit(1)
    
    # Run the simulation with the intentional miss policy for low severity events.
    report, incident_logs = simulate_deployment(df_wildfire, allowed_low_misses=4)
    
    # Display the summary report
    print("----- Wildfire Response Report -----")
    print(f"Number of fires addressed: {report['Number of fires addressed']}")
    print(f"Number of fires delayed (missed responses): {report['Number of fires delayed (missed responses)']}")
    print(f"Total operational costs: ${report['Total operational costs']}")
    print(f"Estimated damage costs from delayed responses: ${report['Estimated damage costs from delayed responses']}")
    print("Fire severity report (addressed vs. missed):")
    for sev in ["low", "medium", "high"]:
        addressed = report['Fire severity report']['addressed'][sev]
        missed = report['Fire severity report']['missed'][sev]
        print(f"  {sev.capitalize()}: Addressed = {addressed}, Missed = {missed}")
    
    # Print detailed incident report
    print_incident_report(incident_logs)
