// File 4_2_1, generated 2025-10-14  08:47:44 by drawNodes
/* [Label Colors] */
// Color for edge labels
label_color = "Black";
// Color for label halo/outline
label_halo_color = "White";

// Number of sides for round things
$fn=31;
// Width as fraction of scale
wFrac=0.25;
// Unit length in drawing
scale=10;
// Height of text as fraction of scale
textFrac=0.75;
wf=1/2-wFrac/2;
hf=1/2;
module drawV(bx, ey, ll)
  translate (scale*[bx+wf,ey+1,0]) square([wFrac*scale,scale*ll]);
module drawH(bx, by, ll)
  translate (scale*[bx,by+wf,0])   square([scale*ll,wFrac*scale]);
module round2(radi, yfar) {
   circle(radi); translate([0,yfar,0]) circle(radi);
}
module drawNode(x,y, xfar) {
  ss=scale/4;  yf=scale/2;
  translate (scale*[x+1/4,y+1/4,0]) hull() {
      round2(ss,yf); translate([scale*(xfar-1/2),0,0]) round2(ss,yf);
  }
}
module drawNodeOutline(x,y, xfar, thickness) {
  ss=scale/4;  yf=scale/2;
  translate (scale*[x+1/4,y+1/4,0])
    difference() {
      hull() {
        round2(ss+thickness,yf);
        translate([scale*(xfar-1/2),0,0]) round2(ss+thickness,yf);
      }
      hull() {
        round2(ss,yf);
        translate([scale*(xfar-1/2),0,0]) round2(ss,yf);
      }
    }
}
module drawComplement(x,y)
  translate (scale*[x+0.5,y+1+wFrac,0]) circle(d=2*wFrac*scale);
module drawArrow(x, y) {
  // Draw upward-pointing triangle at position (x, y)
  // y is the bottom of the node, arrow points up into it
  // Base is 1.875x wider than line width, height is 1.25x line width (25% larger than original)
  translate(scale*[x, y, 0])
    polygon([[0, 0], [-1.875*wFrac*scale, -1.25*wFrac*scale], [1.875*wFrac*scale, -1.25*wFrac*scale]]);
}
module drawXorSymbol(x, y, xfar) {
  // Draw circled plus (XOR symbol) in center of node
  // x, y is bottom-left of node, xfar is node width
  cx = x + xfar/2;
  cy = y + 0.5;
  radius = 0.3;
  ringThickness = wFrac/3;
  barWidth = wFrac/3;
  barHalfLen = 0.2;

  translate(scale*[cx, cy, 0]) {
    // Circle ring
    difference() {
      circle(r=scale*radius);
      circle(r=scale*(radius-ringThickness));
    }
    // Horizontal bar of +
    translate(scale*[-barHalfLen, -barWidth/2, 0])
      square(scale*[2*barHalfLen, barWidth]);
    // Vertical bar of +
    translate(scale*[-barWidth/2, -barHalfLen, 0])
      square(scale*[barWidth, 2*barHalfLen]);
  }
}
module drawChar(x,y,t)
  translate (scale*[x,y,0]) text(t, size=textFrac*scale);
module drawCharHalo(x,y,t) {
  translate (scale*[x,y,0]) text(t, size=textFrac*scale, font=":style=Bold");
  translate (scale*[x-0.04,y,0]) text(t, size=textFrac*scale, font=":style=Bold");
}
module drawCorner(x,y,dx,dy, label="")
  translate (scale*[x,y,0]) {
    //text(label, size=textFrac*scale/2); // uncomment to see corner#
    intersection() {
      square(scale*[1,1], center=false);
      translate(scale*[dx,dy,0])
        difference() {
          circle(d=scale*(1+wFrac));
          circle(d=scale*(1-wFrac));
        }
      }
    }
