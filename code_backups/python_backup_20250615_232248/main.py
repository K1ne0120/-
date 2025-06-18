from CodeTreeApp import *
from util import *
if __name__ == "__main__":
    # 设置备份目录，默认为当前目录下的code_backups文件夹
    backup_directory = './code_backups'

    # 执行备份
    backup_current_script(backup_directory)

    # 启动GUI应用
    app = CodeTreeApp()
    app.mainloop()