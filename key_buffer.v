// The key buffer contains 256 BRAM blocks
// storing 2*beta = 6 limbs
// 384 banks = 256 banks * 1.5

module key_buffer #(
    parameter ADDR_WIDTH = 11,
    parameter DATA_WIDTH = 54,
    parameter dp = 256
) (
    input wire clk,
    input wire [dp*ADDR_WIDTH-1:0] addr_read,         // 10-bit address for 256 bram_banks
    input wire [dp*ADDR_WIDTH-1:0] addr_write,        // 10-bit address for 256 bram_banks
    input wire [dp*DATA_WIDTH-1:0] data_in,           // 54-bit data input for each BRAM_bank
    output wire [dp*DATA_WIDTH-1:0] data_out,         // 54-bit data output for each BRAM_bank
    input wire we
);
    
    genvar i;

    // instantiate dp bram_banks
    generate
        for (i = 0; i < dp/2; i = i + 1) begin : bram_bank_instances
            bram_bank #(.DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)) bram_bank_2_inst (
                .clk(clk),
                .addr_read(addr_read[k*ADDR_WIDTH +: ADDR_WIDTH]),
                .addr_write(addr_write[k*ADDR_WIDTH +: ADDR_WIDTH]),
                .data_in(data_in[i*DATA_WIDTH +: DATA_WIDTH]),
                .data_out(data_out[i*DATA_WIDTH +: DATA_WIDTH]),
                .we(we)
            );
        end
    endgenerate

    generate
        for (i = 0; i < dp/2; i = i + 1) begin : bram_bank_instances
            bram_bank #(.DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH-1)) bram_bank_inst (
                .clk(clk),
                .addr_read(addr_read[k*ADDR_WIDTH +: ADDR_WIDTH-1]),
                .addr_write(addr_write[k*ADDR_WIDTH +: ADDR_WIDTH-1]),
                .data_in(data_in[i*DATA_WIDTH +: DATA_WIDTH]),
                .data_out(data_out[i*DATA_WIDTH +: DATA_WIDTH]),
                .we(we)
            );
        end
    endgenerate

endmodule