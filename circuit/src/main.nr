// Auto-generated Noir Eligibility Circuit
// Configured with num_past_jobs = 5, scale = 100

fn main(
    // -------------------------------------------------------------
    // PRIVATE INPUTS (Freelancer Reputation Profile - Kept Secret)
    // -------------------------------------------------------------
    freelancer_rating_scaled: u32,
    freelancer_completed_jobs: u32,
    freelancer_on_time_rate: u32,
    freelancer_disputes: u32,
    
    // Array of recent job ratings (demonstrates array handling in Noir)
    recent_job_ratings: [u32; 5],

    // -------------------------------------------------------------
    // PUBLIC INPUTS (Client Job Criteria - Public on Marketplace)
    // -------------------------------------------------------------
    min_rating_scaled: pub u32,
    min_completed_jobs: pub u32,
    min_on_time_rate: pub u32,
    max_disputes: pub u32
) {
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
    for i in 0..5 {
        assert(recent_job_ratings[i] <= 500); // Ratings within 0.00 to 5.00
        ratings_sum += recent_job_ratings[i];
    }
    // Verification that average of recent jobs is non-trivial (> 0)
    assert(ratings_sum > 0);
}

#[test]
fn test_eligible_freelancer() {
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
}
