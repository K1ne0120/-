import os
import shutil
import datetime


def backup_current_script(backup_dir='./code_backups'):
    """
    备份当前目录下的所有Python脚本到指定目录

    参数:
    backup_dir (str): 备份文件存储的目录路径，默认为当前目录下的code_backups文件夹
    """
    # 获取当前目录
    current_dir = os.getcwd()

    # 创建备份根目录（如果不存在）
    os.makedirs(backup_dir, exist_ok=True)

    # 生成带时间戳的备份文件夹名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder_name = f"python_backup_{timestamp}"
    backup_folder_path = os.path.join(backup_dir, backup_folder_name)

    # 创建备份文件夹
    os.makedirs(backup_folder_path, exist_ok=True)

    try:
        # 遍历当前目录下的所有文件
        for filename in os.listdir(current_dir):
            # 只处理.py文件
            if filename.endswith('.py'):
                file_path = os.path.join(current_dir, filename)
                # 确保是文件而不是目录
                if os.path.isfile(file_path):
                    # 复制文件到备份文件夹
                    shutil.copy2(file_path, os.path.join(backup_folder_path, filename))

        print(f"代码已备份到: {backup_folder_path}")
        return backup_folder_path
    except Exception as e:
        print(f"备份失败: {e}")
        return None