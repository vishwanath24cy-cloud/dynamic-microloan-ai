import urllib.request
import json
import time
import subprocess
import sys


def run():
    print("Launching live uvicorn server on port 8000...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd="C:/Users/vishw/.gemini/antigravity/scratch/dynamic-microloan-ai/backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        time.sleep(2)

        # 1. Health check
        res_h = urllib.request.urlopen("http://127.0.0.1:8000/health")
        health_json = json.loads(res_h.read().decode("utf-8"))
        print("LIVE HEALTH:", health_json)
        assert health_json["status"] == "healthy"
        assert health_json["database"] == "connected"

        # 2. List borrowers
        res_b = urllib.request.urlopen("http://127.0.0.1:8000/api/borrowers")
        borrowers = json.loads(res_b.read().decode("utf-8"))
        print(f"LIVE BORROWERS COUNT: {len(borrowers)}")
        assert len(borrowers) == 5

        # 3. Specific borrower detail
        res_c = urllib.request.urlopen("http://127.0.0.1:8000/api/borrowers/3")
        borrower_c = json.loads(res_c.read().decode("utf-8"))
        rec_c = borrower_c["recommendations"][0]
        print(f"BORROWER C: {borrower_c['name']} | Stress: {rec_c['stress_level']} | Persistent: {rec_c['persistent_stress']}")
        assert rec_c["stress_level"] == "HIGH"
        assert rec_c["persistent_stress"] is True

        # 4. Summary
        res_s = urllib.request.urlopen("http://127.0.0.1:8000/api/dashboard/summary")
        summary = json.loads(res_s.read().decode("utf-8"))
        print("PORTFOLIO SUMMARY:", summary)
        assert summary["total_borrowers"] == 5

        print("\nALL LIVE SERVER TESTS PASSED PERFECTLY!")
    finally:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    run()
