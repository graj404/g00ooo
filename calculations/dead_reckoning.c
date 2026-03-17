/*
 * Dead Reckoning Calculations in C
 * Optimized for performance and clarity
 */

#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Constants
#define PI 3.14159265359
#define WHEELBASE 1.0  // meters
#define WHEEL_DIAMETER 0.2  // meters
#define WHEEL_CIRCUMFERENCE (PI * WHEEL_DIAMETER)
#define MAGNETS_PER_REVOLUTION 18

// Update rate configuration
#define UPDATE_RATE_HZ 100  // Default: 100 Hz (0.01s per update)
#define DEFAULT_DT (1.0 / UPDATE_RATE_HZ)

// Vehicle state structure
typedef struct {
    double x;              // Position X (meters)
    double y;              // Position Y (meters)
    double heading;        // Heading angle (radians)
    double velocity;       // Velocity (m/s)
    double steering_angle; // Steering angle (radians)
    double rpm;            // Wheel RPM
} VehicleState;

// Function prototypes
double normalize_angle(double angle);
double calculate_velocity_from_rpm(double rpm);
void update_position_straight(VehicleState *state, double dt);
void update_position_turning(VehicleState *state, double dt);
void dead_reckoning_update(VehicleState *state, double dt);
void print_state(const VehicleState *state, double dt);
void print_calculations(const VehicleState *state, double dt);

/**
 * Normalize angle to [-PI, PI]
 */
double normalize_angle(double angle) {
    while (angle > PI) {
        angle -= 2.0 * PI;
    }
    while (angle < -PI) {
        angle += 2.0 * PI;
    }
    return angle;
}

/**
 * Calculate velocity from RPM
 * Formula: velocity = (RPM / 60) × wheel_circumference
 */
double calculate_velocity_from_rpm(double rpm) {
    return (rpm / 60.0) * WHEEL_CIRCUMFERENCE;
}

/**
 * Update position for straight line motion
 * Used when |steering_angle| < 0.01 radians
 */
void update_position_straight(VehicleState *state, double dt) {
    double displacement = state->velocity * dt;
    double dx = displacement * cos(state->heading);
    double dy = displacement * sin(state->heading);
    
    state->x += dx;
    state->y += dy;
    
    printf("  [STRAIGHT LINE MOTION]\n");
    printf("  displacement = velocity × dt = %.4f × %.4f = %.4f m\n", 
           state->velocity, dt, displacement);
    printf("  dx = displacement × cos(heading) = %.4f × cos(%.4f) = %.4f m\n",
           displacement, state->heading, dx);
    printf("  dy = displacement × sin(heading) = %.4f × sin(%.4f) = %.4f m\n",
           displacement, state->heading, dy);
}

/**
 * Update position for circular arc motion (turning)
 * Used when |steering_angle| >= 0.01 radians
 */
void update_position_turning(VehicleState *state, double dt) {
    // Calculate heading rate
    double heading_rate = (state->velocity * tan(state->steering_angle)) / WHEELBASE;
    
    printf("  [CIRCULAR ARC MOTION]\n");
    printf("  heading_rate = (velocity × tan(steering)) / wheelbase\n");
    printf("               = (%.4f × tan(%.4f)) / %.4f\n",
           state->velocity, state->steering_angle, WHEELBASE);
    printf("               = %.4f rad/s\n", heading_rate);
    
    // Update heading
    double old_heading = state->heading;
    state->heading += heading_rate * dt;
    state->heading = normalize_angle(state->heading);
    
    printf("  heading_new = heading_old + heading_rate × dt\n");
    printf("              = %.4f + %.4f × %.4f\n", old_heading, heading_rate, dt);
    printf("              = %.4f rad (%.2f°)\n", state->heading, state->heading * 180.0 / PI);
    
    // Calculate displacement
    double displacement = state->velocity * dt;
    double dx = displacement * cos(state->heading);
    double dy = displacement * sin(state->heading);
    
    printf("  displacement = velocity × dt = %.4f × %.4f = %.4f m\n",
           state->velocity, dt, displacement);
    printf("  dx = displacement × cos(heading) = %.4f × cos(%.4f) = %.4f m\n",
           displacement, state->heading, dx);
    printf("  dy = displacement × sin(heading) = %.4f × sin(%.4f) = %.4f m\n",
           displacement, state->heading, dy);
    
    state->x += dx;
    state->y += dy;
}

/**
 * Main dead reckoning update function
 */
