#!/bin/bash
FILE=$2
if [ "$1" = "d" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c d -f "$FILE"  
fi
if [ "$1" = "f" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c f -f "$FILE"  
fi
if [ "$1" = "vs" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c vs -f "$FILE"  
fi
if [ "$1" = "trae" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c trae -f "$FILE"  
fi
if [ "$1" = "antigravity" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c antigravity -f "$FILE"  
fi
if [ "$1" = "services" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c services  
fi
if [ "$1" = "services11" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c services11  
fi
if [ "$1" = "selinux" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c selinux  
fi
if [ "$1" = "selinux11" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c selinux11  
fi
if [ "$1" = "apush" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c apush -f "$FILE"  -p  "$3" "$4" "$5" "$6"
fi
if [ "$1" = "areboot" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c areboot  
fi
if [ "$1" = "adb" ]; then
    python3 /home/quwj/work/worktools/fastopen/server.py -c adb  -p $2 "$3" "$4" "$5" "$6"
fi
