// 54-bit modular multiplication unit

module mm_unit_54 # (
  parameter DATA_WIDTH = 54
) (
  input wire [DATA_WIDTH-1:0]modulus,
  input wire [DATA_WIDTH:0] modulus_inv,
  input wire [DATA_WIDTH-1:0] input_data0,
  input wire [DATA_WIDTH-1:0] input_data1,
  output reg output_data,
  input wire clk,
  input wire rst
);


  reg [DATA_WIDTH-1:0] a_stage_01,a_stage_12,a_stage_23,a_stage_34,a_stage_45,a_stage_56;
  reg [DATA_WIDTH:0] b_stage_01,b_stage_12,b_stage_23,b_stage_34,b_stage_45,b_stage_56;
  reg [2*DATA_WIDTH-1:0] u_stage_01,u_stage_12,u_stage_23,u_stage_34,u_stage_45,u_stage_56;
  reg [DATA_WIDTH:0] v_stage_01,v_stage_12,v_stage_23,v_stage_34,v_stage_45,v_stage_56;

  reg [DATA_WIDTH:0] y_stage_01,y_stage_12,y_stage_23,y_stage_34,y_stage_45,y_stage_56,y_stage_67,y_stage_78,y_stage_89,y_stage_910,y_stage_1011,y_stage_1112,y_stage_1213,y_stage_1314;

  reg [2*DATA_WIDTH+1:0] w_stage_01,w_stage_12,w_stage_23,w_stage_34,w_stage_45,w_stage_56;
  reg [DATA_WIDTH:0] w_stage_67,w_stage_78,w_stage_89,w_stage_910,w_stage_1011,w_stage_1112;

  reg [2*DATA_WIDTH:0] x_stage_01,x_stage_12,x_stage_23,x_stage_34,x_stage_45,x_stage_56;
  reg [DATA_WIDTH-1:0] z_stage_01;

  always @(posedge clk or negedge rst)
  begin
    if(!rst) 
      output_data<=64'd0;
    else begin
        // Full IntMult1 data preparation
        a_stage_01<={input_data0};
        b_stage_01<={input_data1};
        
        a_stage_12<=a_stage_01;
        a_stage_23<=a_stage_12;
        a_stage_34<=a_stage_23;
        a_stage_45<=a_stage_34;
        a_stage_56<=a_stage_45;

        b_stage_12<=b_stage_01;
        b_stage_23<=b_stage_12;
        b_stage_34<=b_stage_23;
        b_stage_45<=b_stage_34;
        b_stage_56<=b_stage_45;
        
        // Full IntMult1 U=A*B
        u_stage_01<=input_data0[26:0]*input_data1[17:0];                                  // Stage 1: A0xB0
        u_stage_12<=u_stage_01+((a_stage_01[26:0]*b_stage_01[35:18])<<18);                // Stage 2: A0xB1
        u_stage_23<=u_stage_12+((a_stage_12[53:27]*b_stage_12[17:0])<<27);                // Stage 3: A1xB0
        u_stage_34<=u_stage_23+((a_stage_34[26:0]*b_stage_34[53:36])<<36);                // Stage 4: A0xB2
        u_stage_45<=u_stage_34+((a_stage_45[53:27]*b_stage_45[35:18])<<(18+27));          // Stage 5: A1xB1
        u_stage_56<=u_stage_45+((a_stage_56[53:27]*b_stage_56[50:34])<<(27+34));          // Stage 6: A1xB2
        
        // UH IntMult2 data preparation
        v_stage_01<=u_stage_56>>(DATA_WIDTH-1);
        v_stage_12<=v_stage_01;
        v_stage_23<=v_stage_12;
        v_stage_34<=v_stage_23;
        v_stage_45<=v_stage_34;
        v_stage_56<=v_stage_45;
    
        // UH IntMult2 W=V*T (T=modulus_inv) 63*63bit
        w_stage_01<=v_stage_01[26:0]*modulus_inv[17:0];                                 
        w_stage_12<=w_stage_01+((v_stage_01[26:0]*modulus_inv[35:18])<<18);               
        w_stage_23<=w_stage_12+((v_stage_12[53:27]*modulus_inv[17:0])<<27);               
        w_stage_34<=w_stage_23+((v_stage_34[26:0]*modulus_inv[53:35])<<34);               
        w_stage_45<=w_stage_34+((v_stage_45[53:27]*modulus_inv[35:18])<<(18+27));                                   
        w_stage_56<=w_stage_45+((v_stage_56[53:27]*modulus_inv[53:36])<<(27+36));         

        // LH IntMult2 data preparation
        w_stage_67<=w_stage_56>>(DATA_WIDTH+1);
        w_stage_78<=w_stage_67;
        w_stage_89<=w_stage_78;
        w_stage_910<=w_stage_89;
        w_stage_1011<=w_stage_910;
        w_stage_1112<=w_stage_1011;

        // LH IntMult2 X=W*q (q=modulus) 63*62bit
        x_stage_01<=w_stage_67[26:0]*modulus[17:0];
        x_stage_12<=x_stage_01+((w_stage_78[26:0]*modulus[35:18])<<18);
        x_stage_23<=x_stage_12+((w_stage_89[53:27]*modulus[17:0])<<27);
        x_stage_34<=x_stage_23+((w_stage_910[26:0]*modulus[53:35])<<35);
        x_stage_45<=x_stage_34+((w_stage_1011[53:27]*modulus[35:18])<<(18+27));
        x_stage_56<=x_stage_45+((w_stage_1112[53:27]*modulus[53:36])<<(27+36));

        // Final process
        y_stage_01<=u_stage_56[DATA_WIDTH:0]; //63bit
        y_stage_12<=y_stage_01;
        y_stage_23<=y_stage_12;
        y_stage_34<=y_stage_23;
        y_stage_45<=y_stage_34;
        y_stage_56<=y_stage_45;
        y_stage_67<=y_stage_56;
        y_stage_78<=y_stage_67;
        y_stage_89<=y_stage_78;
        y_stage_910<=y_stage_89;
        y_stage_1011<=y_stage_910;
        y_stage_1112<=y_stage_1011;
        y_stage_1213<=y_stage_1112;
        y_stage_1314<=y_stage_1213;

        z_stage_01<=y_stage_1314-x_stage_56[DATA_WIDTH:0];
        
        if(z_stage_01>=2*modulus) begin
          output_data<=z_stage_01-2*modulus;
        end else if (z_stage_01>modulus) begin
          output_data<=z_stage_01-modulus;
        end else begin
          output_data<=z_stage_01;
        end
    end
  end
endmodule
