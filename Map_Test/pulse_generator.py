#!/usr/bin/env python3
"""
Hardware Pulse Generator for Testing
Uses Raspberry Pi GPIO to generate pulses that simulate hall effect sensor

Hardware Setup:
- Output pin (e.g., GPIO 27) generates pulses
- Input pin (e.g., GPIO 17) receives pulses
- Connect GPIO 27 → GPIO 17 with a wire

This tests the ACTUAL hardware interrupt system!
"""

import time
import threading
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("RPi.GPIO not available - simulation mode")

# Configuration
PULSE_OUTPUT_PIN = 27  # GPIO pin that generates pulses
PULSE_INPUT_PIN = 17   # GPIO pin that receives pulses (hall sensor pin)
MAGNETS_PER_REVOLUTION = 18

class PulseGenerator:
    """
    Generates hardware pulses to simulate hall effect sensor
    Uses actual GPIO hardware - tests real interrupt system!
    """
    
    def __init__(self, output_pin=PULSE_OUTPUT_PIN):
        self.output_pin = output_pin
        self.running = False
        self.thread = None
        
        # Simulation parameters
        self.rpm = 0.0
        self.target_rpm = 0.0
        self.acceleration = 500.0  # RPM/s
        
        if RPI_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.output_pin, GPIO.OUT)
            GPIO.output(self.output_pin, GPIO.HIGH)  # Start high
            print(f"Pulse generator initialized on GPIO {self.output_pin}")
            print(f"Connect GPIO {self.output_pin} → GPIO {PULSE_INPUT_PIN} with a wire")
        else:
            print("Pulse generator in simulation mode (no hardware)")
    
    def set_rpm(self, rpm):
        """Set target RPM (will accelerate/decelerate smoothly)"""
        self.target_rpm = max(0, min(rpm, 10000))  # Limit 0-10000 RPM
        print(f"Target RPM set to: {self.target_rpm:.0f}")
    
    def set_velocity(self, velocity_ms, wheel_circumference=0.628):
        """Set target velocity in m/s (converts to RPM)"""
        rpm = (velocity_ms / wheel_circumference) * 60.0
        self.set_rpm(rpm)
    
    def _generate_pulses(self):
        """
        Background thread that generates pulses
        Simulates realistic acceleration/deceleration
        """
        last_time = time.perf_counter()
        
        while self.running:
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time
            
            # Smooth acceleration/deceleration
            if self.rpm < self.target_rpm:
                self.rpm = min(self.rpm + self.acceleration * dt, self.target_rpm)
            elif self.rpm > self.target_rpm:
                self.rpm = max(self.rpm - self.acceleration * dt, self.target_rpm)
            
            if self.rpm < 1.0:
                # Stopped - no pulses
                time.sleep(0.1)
                continue
            
            # Calculate pulse interval
            # pulses_per_second = (RPM / 60) * magnets_per_rev
            pulses_per_second = (self.rpm / 60.0) * MAGNETS_PER_REVOLUTION
            pulse_interval = 1.0 / pulses_per_second if pulses_per_second > 0 else 1.0
            
            # Generate pulse (falling edge)
            if RPI_AVAILABLE:
                GPIO.output(self.output_pin, GPIO.LOW)
                time.sleep(0.0001)  # 0.1ms pulse width
                GPIO.output(self.output_pin, GPIO.HIGH)
            
            # Wait for next pulse
            time.sleep(pulse_interval - 0.0001)
    
    def start(self):
        """Start generating pulses"""
        if self.running:
            print("Pulse generator already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._generate_pulses, daemon=True)
        self.thread.start()
        print("Pulse generator started")
    
    def stop(self):
        """Stop generating pulses"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("Pulse generator stopped")
    
    def cleanup(self):
        """Clean up GPIO"""
        self.stop()
        if RPI_AVAILABLE:
            GPIO.cleanup(self.output_pin)


def interactive_test():
    """Interactive test mode"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║         HARDWARE PULSE GENERATOR - TEST MODE          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("This generates REAL hardware pulses on Raspberry Pi GPIO")
    print()
    print("Hardware Setup:")
    print(f"  1. Connect GPIO {PULSE_OUTPUT_PIN} → GPIO {PULSE_INPUT_PIN} with a wire")
    print("  2. Run your dead reckoning system in another terminal")
    print("  3. Control speed from this terminal")
    print()
    
    if not RPI_AVAILABLE:
        print("ERROR: RPi.GPIO not available!")
        print("This must run on a Raspberry Pi")
        return
    
    generator = PulseGenerator()
    generator.start()
    
    print("\nCommands:")
    print("  rpm <value>     - Set RPM (e.g., 'rpm 1800')")
    print("  vel <value>     - Set velocity in m/s (e.g., 'vel 20')")
    print("  stop            - Stop (RPM = 0)")
    print("  quit            - Exit")
    print()
    
    try:
        while True:
            cmd = input(f"[Current: {generator.rpm:.0f} RPM] > ").strip().lower()
            
            if cmd.startswith('rpm '):
                try:
                    rpm = float(cmd.split()[1])
                    generator.set_rpm(rpm)
                except (ValueError, IndexError):
                    print("Usage: rpm <value>")
            
            elif cmd.startswith('vel '):
                try:
                    vel = float(cmd.split()[1])
                    generator.set_velocity(vel)
                    print(f"Velocity: {vel:.1f} m/s")
                except (ValueError, IndexError):
                    print("Usage: vel <value>")
            
            elif cmd == 'stop':
                generator.set_rpm(0)
            
            elif cmd == 'quit':
                break
            
            else:
                print("Unknown command. Try: rpm, vel, stop, quit")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    finally:
        generator.cleanup()
        print("Pulse generator stopped")


def scenario_test():
    """Run predefined test scenarios"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║         HARDWARE PULSE GENERATOR - SCENARIOS          ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    if not RPI_AVAILABLE:
        print("ERROR: RPi.GPIO not available!")
        return
    
    generator = PulseGenerator()
    generator.start()
    
    scenarios = [
        ("Idle", 0, 2),
        ("Slow acceleration", 10, 3),
        ("Cruising", 20, 5),
        ("Fast acceleration", 30, 3),
        ("Racing speed", 40, 5),
        ("Deceleration", 20, 3),
        ("Braking", 5, 2),
        ("Stop", 0, 2),
    ]
    
    print("Running test scenarios...")
    print(f"Connect GPIO {PULSE_OUTPUT_PIN} → GPIO {PULSE_INPUT_PIN}")
    print()
    
    try:
        for name, velocity_ms, duration in scenarios:
            print(f"Scenario: {name} ({velocity_ms} m/s) for {duration}s")
            generator.set_velocity(velocity_ms)
            time.sleep(duration)
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    finally:
        generator.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'scenario':
        scenario_test()
    else:
        interactive_test()
