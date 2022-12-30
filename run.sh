#!/bin/bash

arguments=''



while getopts ":i:f:w:o:t:s:h:" opt; do
  case $opt in
    i)
      option_i=$OPTARG
      arguments+=" -i $option_i"
      ;;
    f)
      option_f=$OPTARG
        arguments+=" -f $option_f"
      ;;
    w)
      option_w=$OPTARG
        arguments+=" -w $option_w"
      ;;
    o)
      option_o=$OPTARG
        arguments+=" -o $option_o"
      ;;
    t)
      option_t=$OPTARG
      arguments+=" -tt $option_t"
      ;;
    s)
      option_s=$OPTARG
        arguments+=" -ts $option_s"
      ;;
    h)
      option_h=$OPTARG
      arguments+=" -ho $option_h"
      ;;
    *)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

exec python3 sensor_data_generator.py $arguments
