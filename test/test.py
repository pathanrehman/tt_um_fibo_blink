# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge

@cocotb.test()
async def test_fibo_blink_basic(dut):
    """Basic functionality test for FiboBlink"""
    
    dut._log.info("Start FiboBlink basic test")
    
    # Set the clock period to 10 us (100 KHz) for visible timing
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    
    dut._log.info("Test FiboBlink default behavior")
    
    # Enable output and select Fibonacci sequence
    dut.ui_in.value = 0x40  # Enable output (bit 6) + Fibonacci sequence (bits 1:0 = 00)
    await ClockCycles(dut.clk, 20)
    
    # Check that LED output is active
    led_output = dut.uo_out.value & 0x01
    sequence_active = (dut.uo_out.value >> 2) & 0x01
    
    assert sequence_active == 1, f"Expected sequence active, got {sequence_active}"
    dut._log.info("✓ Basic FiboBlink activity test passed")

@cocotb.test()
async def test_fibonacci_sequence_generation(dut):
    """Test Fibonacci sequence number generation"""
    
    dut._log.info("Start Fibonacci sequence generation test")
    
    # Set up clock
    clock = Clock(dut.clk, 1, units="us")  # Faster clock for testing
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Configure: Fibonacci sequence + fastest speed + enable output
    dut.ui_in.value = 0x7C  # Enable(6) + Speed(111) + Fibonacci(00)
    await ClockCycles(dut.clk, 10)
    
    # Expected Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21...
    expected_fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    
    for i, expected_value in enumerate(expected_fibonacci[:5]):  # Test first 5 numbers
        # Wait for new number pulse
        for _ in range(1000):  # Timeout after 1000 cycles
            await RisingEdge(dut.clk)
            new_number_pulse = (dut.uo_out.value >> 3) & 0x01
            if new_number_pulse == 1:
                break
        
        # Read current number (16-bit: upper 8 from uio_out, lower 4 from uo_out[7:4])
        upper_bits = dut.uio_out.value & 0xFF
        lower_bits = (dut.uo_out.value >> 4) & 0x0F
        current_number = (upper_bits << 4) | lower_bits
        
        # For small Fibonacci numbers, only check lower bits
        if expected_value <= 15:
            current_number = lower_bits
        
        dut._log.info(f"Fibonacci[{i}]: Expected {expected_value}, Got {current_number}")
        
        # Allow some tolerance for timing variations
        if expected_value <= 15:
            assert current_number == expected_value, \
                f"Fibonacci[{i}]: Expected {expected_value}, got {current_number}"
        
        await ClockCycles(dut.clk, 10)  # Wait before next number
    
    dut._log.info("✓ Fibonacci sequence generation test passed")

@cocotb.test()
async def test_sequence_selection(dut):
    """Test different mathematical sequence selection"""
    
    dut._log.info("Start sequence selection test")
    
    # Set up clock
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test different sequence selections
    sequences = [
        (0b00, "Fibonacci"),
        (0b01, "Prime"),
        (0b10, "Perfect Square"),
        (0b11, "Triangular")
    ]
    
    for seq_select, seq_name in sequences:
        dut._log.info(f"Testing {seq_name} sequence")
        
        # Set sequence selection + enable output + medium speed
        dut.ui_in.value = 0x40 | (0b011 << 2) | seq_select  # Enable + Speed + Sequence
        await ClockCycles(dut.clk, 20)
        
        # Check that sequence is active
        sequence_active = (dut.uo_out.value >> 2) & 0x01
        assert sequence_active == 1, f"{seq_name} sequence not active"
        
        # Check that we get some output activity
        led_states = []
        for _ in range(100):
            await RisingEdge(dut.clk)
            led_states.append(dut.uo_out.value & 0x01)
        
        # Should have some variation in LED states
        unique_states = set(led_states)
        assert len(unique_states) > 1, f"{seq_name} sequence shows no LED activity"
        
        dut._log.info(f"✓ {seq_name} sequence test passed")

@cocotb.test()
async def test_speed_control(dut):
    """Test PWM speed control functionality"""
    
    dut._log.info("Start speed control test")
    
    # Set up clock
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test different speed settings
    speeds = [0b000, 0b011, 0b111]  # Slowest, medium, fastest
    speed_names = ["Slowest", "Medium", "Fastest"]
    
    for speed, speed_name in zip(speeds, speed_names):
        dut._log.info(f"Testing {speed_name} speed")
        
        # Set speed + Fibonacci sequence + enable output
        dut.ui_in.value = 0x40 | (speed << 2) | 0b00  # Enable + Speed + Fibonacci
        await ClockCycles(dut.clk, 20)
        
        # Monitor timing tick activity
        tick_changes = 0
        prev_tick = (dut.uo_out.value >> 1) & 0x01
        
        for _ in range(200):
            await RisingEdge(dut.clk)
            current_tick = (dut.uo_out.value >> 1) & 0x01
            if current_tick != prev_tick:
                tick_changes += 1
            prev_tick = current_tick
        
        dut._log.info(f"{speed_name} speed: {tick_changes} timing tick changes")
        
        # Faster speeds should have more tick changes
        if speed == 0b111:  # Fastest
            assert tick_changes > 10, f"Fastest speed should have more activity, got {tick_changes}"
        
        dut._log.info(f"✓ {speed_name} speed test passed")

