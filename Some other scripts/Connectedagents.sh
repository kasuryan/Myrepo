{\rtf1\ansi\ansicpg1252\deff0\deflang1033{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\colortbl ;\red0\green0\blue255;}
{\*\generator Msftedit 5.41.21.2510;}\viewkind4\uc1\pard\sa200\sl276\slmult1\lang9\f0\fs22 #!/bin/bash\par
FILE=$1\par
for i in `cat $FILE`;\par
do\par
#ssh root@$\{i\} "hostname; psql -U bismon -l | grep 'bismon30*' | grep -v bismon30_config | awk '\{print $1\}' "\par
DBLIST=`ssh root@$\{i\} "psql -U bismon -l | grep 'bismon30*' | grep -v bismon30_config | awk '\{print {\field{\*\fldinst{HYPERLINK "\\\\\\\\$1\}'"`"}}{\fldrslt{\ul\cf1\\\\$1\}'"`}}}\f0\fs22 ;\par
#echo "$i - $DBLIST"\par
for line in `echo "$\{DBLIST\}"`;\par
#       do ssh root@$\{i\} "ps auxwww | grep $\{line\} |grep -v grep | awk '\{print \\$14\}' | cut -c1-14";\par
        do\par
        echo "$i - $line"\par
#       IP=`ssh root@$\{i\} "ps auxwww | grep $\{line\} |grep -v grep | awk '\{print "{\field{\*\fldinst{HYPERLINK "\\\\\\\\$14"}}{\fldrslt{\ul\cf1\\\\$14}}}\f0\fs22 "\}'  | cut -c1-14 "`;\par
        IP=`ssh root@$\{i\} "ps auxwww | grep postgres|grep -v vacuum|grep $\{line\} |grep -v grep | awk '\{print "{\field{\*\fldinst{HYPERLINK "\\\\\\\\$14"}}{\fldrslt{\ul\cf1\\\\$14}}}\f0\fs22 "\}' | cut -d\\( -f1|sort|uniq "`;\par
        for ip in `echo "$IP"`;\par
                do\par
                        #ssh root@$\{i\} "echo "$\{line\}" | cut -c1-14,49- "\par
                        HNAME=$(dig +short -x "$\{ip\}")\par
                        echo "  $\{ip\}   $\{HNAME\}"\par
                done\par
        echo\par
        done\par
done\par
exit 0\par
}
 