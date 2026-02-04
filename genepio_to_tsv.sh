#!/bin/bash

<<comment

This script extracts the GENEPIO terms from genepio/src/ontology/genepio-edit.owl and puts the type, IRI, and label in a TSV file called genepio_edit_terms.tsv. To run it, open up the shell and run ./genepio_to_tsv.sh.


In genepio-edit.owl, the terms that have been ontologized (ie. the terms we want to take) are written in like this:
   # Class: obo:GENEPIO_0000047 (secondary enzyme (LMACI))
"Class" could also be "Annotation Property" or "Object Property" or "Individual".

In order, here's what the operations do. There are neater ways to do this, but for the sake of speed, this works for now.

	cat /home/madeline/Desktop/git_temp/genepio/src/ontology/genepio-edit.owl = read the file at this path
	grep '^#' = keep all lines beginning with '#'
	grep "GENEPIO_" = keep all lines that contain the string "GENEPIO_" anywhere
	sed 's/: obo:/\t/g' = find and replace all instances of ': obo:' with a tab (\t)
	sed 's/^# //g' = find and remove all instances of '# ' where '# ' is the first character set in a line
	sed 's/GENEPIO_/GENEPIO:/g' = find and replace 'GENEPIO_' with 'GENEPIO:'
	sed 's/)$//g' = find and remove all instances of ')' where ')' is the last character in a line
	sed 's/ Property/Property/' = take out the space in the Type column if there is one
	sed 's/ /\t/' = now replace the first space with a tab--since the Type space is gone, this is the space between the IRI and the Label.
	's/Property/ Property/' = put the space back in the Type column
	> genepio_edit_terms.tsv = save to a file called genepio_edit_terms.tsv

comment

echo -e "type\tIRI\tlabel" > genepio_edit_terms.tsv # initiate TSV with header row
cat /home/madeline/Desktop/git_temp/genepio/src/ontology/genepio-edit.owl | grep '^#' | grep "GENEPIO_" | sed 's/: obo:/\t/g' | sed 's/^# //g' | sed 's/GENEPIO_/GENEPIO:/g' | sed 's/)$//g' | sed 's/(//' | sed 's/ Property/Property/' | sed 's/ /\t/' | sed 's/Property/ Property/' >> genepio_edit_terms.tsv

