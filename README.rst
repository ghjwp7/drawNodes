.. -*- mode: rst -*-

===========================
drawNodes - jiw - Jan 2020
===========================

Given ascii-graphics drawings of certain graphs, the ``drawNodes``
program produces files of OpenSCAD code to represent those graphs in a
line-art format.

Description
===========

Given an ascii graphic of a graph, drawn with ``/ # \ _ X`` and space
characters, ``drawNodes`` writes a .scad file to draw that graph,
using OpenSCAD 2D graphics, extruded to 3D.  Lines containing
characters other than the six characters listed above are treated as
text lines, and may be displayed or not in output, depending on
command-line options.

The rest of this file has the following sections:

 • Software requirements
 • Running the program
 • Command-line Options
 • Command-line Options Examples
 • Input file formats
 • X-marks and Trace Colors
 • Graph Parsing limitations
 • How to make a .png output with openscad results
 • Automatic updates in OpenSCAD 
 • Automatically running ``drawNodes`` upon changes to your input file


Software requirements
=====================

 • Install python3 if your system lacks it
 • Install ``drawNodes.py`` as a findable executable file, so that you can
   start it with a command like ``./drawNodes.py`` or ``drawNodes.py``
   or ``python3 drawNodes.py``, etc
 • Install OpenSCAD per its instructions
 • Install a picture viewer (such as gpicview, eog, xv, etc)

Running the program
=====================
  
When you run the program to process an input file, it will write SCAD
code to a file or files, as named by =filename lines within the input.
If the run is successful, you can then use openscad to display
results.  For example, if ``myfile`` is a proper input file and
contains a line ``=234`` to name an output file, you might say::

    drawNodes.py myfile
    openscad 234.scad &

[For two ways to speed up seeing the effects of changes to your input
file, see the sections *Automatic updates in OpenSCAD* and
*Automatically running drawNodes* below.]

Command-line Options
=====================

Command-line options take the form `value` or `opt=value` where `opt`
is in the set {`blob, loci, text, file`} and where `value` is an input
file name or is a color name or number.

For the first three option codes, `value` should a color name or
6-digit hex RGB number or 8-digit hex RGBA number.  Color examples
include::

  Red   BC0000   Green   00FF00   Blue   0000FF20

Defaults for `blob, loci, text` are **0000FF20, Red, ''** (the latter
an empty string) to turn on **pale blue** `blob` coloring; turn on
**Red** `loci` numbers; and turn off `text` display.  (Generally, use
an empty-string value **''** to turn off an option.  Eg, ``loci=''``
would suppress loci numbering.)

The default value for the `file` option is ``aTestSet``, which is a
file of test examples.  Note, a bare value is treated as a file name,
`ie`, is treated like file=value.  For example, ``drawNodes.py
myfile`` reads data from myfile with other options defaulted.


Command-line Option Examples
===============================

Two example command lines appear below.  The first reads from bigdata,
draws text lines in beige, loci numbers in green, and suppresses
blobs.  The second draws loci numbers in red on a pale green
background (since 00ff0010 is solid green, 0x00ff00, but at
alpha=0x10) with text lines suppressed::

  drawNodes.py bigdata text=beige loci=green blob=''
  drawNodes.py bigdata loci=red blob=00ff0010

Input File Formats
===============================

In the input file, separate graphs are demarcated by an `=` line at
each section end, and an `=f` line at each section start (where `f` is
some output file name, to which `.scad` will be appended).  See file
``aTestSet`` for examples of input file format.  Generally, the lines
between the opening `=f` line and the closing `=` line should
represent a graph using any of ``/ # \ _ X`` and space to draw the
graph, with the stipulation that three consecutive ``#`` characters
represent a graph node.  Lines that have characters other than those
mentioned are treated as lines of text.  If a color is set for the
``text=color`` command-line option, then along with the graph drawing,
text lines will appear in the output.  If no text color is set, text
lines are ignored.  Here is an example, with default options::

    =235small
         __________
        /  _   ___ \
        | / \ / X \|
        ### | ### ||
        X | \_/ \_/|
          \________/
    =

.. image:: 235small.png
   :scale: 50%

X-marks and Trace Colors
========================
X-marks in graph lines are drawn using OpenSCAD's default brownish
color.

Trace colors are taken from a list of colors (``colist``, in function
``aColor``) that you can change as you like.

Graph Parsing Limitations
=========================

An example in ``aTestSet`` called `234etc` has some traces that
``drawNodes`` doesn't handle correctly.  The parsing method used in the
program is simplistic; it is ok for many ascii graphs but at present
fails when a trace goes down, then left or right, then down again,
because the second corner's / or \\ is in a different line than the
first corner's / or \\ and the current version only looks in current
line.  This may or may not be simple to fix.  In addition, hairpin
turns (eg, ``_/\_``) are not properly treated, although slightly wider
turns work ok. See example 235long.

How to make a .png output
==========================

After running drawNodes, open a resulting output file in openscad, and
then:

 • Press ``ctrl-4`` or click the ``Top`` button (icon: cube with up triangle)
 • If axes are on, press ``ctrl-2`` or click ``Show Axes`` (icon:
   three lines from a corner) to turn off axis display
 • Press ``ctrl-shift-V`` or click ``View All`` to center the image
 • Use scroll wheel to magnify properly
 • Click ``File / Export / Export-as-Image``
 • Enter or accept a name ending with ``.png``
 • Use a picture viewer to check the ``.png`` file

Automatic updates in OpenSCAD 
========================================
  
If OpenSCAD's ``Design / Automatic-Reload-and-Preview`` option is on,
then once you've started OpenSCAD for a given file, it will notice
whenever that ``.scad`` file changes, and will re-render the image.
Note, if you modify ``.scad`` code in OpenSCAD's Editor window, you
may need to press ``F5`` to re-render.  However, if you use OpenSCAD's
Customizer to change and enter some parameter values -- such as
``wFrac`` to control trace width, or ``scale`` to control overall
sizing, or ``textFrac`` to control text size -- OpenSCAD should update
the result by itself.

Automatically running ``drawNodes`` upon changes to your input file
========================================================================

During input file development, it may be convenient to automatically
run ``drawNodes`` when your file changes.  To do so: Obtain and
install the ``exec-on-change`` shell script and its requirements.
Then a command as below will automatically run ``drawNodes`` upon
changes to ``myfile`` (after which OpenSCAD can re-render results, per
previous section).  Add any desired options within the quoted command.
The ``exec-on-change`` URL is
https://github.com/ghjwp7/plastics/blob/master/exec-on-change ::

     exec-on-change myfile  'drawNodes.py myfile' &

