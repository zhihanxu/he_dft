// uram storage unit consuming 1 URAM
// 4096 72-bit coefficients
// single-port

module uram_unit #(
    parameter DATA_WIDTH = 72,
    parameter ADDR_WIDTH = 12
) (
    input clk,
    input [ADDR_WIDTH-1:0] addr,
    input [DATA_WIDTH-1:0] data_in,
    output reg [DATA_WIDTH-1:0] data_out,
    input we
);
    // Declare the URAM memory array
    (* ram_style = "ultra" *) reg [DATA_WIDTH-1:0] ram [0:(1<<ADDR_WIDTH)-1];

    always @(posedge clk) begin
        if (we) begin
            ram[addr] <= data_in;
        end
        data_out <= ram[addr];
    end
endmodule