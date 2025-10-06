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

# Note, default for `file` is 'aTestSet', which is a file of test
# examples.  Note, a bare value is treated like file=value.  For
# example, "drawNodes myfile" reads data from myfile with other
# options defaulted.

from sys import argv
from collections import deque

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
class Edge:
    def __init__(self, label, start_row, start_col, end_row, end_col, source_node, dest_node):
        self.label = label
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.source_node = source_node
        self.dest_node = dest_node

    def draw_labels(self, fout, maxy):
        """Draw label at both ends of the edge"""
        # Draw at output (just above source node at row+1.3)
        fout.write(f'    drawChar({self.start_col}, {maxy-self.source_node.row+1.3}, "{self.label}");\n')
        # Draw at input (at input row position, same level as X marks)
        fout.write(f'    drawChar({self.end_col}, {maxy-self.end_row}, "{self.label}");\n')

    def __repr__(self):
        return f'Edge({self.label}: ({self.start_row},{self.start_col}) -> ({self.end_row},{self.end_col}))'
#==============================================================
def process(idata, ofile):
    UR, LR, UL, LL, CL, XM, HM, HX = range(8) # Set Corner & Mark Codes
    def upChar(dx):   # Return neighbor char from previous line
        if linn>0 and (0<= col+dx < len(idata[linn-1])):
            return idata[linn-1][col+dx]
        return '?'   # No character available?

    # Find locations of corners etc
    corners, nodes, xlist, chars, linn, maxy = [], [], [], [], 0, len(idata)
    labels = {}  # Store (row, col) -> letter for edge labels

    for linn, l in enumerate(idata):
        # Extract labels (single letters) from each line
        for col, c in enumerate(l):
            if c.isalpha() and c.islower():
                labels[(linn, col)] = c

        # Check if line has any drawing characters for junction processing
        has_drawing_chars = any(c in 'X#_ /\\' for c in l)
        # Check if line has any non-drawing, non-space, non-label characters
        has_other_chars = any(c not in 'X#|_ /\\' and not c.isspace() and not (c.isalpha() and c.islower()) for c in l)

        if not has_drawing_chars or has_other_chars:
            chars.append((linn,l)); continue
        # Now l has drawing characters and possibly labels
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
        # Colors like RGB ff00ff and RGBA 7F9F0080 also are ok to list
        colist = ('Black','Red','Green','Yellow','Blue','Magenta','Cyan','White','Orange')
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

    def find_destination(c, d, visited=None):
        """Follow a trace path to find its destination node/X-mark and column.
        Similar to colorTrace but returns destination info instead of drawing."""
        if visited is None:
            visited = set()

        canon = c.canon(d)
        if canon in visited:
            return None, None
        visited.add(canon)

        # If d is a destination (node or X mark), return it
        if d.code >= CL:  # HM, HX, or XM
            dest_col = c.col  # Use the column where trace actually arrives
            dest_junction = d  # Default to d

            # If it's an HX (node continuation), find the HM for node reference
            if d.code == HX:
                # Search backward to find the HM that starts this node
                # Keep dest_col as c.col (actual arrival), but return HM junction
                for i in range(d.num - 1, -1, -1):
                    if corners[i].row == d.row and corners[i].code == HM:
                        dest_junction = corners[i]  # Use HM for node reference
                        break

            return dest_junction, dest_col

        # If d is a corner, continue tracing through its connections
        if d.code < CL:
            for e in d.conn:
                # colorTrace doesn't filter connections at corners, only at the starting node
                dest, dest_col = find_destination(d, e, visited)
                if dest:
                    return dest, dest_col

        return None, None

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

    # Find the row where node labels appear (row above nodes)
    label_row = None
    if nodes:
        label_row = min(n.row for n in nodes) - 1

    # Build edges with labels
    edges = []
    used_outputs = set()  # Track (node_row, out_col) for outputs that have edges
    all_output_labels = []  # Track all (node_row, out_col, label) tuples

    for node in nodes:
        if node.code != HM:
            continue

        # Find the extent of this node (HM + consecutive HX)
        xfar = 1
        while node.num+xfar < len(corners) and corners[node.num+xfar].col==node.col+xfar and corners[node.num+xfar].code==HX:
            xfar += 1
        node_end_col = node.col + xfar

        # Find all labels in the label row that are above this node
        output_labels = {}  # Map col -> label
        if label_row is not None:
            for (lr, lc), label in labels.items():
                if lr == label_row and node.col <= lc < node_end_col:
                    output_labels[lc] = label
                    # Track all output labels for later unused output detection
                    all_output_labels.append((node.row, lc, label))

        # Collect connections from ALL junctions within the node's extent (HM + HX)
        # Each HX junction can also have upward connections for additional outputs
        all_conns = []
        for junction in corners:
            # Check if this junction is part of this node (same row, within node extent)
            if junction.row == node.row and node.col <= junction.col < node_end_col:
                # Collect upward connections from this junction
                for d in junction.conn:
                    if d.num <= junction.num:  # Same filter as colorTrace
                        all_conns.append((junction.col, d))
        all_conns.sort(key=lambda x: x[0])  # Sort by column only

        # Get sorted output labels
        sorted_labels = sorted(output_labels.items())  # [(col, label), ...]

        # Match labels with connections by index
        # If more labels than connections, later labels won't get matched
        for idx, (out_col, label) in enumerate(sorted_labels):
            dest = None
            dest_col = None

            if idx < len(all_conns):
                conn_col, d = all_conns[idx]

                # Find the junction at conn_col to use as starting point
                start_junction = None
                for j in corners:
                    if j.row == node.row and j.col == conn_col:
                        start_junction = j
                        break

                # Find destination for this connection
                if start_junction:
                    dest, dest_col = find_destination(start_junction, d)

            # Only create edges to nodes (not X marks - those are for inputs)
            if dest and dest.code >= HM:  # HM or HX (node junctions, not XM)
                # Create Edge object with label positions
                start_row = node.row - 1  # Just above source node
                start_col = out_col
                end_row = dest.row + 1    # Just below destination
                end_col = dest_col

                edge = Edge(label, start_row, start_col, end_row, end_col, node, dest)
                edges.append(edge)

                # Mark this output as used
                used_outputs.add((node.row, out_col))

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

            # Draw X marks at input positions
            for x in xlist:
                fout.write (f'  linear_extrude(height=1.2) drawChar({x.col}, {maxy-x.row}, "X");\n')

        # Draw edge labels in black
        if edges:
            fout.write ('  color("Black") linear_extrude(height=1.1) {\n')
            for edge in edges:
                edge.draw_labels(fout, maxy)
            fout.write ('  }\n')    # Close edge labels color block

        # Draw gray labels for unused outputs
        unused_outputs = [(row, col, label) for (row, col, label) in all_output_labels
                          if (row, col) not in used_outputs]
        if unused_outputs:
            fout.write ('  color("Grey") linear_extrude(height=1.2) {\n')
            for row, col, label in unused_outputs:
                # Draw at output position (above node)
                fout.write (f'    drawChar({col}, {maxy-row+1.3}, "{label}");\n')
            fout.write ('  }\n')    # Close unused output labels color block

        colorNum = 1                # Skip first two colors at outset
        for b in nodes:   # Do traces from tops of nodes
            for d in b.conn:
                # Only draw traces from tops of nodes
                if d.num > b.num: continue
                # Start a current-trace color-block
                colorNum += 1
                colorName = aColor(colorNum)
                fout.write (f'  color(c="{aColor(colorNum)}") linear_extrude(height=1) ' + '{\n')
                colorTrace(b, d) # Draw the whole path
                # Close the current-trace color-block
                fout.write ('  }\n')

        # Draw complement circles on 2nd output of each node (drawn last so they appear on top)
        fout.write ('  color("Black") linear_extrude(height=1) {\n')
        for node in nodes:
            if node.code != HM:
                continue
            # Find the extent of this node (HM + consecutive HX)
            xfar = 1
            while node.num+xfar < len(corners) and corners[node.num+xfar].col==node.col+xfar and corners[node.num+xfar].code==HX:
                xfar += 1
            node_end_col = node.col + xfar

            # Draw complement circle on 2nd output
            # The 2nd output is at the last column of the node extent
            second_col = node_end_col - 1
            fout.write(f'    drawComplement({second_col}, {maxy-node.row});\n')
        fout.write ('  }\n')    # Close complement circles color block

        # Close drawStuff module and invoke it
        fout.write ('}\ndrawStuff();\n')
#======================================================================
# Set up default options to number the loci in red; suppress text;
# paint node bodies in a pale blue; and by default read from t1-data.
options = { 'loci':'Red', 'text':'', 'node':'0000FF20', 'file':'aTestSet'}
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
            while a := fin.readline():   # Allow blank lines
                a = a.rstrip()  # Drop ending whitespace
                if a and a=='=':   # Detect closing =
                    process(idata, ofile)
                    break
                idata.append(a)
