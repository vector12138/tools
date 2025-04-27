import os
import hashlib

def calculate_md5(file_path):
    """计算文件的MD5值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_files_info(folder_path):
    """获取文件夹中所有文件的文件名和MD5值"""
    files_info = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_md5 = calculate_md5(file_path)
            files_info[file] = file_md5
    return files_info

def compare_folders(folder1, folder2):
    """比较两个文件夹中的文件"""
    files_info1 = get_files_info(folder1)
    files_info2 = get_files_info(folder2)

    print(f"正在比较文件夹 {folder1} 和 {folder2}...")
    print("文件名和MD5值匹配情况：")

    fail = []

    all = True
    for file_name, file_md5 in files_info1.items():
        if file_name in files_info2:
            if file_md5 != files_info2[file_name]:
                all = False
                fail.append(file_name)
                print(f"文件名匹配但MD5值不同或文件不存在: {file_name}")

    print("检查完成: " + str(all))
    print(fail)

if __name__ == "__main__":
    folder1 = "V:\\photo\\root\\DCIM\\DJI Album"
    folder2 = "Z:\\photo\\DJI Album"

    if not os.path.exists(folder1) or not os.path.exists(folder2):
        print("输入的文件夹路径无效，请检查路径是否正确。")
    else:
        compare_folders(folder1, folder2)