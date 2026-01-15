alias b1='cd ../'
alias b2='cd ../../'
alias b3='cd ../../../'
alias b4='cd ../../../../'
alias b5='cd ../../../../../'
alias b6='cd ../../../../../../'
alias b7='cd ../../../../../../../'
alias grn="grep -rn"
alias gnr="grep -rn"
alias fn="find . -name"
alias vi=vim
alias rgu="rg -uu"
alias tat="tmux attach -t"

alias d='/home/quwj/work/worktools/fastopen/open.sh d '
alias f='/home/quwj/work/worktools/fastopen/open.sh f '
alias vs='/home/quwj/work/worktools/fastopen/open.sh vs '
alias trae='/home/quwj/work/worktools/fastopen/open.sh trae '
alias antigravity='/home/quwj/work/worktools/fastopen/open.sh antigravity '
alias services='/home/quwj/work/worktools/fastopen/open.sh services '
alias services11='/home/quwj/work/worktools/fastopen/open.sh services11 '
alias selinux='/home/quwj/work/worktools/fastopen/open.sh selinux '
alias selinux11='/home/quwj/work/worktools/fastopen/open.sh selinux11 '
alias apush='/home/quwj/work/worktools/fastopen/open.sh apush '
alias areboot='/home/quwj/work/worktools/fastopen/open.sh areboot '
alias adb='/home/quwj/work/worktools/fastopen/open.sh adb '
alias meminfo='free -m -l -t'
## get top process eating memory
alias psmem='ps auxf | sort -nr -k 4'
alias psmem10='ps auxf | sort -nr -k 4 | head -10'
 ## get top process eating cpu ##
alias pscpu='ps auxf | sort -nr -k 3'
alias pscpu10='ps auxf | sort -nr -k 3 | head -10'

## Get server cpu info ##
alias cpuinfo='lscpu'
#------------
# Disk
#------------
alias dfree='df -HPT'
PS1='\[\e[96;49m\][\[\e[92;49m\]\u@\h \[\e[93;49m\]\t\[\e[96;49m\]] \w\n \[\e[91;49m\]\$ \[\e[0m\]'
