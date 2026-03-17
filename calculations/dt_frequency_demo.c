/*
 * Delta t (dt) and Update Frequency Demonstration
 * Shows the relationship between update rate and dt
 */

#include <stdio.h>

int main() {
    printf("╔════════════════════════════════════════════════════════╗\n");
    printf("║   DELTA t (dt) AND UPDATE FREQUENCY RELATIONSHIP      ║\n");
    printf("╚════════════════════════════════════════════════════════╝\n\n");
    
    printf("FORMULA: dt = 1 / update_frequency\n\n");
    
    printf("═══════════════════════════════════════════════════════\n");
    printf("UPDATE FREQUENCY TABLE\n");
    printf("═══════════════════════════════════════════════════════\n\n");
    
    printf("┌──────────────┬──────────────┬─────────────────────────┐\n");
    printf("│ Update Rate  │   Delta t    │  Meaning                │\n");
    printf("├──────────────┼──────────────┼─────────────────────────┤\n");
    printf("│   10 Hz      │  0.1000 s    │  10 updates/second      │\n");
    printf("│   50 Hz      │  0.0200 s    │  50 updates/second      │\n");
    printf("│  100 Hz      │  0.0100 s    │ 100 updates/second ✓    │\n");
    printf("│  200 Hz      │  0.0050 s    │ 200 updates/second      │\n");
    printf("│  500 Hz      │  0.0020 s    │ 500 updates/second      │\n");
    printf("│ 1000 Hz      │  0.0010 s    │ 1000 updates/second     │\n");
    printf("└──────────────┴──────────────┴─────────────────────────┘\n\n");
    
    printf("═══════════════════════════════════════════════════════\n");
    printf("EXAMPLE: VEHICLE AT 20 m/s (72 km/h)\n");
    printf("═══════════════════════════════════════════════════════\n\n");
    
    double velocity = 20.0;  // m/s
    
    printf("Velocity: %.1f m/s\n\n", velocity);
    
    printf("┌──────────────┬──────────────┬──────────────────┬──────────────────┐\n");
    printf("│ Update Rate  │   Delta t    │  Distance/Update │  Distance/Second │\n");
    printf("├──────────────┼──────────────┼──────────────────┼──────────────────┤\n");
    
    double frequencies[] = {10, 50, 100, 200, 500, 1000};
    int num_freq = 6;
    
    for (int i = 0; i < num_freq; i++) {
        double freq = frequencies[i];
        double dt = 1.0 / freq;
        double dist_per_update = velocity * dt;
        double dist_per_second = velocity * 1.0;
        
        printf("│ %4.0f Hz      │  %.4f s    │    %.4f m      │     %.1f m        │\n",
               freq, dt, dist_per_update, dist_per_second);
    }
    
    printf("└──────────────┴──────────────┴──────────────────┴──────────────────┘\n\n");
    
    printf("NOTICE: Distance per second is ALWAYS 20m (velocity × 1s)\n");
    printf("        But it's calculated differently:\n");
    printf("        - 100 Hz: 100 updates × 0.2m = 20m\n");
    printf("        - 1000 Hz: 1000 updates × 0.02m = 20m\n\n");
    
    printf("═══════════════════════════════════════════════════════\n");
    printf("INTERACTIVE CALCULATOR\n");
    printf("═══════════════════════════════════════════════════════\n\n");
    
    double user_freq, user_velocity;
    
    printf("Enter update frequency (Hz): ");
    scanf("%lf", &user_freq);
    
    printf("Enter velocity (m/s): ");
    scanf("%lf", &user_velocity);
    
    double user_dt = 1.0 / user_freq;
    double user_dist_per_update = user_velocity * user_dt;
    double user_dist_per_second = user_velocity * 1.0;
    
    printf("\n--- RESULTS ---\n");
    printf("Update frequency: %.0f Hz\n", user_freq);
    printf("Delta t (dt): %.6f seconds\n", user_dt);
    printf("Velocity: %.2f m/s\n", user_velocity);
    printf("\nPer Update:\n");
    printf("  Distance = velocity × dt\n");
    printf("           = %.2f × %.6f\n", user_velocity, user_dt);
    printf("           = %.6f meters\n", user_dist_per_update);
    printf("\nPer Second:\n");
    printf("  Total distance = velocity × 1 second\n");
    printf("                 = %.2f × 1\n", user_velocity);
    printf("                 = %.2f meters\n", user_dist_per_second);
    printf("\nVerification:\n");
    printf("  %.0f updates × %.6f m/update = %.2f m ✓\n",
           user_freq, user_dist_per_update, user_freq * user_dist_per_update);
    
    printf("\n═══════════════════════════════════════════════════════\n");
    printf("KEY TAKEAWAYS\n");
    printf("═══════════════════════════════════════════════════════\n\n");
    
    printf("1. dt = 1 / update_frequency\n");
    printf("   Example: 100 Hz → dt = 1/100 = 0.01 seconds\n\n");
    
    printf("2. Distance per update = velocity × dt\n");
    printf("   Example: 20 m/s × 0.01s = 0.2 meters\n\n");
    
    printf("3. Total distance = velocity × total_time\n");
    printf("   Example: 20 m/s × 1s = 20 meters\n\n");
    
    printf("4. Higher frequency = smaller dt = more updates\n");
    printf("   100 Hz: 100 updates/second, 0.2m each\n");
    printf("   1000 Hz: 1000 updates/second, 0.02m each\n");
    printf("   Both travel 20m in 1 second!\n\n");
    
    printf("5. For go-kart: 100 Hz is perfect\n");
    printf("   - 20-30cm accuracy at racing speed\n");
    printf("   - Low CPU usage\n");
    printf("   - Matches sensor resolution\n\n");
    
    printf("╔════════════════════════════════════════════════════════╗\n");
    printf("║                    PROGRAM COMPLETE                    ║\n");
    printf("╚════════════════════════════════════════════════════════╝\n");
    
    return 0;
}
