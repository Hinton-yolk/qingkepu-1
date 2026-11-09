#!/bin/bash
# run.sh <id> <qfile> <segsec> <maxsec> ：从 0 开始每 segsec 秒一段，直到超出片长（Gemini 报错 400 或回答 END OF VIDEO）
id=$1; q=$(cat $2); seg=$3; max=$4; tag=${2%.txt}
M=gemini-3.5-flash,gemini-3.8-flash,gemini-3.7-flash,gemini-3.6-flash,gemini-3-flash-preview,gemini-3.1-pro-preview,gemini-pro-latest
fmt() { printf "%d:%02d" $(( $1 / 60 )) $(( $1 % 60 )); }
for ((s=${5:-0}; s<max; s+=seg)); do e=$((s+seg)); S=$(fmt $s); E=$(fmt $e); out="${tag}_$(printf %04d $s).md"; ok=no
  for try in 1 2 3; do
    if timeout 900 python3 /home/user/kepu-studio/tools/gemini_watch.py "https://www.youtube.com/watch?v=$id" --start $S --end $E --models $M -q "$q" --out "$out" > "log_${tag}_$s.txt" 2>&1; then ok=yes; break; fi
    grep -q "HTTP 400" "log_${tag}_$s.txt" && break; sleep 45; done
  echo "$tag $S-$E ok=$ok"; sleep 20
  if [ $ok = no ] && grep -q "HTTP 400" "log_${tag}_$s.txt"; then echo "$tag END(400)"; break; fi
  if [ $ok = yes ] && sed -n "/^> 以下/,\$p" "$out" | grep -qiE "END OF VIDEO|^NO CONTENT"; then echo "$tag END"; break; fi
done; echo "$tag ALLDONE"
