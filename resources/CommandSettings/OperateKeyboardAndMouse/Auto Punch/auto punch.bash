# 生成随机等待时间（60秒到300秒之间）
random_wait=$((RANDOM % 241 + 60))
sleep $random_wait
# 获取当前时间
current_time=$(date +"%Y-%m-%d %H:%M:%S")
echo ${current_time} 已经等待了${random_wait}秒, 开始打卡 >> "D:/others.projects/tools/log.txt"

python D:/others.projects/tools/kakaxi.py -f "D:/others.projects/tools/resources/CommandSettings/OperateKeyboardAndMouse/Auto Punch/title robots punch.txt" >> "D:/others.projects/tools/log.txt"
sleep 10