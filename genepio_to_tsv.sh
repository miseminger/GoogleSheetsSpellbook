#In genepio-edit.owl, the terms that have been ontologized are written in like this:
#    # Class: obo:GENEPIO_0000047 (secondary enzyme (LMACI))

 
cat /home/madeline/Desktop/git_temp/genepio/src/ontology/genepio-edit.owl | grep '^#' | grep "GENEPIO_" | sed 's/: obo:/\t/g' | sed 's/#//g' | sed 's/GENEPIO_/GENEPIO:/g' > genepio_terms.txt

#sed -i 's/)//g' genepio_terms.txt
#sed -i 's/ (/\t/g' genepio_terms.txt