module drawStuff() {
  color("Black") linear_extrude(height=1) {
    drawNodeOutline(4, 6,3,wFrac);
    drawNodeOutline(12, 6,3,wFrac);
    drawNodeOutline(20, 6,3,wFrac);
    drawNodeOutline(28, 6,3,wFrac);
  }
  color("#0000FF20") linear_extrude(height=1) {
    drawNode(4, 6,3);
    drawNode(12, 6,3);
    drawNode(20, 6,3);
    drawNode(28, 6,3);
  }
  color("Black") linear_extrude(height=1.1) {
    drawXorSymbol(4, 6,3);
    drawXorSymbol(12, 6,3);
    drawXorSymbol(20, 6,3);
    drawXorSymbol(28, 6,3);
  }
  color("Grey") linear_extrude(height=1.2) {
    drawChar(22, 5, "X");
    drawChar(30, 5, "X");
  }
  color(label_halo_color) linear_extrude(height=1.09) {
    drawCharHalo(4, 7.3, "f");
    drawCharHalo(28, 5, "f");
    drawCharHalo(6, 7.3, "c");
    drawCharHalo(12, 5, "c");
    drawCharHalo(12, 7.3, "c");
    drawCharHalo(20, 5, "c");
    drawCharHalo(14, 7.3, "f");
    drawCharHalo(4, 5, "f");
    drawCharHalo(20, 7.3, "b");
    drawCharHalo(6, 5, "b");
    drawCharHalo(22, 7.3, "e");
    drawCharHalo(14, 5, "e");
  }
  color(label_color) linear_extrude(height=1.1) {
    drawChar(4, 7.3, "f");
    drawChar(28, 5, "f");
    drawChar(6, 7.3, "c");
    drawChar(12, 5, "c");
    drawChar(12, 7.3, "c");
    drawChar(20, 5, "c");
    drawChar(14, 7.3, "f");
    drawChar(4, 5, "f");
    drawChar(20, 7.3, "b");
    drawChar(6, 5, "b");
    drawChar(22, 7.3, "e");
    drawChar(14, 5, "e");
  }
  color(label_halo_color) linear_extrude(height=1.19) {
    drawCharHalo(28, 7.3, "e");
    drawCharHalo(30, 7.3, "b");
  }
  color("Grey") linear_extrude(height=1.2) {
    drawChar(28, 7.3, "e");
    drawChar(30, 7.3, "b");
  }
  color(c="#A6CEE3") linear_extrude(height=1) {
    drawV(4, 6, 3);
    drawCorner(4, 10, 1,0, "1");
    drawH(5, 10, 21);
    drawCorner(26, 10, 0,0, "2");
    drawV(26, 5, 4);
    drawCorner(26, 5, 1,1, "35");
    drawH(27, 5, 1);
    drawCorner(28, 5, 0,1, "36");
    drawV(28, 5, 0);
    drawArrow(28.5, 6);
  }
  color(c="#1F78B4") linear_extrude(height=1) {
    drawV(6, 6, 1);
    drawCorner(6, 8, 1,0, "7");
    drawH(7, 8, 1);
    drawCorner(8, 8, 0,0, "8");
    drawV(8, 5, 2);
    drawCorner(8, 5, 1,1, "30");
    drawH(9, 5, 3);
    drawCorner(12, 5, 0,1, "31");
    drawV(12, 5, 0);
    drawArrow(12.5, 6);
  }
  color(c="#B2DF8A") linear_extrude(height=1) {
    drawV(12, 6, 1);
    drawCorner(12, 8, 1,0, "9");
    drawH(13, 8, 3);
    drawCorner(16, 8, 0,0, "10");
    drawV(16, 5, 2);
    drawCorner(16, 5, 1,1, "32");
    drawH(17, 5, 3);
    drawCorner(20, 5, 0,1, "33");
    drawV(20, 5, 0);
    drawArrow(20.5, 6);
  }
  color(c="#33A02C") linear_extrude(height=1) {
    drawV(14, 6, 2);
    drawCorner(14, 9, 0,0, "5");
    drawH(11, 9, 3);
    drawCorner(10, 9, 1,0, "4");
    drawV(10, 3, 5);
    drawCorner(10, 3, 0,1, "43");
    drawH(5, 3, 5);
    drawCorner(4, 3, 1,1, "42");
    drawV(4, 3, 2);
    drawArrow(4.5, 6);
  }
  color(c="#FB9A99") linear_extrude(height=1) {
    drawV(20, 6, 1);
    drawCorner(20, 8, 0,0, "12");
    drawH(19, 8, 1);
    drawCorner(18, 8, 1,0, "11");
    drawV(18, 4, 3);
    drawCorner(18, 4, 0,1, "40");
    drawH(7, 4, 11);
    drawCorner(6, 4, 1,1, "39");
    drawV(6, 4, 1);
    drawArrow(6.5, 6);
  }
  color(c="#E31A1C") linear_extrude(height=1) {
    drawV(22, 6, 1);
    drawCorner(22, 8, 1,0, "13");
    drawH(23, 8, 1);
    drawCorner(24, 8, 0,0, "14");
    drawV(24, 3, 4);
    drawCorner(24, 3, 0,1, "45");
    drawH(15, 3, 9);
    drawCorner(14, 3, 1,1, "44");
    drawV(14, 3, 2);
    drawArrow(14.5, 6);
  }
  color("Black") linear_extrude(height=1) {
    drawComplement(6, 6);
    drawComplement(14, 6);
    drawComplement(22, 6);
    drawComplement(30, 6);
  }
}
drawStuff();
