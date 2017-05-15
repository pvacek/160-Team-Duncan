for f in *.json
do
	fname="${f%.*}"
	jq -r 'events[].moments[] | @text' $fname.json > $fname.txt
done