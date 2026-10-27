import os
import sys

def generate_main_nr(
    output_path=None,
    num_past_jobs=5,
    min_rating_scale=100
):
    """
    Generates the Noir circuit (main.nr) for privacy-preserving freelance eligibility verification.
    
    Parameters:
      - output_path: Destination path for main.nr (default: circuit/src/main.nr)
      - num_past_jobs: Number of past job ratings/records in the private array (demonstrating configurable array size)
      - min_rating_scale: Multiplier for rating decimals (e.g. 100 for 4.85 -> 485)
    """
    if output_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(base_dir, "circuit", "src", "main.nr")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    code = f"""// Auto-generated Noir Eligibility Circuit
// Configured with num_past_jobs = {num_past_jobs}, scale = {min_rating_scale}

fn main(
    // -------------------------------------------------------------
    // PRIVATE INPUTS (Freelancer Reputation Profile - Kept Secret)
    // -------------------------------------------------------------
    freelancer_rating_scaled: u32,
    freelancer_completed_jobs: u32,
    freelancer_on_time_rate: u32,
    freelancer_disputes: u32,
    
    // Array of recent job ratings (demonstrates array handling in Noir)
    recent_job_ratings: [u32; {num_past_jobs}],

    // -------------------------------------------------------------
    // PUBLIC INPUTS (Client Job Criteria - Public on Marketplace)
    // -------------------------------------------------------------
    min_rating_scaled: pub u32,
    min_completed_jobs: pub u32,
    min_on_time_rate: pub u32,
    max_disputes: pub u32
) {{
    // 1. Minimum rating constraint
    assert(freelancer_rating_scaled >= min_rating_scaled);

    // 2. Completed jobs volume constraint
    assert(freelancer_completed_jobs >= min_completed_jobs);

    // 3. On-time delivery rate constraint (in %)
    assert(freelancer_on_time_rate >= min_on_time_rate);

    // 4. Maximum allowable disputes constraint
    assert(freelancer_disputes <= max_disputes);

    // 5. Consistency check over recent job ratings array
    let mut ratings_sum: u32 = 0;
    for i in 0..{num_past_jobs} {{
        assert(recent_job_ratings[i] <= 500); // Ratings within 0.00 to 5.00
        ratings_sum += recent_job_ratings[i];
    }}
    // Verification that average of recent jobs is non-trivial (> 0)
    assert(ratings_sum > 0);
}}

#[test]
fn test_eligible_freelancer() {{
    let recent = [480, 490, 500, 495, 485];
    main(
        490,  // rating: 4.90
        120,  // completed jobs: 120
        99,   // on-time: 99%
        0,    // disputes: 0
        recent,
        480,  // min_rating: 4.80
        25,   // min_completed: 25
        95,   // min_on_time: 95%
        1     // max_disputes: 1
    );
}}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(code)

    return output_path

if __name__ == "__main__":
    out = generate_main_nr()
    print(f"Noir circuit successfully generated at: {out}")
