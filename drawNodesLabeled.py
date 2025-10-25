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
import subprocess

def heading(ofile):
    import datetime
    dt = datetime.datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
    return f'// File {ofile}, generated {dt} by drawNodes' + '''
/* [Label Colors] */
// Color for edge labels
label_color = "Black";
// Color for label halo/outline (using over-bright RGB to compensate for lighting)
label_halo_color = [1.5,1.5,1.5];

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
module drawCharBold(x,y,t)
  translate (scale*[x,y,0]) text(t, size=textFrac*scale, font=":style=Bold");
module drawCharBoldItalic(x,y,t)
  translate (scale*[x,y,0]) text(t, size=textFrac*scale, font=":style=Bold Italic");
module drawCharItalic(x,y,t)
  translate (scale*[x,y,0]) text(t, size=textFrac*scale, font=":style=Italic");
module drawCharHalo(x,y,t) {
  // Regular font halo with 4-directional shifts for complete outline
  translate (scale*[x-0.04,y,0]) text(t, size=textFrac*scale);
  translate (scale*[x+0.04,y,0]) text(t, size=textFrac*scale);
  translate (scale*[x,y-0.04,0]) text(t, size=textFrac*scale);
  translate (scale*[x,y+0.04,0]) text(t, size=textFrac*scale);
}
module drawCharHaloBold(x,y,t) {
  // Bold font halo with 4-directional shifts for complete outline
  translate (scale*[x-0.04,y,0]) text(t, size=textFrac*scale, font=":style=Bold");
  translate (scale*[x+0.04,y,0]) text(t, size=textFrac*scale, font=":style=Bold");
  translate (scale*[x,y-0.04,0]) text(t, size=textFrac*scale, font=":style=Bold");
  translate (scale*[x,y+0.04,0]) text(t, size=textFrac*scale, font=":style=Bold");
}
module drawCharHaloBoldItalic(x,y,t) {
  // Bold italic font halo with 4-directional shifts for complete outline
  translate (scale*[x-0.04,y,0]) text(t, size=textFrac*scale, font=":style=Bold Italic");
  translate (scale*[x+0.04,y,0]) text(t, size=textFrac*scale, font=":style=Bold Italic");
  translate (scale*[x,y-0.04,0]) text(t, size=textFrac*scale, font=":style=Bold Italic");
  translate (scale*[x,y+0.04,0]) text(t, size=textFrac*scale, font=":style=Bold Italic");
}
module drawCharHaloItalic(x,y,t) {
  // Italic font halo with 4-directional shifts for complete outline
  translate (scale*[x-0.04,y,0]) text(t, size=textFrac*scale, font=":style=Italic");
  translate (scale*[x+0.04,y,0]) text(t, size=textFrac*scale, font=":style=Italic");
  translate (scale*[x,y-0.04,0]) text(t, size=textFrac*scale, font=":style=Italic");
  translate (scale*[x,y+0.04,0]) text(t, size=textFrac*scale, font=":style=Italic");
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
'''

def colorFix(h):  # Put # at front of color-value hex-digits string
    try:  x = int(h,16); return '#'+h
    except: return h
