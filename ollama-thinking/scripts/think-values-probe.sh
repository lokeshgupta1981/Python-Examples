#!/bin/bash
U=localhost:11434/api/chat
Q='A shop sells pens at 3 dollars each. How much do 4 pens cost? Reply with the number only.'
for T in false true '"low"' '"max"' 512; do
  echo "=== think=$T num_predict=64"
  curl -s -w '\nHTTP %{http_code} %{time_total}s\n' $U -d "{\"model\":\"qwen3:1.7b\",\"stream\":false,\"think\":$T,\"options\":{\"temperature\":0,\"num_predict\":64},\"messages\":[{\"role\":\"user\",\"content\":\"$Q\"}]}" | head -c 1500
  echo
done
