from typing import List
import csv

WILDFIRE_FILENAME = 'Data/current_wildfiredata.csv'
SEVERITY_COLUMNNAME = 'severity'

damage_cost = {
    'low': 50000,
    'medium': 100000,
    'high': 200000
}

def get_severity_list() -> list[int]:
    """
    Reads data in WILDFIRE_FILENAME returns a list of the severity in the order that occurs
    We are assuming that the list is in chronological order
    
    Returns:
        list: A list containing the damage cost of the fires in current wild fire data
        
    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the column name does not exist in the CSV.
    """
    severity_data = []
    
    with open(WILDFIRE_FILENAME, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        if SEVERITY_COLUMNNAME not in reader.fieldnames:
            raise ValueError(f"Column '{SEVERITY_COLUMNNAME}' not found in the CSV file.")
        
        for row in reader:
            severity_data.append(damage_cost[row[SEVERITY_COLUMNNAME]])
    
    return severity_data

def get_units() -> list[int]:
    units = []
    
    num_smoke_jumper = 5
    # depTime_smoke_jumper = 0.5
    cost_smoke_jumper = 5000
    for _ in num_smoke_jumper:
        units.append(cost_smoke_jumper)

    num_fire_engine = 10
    # depTime_fire_engine = 1
    cost_fire_engine = 2000
    for _ in num_fire_engine:
        units.append(cost_fire_engine)

    num_helicopters = 3
    # depTime_helicopters = 0.75
    cost_helicopters = 8000
    for _ in num_helicopters:
        units.append(cost_helicopters)

    num_tanker_planes = 2
    # depTime_tanker_planes = 2
    cost_tanker_planes = 15000
    for _ in num_tanker_planes:
        units.append(cost_tanker_planes)

    num_ground_crew = 8
    # depTime_ground_crew = 1.5
    cost_ground_crew = 3000
    for _ in num_ground_crew:
        units.append(cost_ground_crew)

    return units

def give_optimal_cost(severity_data: list[int]) -> int:
    total_cost = severity_data




if __name__ == '__main__':
    severity_data = get_severity_list()
    print(severity_data)