#==============================================================
def calculate_camera_params(bbox, border=0, scale=10, target_imgsize=None):
    """Calculate camera position and image size from bounding box using orthographic projection formula

    OpenSCAD orthographic projection formula:
        visible_width = ($vpd / sqrt(1 + aspect^2)) * aspect
        visible_height = $vpd / sqrt(1 + aspect^2)

    Solving for $vpd:
        $vpd = visible_width * sqrt(1 + aspect^2) / aspect
        $vpd = visible_height * sqrt(1 + aspect^2)

    Args:
        bbox: (min_col, max_col, min_row, max_row, maxy)
        border: Border padding as percentage (default 0%)
        scale: OpenSCAD scale factor (default 10)
        target_imgsize: Optional (width, height) to fit drawing into with minimum border
    """
    import math

    min_col, max_col, min_row, max_row, maxy = bbox

    # Calculate center point in OpenSCAD coordinates
    # Add +1 to center_x and dimensions to account for grid cell extent (elements occupy full cells)
    # Note: center_y uses inverted coordinates (maxy - row) so +1 adjustment not needed
    center_x = (min_col + max_col + 1) / 2 * scale
    center_y = (maxy - (min_row + max_row) / 2) * scale

    # Calculate drawing dimensions in OpenSCAD units
    # Add +1 to account for grid cell extent
    width = (max_col - min_col + 1) * scale
    height = (max_row - min_row + 1) * scale

    if target_imgsize:
        # When imgsize is specified, calculate $vpd to fit drawing with border
        img_width, img_height = target_imgsize

        # Calculate image aspect ratio
        image_aspect = img_width / img_height if img_height > 0 else 1

        # Calculate desired visible dimensions (drawing + border)
        border_fraction = border / 100
        visible_width = width * (1 + border_fraction)
        visible_height = height * (1 + border_fraction)

        # Calculate diagonal scaling factor
        diag_scale = math.sqrt(1 + image_aspect**2)

        # Calculate $vpd needed for each dimension
        vpd_for_width = visible_width * diag_scale / image_aspect
        vpd_for_height = visible_height * diag_scale

        # Use the larger $vpd to ensure both dimensions fit
        z_height = max(vpd_for_width, vpd_for_height)

        return (center_x, center_y, z_height), target_imgsize
    else:
        # Auto-calculate imgsize with border percentage applied to each dimension
        border_fraction = border / 100

        # Add border to each dimension
        visible_width = width * (1 + border_fraction)
        visible_height = height * (1 + border_fraction)

        # Calculate imgsize at 10px per unit
        img_width = int(visible_width * 10)
        img_height = int(visible_height * 10)

        # Round to nearest 50 pixels
        img_width = ((img_width + 25) // 50) * 50
        img_height = ((img_height + 25) // 50) * 50

        # Calculate actual aspect ratio after rounding
        image_aspect = img_width / img_height if img_height > 0 else 1

        # Calculate diagonal scaling factor
        diag_scale = math.sqrt(1 + image_aspect**2)

        # Calculate $vpd needed for each dimension
        vpd_for_width = visible_width * diag_scale / image_aspect
        vpd_for_height = visible_height * diag_scale

        # Use the larger $vpd to ensure both dimensions fit
        z_height = max(vpd_for_width, vpd_for_height)

        return (center_x, center_y, z_height), (img_width, img_height)

def generate_png(ofile, imgsize, camera, border=0):
    """Generate PNG from SCAD file using OpenSCAD CLI

    Args:
        border: Border size in pixels (default 0). Applied via ImageMagick after trimming.
    """
    if not imgsize or not camera:
        print(f"Warning: Missing metadata for {ofile}, skipping PNG generation")
        return

    w, h = imgsize
    x, y, z = camera

    cmd = [
        'openscad',
        '-o', f'{ofile}.png',
        '--imgsize', f'{w},{h}',
        '--camera', f'{x},{y},{z},{x},{y},0',
        '--projection=ortho',
        '--autocenter',
        '--colorscheme', 'Cornfield',
        f'{ofile}.scad'
    ]

    try:
        print(f"Generating {ofile}.png...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"Successfully generated {ofile}.png")

            # Make background transparent, trim excess, and add border using ImageMagick
            # Cornfield colorscheme uses RGB(255,255,229) as background
            # Use -fuzz to handle anti-aliasing at edges
            convert_cmd = [
                'convert',
                f'{ofile}.png',
                '-fuzz', '5%',
                '-transparent', 'rgb(255,255,229)',
                '-trim',  # Always trim to remove excess transparent border
            ]
            # Add border if requested
            if border > 0:
                convert_cmd.extend(['-bordercolor', 'none', '-border', str(int(border))])
            convert_cmd.append(f'{ofile}.png')

            print(f"Making background transparent and trimming...")
            convert_result = subprocess.run(convert_cmd, capture_output=True, text=True, timeout=30)
            if convert_result.returncode == 0:
                if border > 0:
                    print(f"Successfully created transparent background with {int(border)}px border")
                else:
                    print(f"Successfully created transparent background (trimmed)")
            else:
                print(f"Warning: Could not process image: {convert_result.stderr}")
        else:
            print(f"Error generating {ofile}.png: {result.stderr}")
    except FileNotFoundError:
        print("Error: openscad command not found. Please install OpenSCAD.")
    except subprocess.TimeoutExpired:
        print(f"Error: OpenSCAD timed out generating {ofile}.png")
    except Exception as e:
        print(f"Error generating {ofile}.png: {e}")
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
    def __init__(self, label, start_row, start_col, end_row, end_col, source_node, dest_node, is_out2=False):
        self.label = label
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.source_node = source_node
        self.dest_node = dest_node
        self.is_out2 = is_out2  # True if this is the second output (out2), False for out1

    def draw_labels(self, fout, maxy, layer='label'):
        """Draw label at both ends of the edge

        Args:
            layer: 'halo' for white background layer, 'label' for actual label
        """
        # Use matching font style for halos and labels
        # Bold for out1, bold italic for out2
        # Italic for inputs from out2, regular for inputs from out1
        if layer == 'halo':
            draw_func_output = 'drawCharHaloBoldItalic' if self.is_out2 else 'drawCharHaloBold'
            draw_func_input = 'drawCharHaloItalic' if self.is_out2 else 'drawCharHalo'
        else:
            draw_func_output = 'drawCharBoldItalic' if self.is_out2 else 'drawCharBold'
            draw_func_input = 'drawCharItalic' if self.is_out2 else 'drawChar'

        # Draw at output (just above source node at row+1.3) - BOLD or BOLD ITALIC
        fout.write(f'    {draw_func_output}({self.start_col}, {maxy-self.source_node.row+1.3}, "{self.label}");\n')
        # Draw at input (at input row position, same level as X marks) - ITALIC if from out2, REGULAR if from out1
        fout.write(f'    {draw_func_input}({self.end_col}, {maxy-self.end_row}, "{self.label}");\n')

    def __repr__(self):
        return f'Edge({self.label}: ({self.start_row},{self.start_col}) -> ({self.end_row},{self.end_col}))'
#==============================================================
def process(idata, ofile, custom_colors=None):
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

        # Draw arrowhead if d is a destination node (HM or HX, not XM)
        if d.code >= HM:  # Node destination
            # Arrow at bottom edge of node, centered on trace (col+0.5 due to wf offset)
            fout.write(f'    drawArrow({c.col+0.5}, {maxy-d.row});\n')

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
        # Map column -> list of connections from that column
        conns_by_col = {}
        for junction in corners:
            # Check if this junction is part of this node (same row, within node extent)
            if junction.row == node.row and node.col <= junction.col < node_end_col:
                # Collect upward connections from this junction
                for d in junction.conn:
                    if d.num <= junction.num:  # Same filter as colorTrace
                        if junction.col not in conns_by_col:
                            conns_by_col[junction.col] = []
                        conns_by_col[junction.col].append((junction, d))

        # Match labels with connections by column position
        for out_col, label in output_labels.items():
            dest = None
            dest_col = None

            # Find connection originating from the same column as the label
            if out_col in conns_by_col:
                # Use the first connection from this column
                # (typically there's only one upward connection per column)
                start_junction, d = conns_by_col[out_col][0]

                # Find destination for this connection
                dest, dest_col = find_destination(start_junction, d)

            # Only create edges to nodes (not X marks - those are for inputs)
            if dest and dest.code >= HM:  # HM or HX (node junctions, not XM)
                # Create Edge object with label positions
                start_row = node.row - 1  # Just above source node
                start_col = out_col
                end_row = dest.row + 1    # Just below destination
                end_col = dest_col

                # Determine if this is out2 (rightmost column of node)
                is_out2 = (out_col == node.col + xfar - 1)

                edge = Edge(label, start_row, start_col, end_row, end_col, node, dest, is_out2)
                edges.append(edge)

                # Mark this output as used
                used_outputs.add((node.row, out_col))

    drawn = {}                  # Nothing yet drawn
    with open(ofile+'.scad', 'w') as fout:

        fout.write (heading(ofile)) # Write some drawing modules

        # Draw node outlines in black (before filled nodes so outline shows)
        fout.write ('  color("Black") linear_extrude(height=1) {\n')
        for b in nodes:
            if b.code == HM:
                xfar = 1
                while corners[b.num+xfar].col==b.col+xfar and corners[b.num+xfar].code==HX:
                    xfar += 1
                fout.write (f'    drawNodeOutline({b.col}, {maxy-b.row},{xfar},wFrac);\n')
        fout.write ('  }\n')    # Close node outline color block

        if options['node']:     # Open nodes color block?
            fout.write (f'  color("{colorFix(options["node"])}") linear_extrude(height=1)' + ' {\n')
            for b in nodes:
                if b.code == HM:
                    xfar = 1
                    while corners[b.num+xfar].col==b.col+xfar and corners[b.num+xfar].code==HX:
                        xfar += 1
                    fout.write (f'    drawNode({b.col}, {maxy-b.row},{xfar});\n')
            fout.write ('  }\n')    # Close drawNode's color block

        # Draw XOR symbols (circled plus) in center of each node
        fout.write ('  color("Black") linear_extrude(height=1.1) {\n')
        for b in nodes:
            if b.code == HM:
                xfar = 1
                while corners[b.num+xfar].col==b.col+xfar and corners[b.num+xfar].code==HX:
                    xfar += 1
                fout.write (f'    drawXorSymbol({b.col}, {maxy-b.row},{xfar});\n')
        fout.write ('  }\n')    # Close XOR symbol color block

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

        # Draw white halos for edge labels (background layer)
        if edges:
            fout.write ('  color(label_halo_color) linear_extrude(height=1.09) {\n')
            for edge in edges:
                edge.draw_labels(fout, maxy, layer='halo')
            fout.write ('  }\n')    # Close edge label halos color block

        # Draw edge labels in black (foreground layer)
        if edges:
            fout.write ('  color(label_color) linear_extrude(height=1.1) {\n')
            for edge in edges:
                edge.draw_labels(fout, maxy, layer='label')
            fout.write ('  }\n')    # Close edge labels color block

        # Draw gray labels for unused outputs
        unused_outputs = [(row, col, label) for (row, col, label) in all_output_labels
                          if (row, col) not in used_outputs]

        # Build a map to determine which outputs are out2 (rightmost column of each node)
        node_rightmost_cols = {}  # node.row -> rightmost column
        for node in nodes:
            if node.code == HM:
                xfar = 1
                while node.num+xfar < len(corners) and corners[node.num+xfar].col==node.col+xfar and corners[node.num+xfar].code==HX:
                    xfar += 1
                node_rightmost_cols[node.row] = node.col + xfar - 1

        # Draw white halos for unused output labels (background layer)
        if unused_outputs:
            fout.write ('  color(label_halo_color) linear_extrude(height=1.19) {\n')
            for row, col, label in unused_outputs:
                # Determine if this is out2 (rightmost column)
                is_out2 = (col == node_rightmost_cols.get(row + 1))  # row+1 because label_row is above node
                halo_func = 'drawCharHaloBoldItalic' if is_out2 else 'drawCharHaloBold'
                # Draw at output position (above node)
                fout.write (f'    {halo_func}({col}, {maxy-row+1.3}, "{label}");\n')
            fout.write ('  }\n')    # Close unused output label halos color block
        # Draw unused output labels in grey (foreground layer) - BOLD or BOLD ITALIC
        if unused_outputs:
            fout.write ('  color("Grey") linear_extrude(height=1.2) {\n')
            for row, col, label in unused_outputs:
                # Determine if this is out2 (rightmost column)
                is_out2 = (col == node_rightmost_cols.get(row + 1))  # row+1 because label_row is above node
                draw_func = 'drawCharBoldItalic' if is_out2 else 'drawCharBold'
                # Draw at output position (above node)
                fout.write (f'    {draw_func}({col}, {maxy-row+1.3}, "{label}");\n')
            fout.write ('  }\n')    # Close unused output labels color block

        # Use label-based approach for color assignment (more robust than node extent detection)
        # Sort output labels by column position (left to right)
        sorted_output_labels = sorted(all_output_labels, key=lambda x: x[1])

        # Create position -> color index mapping from sorted labels
        col_to_color_idx = {col: idx for idx, (row, col, label) in enumerate(sorted_output_labels)}

        # Second pass: collect output traces (only connected outputs)
        output_traces = []
        for b in nodes:
            for d in b.conn:
                # Only collect traces from tops of nodes
                if d.num > b.num: continue
                output_traces.append((b.col, b, d))

        # Draw traces with colors based on positional index from sorted labels
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

    # Calculate bounding box from all corners
    if corners:
        min_col = min(c.col for c in corners if c.code != 0)
        max_col = max(c.col for c in corners if c.code != 0)
        min_row = min(c.row for c in corners if c.code != 0)
        max_row = max(c.row for c in corners if c.code != 0)

        # No fixed padding - use border parameter for padding control
        # This ensures symmetric borders when border > 0
        # Fixed padding was causing asymmetric borders due to center shift
    else:
        min_col = max_col = min_row = max_row = 0

    return (min_col, max_col, min_row, max_row, maxy)
#======================================================================
def print_help():
    """Display help information about command-line options and usage"""
    help_text = """
drawNodesLabeled.py - ASCII Graph to OpenSCAD Converter
========================================================

Convert ASCII art graphs (drawn with _, /, \\, #, X, and spaces) into
OpenSCAD files and optionally PNG images with transparent backgrounds.

USAGE:
    drawNodesLabeled.py [options] [filename]

COMMAND-LINE OPTIONS:
    file=FILENAME       Input file containing ASCII graphs
                        (default: aTestSet)
                        Note: Bare filename also works (e.g., 'myfile')

    node=COLOR          Color for node bodies
                        (default: 0000FF20 - pale blue with transparency)

    loci=COLOR          Color for loci numbers (enables display)
                        (default: '' - disabled)

    text=COLOR          Color for text elements (enables display)
                        (default: '' - disabled)

    png=VALUE           Enable PNG generation (any non-empty value)
                        (default: '' - disabled)

COLOR FORMATS:
    - Named colors:     Red, Green, Blue, Yellow, Black, etc.
    - Hex RGB:          FF0000 (red), 00FF00 (green)
    - Hex RGBA:         FF000080 (red with 50% transparency)
    Note: Do NOT include '#' prefix - it will be added automatically

IN-FILE DIRECTIVES:
    Place these within diagram sections (between = markers):

    @imgsize=WIDTH,HEIGHT    PNG output dimensions in pixels
                             Example: @imgsize=800,600

    @camera=X,Y,Z            Camera position override
                             Example: @camera=150.0,75.0,250.0

    @border=PIXELS           Border size in pixels
                             (default: 0 - trimmed with no border)
                             Example: @border=10

EXAMPLES:
    # Process file with default settings
    drawNodesLabeled.py myfile.txt

    # Generate PNG with custom node color
    drawNodesLabeled.py node=00FF00 png=1 myfile.txt

    # Show loci numbers in red, disable node fill
    drawNodesLabeled.py loci=Red node= myfile.txt

    # Multiple options
    drawNodesLabeled.py file=graphs.txt node=FF0000AA loci=Blue png=1

INPUT FILE FORMAT:
    Files contain one or more diagrams, each enclosed in = markers:

    =diagram_name
    [ASCII art using _, /, \\, #, X characters]
    [Optional: @imgsize=800,600]
    [Optional: @border=10]
    =

    =another_diagram
    [More ASCII art]
    =

OUTPUT:
    - Always generates: diagram_name.scad (OpenSCAD file)
    - With png option:  diagram_name.png (transparent background)

For more information, see README.rst
"""
    print(help_text)
#======================================================================
# Set up default options to suppress loci numbers; suppress text;
# paint node bodies in a pale blue; and by default read from t1-data.
options = { 'loci':'', 'text':'', 'node':'0000FF20', 'file':'aTestSet', 'png':''}

# Check for help flag first
if '--help' in argv or '-h' in argv:
    print_help()
    exit(0)

arn, idata = 0, []
while (arn := arn+1) < len(argv):
    if '=' in argv[arn]:
        opt, val = argv[arn].split('=')
        options[opt] = val
    else: options['file'] = argv[arn] # Default case = file name

# Parse global options (before first diagram)
global_options = {}
with open(options['file'], 'r') as fin:
    # First pass: read global options (lines before first =)
    while True:
        pos = fin.tell()  # Save position before reading
        a = fin.readline()
        if not a:  # EOF
            break
        if a[0] == '=':
            # Found first diagram, go back to this line
            fin.seek(pos)
            break
        # Parse global options
        a = a.rstrip()
        if a.startswith('@imgsize='):
            parts = a[9:].split(',')
            if len(parts) == 2:
                try:
                    global_options['imgsize'] = (int(parts[0]), int(parts[1]))
                except ValueError:
                    print(f"Warning: Invalid global imgsize format: {a}")
        elif a.startswith('@camera='):
            parts = a[8:].split(',')
            if len(parts) == 3:
                try:
                    global_options['camera'] = (float(parts[0]), float(parts[1]), float(parts[2]))
                except ValueError:
                    print(f"Warning: Invalid global camera format: {a}")
        elif a.startswith('@border='):
            try:
                global_options['border'] = float(a[8:])
            except ValueError:
                print(f"Warning: Invalid global border format: {a}")
        elif a.startswith('@colors='):
            try:
                color_string = a[8:].strip()
                if color_string:
                    global_options['colors'] = [c.strip() for c in color_string.split(',')]
            except Exception as e:
                print(f"Warning: Invalid global colors format: {a} - {e}")

    # Second pass: process diagrams
    while a := fin.readline():
        # Read text for one diagram; send that text to process().
        if a[0]=='=':           # Detect opening =
            idata, ofile = [], a[1:].rstrip()
            # Initialize with global defaults
            imgsize = global_options.get('imgsize', None)
            camera = global_options.get('camera', None)
            border = global_options.get('border', None)
            custom_colors = global_options.get('colors', None)

            while a := fin.readline():   # Allow blank lines
                a = a.rstrip()  # Drop ending whitespace
                if a and a=='=':   # Detect closing =
                    # Process the SCAD file (file is fully written when this returns)
                    bbox = process(idata, ofile, custom_colors)

                    # Generate PNG if requested
                    if options['png']:
                        # Use default border if not specified
                        final_border = border if border is not None else 0

                        # Calculate camera/imgsize from bounding box (always with 0 border for tight fit)
                        # Border is applied later via ImageMagick trim+border
                        # Pass imgsize if specified so z_height can be calculated to fit
                        calc_camera, calc_imgsize = calculate_camera_params(
                            bbox, border=0, target_imgsize=imgsize
                        )

                        # Use explicit camera if provided, otherwise use calculated
                        final_camera = camera if camera else calc_camera
                        final_imgsize = imgsize if imgsize else calc_imgsize

                        # Print calculated values for user reference
                        if border is None:
                            print(f"Calculated border: @border={final_border}")
                        if not camera:
                            print(f"Calculated camera: @camera={calc_camera[0]:.1f},{calc_camera[1]:.1f},{calc_camera[2]:.1f}")
                        if not imgsize:
                            print(f"Calculated imgsize: @imgsize={calc_imgsize[0]},{calc_imgsize[1]}")

                        generate_png(ofile, final_imgsize, final_camera, final_border)
                    break
                elif a.startswith('@imgsize='):
                    # Parse @imgsize=800,250
                    parts = a[9:].split(',')
                    if len(parts) == 2:
                        try:
                            imgsize = (int(parts[0]), int(parts[1]))
                        except ValueError:
                            print(f"Warning: Invalid imgsize format: {a}")
                elif a.startswith('@camera='):
                    # Parse @camera=150,50,250
                    parts = a[8:].split(',')
                    if len(parts) == 3:
                        try:
                            camera = (float(parts[0]), float(parts[1]), float(parts[2]))
                        except ValueError:
                            print(f"Warning: Invalid camera format: {a}")
                elif a.startswith('@border='):
                    # Parse @border=20
                    try:
                        border = float(a[8:])
                    except ValueError:
                        print(f"Warning: Invalid border format: {a}")
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
