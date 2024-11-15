#!/bin/bash

PID=$1
BID=$2
SID=$3
work_dir=$(pwd)

export GZOLTAR_AGENT_JAR=$work_dir/gzoltaragent.jar
export GZOLTAR_CLI_JAR=$work_dir/gzoltarcli.jar
export D4J_HOME=/home/qyh/GrowingBugRepository  # Change to your own defects4j home!
export TZ='America/Los_Angeles' # some D4J's requires this specific TimeZone
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8

localize(){  # 1st arg: PID, 2nd arg: BID
  PID=$1
  BID=$2
  SID=$3

  # Checkout
  cd "$work_dir"

  if [ "$SID" = "None" ]; then
    rm -rf "$PID-${BID}b"; "$D4J_HOME/framework/bin/defects4j" checkout -p "$PID" -v "${BID}b" -w "$PID-${BID}b"
    bug_dir="$work_dir/$PID-${BID}b"
  else
    rm -rf "$PID-${BID}b"; "$D4J_HOME/framework/bin/defects4j" checkout -p "$PID" -v "${BID}b" -w "$PID-${BID}b" -s "$SID"
    bug_dir="$work_dir/$PID-${BID}b/$SID"
  fi

  # Compile
  cd "$bug_dir"
  "$D4J_HOME/framework/bin/defects4j" compile

  # Collect metadata
  cd "$bug_dir"
  test_classpath=$($D4J_HOME/framework/bin/defects4j export -p cp.test)
  src_classes_dir=$($D4J_HOME/framework/bin/defects4j export -p dir.bin.classes)
  src_classes_dir="$bug_dir/$src_classes_dir"
  test_classes_dir=$($D4J_HOME/framework/bin/defects4j export -p dir.bin.tests)
  test_classes_dir="$bug_dir/$test_classes_dir"
  echo "$PID-${BID}b's classpath: $test_classpath" >&2
  echo "$PID-${BID}b's bin dir: $src_classes_dir" >&2
  echo "$PID-${BID}b's test bin dir: $test_classes_dir" >&2

  # Collect unit tests to run GZoltar with

  cd "$bug_dir"
  unit_tests_file="$bug_dir/unit_tests.txt"
  relevant_tests="*"  # Note, you might want to consider the set of relevant tests provided by D4J, i.e., $D4J_HOME/framework/projects/$PID/relevant_tests/$BID

  java -cp "$D4J_HOME/framework/projects/lib/junit-4.11.jar:$test_classpath:$test_classes_dir:$GZOLTAR_CLI_JAR" \
    com.gzoltar.cli.Main listTestMethods \
      "$test_classes_dir" \
      --outputFile "$unit_tests_file" \
      --includes "$relevant_tests"
  head "$unit_tests_file"

  # Collect classes to perform fault localization on

  cd "$bug_dir"

  loaded_classes_file="$D4J_HOME/framework/projects/$PID/loaded_classes/$BID.src"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    normal_classes=$(cat "$loaded_classes_file" | gsed 's/$/:/' | gsed ':a;N;$!ba;s/\n//g')
    inner_classes=$(cat "$loaded_classes_file" | gsed 's/$/$*:/' | gsed ':a;N;$!ba;s/\n//g')
  else
    normal_classes=$(cat "$loaded_classes_file" | sed 's/$/:/' | sed ':a;N;$!ba;s/\n//g')
    inner_classes=$(cat "$loaded_classes_file" | sed 's/$/$*:/' | sed ':a;N;$!ba;s/\n//g')
  fi
  classes_to_debug="$normal_classes$inner_classes"
  echo "Likely faulty classes: $classes_to_debug" >&2

  # Run GZoltar

  cd "$bug_dir"

  ser_file="$bug_dir/gzoltar.ser"
  export _JAVA_OPTIONS="-Xmx6144M -XX:MaxHeapSize=4096M"
  java -XX:MaxMetaspaceSize=4096M -javaagent:$GZOLTAR_AGENT_JAR=destfile=$ser_file,buildlocation=$src_classes_dir,includes=$classes_to_debug,excludes="",inclnolocationclasses=false,output="FILE" \
    -cp "$src_classes_dir:$D4J_HOME/framework/projects/lib/junit-4.11.jar:$test_classpath:$GZOLTAR_CLI_JAR" \
    com.gzoltar.cli.Main runTestMethods \
      --testMethods "$unit_tests_file" \
      --collectCoverage

  echo "Run GZoltar for $PID-${BID}b succeeds!"
  # Generate fault localization report
  # "Tarantula:Ochiai:Jaccard:Ample:RUSSEL_RAO:Hamann:SORENSEN_DICE:Dice:Kulczynski1:Kulczynski2:SIMPLE_MATCHING:Sokal:M1:M2:ROGERS_TANIMOTO:Goodman:Hamming:Euclid:Overlap:Anderberg:Ochiai2:Zoltar:Wong1:Wong2:ER5c:GP02:GP03:GP13:GP19:SBI:DStar2:Wong3:ER1a:ER1b"

  cd "$bug_dir"

  java -cp "$src_classes_dir:$D4J_HOME/framework/projects/lib/junit-4.11.jar:$test_classpath:$GZOLTAR_CLI_JAR" \
      com.gzoltar.cli.Main faultLocalizationReport \
        --buildLocation "$src_classes_dir" \
        --granularity "line" \
        --inclPublicMethods \
        --inclStaticConstructors \
        --inclDeprecatedMethods \
        --dataFile "$ser_file" \
        --outputDirectory "$bug_dir" \
        --family "sfl" \
        --formula "Tarantula:Ochiai:Jaccard:Ample:Ochiai2:DStar2" \
        --metric "entropy" \
        --formatter "txt"
  
  echo "Generate FL report for $PID-${BID}b succeeds!"
}

collectResult(){  # 1st arg: PID, 2nd arg: BID
  PID=$1
  BID=$2
  cd "$work_dir"
  if [ ! -d "results/$PID" ]; then
    mkdir -p "results/$PID"
  fi
  if [ ! -d "$bug_dir" ]; then
    echo "[ERROR] Buggy project dir not found: $PID-${BID}b"
    return
  fi
  if [ ! -d "$bug_dir/sfl/txt" ]; then
    echo "[ERROR] FL report dir not found: $PID-${BID}b/sfl/txt"
    return 
  fi
  cp -r "$bug_dir/sfl/txt" "results/$PID/${BID}"
#   tar -zcvf "$bug_dir".tar.gz "$bug_dir"
  rm -rf "$work_dir/$PID-${BID}b"
#   [ ! -d projects ] && mkdir projects
#   mv "$bug_dir".tar.gz projects/
  echo "Fault Localization for $PID-${BID} succeeds!"
}

cd "$work_dir"
# if [ -d "results/$PID/${BID}" ]; then
#   echo "results/$PID/${BID} already exists, skip $PID-$BID"
#   exit 0
# fi
echo ====================================================
echo "                     $PID $BID                      "
echo ====================================================
localize $PID $BID $SID
collectResult $PID $BID
python remove_unused_result.py "results/$PID/${BID}"
