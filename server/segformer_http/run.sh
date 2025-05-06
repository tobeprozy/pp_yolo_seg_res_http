if [ $1 -eq 1 ]; then
  nohup python3 httpdemo.py > output.log 2>&1 &
else
  ps -aux | grep httpdemo | awk -F' ' '{print $2}' | xargs kill -9
fi