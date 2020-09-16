#!/usr/bin/bash
# Pcap 轉 Csv 檔案
tshark -r "$1" \
-T fields -e frame.number -e ip.src -e ip.dst -e frame.len |
# awk 預處理
awk -f ~/文件/專題/Program/lib/PreProcess.awk