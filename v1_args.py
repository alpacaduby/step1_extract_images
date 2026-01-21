import os
import cv2
import re
import argparse
import numpy as np

def extract_digits_by_regex(s):
    """
    用正则表达式提取字符串中所有连续的数字序列，返回数字字符串列表
    """
    digits_list = re.findall(r'\d+', s)
    return digits_list if digits_list else ['0']  # 兜底：无数字时返回['0']避免索引错误

def extract_frames(video_path, interval_seconds=30, output_dir="extracted_frames"):
    """
    从视频中每隔指定秒数提取一帧并保存（支持中文路径）
    
    Args:
        video_path (str): 视频文件的路径（可含中文）
        interval_seconds (int): 提取帧的时间间隔（秒），默认30
        output_dir (str): 提取的帧保存的目录（可含中文）
    """
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)  # 替代os.path.exists+os.makedirs，更简洁
    
    # 打开视频文件（支持中文路径）
    cap = cv2.VideoCapture()
    cap.open(video_path, cv2.CAP_FFMPEG)  # 指定FFMPEG后端兼容中文路径
    if not cap.isOpened():
        print(f"【错误】无法打开视频文件：{video_path}")
        return
    
    # 获取视频的帧率（fps）和总帧数
    fps = cap.get(cv2.CAP_PROP_FPS)  # 每秒帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # 视频总帧数
    frame_interval = int(fps * interval_seconds)  # 指定秒数对应的帧数
    
    # 初始化变量
    current_frame = 0
    saved_frame_count = 0
    
    print(f"\n【视频信息】{os.path.basename(video_path)}")
    print(f"  帧率：{fps:.2f} FPS | 总帧数：{total_frames} | 提取间隔：{interval_seconds}秒（{frame_interval}帧）")
    print("  开始提取帧...")
    
    while True:
        # 读取一帧
        ret, frame = cap.read()
        # 如果读取失败（到视频末尾），退出循环
        if not ret:
            break
        
        # 每到指定间隔帧数，保存该帧
        if current_frame % frame_interval == 0:
            current_time = current_frame / fps
            # 构造保存的文件名（用秒数命名，如 0.jpg、30.jpg、60.jpg...）
            frame_filename = os.path.join(output_dir, f"{int(current_time)}.jpg")
            if os.path.exists(frame_filename):
                continue
            
            # ========== 支持中文路径保存 ==========
            # 1. 获取文件扩展名
            ext = os.path.splitext(frame_filename)[1].lower()
            # 2. 设置编码参数
            if ext in ['.jpg', '.jpeg']:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            elif ext == '.png':
                encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 0]
            else:
                print(f"【警告】不支持的扩展名 {ext}，默认使用.jpg编码")
                ext = '.jpg'
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
                frame_filename = os.path.splitext(frame_filename)[0] + '.jpg'
            
            # 3. 编码为二进制缓冲区
            retval, img_buf = cv2.imencode(ext, frame, encode_param)
            if not retval:
                print(f"  【失败】帧 {current_frame} 编码失败，跳过保存")
                current_frame += 1
                continue
            
            # 4. 写入文件（支持中文路径）
            try:
                with open(frame_filename, 'wb') as f:
                    img_buf.tofile(f)
                print(f"  【成功】保存：{frame_filename}（对应视频时间：{current_time:.1f}秒）")
                saved_frame_count += 1
            except Exception as e:
                print(f"  【失败】保存 {frame_filename} 出错：{str(e)}")
        
        current_frame += 1
    
    # 释放视频资源
    cap.release()
    print(f"  【完成】共保存 {saved_frame_count} 帧，保存路径：{os.path.abspath(output_dir)}")

def main():
    # 1. 创建argparse参数解析器
    parser = argparse.ArgumentParser(
        description="批量提取视频帧工具（支持中文路径）",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # 显示默认值
    )
    
    # 2. 添加命令行参数
    parser.add_argument(
        "-i", "--input-dir", 
        # required=True,  # 必填参数
        default=rf"F:\人世间",
        help="视频文件所在的输入目录（支持中文）"
    )
    parser.add_argument(
        "-o", "--output-base-dir", 
        default=rf"vlm_eval/step1_extract_images/images",  # 默认输出目录
        help="提取帧的基础输出目录（支持中文）"
    )
    parser.add_argument(
        "-s", "--interval-seconds", 
        type=int, 
        default=10,  # 默认30秒提取一次
        help="提取帧的时间间隔（秒）"
    )
    
    # 3. 解析命令行参数
    args = parser.parse_args()
    
    # 4. 验证输入目录是否存在
    if not os.path.isdir(args.input_dir):
        print(f"【错误】输入目录不存在：{args.input_dir}")
        return
    
    # 5. 构造输出目录
    output_dir = os.path.join(
        args.output_base_dir,
        os.path.basename(args.input_dir),
        f"interval_{args.interval_seconds}s"
    )
    exist_files = os.listdir(output_dir)
    exist_files.sort(key=lambda x: int(x))
    last_exist_video_name=exist_files[-1]
    
    # 6. 获取并排序输入目录下的mp4文件
    input_files = [f for f in os.listdir(args.input_dir) if f.endswith('.mp4')]
    if not input_files:
        print(f"【警告】输入目录 {args.input_dir} 下未找到.mp4文件")
        return
    
    # 按文件名中的数字排序
    input_files.sort(key=lambda x: int(extract_digits_by_regex(x)[0]))
    print(f"\n【批量处理】共找到 {len(input_files)} 个mp4视频文件，开始批量提取...")
    
    # 7. 遍历处理每个视频
    for idx, filename in enumerate(input_files, 1):
        filename_int=int(extract_digits_by_regex(filename)[0])
        if filename_int<int(last_exist_video_name):
            continue
        print(f"\n===== 处理第 {idx}/{len(input_files)} 个文件 =====")
        video_path = os.path.join(args.input_dir, filename)
        # 提取文件名中的数字作为子目录名
        name = extract_digits_by_regex(os.path.splitext(filename)[0])[0]
        output_dir_i = os.path.join(output_dir, name)
        # 提取帧
        extract_frames(video_path, args.interval_seconds, output_dir_i)

if __name__ == "__main__":
    main()