import os
import sys
import sqlite3
from database import get_db_connection

def generate_prover_toml(
    freelancer_id: int,
    job_id: int,
    output_path: str = None,
    num_past_jobs: int = 5,
    rating_scale: int = 100
) -> dict:
    """
    Fetches applicant freelancer (Person A) and target job (Job B) data from the DB,
    and formats them into Prover.toml inputs according to the circuit requirements:
      - Private data: freelancer reputation metrics & recent ratings array
      - Public data: job requirements/thresholds
    """
    conn = get_db_connection()
    freelancer = conn.execute("SELECT * FROM users WHERE id = ?", (freelancer_id,)).fetchone()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()

    if not freelancer:
        raise ValueError(f"Freelancer with ID {freelancer_id} not found in database.")
    if not job:
        raise ValueError(f"Job with ID {job_id} not found in database.")

    # 1. Scale private ratings (e.g. 4.9 -> 490)
    rating_scaled = int(round(freelancer["rating_score"] * rating_scale))
    completed_jobs = int(freelancer["completed_jobs"])
    on_time_rate = int(freelancer["on_time_rate"])
    disputes = int(freelancer["dispute_count"])

    # Synthesize representative past job ratings array based on freelancer's rating
    # E.g., slight variation around rating_scaled
    recent_ratings = []
    base_val = rating_scaled
    variations = [0, 5, -5, 10, -10]
    for i in range(num_past_jobs):
        var = variations[i % len(variations)]
        val = max(100, min(500, base_val + var))
        recent_ratings.append(val)

    # 2. Public job thresholds
    min_rating_scaled = int(round(job["min_rating"] * rating_scale))
    min_completed_jobs = int(job["min_completed_jobs"])
    min_on_time_rate = int(job["min_on_time_rate"])
    max_disputes = int(job["max_disputes"])

    # 3. Format TOML content
    # In Noir TOML, arrays are formatted as [val1, val2, ...]
    recent_ratings_str = "[" + ", ".join(f'"{r}"' for r in recent_ratings) + "]"

    toml_content = f"""# Prover.toml - Input values for Noir Eligibility Circuit
# Generated for Freelancer: {freelancer['username']} (ID: {freelancer_id}) -> Job: {job['title']} (ID: {job_id})

# -----------------------------------------------------------------
# PRIVATE INPUTS (Applicant A Credentials - Kept secret by Prover)
# -----------------------------------------------------------------
freelancer_rating_scaled = "{rating_scaled}"
freelancer_completed_jobs = "{completed_jobs}"
freelancer_on_time_rate = "{on_time_rate}"
freelancer_disputes = "{disputes}"
recent_job_ratings = {recent_ratings_str}

# -----------------------------------------------------------------
# PUBLIC INPUTS (Job B Criteria - Disclosed publicly)
# -----------------------------------------------------------------
min_rating_scaled = "{min_rating_scaled}"
min_completed_jobs = "{min_completed_jobs}"
min_on_time_rate = "{min_on_time_rate}"
max_disputes = "{max_disputes}"
"""

    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "circuit", "Prover.toml")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(toml_content)

    return {
        "output_path": output_path,
        "freelancer_username": freelancer["username"],
        "job_title": job["title"],
        "private_inputs": {
            "freelancer_rating_scaled": rating_scaled,
            "freelancer_completed_jobs": completed_jobs,
            "freelancer_on_time_rate": on_time_rate,
            "freelancer_disputes": disputes,
            "recent_job_ratings": recent_ratings
        },
        "public_inputs": {
            "min_rating_scaled": min_rating_scaled,
            "min_completed_jobs": min_completed_jobs,
            "min_on_time_rate": min_on_time_rate,
            "max_disputes": max_disputes
        }
    }

if __name__ == "__main__":
    f_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3 # alex_dev
    j_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1 # Job 1
    res = generate_prover_toml(f_id, j_id)
    print(f"Generated Prover.toml for {res['freelancer_username']} applying to job '{res['job_title']}':")
    print(f"Location: {res['output_path']}")
