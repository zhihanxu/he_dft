module PE_array # (
    parameter dp = 256,
    parameter DATA_WIDTH = 54
)(
    input wire clk,
    input wire rst,
    input wire [1:0] ctrl_pe,
    input wire [DATA_WIDTH-1:0] modulus,
    input wire [DATA_WIDTH:0] modulus_inv,
    input wire [DATA_WIDTH * dp -1:0] input_data0,
    input wire [DATA_WIDTH * dp -1:0] input_data1,
    input wire [DATA_WIDTH * dp -1:0] input_data2,
    output wire [DATA_WIDTH * dp - 1:0] output_data
);

    genvar i;

    generate
        for (i = 0; i < dp; i = i + 1) begin : pe_units
            pe_unit_54 pe_inst (
                .clk(clk),
                .rst(rst),
                .ctrl_pe(ctrl_pe),
                .modulus(modulus),
                .modulus_inv(modulus_inv),
                .input_data0(input_data0[i * DATA_WIDTH +: DATA_WIDTH]),
                .input_data1(input_data1[i * DATA_WIDTH +: DATA_WIDTH]),
                .input_data2(input_data2[i * DATA_WIDTH +: DATA_WIDTH]),
                .output_data(output_data[i * DATA_WIDTH +: DATA_WIDTH])
            );
        end
    endgenerate

endmodule
