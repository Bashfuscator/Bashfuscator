#!/bin/bash

echo '#!/bin/bash
time $1' > wrapper.sh

repeat_cmd=':;\n'
let len_cmd=${#repeat_cmd}-1

for n in 1 2 3 4 5 10 20 30 40 50 100 200 300 400 500 1000 2000 3000 4000 5000 10000 20000 30000 40000 50000;
do
	python -c 'print("'"$repeat_cmd"'"*'$n');' > payload

	baseline=`bash wrapper.sh "bash payload" 2>&1 | head -n2 | tail -n1 | cut -f2 | sed 's/s//' | sed 's/m/*60+/' | bc`
	
	echo Generating obfuscated code... >&2
	#obf=`time bashfuscator -f payload -sM --choose-mutators string/file_glob -q`
	#obf=`time bashfuscator -f payload --choose-mutators string/folder_glob -q`
	obf=`time bashfuscator -f payload --choose-mutators string/hex_hash -q`


	echo -n "$obf" > new.sh
	obtime=`bash wrapper.sh "bash new.sh" 2>&1 | head -n2 | tail -n1 | cut -f2 | sed 's/s//' | sed 's/m/*60+/' | bc`

	ms_ch=`echo \($obtime-$baseline\)/$n/$len_cmd"*1000" | bc -l | sed -r 's/0+$//'`
	echo `echo $n"*"$len_cmd | bc` $ms_ch "ms/ch" >> output.log

done


