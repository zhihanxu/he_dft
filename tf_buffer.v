// buffer for the twiddle factors
// storing L+k+1 = 32 limbs



module tf_buffer #(
    parameter ADDR_WIDTH = 13;
    parameter DATA_WIDTH = 72*3,
    parameter dp = 256
) (
    input wire clk,
    input wire [dp/2*ADDR_WIDTH-1:0] addr,              
    input wire [dp/2*DATA_WIDTH-1:0] data_in,       
    output wire [dp/2*DATA_WIDTH-1:0] data_out,        
    input wire we
);
    
    genvar i;

    // instantiate dp/2 uram_banks
    generate
        for (i = 0; i < dp/2; i = i + 1) begin : bram_bank_instances
            uram_bank #(.DATA_WIDTH(DATA_WIDTH), .ADDR_WIDTH(ADDR_WIDTH)) uram_bank_inst (
                .clk(clk),
                .addr(addr[i*ADDR_WIDTH +: ADDR_WIDTH]),
                .data_in(data_in[i*DATA_WIDTH +: DATA_WIDTH]),
                .data_out(data_out[i*DATA_WIDTH +: DATA_WIDTH]),
                .we(we)
            );
        end
    endgenerate

endmodule