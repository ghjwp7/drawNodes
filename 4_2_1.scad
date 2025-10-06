// File 4_2_1, generated 2025-10-06  12:36:55 by drawNodes
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
module drawComplement(x,y)
  translate (scale*[x+0.5,y+1+wFrac,0]) circle(d=2*wFrac*scale);
module drawChar(x,y,t)
  translate (scale*[x,y,0]) text(t, size=textFrac*scale);
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
  color("#0000FF20") linear_extrude(height=1) {
    drawNode(4, 6,3);
    drawNode(12, 6,3);
    drawNode(20, 6,3);
    drawNode(28, 6,3);
  }
  color(c="Red") linear_extrude(height=1.2) {
    drawChar(4.2, 6.1, "0");
    drawChar(6.2, 6.1, "1");
    drawChar(12.2, 6.1, "2");
    drawChar(14.2, 6.1, "3");
    drawChar(20.2, 6.1, "4");
    drawChar(22.2, 6.1, "5");
    drawChar(28.2, 6.1, "6");
    drawChar(30.2, 6.1, "7");
  }
  linear_extrude(height=1.2) drawChar(22, 5, "X");
  linear_extrude(height=1.2) drawChar(30, 5, "X");
  color("Black") linear_extrude(height=1.1) {
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
  color("Grey") linear_extrude(height=1.2) {
    drawChar(28, 7.3, "e");
    drawChar(30, 7.3, "b");
  }
  color(c="Green") linear_extrude(height=1) {
    drawV(4, 6, 3);
    drawCorner(4, 10, 1,0, "1");
    drawH(5, 10, 21);
    drawCorner(26, 10, 0,0, "2");
    drawV(26, 5, 4);
    drawCorner(26, 5, 1,1, "35");
    drawH(27, 5, 1);
    drawCorner(28, 5, 0,1, "36");
    drawV(28, 5, 0);
  }
  color(c="Yellow") linear_extrude(height=1) {
    drawV(6, 6, 1);
    drawCorner(6, 8, 1,0, "7");
    drawH(7, 8, 1);
    drawCorner(8, 8, 0,0, "8");
    drawV(8, 5, 2);
    drawCorner(8, 5, 1,1, "30");
    drawH(9, 5, 3);
    drawCorner(12, 5, 0,1, "31");
    drawV(12, 5, 0);
  }
  color(c="Blue") linear_extrude(height=1) {
    drawV(12, 6, 1);
    drawCorner(12, 8, 1,0, "9");
    drawH(13, 8, 3);
    drawCorner(16, 8, 0,0, "10");
    drawV(16, 5, 2);
    drawCorner(16, 5, 1,1, "32");
    drawH(17, 5, 3);
    drawCorner(20, 5, 0,1, "33");
    drawV(20, 5, 0);
  }
  color(c="Magenta") linear_extrude(height=1) {
    drawV(14, 6, 2);
    drawCorner(14, 9, 0,0, "5");
    drawH(11, 9, 3);
    drawCorner(10, 9, 1,0, "4");
    drawV(10, 3, 5);
    drawCorner(10, 3, 0,1, "43");
    drawH(5, 3, 5);
    drawCorner(4, 3, 1,1, "42");
    drawV(4, 3, 2);
  }
  color(c="Cyan") linear_extrude(height=1) {
    drawV(20, 6, 1);
    drawCorner(20, 8, 0,0, "12");
    drawH(19, 8, 1);
    drawCorner(18, 8, 1,0, "11");
    drawV(18, 4, 3);
    drawCorner(18, 4, 0,1, "40");
    drawH(7, 4, 11);
    drawCorner(6, 4, 1,1, "39");
    drawV(6, 4, 1);
  }
  color(c="White") linear_extrude(height=1) {
    drawV(22, 6, 1);
    drawCorner(22, 8, 1,0, "13");
    drawH(23, 8, 1);
    drawCorner(24, 8, 0,0, "14");
    drawV(24, 3, 4);
    drawCorner(24, 3, 0,1, "45");
    drawH(15, 3, 9);
    drawCorner(14, 3, 1,1, "44");
    drawV(14, 3, 2);
  }
  color("Black") linear_extrude(height=1) {
    drawComplement(6, 6);
    drawComplement(14, 6);
    drawComplement(22, 6);
    drawComplement(30, 6);
  }
}
drawStuff();
