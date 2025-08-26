<!---
This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.
You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

# FiboBlink - Mathematical Sequence LED Timing Generator

**FiboBlink** transforms abstract mathematical sequences into visual, tangible experiences through precisely timed LED patterns. Watch the beauty of mathematics unfold as LED pulses follow Fibonacci numbers, prime sequences, perfect squares, and triangular numbers with intervals that match their mathematical values.

## How it works

FiboBlink implements sophisticated mathematical sequence generators in pure digital hardware, creating LED timing patterns that directly correspond to mathematical values.

### Core Architecture

The system consists of several interconnected mathematical engines:

1. **Fibonacci Generator**: Uses classical two-register addition (F(n) = F(n-1) + F(n-2)) to generate the famous sequence: 1, 1, 2, 3, 5, 8, 13, 21...
2. **Prime Number Generator**: Implements trial division algorithm with optimized even-number skipping to identify primes: 2, 3, 5, 7, 11, 13, 17...
3. **Perfect Square Calculator**: Generates squares using incremental computation: 1, 4, 9, 16, 25, 36...
4. **Triangular Number Engine**: Computes triangular numbers using the formula T(n) = n(n+1)/2: 1, 3, 6, 10, 15, 21...

### Visual Mathematics Algorithm

The key innovation is the **mathematical timing engine**:
- Each generated number becomes the LED blink interval in time units
- Fibonacci number 5 → LED blinks every 5 time units
- Prime number 7 → LED blinks every 7 time units  
- Perfect square 16 → LED blinks every 16 time units

This creates **visually verifiable mathematical patterns** where you can count and confirm sequence accuracy by timing the LED pulses.

### Precision Timing Control

- **8-level speed control**: From educational slow-motion to demonstration speed
- **24-bit base counter**: Provides precise timing resolution
- **Mathematical delay scaling**: Each sequence number directly controls timing
- **Sequence synchronization**: Clean transitions between mathematical values

### Advanced Features

- **Real-time sequence switching**: Change mathematical sequences without reset
- **Sequence reset capability**: Return to beginning of any sequence
- **16-bit number range**: Supports large mathematical values
- **Visual feedback system**: Multiple status indicators for system state

## How to test

### Basic Setup

1. **Power on** your TinyTapeout demo board and select the FiboBlink project
2. **Default state**: System initializes to Fibonacci sequence at medium speed
3. **Main LED**: Connect LED with 470Ω resistor to `uo_out[0]` for primary visualization

### Control Interface

#### Sequence Selection (ui_in[1:0])
```
00 = Fibonacci sequence (1,1,2,3,5,8,13,21...)
01 = Prime numbers (2,3,5,7,11,13,17,19...)  
10 = Perfect squares (1,4,9,16,25,36,49...)
11 = Triangular numbers (1,3,6,10,15,21,28...)
```

#### Speed Control (ui_in[4:2])
```
000 = Slowest (educational pace)
001 = Very slow  
010 = Slow
011 = Medium (recommended)
100 = Fast
101 = Very fast
110 = Ultra fast
111 = Maximum speed (demonstration)
```

### Testing Procedures

#### Fibonacci Sequence Verification
1. Set `ui_in[1:0] = 00` (Fibonacci mode)
2. Set `ui_in[4:2] = 011` (medium speed)
3. Set `ui_in[6] = 1` (enable output)
4. **Expected pattern**: LED blinks with intervals of 1, 1, 2, 3, 5, 8, 13... time units
5. **Verification**: Count the timing - each interval should follow F(n) = F(n-1) + F(n-2)

#### Prime Number Verification  
1. Set `ui_in[1:0] = 01` (prime mode)
2. **Expected pattern**: LED blinks every 2, 3, 5, 7, 11, 13... time units
3. **Verification**: Prime intervals should skip composite numbers (4, 6, 8, 9, 10, 12...)

#### Perfect Square Verification
1. Set `ui_in[1:0] = 10` (square mode)  
2. **Expected pattern**: LED blinks every 1, 4, 9, 16, 25... time units
3. **Verification**: Intervals should be perfect squares (1², 2², 3², 4², 5²...)

### Advanced Testing

#### Sequence Reset Test
1. Let any sequence run for several cycles
2. Assert `ui_in[5] = 1` (reset sequence)
3. **Expected result**: Sequence immediately returns to first number (LED timing resets to initial value)

