#!/bin/bash

# 定位到当前目录
cd /d/others.projects/

# 生成随机等待时间（60秒到300秒之间）
random_wait=$((RANDOM % 241 + 60))
sleep $random_wait
# 获取当前时间
current_time=$(date +"%Y-%m-%d %H:%M:%S")
echo ${current_time} 已经等待了${random_wait}秒, 开始打卡

# 检查是否安装了 adb
if ! command -v adb &> /dev/null
then
    echo "未找到 adb 命令。请确保已安装 Android 调试桥 (adb)。"
    exit 1
fi

# 获取设备列表
device_list=$(adb devices | awk 'NR>1 {print $1}')

# 检查设备数量
device_count=$(echo "$device_list" | wc -l)

# 多个设备让用户选择
# if [[ $device_count -eq 0 ]]; then
#     echo "未找到连接的设备。请确保至少有一个设备连接到计算机。"
#     exit 1
# elif [[ $device_count -gt 1 ]]; then
#     echo "找到多个设备，请选择要操作的设备："
#     select device_ip in $device_list; do
#         if [[ -n $device_ip ]]; then
#             break
#         else
#             echo "无效的选择。请重新输入："
#         fi
#     done
# else
#     # 只有一个设备时，直接使用该设备
#     device_ip=$device_list
# fi

# 默认选择第一个设备
# device_ip=$(echo "$device_list" | head -n 1)
# 有时候找不到设备, 可以暂时直接写死手机的内网IP
device_ip="192.168.1.56"

# 连接到设备
adb connect $device_ip

# 检查连接是否成功
if adb devices | grep -q "$device_ip"
then
    echo "设备连接成功"
    # 连接成功后执行其他操作
else
    echo "设备连接失败"
    exit 1  # 中断脚本
fi

# 按下电源键点亮手机屏幕
adb -s $device_ip shell input keyevent KEYCODE_POWER
echo "点亮屏幕"

# 上滑解锁
adb -s $device_ip shell input swipe 780 1888 780 800

# 密码解锁
adb -s $device_ip shell input tap xxx xxx
# ...
echo "已经解锁"

# 打开钉钉
adb -s $device_ip shell am start -n com.alibaba.android.rimet/com.alibaba.android.rimet.biz.LaunchHomeActivity
echo "打开钉钉"

# 等待自动打卡10秒钟
sleep 10
echo "已经等待10秒钟, 打卡完成"

# 回到主界面
adb -s $device_ip shell input keyevent KEYCODE_HOME
echo "回到主界面"

# 按下电源键关闭手机屏幕
adb -s $device_ip shell input keyevent KEYCODE_POWER
echo "按下电源按钮关闭屏幕"
echo ""
