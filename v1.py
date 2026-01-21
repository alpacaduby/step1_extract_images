import os
import cv2

def extract_frames(video_path, interval_seconds=30, output_dir="extracted_frames"):
    """
    从视频中每隔30秒提取一帧并保存
    
    Args:
        video_path (str): 视频文件的路径
        output_dir (str): 提取的帧保存的目录，默认是extracted_frames
    """
    # 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误：无法打开视频文件 {video_path}")
        return
    
    # 获取视频的帧率（fps）和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)  # 每秒帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 视频总帧数
    frame_interval = int(fps *  interval_seconds)  #  interval_seconds秒对应的帧数
    
    # 初始化变量
    current_frame = 0
    saved_frame_count = 0
    
    print(f"视频帧率：{fps} FPS")
    print(f"30秒对应帧数：{frame_interval} 帧")
    print(f"视频总帧数：{total_frames} 帧")
    print("开始提取帧...")
    
    while True:
        # 读取一帧
        ret, frame = cap.read()
        # 如果读取失败（到视频末尾），退出循环
        if not ret:
            break
        
        # 每到30秒对应的帧数，保存该帧
        if current_frame % frame_interval == 0:
            # 构造保存的文件名（格式：frame_000.jpg、frame_001.jpg...）
            current_time=current_frame/fps
            frame_filename = os.path.join(output_dir, f"{int(current_time)}.jpg")
            # 保存帧
            # cv2.imwrite(frame_filename, frame)
            # ========== 核心修改：支持中文路径保存 ==========
            # 1. 获取文件扩展名（确保编码格式匹配）
            ext = os.path.splitext(frame_filename)[1].lower()
            # 2. 设置编码参数（JPG质量95，PNG压缩0）
            if ext == '.jpg' or ext == '.jpeg':
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            elif ext == '.png':
                encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 0]
            else:
                print(f"警告：不支持的扩展名 {ext}，默认用JPG编码")
                ext = '.jpg'
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
                frame_filename = os.path.splitext(frame_filename)[0] + '.jpg'
            
            # 3. 将图像编码为二进制缓冲区（关键：避开cv2.imwrite的中文路径问题）
            retval, img_buf = cv2.imencode(ext, frame, encode_param)
            if not retval:
                print(f"失败：帧 {current_frame} 编码失败，跳过保存")
                saved_frame_count += 1
                current_frame += 1
                continue
            
            # 4. 用Python原生IO写入文件（支持中文路径）
            try:
                with open(frame_filename, 'wb') as f:
                    img_buf.tofile(f)
                print(f"已保存：{frame_filename} (对应视频时间：{current_frame/fps:.1f} 秒)")
            except Exception as e:
                print(f"失败：保存 {frame_filename} 出错 - {str(e)}")
            print(f"已保存：{frame_filename} (对应视频时间：{current_time:.1f} 秒)")
            saved_frame_count += 1
        
        current_frame += 1
    
    # 释放视频资源
    cap.release()
    print(f"\n提取完成！共保存 {saved_frame_count} 帧，保存路径：{os.path.abspath(output_dir)}")
    
import re
def extract_digits_by_regex(s):
    """
    用正则表达式提取字符串中所有连续的数字序列，返回数字字符串列表
    """
    # \d+ 匹配1个或多个连续的数字
    digits_list = re.findall(r'\d+', s)
    return digits_list

input_dir=rf"F:\欢乐颂"
output_base_dir=rf"vlm_eval\step1_extract_images\images"
interval_seconds=30

output_dir=os.path.join(output_base_dir,os.path.basename(input_dir),f"interval_{interval_seconds}s")
input_files=os.listdir(input_dir)
input_files.sort(key=lambda x: int(extract_digits_by_regex(x)[0]))

for i in input_files:
    video_path=os.path.join(input_dir,i)
    if not video_path.endswith('.mp4'): continue
    name=extract_digits_by_regex(os.path.splitext(i)[0])[0]
    output_dir_i=os.path.join(output_dir,name)
    extract_frames(video_path,interval_seconds=interval_seconds, output_dir=output_dir_i)
    