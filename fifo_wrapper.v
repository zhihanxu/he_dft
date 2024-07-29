module fifo_wrapper # (
    parameter DATA_WIDTH = 256,
    parameter axi_channel = 32
) (
    input wire clk_wr,  // 450 MHz
    input wire clk_rd,  // 300 MHz
    input wire reset,
    input wire wr_write_enable,
    input wire wr_read_enable,
    input wire rd_write_enable,
    input wire rd_read_enable,
    input wire [DATA_WIDTH * axi_channel-1:0] wr_fifo_write_data,
    output wire [DATA_WIDTH * axi_channel-1:0] wr_fifo_read_data,
    input wire [DATA_WIDTH * axi_channel-1:0] rd_fifo_write_data,
    output wire [DATA_WIDTH * axi_channel-1:0] rd_fifo_read_data,
    output wire [axi_channel-1:0] wr_fifo_full,
    output wire [axi_channel-1:0] wr_fifo_empty
    output wire [axi_channel-1:0] rd_fifo_full,
    output wire [axi_channel-1:0] rd_fifo_empty
);

    genvar i;
    generate
        for (i = 0; i < axi_channel; i = i + 1) begin : gen_fifo
            fifo #(
                .DATA_WIDTH(DATA_WIDTH),
                .DEPTH(128) // Write FIFO depth is 128
            ) wr_fifo_inst (
                .clk(clk_wr), // Write clock
                .reset(reset),
                .write_enable(wr_write_enable),
                .read_enable(rd_read_enable),
                .write_data(wr_fifo_write_data[i*DATA_WIDTH +: DATA_WIDTH]),
                .read_data(wr_fifo_read_data[i*DATA_WIDTH +: DATA_WIDTH]),
                .full(wr_fifo_full[i]),
                .empty(wr_fifo_empty[i])
            );

            fifo #(
                .DATA_WIDTH(DATA_WIDTH),
                .DEPTH(512) // Read FIFO depth is 512
            ) rd_fifo_inst (
                .clk(clk_rd), // Read clock
                .reset(reset),
                .write_enable(rd_write_enable),
                .read_enable(rd_read_enable),
                .write_data(rd_write_data[i*DATA_WIDTH +: DATA_WIDTH]),
                .read_data(rd_read_data[i*DATA_WIDTH +: DATA_WIDTH]),
                .full(rd_fifo_full[i]),
                .empty(rd_fifo_empty[i])
            );
        end
    endgenerate

endmodule
