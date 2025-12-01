#!/usr/bin/env python3
# -*- mode: python -*-

# Given an ascii graphic of a graph, drawn with _, /, \, #, X, and
# space characters, write a .scad file to draw it using OpenSCAD 2D
# graphics, extruded to 3D.  Lines containing characters other than
# those are treated as text lines, and may be displayed or not
# depending on options.

# Command-line options take the form `value` or `opt=value` (less
# quotes) where opt is in the set {node, loci, text, file} and where
# value is an input file name or is a color name or number (6-digit
# hex RGB or 8-digit hex RGBA).  See README.rst for examples.

# Note, default for `file` is 'validation/draw_nodes/basic_test_set.txt', which is a file of test
# examples.  Note, a bare value is treated like file=value.  For
# example, "drawNodes myfile" reads data from myfile with other
# options defaulted.

from sys import argv

def heading(ofile):
    import datetime
    dt = datetime.datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
    return f'// File {ofile}, generated {dt} by drawNodes' + '''
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
'''

def colorFix(h):  # Put # at front of color-value hex-digits string
    try:  x = int(h,16); return '#'+h
    except: return h
#==============================================================
class Junction:
    cc = ['UR','LR','UL','LL','CL','XM','HM','HX']
    def __init__(self, num, row, col, code):
        self.num, self.code = num, code
        self.row, self.col  = row, col
        self.conn  = []         # No links yet to any neighbors
    def setConn(self, c):
        if c and c not in self.conn:
            self.conn.append(c)
            c.setConn(self)
    def canon(p,q): return (min(p.col,q.col),max(p.col,q.col),min(p.row,q.row),max(p.row,q.row))
    def __str__(self):
        return f' {self.num:2} {self.row:2} {self.col:2} {self.cc[self.code]}'
    def __repr__(self): return f'{str(self)} {[str(c) for c in self.conn]}'
