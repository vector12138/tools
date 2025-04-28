import os
import hashlib

# 计算文件的 MD5 值
# 此函数用于计算指定文件的 MD5 哈希值
# Args:
#     file_path (str): 文件的路径
# Returns:
#     str: 文件的 MD5 哈希值
def calculate_md5(file_path):
    """计算指定文件的 MD5 哈希值。
    
    Args:
        file_path (str): 文件的路径。
    
    Returns:
        str: 文件的 MD5 哈希值。
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# 获取目录下所有文件的信息，包含文件名和 MD5 值
# 此函数用于获取指定目录下所有文件的信息
# Args:
#     folder_path (str): 目录的路径
# Returns:
#     dict: 包含文件名和对应 MD5 值的字典
def get_files_info(folder_path):
    """获取指定目录下所有文件的信息。
    
    Args:
        folder_path (str): 目录的路径。
    
    Returns:
        dict: 包含文件名和对应 MD5 值的字典。
    """
    files_info = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_md5 = calculate_md5(file_path)
            files_info[file] = file_md5
    return files_info

# 比较两个目录下的文件差异
# 此函数用于比较两个目录下的文件差异
# Args:
#     folder1 (str): 第一个目录的路径
#     folder2 (str): 第二个目录的路径
def compare_folders(folder1, folder2):
    """比较两个目录下的文件差异。
    
    Args:
        folder1 (str): 第一个目录的路径。
        folder2 (str): 第二个目录的路径。
    """
    files_info1 = get_files_info(folder1)
    files_info2 = get_files_info(folder2)

    print(f"正在比较文件夹 {folder1} 和 {folder2}...")
    print("文件名和 MD5 值匹配情况：")

    fail = []
    all = True
    for file_name, file_md5 in files_info1.items():
        if file_name in files_info2:
            if file_md5 != files_info2[file_name]:
                all = False
                fail.append(file_name)
                print(f"文件名匹配但 MD5 值不同或文件不存在: {file_name}")
        else:
            all = False
            fail.append(file_name)
            print(f"文件只存在于 {folder1}: {file_name}")

    for file_name in files_info2.keys():
        if file_name not in files_info1:
            all = False
            fail.append(file_name)
            print(f"文件只存在于 {folder2}: {file_name}")

    print("检查完成: " + str(all))
    print(fail)

# 主程序入口
if __name__ == "__main__":
    """主程序入口，用于测试目录比较功能。"""
    folder1 = "V:\photo\root\DCIM\DJI Album"
    folder2 = "Z:\photo\DJI Album"

    if not os.path.exists(folder1) or not os.path.exists(folder2):
        print("输入的文件夹路径无效，请检查路径是否正确。")
    else:
        compare_folders(folder1, folder2)