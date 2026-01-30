from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import statistics
import math

app = FastAPI()

# Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

def p95(values):
    values = sorted(values)
    index = math.ceil(0.95 * len(values)) - 1
    return values[index]

@app.post("/")
def analyze(data: AnalyticsRequest):
    with open("q-vercel-latency.json") as f:
        records = json.load(f)

    result = {}

    for region in data.regions:
        region_data = [r for r in records if r["region"] == region]

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime"] for r in region_data]

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": p95(latencies),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(1 for l in latencies if l > data.threshold_ms)
        }

    return result
