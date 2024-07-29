// bram storage unit consuming 2^{Addr_width-10} BRAM18
// 1024*2^{Addr_width-10} 18-bit coefficients

module bram_unit #(
    parameter DATA_WIDTH = 18,
    parameter ADDR_WIDTH = 10
) (
    input clk,
    input [ADDR_WIDTH-1:0] addr_read,
    input [ADDR_WIDTH-1:0] addr_write,
    input [DATA_WIDTH-1:0] data_in,
    output reg [DATA_WIDTH-1:0] data_out,
    input we
);
    // Declare the BRAM memory array
    (* ram_style = "block" *) reg [DATA_WIDTH-1:0] ram [0:(1<<ADDR_WIDTH)-1];

    always @(posedge clk) begin
        if (we) begin
            ram[addr_write] <= data_in;
        end
        data_out <= ram[addr_read];
    end
endmodule