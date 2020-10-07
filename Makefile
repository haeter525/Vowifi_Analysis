
.phony: setup intercept restore clean

all: intercept

setup:
	# 設定 iptable
	iptables -I FORWARD --source 10.42.0.0/24 -p udp -j NFQUEUE --queue-num 1
	iptables -I FORWARD --destination 10.42.0.0/24 -p udp -j NFQUEUE --queue-num 1

intercept:
	# 執行 NetFilter.py
	python NetFilter.py

restore:
	# 復原 iptable
	iptables -D FORWARD --source 10.42.0.0/24 -p udp -j NFQUEUE --queue-num 1
	iptables -D FORWARD --destination 10.42.0.0/24 -p udp -j NFQUEUE --queue-num 1

clean:restore