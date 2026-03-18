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
pip3 install -r requirements.txt

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
echo "2. Test sensors: python3 test_sensors.py"
echo "3. Run system: python3 main.py"
echo ""
echo "Web dashboard will be available at: http://$(hostname -I | awk '{print $1}'):5000"
