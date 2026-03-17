#!/usr/bin/env python3
"""
Test Hardware Interrupts on Raspberry Pi
Verifies that GPIO interrupts work correctly
"""

import time
import threading
from collections import deque

try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("RPi.GPIO not available")
    exit(1)

# Configuration
INPUT_PIN = 17  # Hall sensor input pin
OUTPUT_PIN = 27  # Pulse generator output pin

# Statistics
pulse_times = deque(maxlen=100)
lock = threading.Lock()
pulse_count = 0

def pulse_interrupt(channel):
    """Hardware interrupt callback - fires INSTANTLY"""
    global pulse_count
    timestamp = time.perf_counter()
    
    with lock:
        pulse_times.append(timestamp)
        pulse_count += 1

def setup_gpio():
    """Setup GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    
    # Input pin with interrupt
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        INPUT_PIN,
        GPIO.FALLING,
        callback=pulse_interrupt,
        bouncetime=1
    )
    
    # Output pin for test pulses
    GPIO.setup(OUTPUT_PIN, GPIO.OUT)
    GPIO.output(OUTPUT_PIN, GPIO.HIGH)
    
    print(f"GPIO setup complete")
    print(f"  Input:  GPIO {INPUT_PIN} (with hardware interrupt)")
    print(f"  Output: GPIO {OUTPUT_PIN} (pulse generator)")
    print(f"\nConnect GPIO {OUTPUT_PIN} → GPIO {INPUT_PIN} with a wire")

def generate_test_pulses(frequency_hz, duration_s):
    """Generate test pulses at specified frequency"""
    interval = 1.0 / frequency_hz
    end_time = time.perf_counter() + duration_s
    
    while time.perf_counter() < end_time:
        # Generate falling edge
        GPIO.output(OUTPUT_PIN, GPIO.LOW)
        time.sleep(0.0001)  # 0.1ms pulse width
        GPIO.output(OUTPUT_PIN, GPIO.HIGH)
        
        # Wait for next pulse
        time.sleep(interval - 0.0001)

def analyze_timing():
    """Analyze interrupt timing accuracy"""
    with lock:
        if len(pulse_times) < 2:
            return None
        
        times = list(pulse_times)
    
    # Calculate intervals
    intervals = [times[i+1] - times[i] for i in range(len(times)-1)]
    
    if not intervals:
        return None
    
    import numpy as np
    
    avg_interval = np.mean(intervals)
    std_interval = np.std(intervals)
    min_interval = np.min(intervals)
    max_interval = np.max(intervals)
    
    return {
        'avg_ms': avg_interval * 1000,
        'std_ms': std_interval * 1000,
        'min_ms': min_interval * 1000,
        'max_ms': max_interval * 1000,
        'jitter_ms': (max_interval - min_interval) * 1000,
        'count': len(intervals)
    }

def run_test():
    """Run interrupt timing test"""
    print("\n" + "="*60)
    print("HARDWARE INTERRUPT TIMING TEST")
    print("="*60)
    
    setup_gpio()
    
    input("\nPress Enter to start test...")
    
    # Test different frequencies
    test_cases = [
        (10, "10 Hz - Slow"),
        (100, "100 Hz - Normal"),
        (1000, "1000 Hz - Fast"),
    ]
    
    for freq, description in test_cases:
        print(f"\n--- Test: {description} ---")
        print(f"Generating {freq} Hz pulses for 2 seconds...")
        
        # Reset counters
        global pulse_count
        with lock:
            pulse_times.clear()
            pulse_count = 0
        
        # Generate pulses
        generate_test_pulses(freq, 2.0)
        
        # Wait a bit for last interrupts
        time.sleep(0.1)
        
        # Analyze
        stats = analyze_timing()
        
        if stats:
            print(f"\nResults:")
            print(f"  Pulses captured: {pulse_count}")
            print(f"  Expected: {freq * 2} pulses")
            print(f"  Success rate: {(pulse_count / (freq * 2)) * 100:.1f}%")
            print(f"\nTiming accuracy:")
            print(f"  Average interval: {stats['avg_ms']:.3f} ms")
            print(f"  Expected interval: {1000/freq:.3f} ms")
            print(f"  Standard deviation: {stats['std_ms']:.3f} ms")
            print(f"  Min interval: {stats['min_ms']:.3f} ms")
            print(f"  Max interval: {stats['max_ms']:.3f} ms")
            print(f"  Jitter: {stats['jitter_ms']:.3f} ms")
            
            # Verdict
            if stats['std_ms'] < 0.1:
                print(f"\n✅ EXCELLENT - Timing is very consistent!")
            elif stats['std_ms'] < 0.5:
                print(f"\n✅ GOOD - Timing is acceptable")
            else:
                print(f"\n⚠️  WARNING - High timing jitter detected")
        else:
            print("❌ No pulses captured!")
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)
    
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\nInterrupted")
        GPIO.cleanup()
