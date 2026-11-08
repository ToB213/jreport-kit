# upLaTeX → DVI → PDF; Japanese references use upBibTeX.
$pdf_mode = 3;
$latex = 'uplatex -synctex=1 -interaction=nonstopmode -halt-on-error -file-line-error %O %S';
$bibtex = 'upbibtex %O %B';
$dvipdf = 'dvipdfmx %O -o %D %S';
$pdf_previewer = 'none';
