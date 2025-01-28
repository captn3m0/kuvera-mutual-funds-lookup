kuvera.csv:
	curl --retry 10 \
	--connect-timeout 30 \
	--retry-max-time 100 \
	--silent https://api.kuvera.in/mf/api/v4/fund_schemes/list.json | \
	jq -r '.[] | .[] | .[] | .[] | .c' | sort -u | xargs -n150 src/fetch.sh
	sort -uo _.csv _.csv
	cat src/header.csv _.csv > kuvera.csv
	rm _.csv

all: kuvera.csv amfi_funds.csv

amfi_funds.csv:
	python src/amc.py

requirements.txt:
	uv pip compile pyproject.toml