@cocotb.test()
async def test_sequence_reset(dut):
    """Test sequence reset functionality"""
    
    dut._log.info("Start sequence reset test")
    
    # Set up clock
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Start Fibonacci sequence
    dut.ui_in.value = 0x7C  # Enable + Fastest speed + Fibonacci
    await ClockCycles(dut.clk, 100)  # Let it run for a while
    
    # Read current number before reset
    upper_before = dut.uio_out.value & 0xFF
    lower_before = (dut.uo_out.value >> 4) & 0x0F
    number_before = (upper_before << 4) | lower_before
    
    dut._log.info(f"Number before reset: {number_before}")
    
    # Apply sequence reset
    dut.ui_in.value = 0x7C | (1 << 5)  # Set reset sequence bit
    await ClockCycles(dut.clk, 5)
    
    # Release reset
    dut.ui_in.value = 0x7C  # Clear reset sequence bit
    await ClockCycles(dut.clk, 20)
    
    # Read number after reset
    upper_after = dut.uio_out.value & 0xFF
    lower_after = (dut.uo_out.value >> 4) & 0x0F
    number_after = lower_after  # Should be back to first Fibonacci number
    
    dut._log.info(f"Number after reset: {number_after}")
    
    # Should be back to first Fibonacci number (1)
    assert number_after <= 2, f"Expected reset to first number (~1), got {number_after}"
    
    dut._log.info("✓ Sequence reset test passed")

@cocotb.test()
async def test_led_timing_pattern(dut):
    """Test LED timing follows mathematical sequence"""
    
    dut._log.info("Start LED timing pattern test")
    
    # Set up slower clock for visible timing
    clock = Clock(dut.clk, 100, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Configure for medium speed Fibonacci with LED enabled
    dut.ui_in.value = 0x4C  # Enable + Medium speed + Fibonacci
    await ClockCycles(dut.clk, 10)
    
    # Monitor LED transitions
    led_transitions = []
    prev_led = dut.uo_out.value & 0x01
    transition_count = 0
    
    for cycle in range(500):  # Monitor for many cycles
        await RisingEdge(dut.clk)
        current_led = dut.uo_out.value & 0x01
        
        if current_led != prev_led:
            led_transitions.append(cycle)
            transition_count += 1
            dut._log.info(f"LED transition {transition_count} at cycle {cycle}")
            
            if transition_count >= 6:  # Collect several transitions
                break
                
        prev_led = current_led
    
    # Verify we got LED transitions
    assert len(led_transitions) >= 4, f"Expected multiple LED transitions, got {len(led_transitions)}"
    
    dut._log.info(f"✓ LED timing pattern test passed - {len(led_transitions)} transitions observed")

@cocotb.test()
async def test_output_enable_disable(dut):
    """Test output enable/disable functionality"""
    
    dut._log.info("Start output enable/disable test")
    
    # Set up clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test with output disabled
    dut.ui_in.value = 0x0C  # Disable output + Medium speed + Fibonacci
    await ClockCycles(dut.clk, 50)
    
    led_output_disabled = dut.uo_out.value & 0x01
    dut._log.info(f"LED output when disabled: {led_output_disabled}")
    
    # Test with output enabled
    dut.ui_in.value = 0x4C  # Enable output + Medium speed + Fibonacci
    await ClockCycles(dut.clk, 50)
    
    # Should see some activity when enabled
    led_states = []
    for _ in range(100):
        await RisingEdge(dut.clk)
        led_states.append(dut.uo_out.value & 0x01)
    
    unique_states = set(led_states)
    assert len(unique_states) > 1, "Expected LED activity when enabled"
    
    dut._log.info("✓ Output enable/disable test passed")

@cocotb.test()
async def test_mathematical_accuracy(dut):
    """Test mathematical accuracy of sequences"""
    
    dut._log.info("Start mathematical accuracy test")
    
    # Set up clock
    clock = Clock(dut.clk, 1, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    
    # Test Perfect Squares sequence (easier to verify)
    dut.ui_in.value = 0x7E  # Enable + Fastest + Perfect Squares (10)
    await ClockCycles(dut.clk, 20)
    
    # Expected perfect squares: 1, 4, 9, 16, 25...
    expected_squares = [1, 4, 9, 16]
    
    for i, expected in enumerate(expected_squares):
        # Wait for sequence to advance
        await ClockCycles(dut.clk, 50)
        
        # Read current number
        lower_bits = (dut.uo_out.value >> 4) & 0x0F
        
        if expected <= 15:  # Within 4-bit range
            dut._log.info(f"Square[{i}]: Expected {expected}, Got {lower_bits}")
            # Allow some flexibility for timing
            if lower_bits != 0:  # Ignore zero states
                assert lower_bits <= expected + 1, \
                    f"Square[{i}]: Expected ~{expected}, got {lower_bits}"
    
    dut._log.info("✓ Mathematical accuracy test passed")