#==============================================================
def process(idata, ofile, custom_colors=None, options=None):
    UR, LR, UL, LL, CL, XM, HM, HX = range(8) # Set Corner & Mark Codes
    def upChar(dx):   # Return neighbor char from previous line
        if linn>0 and (0<= col+dx < len(idata[linn-1])):
            return idata[linn-1][col+dx]
        return '?'   # No character available?
        
    # Find locations of corners etc
    corners, nodes, xlist, chars, linn, maxy = [], [], [], [], 0, len(idata)
    for linn, l in enumerate(idata):
        if not all(c in 'X#|_ /\\' for c in l):
            chars.append((linn,l)); continue
        # Now l only has suitable drawing characters
        pc = None
        for col, c in enumerate(l):
            num = len(corners)
            if c=='/':
                if upChar(0) in '|#\\': # Need to check LR before UL
                    corners.append(Junction(num, linn,col,LR)) # Lower Right
                elif upChar(1)=='_':
                    corners.append(Junction(num, linn,col,UL)) # Upper Left
            elif c=='\\':
               if upChar(0) in '|#/': # Need to check LL before UR
                    corners.append(Junction(num, linn,col,LL)) # Lower Left
               elif upChar(-1)=='_':
                    corners.append(Junction(num, linn,col,UR)) # Upper Right
            elif c=='#':
                hcode = HX if pc=='#' else HM
                corners.append(Junction(num, linn,col, hcode)) # Hashmark
                nodes.append(corners[num])
            elif c=='X':
                corners.append(Junction(num, linn,col,XM)) # Xmark
                xlist.append(corners[num])
            pc = c
        corners.append(Junction(0,0,0,0)) # Need extra node for xfar testing

    def hhfind(cor):
        for c in corners[1+cor.num:]:
            #if (c.code==UR or c.code==LR) and c.row==cor.row: return corners[c.num]
            if c.code==UR and c.row==cor.row: return corners[c.num]
            if c.code==LR and c.row==cor.row: return corners[c.num]

        return None   # not found??
    def vvfind(cor):
        for c in corners[1+cor.num:]:
            if (c.code==LL or c.code==LR or c.code>CL) and c.col==cor.col:
                return corners[c.num]
        return None   # not found??
        
    for cor in corners:         # Connect up the pieces
        if cor.code in (UL, LL):            
            cor.setConn(hhfind(cor))    # Find & set end-column
        if cor.code in (UL, UR, HM, HX):
            cor.setConn(vvfind(cor))    # Find & set end-row

    if 'x234etc' == ofile:
        for c in corners[:25]: print(repr(c))

    def aColor(n): # Return nth entry from list of colors
        # Default colors: ColorBrewer's Paired palette (12 colors)
        # Designed for categorical data with built-in light-dark pairing
        colist = ('#A6CEE3','#1F78B4','#B2DF8A','#33A02C','#FB9A99','#E31A1C',
                  '#FDBF6F','#FF7F00','#CAB2D6','#6A3D9A','#FFFF99','#B15928')
        return colist[(n if n else 0)%len(colist)]

    def drawCorner(c):
        dy, dx = c.code&1, c.code//2
        fout.write (f'    drawCorner({c.col}, {maxy-c.row}, {dx},{dy}, "{c.num}");\n')
    def drawV(c, erow):
        if not erow==c.row:
            base = min(maxy-c.row, maxy-erow)
            #fout.write (f'    drawV({c.col}, {base}, {abs(c.row+1-erow)});\n')
            fout.write (f'    drawV({c.col}, {base}, {abs(c.row-erow)-1});\n')
    def drawH(c, ecol):
        if not ecol==c.col:
            base = min(c.col, ecol)
            fout.write (f'    drawH({base+1}, {maxy-c.row}, {abs(c.col-ecol)-1});\n')

    def colorTrace(c, d):
        if c.canon(d) in drawn: return
        code = c.code
        # Draw c to d
        if code<CL:
            drawCorner(c)
        drawH(c, d.col) # Draw to end-column, if ok
        drawV(c, d.row) # Draw to end-row, if ok
        drawn[c.canon(d)] = 1
        if d.code < CL:
            for e in d.conn:
                colorTrace(d, e)

    drawn = {}                  # Nothing yet drawn
    with open(ofile+'.scad', 'w') as fout:

        fout.write (heading(ofile)) # Write some drawing modules
        
        if options['node']:     # Open nodes color block?
            fout.write (f'  color("{colorFix(options["node"])}") linear_extrude(height=1)' + ' {\n')
            for b in nodes:
                if b.code == HM:
                    xfar = 1
                    while corners[b.num+xfar].col==b.col+xfar and corners[b.num+xfar].code==HX:
                        xfar += 1
                    fout.write (f'    drawNode({b.col}, {maxy-b.row},{xfar});\n')
            fout.write ('  }\n')    # Close drawNode's color block

        if options['text']:     # Open show-loci-numbers color block?
            fout.write (f'  color(c="{colorFix(options["text"])}") linear_extrude(height=1)' + ' {\n')
            for row, txt in chars:
                for (col, c) in enumerate(txt):
                    if c != ' ':
                        fout.write (f'  drawChar({col}, {maxy-row}, "{c}");\n')
            fout.write ('  }\n')    # Close text-stuff color block

        loci = 0
        if options['loci']:
            # Open show-loci-numbers color block
            fout.write (f'  color(c="{colorFix(options["loci"])}") linear_extrude(height=1.2)' + ' {\n')
            for b in nodes:   # Display loci numbers in selected color
                if b.conn:
                    fout.write (f'    drawChar({b.col+0.2}, {maxy-b.row+0.1}, "{loci}");\n')
                    loci += 1
            fout.write ('  }\n')    # Close loci-numbering color block

        # Draw X marks at input positions in grey (matches unused output color)
        if xlist:
            fout.write ('  color("Grey") linear_extrude(height=1.2) {\n')
            for x in xlist:
                fout.write (f'    drawChar({x.col}, {maxy-x.row}, "X");\n')
            fout.write ('  }\n')    # Close X marks color block

        # First pass: collect ALL output column positions from all nodes
        all_output_columns = []
        for b in nodes:
            if b.code == HM:
                # Find the extent of this node (HM + consecutive HX)
                xfar = 1
                while corners[b.num+xfar].col==b.col+xfar and corners[b.num+xfar].code==HX:
                    xfar += 1
                # Add only actual output columns (first and last of node extent)
                all_output_columns.append(b.col)  # First output
                if xfar > 1:
                    all_output_columns.append(b.col + xfar - 1)  # Second output (rightmost)

        # Sort columns and create position -> color index mapping
        all_output_columns.sort()
        col_to_color_idx = {col: idx for idx, col in enumerate(all_output_columns)}

        # Second pass: collect output traces (only connected outputs)
        output_traces = []
        for b in nodes:
            for d in b.conn:
                # Only collect traces from tops of nodes
                if d.num > b.num: continue
                output_traces.append((b.col, b, d))

        # Draw traces with colors based on positional index
        colorNum = 1                # Skip first two colors at outset
        for (col, b, d) in output_traces:
            # Look up positional index for this column
            pos_idx = col_to_color_idx.get(col, 0)

            # Determine color for this output position
            if custom_colors:
                # Use custom color if available, cycling if necessary
                color_idx = pos_idx % len(custom_colors)
                colorName = colorFix(custom_colors[color_idx])
            else:
                # Fall back to auto-assigned colors (use positional index directly)
                colorName = aColor(pos_idx)

            # Start a current-trace color-block
            fout.write (f'  color(c="{colorName}") linear_extrude(height=1) ' + '{\n')
            colorTrace(b, d) # Draw the whole path
            # Close the current-trace color-block
            fout.write ('  }\n')

        # Close drawStuff module and invoke it
        fout.write ('}\ndrawStuff();\n')
#======================================================================
def main():
    # Set up default options to number the loci in red; suppress text;
    # paint node bodies in a pale blue; and by default read from t1-data.
    options = { 'loci':'Red', 'text':'', 'node':'0000FF20', 'file':'validation/draw_nodes/basic_test_set.txt'}
    arn, idata = 0, []
    while (arn := arn+1) < len(argv):
        if '=' in argv[arn]:
            opt, val = argv[arn].split('=')
            options[opt] = val
        else: options['file'] = argv[arn] # Default case = file name
    with open(options['file'], 'r') as fin:
        while a := fin.readline():
            # Read text for one diagram; send that text to process().
            if a[0]=='=':           # Detect opening =
                idata, ofile = [], a[1:].rstrip()
                custom_colors = None
                while a := fin.readline():   # Allow blank lines
                    a = a.rstrip()  # Drop ending whitespace
                    if a and a=='=':   # Detect closing =
                        process(idata, ofile, custom_colors, options)
                        break
                    elif a.startswith('@colors='):
                        # Parse @colors=Red,Blue,Green,#FF00FF,...
                        try:
                            color_string = a[8:].strip()
                            if color_string:
                                custom_colors = [c.strip() for c in color_string.split(',')]
                            else:
                                custom_colors = None
                        except Exception as e:
                            print(f"Warning: Invalid colors format: {a} - {e}")
                            custom_colors = None
                    else:
                        idata.append(a)

if __name__ == "__main__":
    main()
