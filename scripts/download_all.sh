#!/bin/bash
# Download all AP1000 DCD Rev 19 documents from the NRC (package ML11171A500)
cd "$(dirname "$0")/.."
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
count=0
while IFS=$'\t' read -r title url; do
  url=$(echo "$url" | tr -d '\r')
  ml=$(basename "$url" .pdf)
  out="data/raw/$ml.pdf"
  if [ -s "$out" ]; then continue; fi
  curl -sL -o "$out" "$url" \
    -H "User-Agent: $UA" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    -H "Accept-Language: en-US,en;q=0.9" \
    -H "Accept-Encoding: gzip, deflate" --compressed \
    -H "Sec-Fetch-Dest: document" -H "Sec-Fetch-Mode: navigate" \
    -H "Sec-Fetch-Site: none" -H "Upgrade-Insecure-Requests: 1"
  # verify it's a PDF, not an error page
  if ! head -c 5 "$out" | grep -q "%PDF"; then
    echo "FAILED: $ml"
    rm -f "$out"
  fi
  count=$((count+1))
  sleep 1.5
done < data/raw/dcd_manifest.tsv
echo "Done. Downloaded $count new files."
ls data/raw/*.pdf | wc -l
