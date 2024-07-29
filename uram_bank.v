// URAM bank includes 3 URAM units, each with 4096 72-bit coefficients

module uram_bank # (
    parameter DATA_WIDTH = 216,
    parameter ADDR_WIDTH = 12
)(
    input clk,
    input [ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] data_in,      
    output [DATA_WIDTH-1:0] data_out,     
    input we                     // Write enable
);
    
    // Split the 216-bit input into three 72-bit inputs
    wire [71:0] data_in_uram0 = data_in[71:0];
    wire [71:0] data_in_uram1 = data_in[143:72];
    wire [71:0] data_in_uram2 = data_in[215:144];
    
    // Outputs from each BRAM
    wire [71:0] data_out_uram0;
    wire [71:0] data_out_uram1;
    wire [71:0] data_out_uram2;

    // Combine the 72-bit outputs into one 216-bit output
    assign data_out = {data_out_uram0, data_out_uram1, data_out_uram2};

    // Instantiate three URAMs
    uram_unit #(.DATA_WIDTH(72), .ADDR_WIDTH(ADDR_WIDTH)) uram0 (
        .clk(clk),
        .addr(addr),
        .data_in(data_in_bram0),
        .data_out(data_out_bram0),
        .we(we)
    );
    
    uram_unit #(.DATA_WIDTH(72), .ADDR_WIDTH(ADDR_WIDTH)) uram1 (
        .clk(clk),
        .addr(addr),
        .data_in(data_in_bram0),
        .data_out(data_out_bram0),
        .we(we)
    );

    uram_unit #(.DATA_WIDTH(72), .ADDR_WIDTH(ADDR_WIDTH)) uram2 (
        .clk(clk),
        .addr(addr),
        .data_in(data_in_bram0),
        .data_out(data_out_bram0),
        .we(we)
    );
  
endmodule