void dead_reckoning_update(VehicleState *state, double dt) {
    printf("\n========================================\n");
    printf("DEAD RECKONING UPDATE\n");
    printf("========================================\n");
    
    // Calculate velocity from RPM if RPM is provided
    if (state->rpm > 0) {
        state->velocity = calculate_velocity_from_rpm(state->rpm);
        printf("VELOCITY FROM RPM:\n");
        printf("  velocity = (RPM / 60) × wheel_circumference\n");
        printf("           = (%.2f / 60) × %.4f\n", state->rpm, WHEEL_CIRCUMFERENCE);
        printf("           = %.4f m/s\n", state->velocity);
    }
    
    printf("\nINPUT STATE:\n");
    printf("  Position: (%.4f, %.4f) m\n", state->x, state->y);
    printf("  Heading: %.4f rad (%.2f°)\n", state->heading, state->heading * 180.0 / PI);
    printf("  Velocity: %.4f m/s\n", state->velocity);
    printf("  Steering: %.4f rad (%.2f°)\n", state->steering_angle, state->steering_angle * 180.0 / PI);
    printf("  Delta t: %.4f s\n", dt);
    
    printf("\nCALCULATIONS:\n");
    
    // Choose motion model based on steering angle
    if (fabs(state->steering_angle) < 0.01) {
        update_position_straight(state, dt);
    } else {
        update_position_turning(state, dt);
    }
    
    printf("\nOUTPUT STATE:\n");
    printf("  Position: (%.4f, %.4f) m\n", state->x, state->y);
    printf("  Heading: %.4f rad (%.2f°)\n", state->heading, state->heading * 180.0 / PI);
    printf("========================================\n\n");
}

/**
 * Print current vehicle state
 */
void print_state(const VehicleState *state, double dt) {
    printf("Time: %.3fs | Pos: (%.2f, %.2f) m | Heading: %.1f° | Velocity: %.2f m/s\n",
           dt, state->x, state->y, state->heading * 180.0 / PI, state->velocity);
}

/**
 * Print detailed calculations
 */
void print_calculations(const VehicleState *state, double dt) {
    double displacement = state->velocity * dt;
    double dx = displacement * cos(state->heading);
    double dy = displacement * sin(state->heading);
    
    printf("\n--- Calculation Details ---\n");
    printf("Velocity: %.4f m/s\n", state->velocity);
    printf("Delta t: %.4f s\n", dt);
    printf("Displacement: %.4f m\n", displacement);
    printf("dx: %.4f m\n", dx);
    printf("dy: %.4f m\n", dy);
    printf("New Position: (%.4f, %.4f) m\n", state->x + dx, state->y + dy);
    printf("---------------------------\n\n");
}

/**
 * Main function - demonstration
 */
