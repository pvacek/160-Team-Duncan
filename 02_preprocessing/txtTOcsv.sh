for f in *.txt
do
	fname="${f%.*}"
	python txtTOcsv.py $fname.txt
done