#### Speed Control Test  
1. Start with `ui_in[4:2] = 000` (slowest)
2. Gradually increase to `111` (fastest)
3. **Expected result**: LED timing proportionally faster while maintaining mathematical ratios

#### Multi-Channel Monitoring
Monitor debug outputs for advanced verification:
- **uo_out[1]**: Timing tick (for oscilloscope synchronization)
- **uo_out[3]**: New number pulse (indicates sequence advancement) 
- **uo_out[7:4] + uio_out[7:0]**: Current 16-bit sequence value for numerical verification

### Educational Testing

#### Mathematics Classroom Use
1. Set slowest speed (`ui_in[4:2] = 000`)
2. Students count LED blink intervals manually
3. Compare counted intervals with mathematical sequence expectations
4. Switch sequences to demonstrate different mathematical patterns

#### STEM Fair Demonstration
1. Set medium speed for clear visibility
2. Show Fibonacci sequence first (most recognizable pattern)
3. Switch to primes to show mathematical filtering concept
4. End with perfect squares to demonstrate polynomial sequences

## External hardware

### Required Components

1. **TinyTapeout Demo Board**
   - Standard TinyTapeout carrier board with project selection
   - 10 MHz clock source for precise mathematical timing
   - Input switches or DIP switches for sequence control

2. **Primary LED Display**
   - **Standard LED** (any color, 3mm or 5mm recommended)
   - **470Ω current-limiting resistor**
   - **Connection**: `uo_out[0]` → Resistor → LED → GND
   - **Purpose**: Main mathematical sequence visualization

### Recommended Testing Equipment

#### Educational Setup
```
Component List:
-  1x LED (red recommended for visibility)
-  1x 470Ω resistor  
-  1x Breadboard
-  Jumper wires
-  Stopwatch (for manual timing verification)

Connections:
uo_out → 470Ω → LED → GND
```

#### Advanced Analysis Setup
```
Component List:
-  Oscilloscope (for precise timing measurement)
-  Logic analyzer (for multi-channel analysis)
-  Frequency counter (for timing verification)

Connections:
uo_out → Scope Ch1 (main LED signal)
uo_out → Scope Ch2 (timing reference)[11]
uo_out → Scope Ch3 (sequence advance pulse)
```

### Optional Enhancements

#### Multi-LED Array
```
-  4x LEDs (different colors)
-  4x 470Ω resistors

Connections:
uo_out → LED1 (main sequence)
uo_out → LED2 (timing tick)[11]
uo_out → LED3 (sequence active)[12]
uo_out → LED4 (new number pulse)
```

#### Numerical Display
```
-  7-segment display or LCD
-  Microcontroller for number decoding
-  Connect to uio_out[7:0] + uo_out[7:4] for 16-bit value display
```

#### Audio Enhancement  
```
-  Small buzzer or speaker
-  Audio amplifier circuit
-  Connect to uo_out for audible mathematical sequences
```

### Control Interface

#### Input Switch Configuration
```
Switch Bank 1 (ui_in[1:0]): 2-position DIP switch for sequence selection
Switch Bank 2 (ui_in[4:2]): 3-position DIP switch for speed control  
Push Button (ui_in): Momentary switch for sequence reset
Toggle Switch (ui_in): Enable/disable output[13]
```

### Pin Connection Reference

| Function | Pin | External Connection | Notes |
|----------|-----|-------------------|--------|
| **Main LED** | uo_out | LED + 470Ω resistor | **Primary output** - mathematical timing |
| **Timing Ref** | uo_out[11] | Oscilloscope Ch2 | Debug timing verification |
| **Sequence Active** | uo_out[12] | Status LED | Shows system activity |
| **New Number** | uo_out | Pulse LED | Indicates sequence advance |
| **Number Display** | uo_out[7:4] + uio_out[7:0] | 16-bit display | Current sequence value |
| **Sequence Select** | ui_in[1:0] | 2-bit switch | Math sequence choice |
| **Speed Control** | ui_in[4:2] | 3-bit switch | Timing speed adjustment |
| **Reset** | ui_in | Push button | Sequence restart |
| **Enable** | ui_in[13] | Toggle switch | Output enable/disable |

FiboBlink transforms abstract mathematical concepts into tangible, observable phenomena, making it perfect for education, demonstration, and anyone who wants to **see mathematics in action**.

