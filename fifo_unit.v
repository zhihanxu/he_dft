module fifo_unit #(
    parameter DATA_WIDTH = 256,
    parameter DEPTH = 128
)(
    input wire clk,
    input wire reset,
    input wire write_enable,
    input wire read_enable,
    input wire [DATA_WIDTH-1:0] write_data,
    output reg [DATA_WIDTH-1:0] read_data,
    output wire full,
    output wire empty
);

    reg [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    reg [7:0] write_ptr = 0;
    reg [7:0] read_ptr = 0;
    reg [7:0] count = 0;

    assign full = (count == DEPTH);
    assign empty = (count == 0);

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            write_ptr <= 0;
            read_ptr <= 0;
            count <= 0;
        end else begin
            if (write_enable && !full) begin
                mem[write_ptr] <= write_data;
                write_ptr <= write_ptr + 1;
                count <= count + 1;
            end
            if (read_enable && !empty) begin
                read_data <= mem[read_ptr];
                read_ptr <= read_ptr + 1;
                count <= count - 1;
            end
        end
    end
endmodule
