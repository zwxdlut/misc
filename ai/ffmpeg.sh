# 抽取关键帧
ffmpeg -i input.mp4 -vf "select=eq(pict_type\,I)" -vsync vfr tmp/input_%04d.jpg

# 获取视频时长（秒）
duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4)
# 均匀抽取一定数量的非关键帧
ffmpeg -i input.mp4 -vf "select='not(key)', fps=1/($duration/20)" -vframes 20 tmp/input_%04d.jpg

# 抽取一定数量的帧
ffmpeg -i input.mp4 -vf "fps=fps=25/$duration" tmp/input_%4d.jpg