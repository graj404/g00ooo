#!/bin/bash
# Installation script for Racing Lap Counter System

echo "Installing Racing Lap Counter System..."
echo "========================================"

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y python3-pip python3-dev i2c-tools

# Enable I2C
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0

# Install Python packages
echo "Installing Python packages..."

# Check if we're on Ubuntu 24.04+ with externally-managed Python
if [ -f /usr/share/doc/python3.12/README.venv ] || [ -f /usr/lib/python3.*/EXTERNALLY-MANAGED ]; then
    echo "Detected externally-managed Python environment"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo ""
    echo "Virtual environment created in 'venv' directory"
    echo "To use the system, run: source venv/bin/activate"
else
    pip3 install -r requirements.txt
fi

# Test I2C devices
echo ""
echo "Scanning for I2C devices..."
sudo i2cdetect -y 1

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Connect your sensors:"
echo "   - IR sensor to GPIO 27"
echo "   - AS5600 to I2C (address 0x36)"
echo "   - Fuel sensor to ADS1115 channel A0"
echo ""

# Check if venv was created
if [ -d "venv" ]; then
    echo "2. Activate virtual environment: source venv/bin/activate"
    echo "3. Test sensors: python test_sensors.py"
    echo "4. Run system: python main.py"
else
    echo "2. Test sensors: python3 test_sensors.py"
    echo "3. Run system: python3 main.py"
fi

echo ""
echo "Web dashboard will be available at: http://$(hostname -I | awk '{print $1}'):5000"
