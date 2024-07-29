// BRAM bank includes 3 BRAM18 units, each with 2^{Addr_width-10} 54-bit coefficients

module bram_bank # (
    parameter DATA_WIDTH = 54,
    parameter ADDR_WIDTH = 10
)(
    input clk,
    input [ADDR_WIDTH-1:0] addr_read,        // 10-bit address for 1024 locations
    input [ADDR_WIDTH-1:0] addr_write,       // 10-bit address for 1024 locations
    input [DATA_WIDTH-1:0] data_in,        // 54-bit data input
    output [DATA_WIDTH-1:0] data_out,      // 54-bit data output
    input we                     // Write enable
);
    
    // Split the 54-bit input into three 18-bit inputs
    wire [17:0] data_in_bram0 = data_in[17:0];
    wire [17:0] data_in_bram1 = data_in[35:18];
    wire [17:0] data_in_bram2 = data_in[53:36];
    
    // Outputs from each BRAM
    wire [17:0] data_out_bram0;
    wire [17:0] data_out_bram1;
    wire [17:0] data_out_bram2;

    // Combine the 18-bit outputs into one 54-bit output
    assign data_out = {data_out_bram0, data_out_bram1, data_out_bram2};

    // Instantiate three BRAMs
    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram0 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram0),
        .data_out(data_out_bram0),
        .we(we)
    );
    
    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram1 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram1),
        .data_out(data_out_bram1),
        .we(we)
    );

    bram_unit #(.DATA_WIDTH(18), .ADDR_WIDTH(ADDR_WIDTH)) bram2 (
        .clk(clk),
        .addr_read(addr_read),
        .addr_write(addr_write),
        .data_in(data_in_bram2),
        .data_out(data_out_bram2),
        .we(we)
    );
  
endmodule