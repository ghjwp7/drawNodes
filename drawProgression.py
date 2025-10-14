#!/usr/bin/env python3
# -*- mode: python -*-

# Given an ASCII graphic with edges (drawn with _, /, \, |) and text,
# write a .scad file to draw it using OpenSCAD 2D graphics, extruded to 3D.

from sys import argv
from collections import deque
import subprocess

def heading(ofile):
    import datetime
    dt = datetime.datetime.today().strftime('%Y-%m-%d  %H:%M:%S')
    return f'// File {ofile}, generated {dt} by drawProgression' + '''
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
module drawChar(x,y,t)
  translate (scale*[x,y,0]) text(t, size=textFrac*scale);
module drawCorner(x,y,dx,dy, label="")
  translate (scale*[x,y,0]) {
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

def calculate_camera_params(bbox, border=20, scale=10, target_imgsize=None):
    """Calculate camera position and image size from bounding box"""
    min_col, max_col, min_row, max_row, maxy = bbox

    # Calculate center point in OpenSCAD coordinates
    center_x = (min_col + max_col) / 2 * scale
    center_y = (maxy - (min_row + max_row) / 2) * scale

    # Calculate drawing dimensions in OpenSCAD units
    width = (max_col - min_col) * scale
    height = (max_row - min_row) * scale

    # Add border padding
    padded_width = width * (1 + border / 100)
    padded_height = height * (1 + border / 100)

    if target_imgsize:
        # When imgsize is specified, calculate z_height to fit with minimum border
        img_width, img_height = target_imgsize

        # Compare aspect ratios to determine limiting dimension
        drawing_aspect = padded_width / padded_height if padded_height > 0 else 1
        image_aspect = img_width / img_height if img_height > 0 else 1

        if drawing_aspect > image_aspect:
            # Drawing is relatively wider - width is limiting factor
            z_height = padded_width
        else:
            # Drawing is relatively taller - height is limiting factor
            z_height = padded_height * image_aspect

        return (center_x, center_y, z_height), target_imgsize
    else:
        # Auto-calculate imgsize with border percentage applied to each dimension
        border_fraction = border / 100

        # Add border to each dimension
        padded_width = width * (1 + border_fraction)
        padded_height = height * (1 + border_fraction)

        # Calculate imgsize at 10px per unit
        img_width = int(padded_width * 10)
        img_height = int(padded_height * 10)

        # Round to nearest 50 pixels
        img_width = ((img_width + 25) // 50) * 50
        img_height = ((img_height + 25) // 50) * 50

        # z_height is the larger padded dimension to ensure everything fits
        z_height = max(padded_width, padded_height)

        return (center_x, center_y, z_height), (img_width, img_height)

def generate_png(ofile, imgsize, camera):
    """Generate PNG from SCAD file using OpenSCAD CLI"""
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
        '--autocenter',
        '--colorscheme', 'Cornfield',
        f'{ofile}.scad'
    ]

    try:
        print(f"Generating {ofile}.png...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"Successfully generated {ofile}.png")
        else:
            print(f"Error generating {ofile}.png: {result.stderr}")
    except FileNotFoundError:
        print("Error: openscad command not found. Please install OpenSCAD.")
    except subprocess.TimeoutExpired:
        print(f"Error: OpenSCAD timed out generating {ofile}.png")
    except Exception as e:
        print(f"Error generating {ofile}.png: {e}")

class Junction:
    cc = ['UR','LR','UL','LL','CL','VL']
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

class Path:
    def __init__(self, label, start_row, start_col, node_index):
        self.label = label
        self.start_row = start_row
        self.start_col = start_col
        self.node_index = node_index
        self.junctions = []  # List of (junction, next_junction) pairs
        self.end_row = None
        self.end_col = None

    def add_segment(self, junction, next_junction):
        """Add a junction pair to this path"""
        self.junctions.append((junction, next_junction))

    def draw(self, fout, maxy, CL, VL):
        """Draw this complete path"""
        # If path has a start_row, draw initial segment from output row to first junction
        if self.start_row is not None and len(self.junctions) > 0:
            first_c, first_d = self.junctions[0]
            # The first junction (first_c) should be at or before the output row
            # If it's before (row < start_row), draw initial vertical segment
            if first_c.row < self.start_row:
                base = min(maxy-first_c.row, maxy-self.start_row)
                length = abs(first_c.row - self.start_row)
                fout.write(f'    drawV({self.start_col}, {base}, {length});\n')

        for i, (c, d) in enumerate(self.junctions):
            # Check if previous segment was horizontal at the same row
            prev_was_horiz_same_row = False
            if i > 0:
                prev_c, prev_d = self.junctions[i - 1]
                prev_was_horiz_same_row = (prev_c.col != prev_d.col and prev_c.row == prev_d.row and prev_d.row == c.row)

            # For horizontal segments, swap the corner codes at each end
            # so they curve toward the horizontal line instead of away from it
            if c.col != d.col and c.row == d.row:
                # Horizontal segment - use swapped corner codes
                # Draw corner at position c using d's corner code (skip if previous segment already drew it)
                if c.code < CL and not prev_was_horiz_same_row:
                    dy, dx = d.code&1, d.code//2
                    fout.write(f'    drawCorner({c.col}, {maxy-c.row}, {dx},{dy}, "{c.num}");\n')
                # Draw the horizontal segment
                base = min(c.col, d.col)
                fout.write(f'    drawH({base+1}, {maxy-c.row}, {abs(c.col-d.col)-1});\n')
                # Draw corner at position d using c's corner code (always draw for horizontal segments)
                if d.code < CL:
                    dy, dx = c.code&1, c.code//2
                    fout.write(f'    drawCorner({d.col}, {maxy-d.row}, {dx},{dy}, "{d.num}");\n')
            else:
                # Vertical segment or same position
                # Only draw corner at position c if it wasn't already drawn by previous horizontal segment
                if c.code < CL and not prev_was_horiz_same_row:
                    dy, dx = c.code&1, c.code//2
                    fout.write(f'    drawCorner({c.col}, {maxy-c.row}, {dx},{dy}, "{c.num}");\n')

                # Draw vertical segment
                if c.row != d.row:
                    base = min(maxy-c.row, maxy-d.row)
                    fout.write(f'    drawV({c.col}, {base}, {abs(c.row-d.row)-1});\n')

        # If path has an end_row, draw final segment from last junction to input row
        if self.end_row is not None and len(self.junctions) > 0:
            last_c, last_d = self.junctions[-1]
            # The last junction (last_d) should be at or before the input row
            # If it's before (row < end_row), draw one more vertical segment
            if last_d.row < self.end_row:
                base = min(maxy-last_d.row, maxy-self.end_row)
                length = abs(last_d.row - self.end_row)
                fout.write(f'    drawV({last_d.col}, {base}, {length});\n')

    def __repr__(self):
        return f'Path({self.label}, node={self.node_index}, start=({self.start_row},{self.start_col}), end=({self.end_row},{self.end_col}), segments={len(self.junctions)})'

def process(idata, ofile, custom_colors=None):
    UR, LR, UL, LL, CL, VL = range(6) # Set Corner Codes + Vertical Line
    def upChar(dx):   # Return neighbor char from previous line
        if linn>0 and (0<= col+dx < len(idata[linn-1])):
            return idata[linn-1][col+dx]
        return '?'   # No character available?

    def downChar(dx):  # Return neighbor char from next line
        if linn < len(idata)-1 and (0 <= col+dx < len(idata[linn+1])):
            return idata[linn+1][col+dx]
        return '?'   # No character available?

    # Find locations of corners and collect text characters
    corners, text_chars, linn, maxy = [], [], 0, len(idata)

    for linn, l in enumerate(idata):
        pc = None
        for col, c in enumerate(l):
            num = len(corners)
            # Detect corners
            if c=='/':
                if upChar(0) in '|\\': # Need to check LR before UL
                    corners.append(Junction(num, linn,col,LR)) # Lower Right
                elif downChar(0) == '|':  # Top of vertical line (path goes UP then RIGHT)
                    corners.append(Junction(num, linn,col,UR)) # Upper Right
                elif upChar(1)=='_':
                    corners.append(Junction(num, linn,col,UL)) # Upper Left
            elif c=='\\':
               if upChar(0) in '|/': # Need to check LL before UR
                    corners.append(Junction(num, linn,col,LL)) # Lower Left
               elif downChar(0) == '|':  # Top of vertical line (path goes UP then LEFT)
                    corners.append(Junction(num, linn,col,UL)) # Upper Left
               elif upChar(-1)=='_':
                    corners.append(Junction(num, linn,col,UR)) # Upper Right
            elif c=='|':
                # Create VL junction at END of vertical runs (last | before non-|)
                if downChar(0) != '|':
                    corners.append(Junction(num, linn,col,VL)) # Vertical Line

            # Collect text characters (anything that's not an edge character or space)
            if c not in '|/\\_' and c not in ' \t\n':
                text_chars.append((linn, col, c))

            pc = c
        corners.append(Junction(0,0,0,0)) # Need extra node for testing

    def hhfind(cor):
        for c in corners[1+cor.num:]:
            # Any corner type on the same row can be a horizontal connection
            if c.row==cor.row and c.code < CL:
                # Check if there's a valid horizontal connection
                min_col, max_col = min(cor.col, c.col), max(cor.col, c.col)
                distance = max_col - min_col
                if cor.row < len(idata):
                    between = idata[cor.row][min_col+1:max_col]
                    # Accept if: (1) has underscore, OR (2) short distance with no blocking corners
                    has_underscore = '_' in between
                    has_corner = any(ch in '/\\' for ch in between)
                    is_short = distance <= 10  # Short connections don't need underscores

                    if has_underscore or (is_short and not has_corner):
                        return corners[c.num]
        return None   # not found??

    def vvfind(cor):
        for c in corners[1+cor.num:]:
            # Find any corner or VL junction in the same column
            if (c.code in (LL, LR, UL, UR, VL)) and c.col==cor.col:
                return corners[c.num]
        return None   # not found??

    for cor in corners:         # Connect up the pieces
        if cor.code in (UL, LL, LR, UR):
            cor.setConn(hhfind(cor))    # Find & set end-column
        if cor.code in (UL, UR, LR, LL, VL):
            cor.setConn(vvfind(cor))    # Find & set end-row

    # Identify label rows and build Path objects
    # Find rows that contain single-letter labels
    # Only include letters that have edge characters (|, /, \) directly above them
    # Exception: 'x' or 'X' represents unconnected inputs and don't need edges above
    label_rows = {}  # row -> list of (col, char)
    for row, col, char in text_chars:
        if char.isalpha() and char.islower():
            # 'x' represents an unconnected input - always include it
            if char == 'x':
                if row not in label_rows:
                    label_rows[row] = []
                label_rows[row].append((col, char))
            # For other letters, check if there's an edge character directly above
            elif row > 0 and col < len(idata[row-1]):
                char_above = idata[row-1][col]
                if char_above in '|/\\':
                    if row not in label_rows:
                        label_rows[row] = []
                    label_rows[row].append((col, char))

    # Sort by row to find first and second label rows
    sorted_label_rows = sorted(label_rows.keys())
    if len(sorted_label_rows) < 2:
        # No labels found, use old behavior
        output_row = None
        input_row = None
    else:
        output_row = sorted_label_rows[0]  # First row with labels (outputs)
        input_row = sorted_label_rows[1]   # Second row with labels (inputs)

    # Build Path objects by tracing from output labels
    paths = []
    if output_row is not None and input_row is not None:
        # Sort output labels by column
        output_labels = sorted(label_rows[output_row], key=lambda x: x[0])

        def trace_path(start_col, visited=None):
            """Trace path from start_col following UP → ACROSS → DOWN pattern"""
            if visited is None:
                visited = set()
            segments = []

            # Find starting VL junction at start_col (closest | above the label)
            start_junction = None
            closest_dist = float('inf')
            for c in corners:
                if c.code == VL and c.col == start_col and c.row <= output_row:
                    dist = output_row - c.row
                    if dist < closest_dist:
                        closest_dist = dist
                        start_junction = c

            if not start_junction:
                return segments, None

            # Phase 1: Trace UPWARD from start_junction to find top corner (UL or UR)
            def trace_up(c):
                """Trace upward by scanning for next junction above, return top corner"""
                # Find next junction in same column with row < c.row
                next_junctions = [
                    j for j in corners
                    if j.col == c.col and j.row < c.row and j.num > 0
                ]

                if not next_junctions:
                    return None

                # Sort by row descending to get nearest one above
                next_junctions.sort(key=lambda j: j.row, reverse=True)
                d = next_junctions[0]

                # Add segment from c to d
                canon = c.canon(d)
                if canon not in visited:
                    visited.add(canon)
                    segments.append((c, d))

                    # Check if we've reached a top corner
                    # LR/LL = path goes up then turns horizontal
                    # UL/UR = path goes horizontal then turns up
                    if d.code in (UL, UR, LR, LL):
                        return d
                    # Continue up through VL junctions
                    elif d.code == VL:
                        return trace_up(d)

                return None

            top_corner = trace_up(start_junction)
            if not top_corner:
                return segments, None

            # Phase 2: Trace ACROSS from top_corner to far corner (UR, LR, or LL)
            def trace_across(c):
                """Trace horizontally, return far corner ready to go down"""
                # Find all horizontal connections
                horiz_conns = [(d, d.col) for d in c.conn if d.row == c.row and d.col != c.col]

                # Prefer correct direction based on corner type:
                # UR (path goes up then right) → prefer larger columns
                # UL (path goes up then left) → prefer smaller columns
                if c.code == UR:
                    horiz_conns.sort(key=lambda x: x[1], reverse=True)  # Largest col first
                elif c.code == UL:
                    horiz_conns.sort(key=lambda x: x[1])  # Smallest col first

                for d, _ in horiz_conns:
                    canon = c.canon(d)
                    if canon not in visited:
                        visited.add(canon)
                        segments.append((c, d))
                        # Any corner on same row can be end of horizontal trace
                        if d.code in (UR, LR, LL, UL):
                            return d
                return None

            far_corner = trace_across(top_corner)
            if not far_corner:
                return segments, None

            # Phase 3: Trace DOWNWARD from far_corner to input row
            def trace_down(c):
                """Trace downward by scanning for next junction below, return end column"""
                # Find next junction in same column with row > c.row
                next_junctions = [
                    j for j in corners
                    if j.col == c.col and j.row > c.row and j.num > 0
                ]

                if not next_junctions:
                    return None

                # Sort by row to get nearest one below
                next_junctions.sort(key=lambda j: j.row)
                d = next_junctions[0]

                # Add segment from c to d
                canon = c.canon(d)
                if canon not in visited:
                    visited.add(canon)
                    segments.append((c, d))

                    # Check if we've reached a VL at or just before the input row
                    # VL junctions are at end of vertical runs, so they're one row before the label
                    if d.code == VL and d.row >= input_row - 1:
                        return d.col
                    # Continue down through any junction type
                    elif d.code == VL or d.code < VL:
                        result = trace_down(d)
                        if result is not None:
                            return result

                return None

            end_col = trace_down(far_corner)
            return segments, end_col

        # Build Path for each output label
        for idx, (col, label) in enumerate(output_labels):
            node_index = idx // 2  # 2 outputs per node
            path = Path(label, output_row, col, node_index)

            segments, end_col = trace_path(col)
            for c, d in segments:
                path.add_segment(c, d)

            if end_col is not None:
                path.end_col = end_col
                path.end_row = input_row

            paths.append(path)

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
            fout.write (f'    drawV({c.col}, {base}, {abs(c.row-erow)-1});\n')

    def drawH(c, ecol):
        if not ecol==c.col:
            base = min(c.col, ecol)
            fout.write (f'    drawH({base+1}, {maxy-c.row}, {abs(c.col-ecol)-1});\n')

    def colorTrace(c, d):
        if c.canon(d) in drawn: return
        code = c.code
        # Draw c to d
        if code < CL:  # Only draw corners for actual corner codes (not VL)
            drawCorner(c)
        drawH(c, d.col) # Draw to end-column, if ok
        drawV(c, d.row) # Draw to end-row, if ok
        drawn[c.canon(d)] = 1

        # Continue tracing through all connections (corners and VL junctions)
        # The drawn dictionary prevents infinite loops
        for e in d.conn:
            colorTrace(d, e)

    with open(ofile+'.scad', 'w') as fout:
        fout.write (heading(ofile)) # Write drawing modules

        # Draw colored traces using Path objects
        # Paths are already built in left-to-right order from sorted output labels
        # So we can use the path index directly for color assignment
        if paths:
            for idx, path in enumerate(paths):
                # Determine color for this path based on its index
                if custom_colors:
                    # Use custom color if available, cycling if necessary
                    color_idx = idx % len(custom_colors)
                    colorName = colorFix(custom_colors[color_idx])
                else:
                    # Fall back to auto-assigned colors using path index
                    colorName = aColor(idx)

                fout.write (f'  color(c="{colorName}") linear_extrude(height=1) ' + '{\n')
                path.draw(fout, maxy, CL, VL)
                # Close the current-trace color-block
                fout.write ('  }\n')
        else:
            # Fallback to old behavior if no paths found
            drawn = {}
            colorNum = 0
            for b in corners:
                if not b.conn: continue
                if b.num>0 and b.code < VL:
                    for d in b.conn:
                        if d.num > b.num:
                            colorNum += 1
                            colorName = aColor(colorNum)
                            fout.write (f'  color(c="{aColor(colorNum)}") linear_extrude(height=1) ' + '{\n')
                            colorTrace(b, d)
                            fout.write ('  }\n')

        # Draw text characters in black
        if text_chars:
            fout.write ('  color("Black") linear_extrude(height=1.2) {\n')
            for row, col, char in text_chars:
                # Escape special characters for OpenSCAD
                escaped_char = char.replace('\\', '\\\\').replace('"', '\\"')
                fout.write (f'    drawChar({col}, {maxy-row}, "{escaped_char}");\n')
            fout.write ('  }\n')

        # Close drawStuff module and invoke it
        fout.write ('}\ndrawStuff();\n')

    # Calculate bounding box from all corners (and text positions)
    if corners or text_chars:
        min_col = min_row = float('inf')
        max_col = max_row = float('-inf')

        for c in corners:
            if c.code != 0:
                min_col = min(min_col, c.col)
                max_col = max(max_col, c.col)
                min_row = min(min_row, c.row)
                max_row = max(max_row, c.row)

        for row, col, char in text_chars:
            min_col = min(min_col, col)
            max_col = max(max_col, col)
            min_row = min(min_row, row)
            max_row = max(max_row, row)

        # Add small padding for text
        min_col = min_col - 1
        max_col = max_col + 2
        min_row = min_row - 1
        max_row = max_row + 1
    else:
        min_col = max_col = min_row = max_row = 0

    return (min_col, max_col, min_row, max_row, maxy)

# Set up default options
options = { 'file':'progression.txt', 'png':''}
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
            imgsize, camera, border, custom_colors = None, None, None, None  # Metadata for PNG generation

            while a := fin.readline():   # Allow blank lines
                a = a.rstrip()  # Drop ending whitespace
                if a and a=='=':   # Detect closing =
                    # Process the SCAD file (file is fully written when this returns)
                    bbox = process(idata, ofile, custom_colors)

                    # Generate PNG if requested
                    if options['png']:
                        # Use default border if not specified
                        final_border = border if border is not None else 20

                        # Calculate camera/imgsize from bounding box
                        calc_camera, calc_imgsize = calculate_camera_params(
                            bbox, border=final_border, target_imgsize=imgsize
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

                        generate_png(ofile, final_imgsize, final_camera)
                    break
                elif a.startswith('@imgsize='):
                    parts = a[9:].split(',')
                    if len(parts) == 2:
                        try:
                            imgsize = (int(parts[0]), int(parts[1]))
                        except ValueError:
                            print(f"Warning: Invalid imgsize format: {a}")
                elif a.startswith('@camera='):
                    parts = a[8:].split(',')
                    if len(parts) == 3:
                        try:
                            camera = (float(parts[0]), float(parts[1]), float(parts[2]))
                        except ValueError:
                            print(f"Warning: Invalid camera format: {a}")
                elif a.startswith('@border='):
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
