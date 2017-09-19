set -e
source /data/workspace/junchen/virt_env/py27/bin/activate
#echo "just a test"
# 1. env
project_dir="/data/workspace/junchen/zhibuAI" 
cd $project_dir

DATE=`date +%Y-%m-%d` 
if [ $# -gt 0   ]; then
    DATE=$(date "+%Y-%m-%d" -d "$1")
    fi
    echo $DATE

    python run.py $DATE production &> log/"$DATE".log 
    
