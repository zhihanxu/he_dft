// 54-bit modular adder and subtractor unit
// ctrl_ma = 0: Modular Addition
// ctrl_ma = 1: Modular Subtraction


module ma_unit_54 #(
    parameter DATA_WIDTH = 54
) (
    input wire clk,
    input wire rst,
    input wire ctrl_ma,
    input wire [DATA_WIDTH-1:0] modulus,
    input wire [DATA_WIDTH-1:0] input_data0,
    input wire [DATA_WIDTH-1:0] input_data1,
    output reg [DATA_WIDTH-1:0] output_data
);

    reg [DATA_WIDTH:0] result; // One extra bit to handle overflow

    always @(posedge clk or negedge rst) begin
        if (!rst)
            output_data <= {DATA_WIDTH{1'b0}};
        else begin
            if (ctrl_ma)
                result = input_data0 + input_data1;
            else
                result = input_data0 - input_data1;

            if (result >= modulus)
                output_data <= result - modulus;
            else if (result[DATA_WIDTH-1] == 1'b1) // Check for negative result
                output_data <= result + modulus;
            else
                output_data <= result[DATA_WIDTH-1:0];
        end
    end

endmodule