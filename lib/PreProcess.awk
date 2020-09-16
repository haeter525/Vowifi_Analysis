BEGIN { 
	FS="[\t]+" 
 
	#Source IP 
	UE = "10.42.0.110" 
       	#ePDG IP 
	ePDG = "221.120.23.1" 
 
	#Direction 
	DIR="" 
	UP="DIRECTION.UPWARD"
	DOWN="DIRECTION.DOWNWARD"

	print("Index\tDirect\tLength\tEvent\tpreEvent\tpreEvent2")
	#$1 $2 $3 $4 $5
	}

NF < 4 || $1!~/[0-9]+/ {
	print("-")
	next
	}

$2==UE  {
	DIR=UP
	print($1"\t"DIR"\t"$4"\t"$5"\t"$6)
	}

$2==ePDG {
	DIR=DOWN
	print($1"\t"DIR"\t"$4"\t"$5"\t"$6)
	}

$2==UP || $2==DOWN {
	print($1"\t"$2"\t"$4"\t"$5"\t"$6)
	}

NF > 6 && $7!=""{
	print($1"\t"DIR"\t"$4"\t"$5"\t"$7)
	}