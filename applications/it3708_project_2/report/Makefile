TEX=pdflatex
TEXFLAGS=--halt-on-error
BIBTEX=bibtex

TARGET=karlsen-it3708-project2-report.pdf

$(TARGET): report.tex
	$(TEX) $(TEXFLAGS) $^ -o $@
	$(BIBTEX) report.aux
	$(TEX) $(TEXFLAGS) $^ -o $@
	$(TEX) $(TEXFLAGS) $^ -o $@

.PHONY: clean
clean: 
	rm -fr $(TARGET) *.out *.aux *.bbl *.bib *.log 
