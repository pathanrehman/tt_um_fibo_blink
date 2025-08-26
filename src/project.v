/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_fibo_blink (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Input Configuration
    wire [1:0] sequence_select = ui_in[1:0];  // 00=Fibo, 01=Prime, 10=Square, 11=Triangular
    wire [2:0] speed_control = ui_in[4:2];    // Speed multiplier (0=slowest, 7=fastest)
    wire reset_sequence = ui_in;           // Reset sequence to beginning
    wire enable_output = ui_in[15];            // Enable/disable LED output
    
    // Internal Registers
    reg [15:0] current_number;                // Current number in sequence
    reg [15:0] sequence_index;                // Index in current sequence
    reg [31:0] target_delay;                  // Target delay for current number
    reg [31:0] delay_counter;                 // Delay counter
    reg led_output;                           // LED output state
    reg sequence_active;                      // Sequence is running
    
    // Fibonacci Generator Registers
    reg [15:0] fib_a, fib_b;                 // Fibonacci sequence registers
    
    // Prime Checker Registers - Use lookup table approach
    reg [3:0] prime_index;                   // Index in prime sequence
    
    // Perfect Square Generator
    reg [7:0] square_root;                   // Square root for perfect squares
    
    // Triangular Number Generator  
    reg [15:0] triangular_n;                 // Current n for triangular numbers
    
    // Speed Control - Create base timing
    reg [23:0] base_counter;                 // Base timing counter
    wire timing_tick;
    
    // Prime lookup table for first 16 primes (synthesis-friendly)
    function [15:0] get_nth_prime;
        input [3:0] index;
        begin
            case (index)
                4'd0:  get_nth_prime = 16'd2;
                4'd1:  get_nth_prime = 16'd3;
                4'd2:  get_nth_prime = 16'd5;
                4'd3:  get_nth_prime = 16'd7;
                4'd4:  get_nth_prime = 16'd11;
                4'd5:  get_nth_prime = 16'd13;
                4'd6:  get_nth_prime = 16'd17;
                4'd7:  get_nth_prime = 16'd19;
                4'd8:  get_nth_prime = 16'd23;
                4'd9:  get_nth_prime = 16'd29;
                4'd10: get_nth_prime = 16'd31;
                4'd11: get_nth_prime = 16'd37;
                4'd12: get_nth_prime = 16'd41;
                4'd13: get_nth_prime = 16'd43;
                4'd14: get_nth_prime = 16'd47;
                4'd15: get_nth_prime = 16'd53;
                default: get_nth_prime = 16'd2;
            endcase
        end
    endfunction
    
    // Base timing generator (adjustable speed)
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            base_counter <= 24'b0;
        end else if (ena) begin
            case (speed_control)
                3'b000: base_counter <= base_counter + 24'd1;      // Slowest
                3'b001: base_counter <= base_counter + 24'd2;      // 2x speed
                3'b010: base_counter <= base_counter + 24'd4;      // 4x speed
                3'b011: base_counter <= base_counter + 24'd8;      // 8x speed
                3'b100: base_counter <= base_counter + 24'd16;     // 16x speed
                3'b101: base_counter <= base_counter + 24'd32;     // 32x speed
                3'b110: base_counter <= base_counter + 24'd64;     // 64x speed
                3'b111: base_counter <= base_counter + 24'd128;    // Fastest
            endcase
        end
    end
    
    assign timing_tick = base_counter;  // Use MSB as timing tick
    
    // Main Sequence Controller
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset all state
            current_number <= 16'd1;
            sequence_index <= 16'd0;
            target_delay <= 32'd100000;  // Initial delay
            delay_counter <= 32'd0;
            led_output <= 1'b0;
            sequence_active <= 1'b1;
            
            // Fibonacci initialization
            fib_a <= 16'd0;
            fib_b <= 16'd1;
            
            // Prime checker initialization
            prime_index <= 4'd0;
            
            // Perfect square initialization
            square_root <= 8'd1;
            
            // Triangular number initialization
            triangular_n <= 16'd1;
            
        end else if (ena) begin
            
            // Handle sequence reset
            if (reset_sequence) begin
                current_number <= 16'd1;
                sequence_index <= 16'd0;
                delay_counter <= 32'd0;
                led_output <= 1'b0;
                
                case (sequence_select)
                    2'b00: begin // Fibonacci reset
                        fib_a <= 16'd0;
                        fib_b <= 16'd1;
                        current_number <= 16'd1;
                    end
                    2'b01: begin // Prime reset
                        prime_index <= 4'd0;
                        current_number <= 16'd2;
                    end
                    2'b10: begin // Perfect square reset
                        square_root <= 8'd1;
                        current_number <= 16'd1;
                    end
                    2'b11: begin // Triangular reset
                        triangular_n <= 16'd1;
                        current_number <= 16'd1;
                    end
                endcase
            end else if (sequence_active && timing_tick) begin
                
                // Update delay counter
                if (delay_counter < target_delay) begin
                    delay_counter <= delay_counter + 32'd1;
                end else begin
                    // Time to move to next number in sequence
                    delay_counter <= 32'd0;
                    led_output <= ~led_output;  // Toggle LED
                    
                    // Generate next number based on sequence type
                    case (sequence_select)
                        2'b00: begin // Fibonacci Sequence
                            fib_a <= fib_b;
                            fib_b <= fib_a + fib_b;
                            current_number <= fib_b;
                            target_delay <= {16'd0, fib_b};  // Delay = Fibonacci number
                        end
                        
                        2'b01: begin // Prime Numbers (using lookup table)
                            prime_index <= prime_index + 4'd1;
                            current_number <= get_nth_prime(prime_index);
                            target_delay <= {16'd0, get_nth_prime(prime_index)};
                        end
                        
                        2'b10: begin // Perfect Squares (1, 4, 9, 16, 25...)
                            square_root <= square_root + 8'd1;
                            current_number <= {8'd0, square_root + 8'd1} * {8'd0, square_root + 8'd1};
                            target_delay <= {16'd0, {8'd0, square_root + 8'd1} * {8'd0, square_root + 8'd1}};
                        end
                        
                        2'b11: begin // Triangular Numbers (1, 3, 6, 10, 15...)
                            triangular_n <= triangular_n + 16'd1;
                            current_number <= ({16'd0, triangular_n + 16'd1} * {16'd0, triangular_n + 16'd2}) >> 1;
                            target_delay <= ({16'd0, triangular_n + 16'd1} * {16'd0, triangular_n + 16'd2}) >> 1;
                        end
                    endcase
                    
                    sequence_index <= sequence_index + 16'd1;
                end
            end
        end
    end
    
    // Single assignment to uo_out - fixes multiple driver error
    assign uo_out = {
        current_number[3:0],                    // [7:4] Lower 4 bits of current number
        (delay_counter == 32'd0),               //  New number pulse
        sequence_active,                        // [16] Sequence active indicator
        timing_tick,                            // [17] Timing reference
        enable_output ? led_output : 1'b0       //  Main LED output
    };
    
    // Bidirectional pins - output current sequence information
    assign uio_out = current_number[15:8];     // Upper 8 bits of current number
    assign uio_oe = 8'hFF;                     // All bidirectional pins as outputs
    
    // List all unused inputs to prevent warnings
    wire _unused = &{uio_in, ui_in, 1'b0};

endmodule
