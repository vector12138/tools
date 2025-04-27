import os
import json
import shutil
import argparse
import datetime
from pathlib import Path
import hashlib

def calculate_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def process_folders(source_dir, target_dir, min_creation_date=None, copy_mode=False):
    """
    递归查找源目录下的所有文件夹，查找mp4文件和project.json文件，
    并将mp4文件移动到目标目录，以project.json中的title字段命名
    
    参数:
    source_dir -- 源目录路径
    target_dir -- 目标目录路径
    min_creation_date -- 最小创建日期，只处理在此日期之后创建的文件夹
    copy_mode -- 如果为True，复制文件而不是移动
    """
    # 确保目标目录存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 计数器
    processed_count = 0
    error_count = 0
    skipped_count = 0
    
    # 遍历源目录下的所有文件夹
    for root, dirs, files in os.walk(source_dir):
        # 检查当前文件夹是否包含project.json文件
        project_json_path = os.path.join(root, 'project.json')
        if os.path.exists(project_json_path):
            # 检查文件夹创建时间
            folder_creation_time = datetime.datetime.fromtimestamp(os.path.getctime(root))
            
            # 如果指定了最小创建日期，且文件夹创建时间早于该日期，则跳过
            if min_creation_date and folder_creation_time < min_creation_date:
                print(f"跳过文件夹 {root} (创建时间: {folder_creation_time}, 早于指定日期: {min_creation_date})")
                skipped_count += 1
                continue
                
            try:
                # 读取project.json文件
                with open(project_json_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                # 获取title字段
                if 'title' in project_data:
                    title = project_data['title']
                    
                    # 查找当前文件夹中的mp4文件
                    mp4_files = [f for f in files if f.lower().endswith('.mp4')]
                    
                    # 如果project.json中有file字段，优先使用该字段指定的mp4文件
                    if 'file' in project_data and project_data['file'].lower().endswith('.mp4'):
                        specified_mp4 = project_data['file']
                        if specified_mp4 in files:
                            mp4_files = [specified_mp4]
                    
                    # 处理找到的mp4文件
                    for mp4_file in mp4_files:
                        source_path = os.path.join(root, mp4_file)
                        
                        # 清理title，移除不允许在文件名中使用的字符
                        safe_title = "".join([c for c in title if c not in r'<>:"/\|?*'])
                        
                        # 构建目标路径，确保文件扩展名正确
                        target_path = os.path.join(target_dir, f"{safe_title}.mp4")
                        
                        # 如果目标文件已存在，检查是否同一文件，如果是则跳过，不是则添加数字后缀
                        while os.path.exists(target_path):
                            if calculate_file_hash(source_path) == calculate_file_hash(target_path):
                                print(f"跳过相同文件: {source_path}")
                                break
                            # 修正计数器逻辑，避免重复自增
                            counter += 1
                            target_path = os.path.join(target_dir, f"{safe_title}_{counter}.mp4")
                            # 持续检查新文件名是否存在，直到找到唯一文件名
                            while os.path.exists(target_path):
                                counter += 1
                                target_path = os.path.join(target_dir, f"{safe_title}_{counter}.mp4")
                        
                        # 移动或复制文件
                        if copy_mode:
                            print(f"复制文件: {source_path} -> {target_path}")
                            shutil.copy2(source_path, target_path)  # 使用copy2保留元数据
                        else:
                            print(f"移动文件: {source_path} -> {target_path}")
                            shutil.move(source_path, target_path)
                        
                        processed_count += 1
                else:
                    print(f"警告: {project_json_path} 中没有找到title字段")
                    error_count += 1
            except Exception as e:
                print(f"处理文件夹 {root} 时出错: {str(e)}")
                error_count += 1
    
    return processed_count, error_count, skipped_count

def parse_date(date_str):
    """解析日期字符串，支持多种格式"""
    formats = [
        "%Y-%m-%d",       # 2023-01-31
        "%Y/%m/%d",       # 2023/01/31
        "%d.%m.%Y",       # 31.01.2023
        "%Y%m%d"          # 20230131
    ]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"无法解析日期: {date_str}。支持的格式: YYYY-MM-DD, YYYY/MM/DD, DD.MM.YYYY, YYYYMMDD")

def main():
    source_dir = r"E:\Steam\steamapps\workshop\content\431960"
    target_dir = r"Z:\entertain\videos"
    after_date = "2025-04-25"
    copy = False
    
    # 验证源目录存在
    if not os.path.isdir(source_dir):
        print(f"错误: 源目录 '{source_dir}' 不存在")
        return
    
    # 解析日期参数
    min_creation_date = None
    if after_date:
        try:
            min_creation_date = parse_date(after_date)
            print(f"只处理在 {min_creation_date} 之后创建的文件夹")
        except ValueError as e:
            print(f"错误: {str(e)}")
            return
    
    print(f"开始处理: 从 {source_dir} 到 {target_dir}")
    processed_count, error_count, skipped_count = process_folders(
        source_dir, 
        target_dir, 
        min_creation_date=min_creation_date,
        copy_mode=copy
    )
    
    print(f"\n处理完成!")
    print(f"成功处理的文件: {processed_count}")
    print(f"跳过的文件夹: {skipped_count}")
    if error_count > 0:
        print(f"处理失败的文件夹: {error_count}")

if __name__ == "__main__":
    main()


