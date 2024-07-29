// pe unit with 54-bit data width for modular operations
// ctrl_pe[1:0] = 00: Modular Addition
// ctrl_pe[1:0] = 01: Modular Multiplication
// ctrl_pe[1:0] = 10: Modular Subtraction
// ctrl_pe[1:0] = 11: Modular Multiply and Addition


module pe_unit_54 #(
    parameter DATA_WIDTH = 54)(
    input wire clk,
    input wire rst,
    input wire [1:0] ctrl_pe,
    input wire [DATA_WIDTH-1:0] modulus,
    input wire [DATA_WIDTH:0] modulus_inv,
    input wire [DATA_WIDTH-1:0] input_data0,
    input wire [DATA_WIDTH-1:0] input_data1,
    input wire [DATA_WIDTH-1:0] input_data2,
    output reg [DATA_WIDTH-1:0] output_data
);

    wire [DATA_WIDTH-1:0] ma_output;
    wire [DATA_WIDTH-1:0] mm_output;
    reg [DATA_WIDTH-1:0] ma_input0, ma_input1;

    ma_unit_54 ma_inst (
        .clk(clk),
        .rst(rst),
        .modulus(modulus),
        .input_data0(ma_input0),
        .input_data1(ma_input1),
        .output_data(ma_output),
        .ctrl_ma(ctrl_pe[0])
    );

    mm_unit_54 mm_inst (
        .clk(clk),
        .rst(rst),
        .modulus(modulus),
        .modulus_inv(modulus_inv),
        .input_data0(input_data0),
        .input_data1(input_data1),
        .output_data(mm_output)
    );

    always @(*) begin
        case (ctrl_pe)
            2'b00, 2'b10: begin
                ma_input0 = input_data0;
                ma_input1 = input_data1;
            end
            2'b11: begin
                ma_input0 = mm_output;
                ma_input1 = input_data2;
            end
            default: begin
                ma_input0 = input_data0;
                ma_input1 = input_data1;
            end
        endcase
    end

    always @(posedge clk or negedge rst) begin
        if (!rst)
            output_data <= {DATA_WIDTH{1'b0}};
        else begin
            case (ctrl_pe)
                2'b00: output_data <= ma_output;  // Modular Addition
                2'b01: output_data <= mm_output;  // Modular Multiplication
                2'b10: output_data <= ma_output;  // Modular Subtraction
                2'b11: output_data <= ma_output;  // Modular Multiply and Addition
                default: output_data <= {DATA_WIDTH{1'b0}};
            endcase
        end
    end

endmodule
