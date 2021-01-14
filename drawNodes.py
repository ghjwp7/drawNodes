#!/usr/bin/env python3
# -*- mode: python -*-

# Given an ascii graphic of a graph, drawn with _, /, \, #, X, and
# space characters, write a .scad file to draw it using OpenSCAD 2D
# graphics, extruded to 3D.  Lines containing characters other than
# those are treated as text lines, and may be displayed or not
# depending on options.

# Command-line options take the form `value` or `opt=value` (less
# quotes) where opt is in the set {blob, loci, text, file} and where
# value is an input file name or is a color name or number (6-digit
# hex RGB or 8-digit hex RGBA).  See README.rst for examples.

# Note, default for `file` is 'aTestSet', which is a file of test
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
module drawBlob(x,y)
  translate (scale*[x,y,0]) square([scale*3,scale]);
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
def process(idata, ofile):
    UR, LR, UL, LL, CL, XM, HM, HX = range(8) # Set Corner & Mark Codes
    def upChar(dx):   # Return neighbor char from previous line
        if linn>0 and (0<= col+dx < len(idata[linn-1])):
            return idata[linn-1][col+dx]
        return '?'   # No character available?
        
    # Find locations of corners etc
    corners, blobs, xlist, chars, linn, maxy = [], [], [], [], 0, len(idata)
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
                blobs.append(corners[num])
            elif c=='X':
                corners.append(Junction(num, linn,col,XM)) # Xmark
                xlist.append(corners[num])
            pc = c

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
        
        if options['blob']:     # Open blobs color block?
            fout.write (f'  color("{colorFix(options["blob"])}") linear_extrude(height=1)' + ' {\n')
            for b in blobs:
                if b.code == HM:
                    fout.write (f'    drawBlob({b.col}, {maxy-b.row});\n')
            fout.write ('  }\n')    # Close drawBlob's color block

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
            for b in blobs:   # Display loci numbers in selected color
                if b.conn:
                    fout.write (f'    drawChar({b.col+0.2}, {maxy-b.row+0.1}, "{loci}");\n')
                    loci += 1
            fout.write ('  }\n')    # Close loci-numbering color block

            for x in xlist:
                fout.write (f'  linear_extrude(height=1) drawChar({x.col}, {maxy-x.row}, "X");\n')

        colorNum = 1                # Skip first two colors at outset
        for b in blobs:   # Do traces from tops of blobs                
            for d in b.conn:
                # Only draw traces from tops of blobs
                if d.num > b.num: continue
                # Start a current-trace color-block
                colorNum += 1
                colorName = aColor(colorNum)
                fout.write (f'  color(c="{aColor(colorNum)}") linear_extrude(height=1) ' + '{\n')
                colorTrace(b, d) # Draw the whole path
                # Close the current-trace color-block
                fout.write ('  }\n')

        # Close drawStuff module and invoke it
        fout.write ('}\ndrawStuff();\n')
#======================================================================
# Set up default options to number the loci in red; suppress text;
# paint blob bodies in a pale blue; and by default read from t1-data.
options = { 'loci':'Red', 'text':'', 'blob':'0000FF20', 'file':'aTestSet'}
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
                if a and a[0]=='=':   # Detect closing =
                    process(idata, ofile)
                    break
                idata.append(a)
