# Makefile for Dead Reckoning Calculations

CC = gcc
CFLAGS = -Wall -Wextra -O2 -std=c99
LDFLAGS = -lm
TARGET = dead_reckoning
DEMO = dt_frequency_demo
SRC = dead_reckoning.c
DEMO_SRC = dt_frequency_demo.c

all: $(TARGET) $(DEMO)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

$(DEMO): $(DEMO_SRC)
	$(CC) $(CFLAGS) -o $(DEMO) $(DEMO_SRC)

clean:
	rm -f $(TARGET) $(TARGET).exe $(DEMO) $(DEMO).exe

run: $(TARGET)
	./$(TARGET)

demo: $(DEMO)
	./$(DEMO)

.PHONY: all clean run demo
