#!/usr/bin/env bash
# Runs the threshold probe, the evaluation and the demo against local Ollama, one after the other.
set -u
JAR=target/hr-policy-assistant-spring-ai-1.0.0.jar
OUT=${1:-sample-output}
mkdir -p "$OUT"

t0=$(date +%s)
timeout 600 java -jar $JAR --spring.profiles.active=probe tuning-questions.psv questions.psv 2>&1 \
  | grep -E "^[TAO][0-9]|ERROR|Exception" > "$OUT/probe.txt"
t1=$(date +%s)

# threshold = midpoint between the weakest answerable and the strongest unanswerable tuning question
TH=$(python3 - "$OUT/probe.txt" <<'PY'
import sys
best = {}
for line in open(sys.argv[1]):
    if line.startswith('T'):
        parts = line.split('|')
        qid, route = parts[0].split()
        best[qid] = (route, float(parts[1].split()[0]))
low_answer = min(s for r, s in best.values() if r == 'ANSWERED')
high_refuse = max(s for r, s in best.values() if r == 'REFUSED')
print(f"{int((low_answer + high_refuse) / 2 * 100) / 100:.2f}")
PY
)
echo "threshold=$TH" | tee "$OUT/threshold.txt"

timeout 900 java -jar $JAR --spring.profiles.active=eval --peopledesk.similarity-threshold=$TH > "$OUT/eval.txt" 2>&1
t2=$(date +%s)
timeout 600 java -jar $JAR --spring.profiles.active=demo --peopledesk.similarity-threshold=$TH > "$OUT/demo.txt" 2>&1
t3=$(date +%s)
printf "probe %ss, eval %ss, demo %ss (wall clock, each includes JVM start and embedding the 30 sections)\n" \
  $((t1-t0)) $((t2-t1)) $((t3-t2)) | tee "$OUT/timings.txt"
