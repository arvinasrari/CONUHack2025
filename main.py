# main.py
from fastapi import FastAPI, File, UploadFile
import uvicorn
import pandas as pd
import os

# Import your simulation function from samp.py
import samp

app = FastAPI(title="Wildfire Simulation API")

@app.get("/")
def read_root():
    return {"message": "Wildfire Simulation API is running!"}

@app.post("/simulate/")
async def simulate(file: UploadFile = File(...)):
    """
    Upload a CSV file (for example, current wildfire data) and run the simulation.
    The CSV file will be saved temporarily as 'current_wildfiredata.csv' (you can change this as needed).
    Then, the simulation code in samp.py is executed.
    """
    # Save the uploaded file to a temporary location
    file_location = "current_wildfiredata.csv"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Run the simulation using your code from samp.py
    try:
        report, logs = samp.run_simulation(input_csv_path=file_location)
    except Exception as e:
        return {"error": str(e)}
    
    # Optionally, remove the temporary file if you don't need it anymore:
    if os.path.exists(file_location):
        os.remove(file_location)
    
    return {"message": "Simulation completed successfully", "report": report, "logs": logs}

# An endpoint to simply get the latest simulation report, if you store it globally
# (For simplicity, we only demonstrate the /simulate/ endpoint in this example.)

if __name__ == "__main__":
    # Run the server on port 8000 and listen on all interfaces (so it can be reached from your iPhone)
    uvicorn.run(app, host="0.0.0.0", port=8000)