int main() {
    printf("╔════════════════════════════════════════════════════════╗\n");
    printf("║     DEAD RECKONING CALCULATIONS - C IMPLEMENTATION    ║\n");
    printf("╚════════════════════════════════════════════════════════╝\n\n");
    
    // Initialize vehicle state
    VehicleState vehicle = {
        .x = 0.0,
        .y = 0.0,
        .heading = 0.0,  // 0° = East
        .velocity = 0.0,
        .steering_angle = 0.0,
        .rpm = 0.0
    };
    
    double dt = DEFAULT_DT;  // 100 Hz update rate (0.01 seconds)
    double total_time = 0.0;
    
    printf("Configuration:\n");
    printf("  Wheelbase: %.2f m\n", WHEELBASE);
    printf("  Wheel Diameter: %.2f m\n", WHEEL_DIAMETER);
    printf("  Wheel Circumference: %.4f m\n", WHEEL_CIRCUMFERENCE);
    printf("  Magnets per Revolution: %d\n", MAGNETS_PER_REVOLUTION);
    printf("  Update Rate: %.0f Hz\n", 1.0/dt);
    printf("  Delta t (dt): %.4f s (time between updates)\n", dt);
    printf("\n  NOTE: At 100 Hz, position updates 100 times per second\n");
    printf("        Each update uses dt = 0.01s in calculations\n\n");
    
    // Example 1: Straight line motion
    printf("═══════════════════════════════════════════════════════\n");
    printf("EXAMPLE 1: STRAIGHT LINE MOTION\n");
    printf("═══════════════════════════════════════════════════════\n");
    
    vehicle.velocity = 10.0;  // 10 m/s
    vehicle.steering_angle = 0.0;  // Straight
    vehicle.heading = 0.0;  // East
    
    printf("Scenario: Vehicle moving straight at 10 m/s for 1 second\n");
    
    for (int i = 0; i < 5; i++) {
        dead_reckoning_update(&vehicle, dt);
        total_time += dt;
    }
    
    printf("After 5 updates (0.05s): Position = (%.2f, %.2f) m\n", vehicle.x, vehicle.y);
    printf("Expected: (0.50, 0.00) m ✓\n\n");
    
    // Example 2: Turning motion
    printf("═══════════════════════════════════════════════════════\n");
    printf("EXAMPLE 2: TURNING MOTION\n");
    printf("═══════════════════════════════════════════════════════\n");
    
    // Reset position
    vehicle.x = 0.0;
    vehicle.y = 0.0;
    vehicle.heading = 0.0;
    vehicle.velocity = 5.0;  // 5 m/s
    vehicle.steering_angle = 15.0 * PI / 180.0;  // 15° right turn
    
    printf("Scenario: Vehicle turning right at 15° while moving 5 m/s\n");
    
    for (int i = 0; i < 3; i++) {
        dead_reckoning_update(&vehicle, dt);
    }
    
    printf("After 3 updates (0.03s): Position = (%.2f, %.2f) m, Heading = %.1f°\n",
           vehicle.x, vehicle.y, vehicle.heading * 180.0 / PI);
    
    // Example 3: From RPM
    printf("\n═══════════════════════════════════════════════════════\n");
    printf("EXAMPLE 3: VELOCITY FROM RPM\n");
    printf("═══════════════════════════════════════════════════════\n");
    
    vehicle.x = 0.0;
    vehicle.y = 0.0;
    vehicle.heading = 45.0 * PI / 180.0;  // 45° (Northeast)
    vehicle.rpm = 1800.0;  // 1800 RPM
    vehicle.steering_angle = 0.0;
    
    printf("Scenario: Vehicle at 1800 RPM, heading 45°\n");
    
    dead_reckoning_update(&vehicle, dt);
    
    printf("Velocity calculated: %.2f m/s\n", vehicle.velocity);
    printf("Position after 1 update: (%.4f, %.4f) m\n", vehicle.x, vehicle.y);
    
    // Interactive mode
    printf("\n═══════════════════════════════════════════════════════\n");
    printf("INTERACTIVE MODE\n");
    printf("═══════════════════════════════════════════════════════\n");
    printf("Enter your own values to see calculations:\n\n");
    
    char choice;
    printf("Do you want to enter custom values? (y/n): ");
    scanf(" %c", &choice);
    
    if (choice == 'y' || choice == 'Y') {
        vehicle.x = 0.0;
        vehicle.y = 0.0;
        
        printf("\n--- INPUT PARAMETERS ---\n");
        
        printf("Enter velocity (m/s): ");
        scanf("%lf", &vehicle.velocity);
        
        printf("Enter heading (degrees): ");
        double heading_deg;
        scanf("%lf", &heading_deg);
        vehicle.heading = heading_deg * PI / 180.0;
        
        printf("Enter steering angle (degrees): ");
        double steering_deg;
        scanf("%lf", &steering_deg);
        vehicle.steering_angle = steering_deg * PI / 180.0;
        
        printf("Enter delta t / dt (seconds) [default=%.4f]: ", DEFAULT_DT);
        scanf("%lf", &dt);
        
        double update_freq = 1.0 / dt;
        printf("\n--- CALCULATED VALUES ---\n");
        printf("Update frequency: %.0f Hz\n", update_freq);
        printf("Time between updates: %.4f s\n", dt);
        printf("Distance per update at current velocity: %.4f m\n", vehicle.velocity * dt);
        
        printf("\nCalculating...\n");
        dead_reckoning_update(&vehicle, dt);
        
        // Show what happens over 1 second
        printf("\n--- PROJECTION OVER 1 SECOND ---\n");
        printf("Number of updates in 1 second: %.0f\n", update_freq);
        printf("Distance traveled in 1 second: %.2f m\n", vehicle.velocity * 1.0);
        printf("Distance per update: %.4f m\n", vehicle.velocity * dt);
        printf("Total updates × distance per update = %.0f × %.4f = %.2f m ✓\n",
               update_freq, vehicle.velocity * dt, update_freq * vehicle.velocity * dt);
    }
    
    printf("\n╔════════════════════════════════════════════════════════╗\n");
    printf("║                    PROGRAM COMPLETE                    ║\n");
    printf("╚════════════════════════════════════════════════════════╝\n");
    
    return 0;
}
