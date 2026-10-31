#!/usr/bin/env bash
# Runs every attack against every in-process sandbox, each case in a fresh JVM (-Xmx512m).
# Build first: mvn -q compile dependency:build-classpath -Dmdep.outputFile=cp.txt
set -u
CP="target/classes:$(cat cp.txt)"
export DB_PASSWORD="s3cr3t-from-env"
for sandbox in unsafe constrained untrusted; do
  for attack in READ_SECRET_ENV READ_FILE OPEN_SOCKET RUN_PROCESS INFINITE_LOOP MEMORY_BOMB; do
    out=$(timeout 30 java -Xmx512m --enable-native-access=ALL-UNNAMED -cp "$CP" \
          com.howtodoinjava.sandbox.AttackProbe "$sandbox" "$attack" 2>&1)
    code=$?
    line=$(echo "$out" | grep '^RESULT|' | head -1)
    if [ -n "$line" ]; then
      echo "$line"
    elif [ $code -eq 124 ]; then
      echo "RESULT|$sandbox|$attack|STILL RUNNING after 30 s (killed by timeout)|-|"
    else
      echo "RESULT|$sandbox|$attack|JVM DIED exit=$code|-|$(echo "$out" | grep -m1 -iE 'error|exception')"
    fi
  done
done
