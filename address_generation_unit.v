module address_generation_unit #(
    parameter N = 65536, 
    parameter MAX_R = 31,   // number of rotations each fftiter
    parameter DATA_WIDTH = 54,
    parameter ADDR_WIDTH = 10
)(
    input wire clk,
    input wire rst,
    input wire [31:0] i,
    input wire [ADDR_WIDTH-1:0] input_address,
    input wire [4:0] r, //  r is between 0 and MAX_R-1
    output reg [ADDR_WIDTH-1:0] output_address
);

    wire [ADDR_WIDTH-1:0] new_index;

    // Register file to store pre-computed powers of 5
    reg [DATA_WIDTH-1:0] pow5 [0:MAX_R-1];

    // Initialize the register file with pre-computed powers of 5 mod 65536
    initial begin
        pow5[0] = 57345;
        pow5[1] = 40961;
        pow5[2] = 16385;
        pow5[3] = 49153;
        pow5[4] = 8193;
        pow5[5] = 24577;
        pow5[6] = 32769;
        pow5[7] = 32769;
        pow5[8] = 24577;
        pow5[9] = 8193;
        pow5[10] = 49153;
        pow5[11] = 16385;
        pow5[12] = 40961;
        pow5[13] = 57345;
        pow5[14] = 1;
        pow5[15] = 1;
        pow5[16] = 57345;
        pow5[17] = 40961;
        pow5[18] = 16385;
        pow5[19] = 49153;
        pow5[20] = 8193;
        pow5[21] = 24577;
        pow5[22] = 32769;
        pow5[23] = 32769;
        pow5[24] = 24577;
        pow5[25] = 8193;
        pow5[26] = 49153;
        pow5[27] = 16385;
        pow5[28] = 40961;
        pow5[29] = 57345;
        pow5[30] = 1;
    end


    assign new_index = (i * pow5[r]) % N;  // automorph


    always @(posedge clk or negedge rst) begin
        if (!rst) begin
            output_address <= 0;
        end else begin
            if (i[7:0] == new_index[7:0]) begin
                output_address <= input_address;
            end else begin
            output_address <= new_index * 256 + input_address[7:0];
            end
        end
    end

endmodule

