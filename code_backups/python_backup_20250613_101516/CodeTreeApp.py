from CodeTree import *
import webbrowser  # 网页浏览器控制
import sys  # 系统参数和函数
import os
import tkinter as tk  # GUI库
from tkinter import scrolledtext, filedialog, messagebox, ttk  # GUI组件
import threading  # 多线程支持

# ====================
# CodeTreeApp类：UI界面
# ====================
class CodeTreeApp(tk.Tk):
    def __init__(self):
        # 调用父类初始化
        super().__init__()
        self.title("C代码树构建与重复率计算系统")
        self.geometry("1000x700")
        self.tree1 = CodeTree()
        self.tree2 = CodeTree()
        # 设置当前操作的代码树
        self.current_tree = self.tree1
        self.tree_names = {id(self.tree1): "代码1", id(self.tree2): "代码2"}
        self.tree_view_images = {}  # 用于存储树视图图像

        # 示例代码
        self.example_codes = [
            """int main() {
    int a = 10;
    printf("Value is %d", a);
    return 0;
}""",
            """int main() {
    int score = 85;
    if (score >= 60) {
        printf("Pass");
    } else {
        printf("Fail");
    }
    return 0;
}""",
            """int main() {
    for (int i = 0; i < 5; i++) {
        printf("%d", i);
    }
    return 0;
}""",
            """int main() {
    int a = 5;
    int b = 10;
    int sum = a + b;
    int product = a * b;
    printf("Sum: %d, Product: %d", sum, product);
    return 0;
}""",
            """int main() {
    for (int i = 1; i <= 10; i++) {
        if (i % 2 == 0) {
            printf("%d is even", i);
        } else {
            printf("%d is odd", i);
        }
    }
    return 0;
}""",
            """
            int main() {
    int a = 5;
    int b = 10;
    int sum = a + b;
    int product = a * b;
    float quotient = (float)b / a;

    printf("Sum: %d, Product: %d, Quotient: %.2f", sum, product, quotient);
    return 0;
}""",
            """int main() {
    int score = 85;
    if (score >= 90) {
        printf("Excellent!");
    } else if (score >= 80) {
        printf("Good job!");
    } else if (score >= 60) {
        printf("Pass");
    } else {
        printf("Fail");
    }
    return 0;
}""",
            """int main() {
    for (int i = 1; i <= 5; i++) {
        for (int j = 1; j <= i; j++) {
            printf("%d ", j);
        }
        return 0;
    }

    int sum = 0;
    int k = 1;
    while (k <= 100) {
        sum += k;
        k = k + 1;
    }
    printf("Sum: %d", sum);
    return 0;
}""",
            """int main() {
    int numbers[5] = {5, 2, 8, 1, 9};
    int min = numbers[0];
    int max = numbers[0];

    for (int i = 1; i < 5; i++) {
        if (numbers[i] < min) min = numbers[i];
        if (numbers[i] > max) max = numbers[i];
    }

    printf("Min: %d, Max: %d", min, max);
    return 0;
}""",
            """int main() {
    int age = 25;
    int experience = 3;

    if ((age >= 18 && experience >= 2) || 
        (age >= 20 && experience >= 1)) {
        printf("Qualified for job");
    } else {
        printf("Not qualified");
    }

    return 0;
}""",
            """int main() {
    int a = 12;  // 二进制: 1100
    int b = 10;  // 二进制: 1010

    int and = a & b;  // 1000 (8)
    int or = a | b;   // 1110 (14)
    int xor = a ^ b;  // 0110 (6)

    printf("AND: %d, OR: %d, XOR: %d", and, or, xor);

    return (0);
}""",
            """int main() {
    if (condition1) {
        for (int i = 0; i < 10; i++) {
            while (j < k) {
                if (sub_condition) {
                    return 0;
                } else {
                    return 0;
                }
                return 0;
            }
        }
    } else {
        switch (value) {
            case 1: handle_case1(); break;
            case 2: handle_case2(); break;
            default: handle_default();
        }
    }
    return 0;
}""",
            """int main() {
    int x = 10;
    int a[10] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9;
    return 0;
}""",
            """int main() {
    int a = (5 + 3) * (2 - 4);  // 正确表达式

    int b = (10 / (5 - 3));  // 正确

    int c = (8 * (2 + 1);  // 缺少闭合小括号

    printf("Results: %d, %d", a, b);

    return 0;
}""",
            """int main() {
    switch (value) {
            case 1: handle_case1(); break;
            case 2: handle_case2(); break;
            default: handle_default();
        }
    return 0;
}"""
        ]

        # 创建主界面
        self.create_widgets()

    def create_widgets(self):
        # 创建左侧控制面板
        control_frame = ttk.LabelFrame(self, text="操作面板", padding=10)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 创建按钮
        buttons = [
            ("输入代码1", self.input_code1),
            ("输入代码2", self.input_code2),
            ("显示预处理代码", self.show_preprocessed),
            ("切换当前代码", self.switch_current),
            ("显示代码树结构", self.show_tree_structure),
            ("可视化代码树", self.visualize_tree),
            ("插入代码行", self.insert_code_line),
            ("计算重复率", self.calculate_similarity),
            ("显示相似子树", self.show_similar_trees),
            ("示例代码演示", self.demo_example),
            ("语法检测", self.check_brackets),
            ("退出系统", self.quit)
        ]

        for i, (text, command) in enumerate(buttons):
            button = ttk.Button(control_frame, text=text, command=command)
            button.grid(row=i, column=0, sticky="ew", pady=3)

        # 创建状态显示
        self.status_var = tk.StringVar()
        self.status_var.set("当前操作代码: 代码1")
        status_label = ttk.Label(control_frame, textvariable=self.status_var)
        status_label.grid(row=len(buttons), column=0, sticky="w", pady=10)

        # 创建右侧输出面板
        self.output_frame = ttk.Notebook(self)
        self.output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # 创建文本输出标签页
        self.text_output = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD)
        self.text_output.grid(row=0, column=0, sticky="nsew")
        self.output_frame.add(self.text_output, text="输出信息")

        # 创建树结构显示标签页
        self.tree_frame = ttk.Frame(self.output_frame)
        self.tree_text = scrolledtext.ScrolledText(self.tree_frame, wrap=tk.WORD)
        self.tree_text.pack(fill="both", expand=True)
        self.output_frame.add(self.tree_frame, text="树结构")

        # 创建图像显示标签页
        self.image_frame = ttk.Frame(self.output_frame)
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(fill="both", expand=True)
        self.output_frame.add(self.image_frame, text="代码树图像")

        # 配置网格布局权重
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 在状态栏显示欢迎信息
        self.log_message("欢迎使用C代码树构建与重复率计算系统")

    def check_brackets(self):
        """执行括号匹配检测"""
        if not self.current_tree.source_code:
            self.log_message("请先构建代码树")
            return

        tree_name = self.tree_names[id(self.current_tree)]
        self.log_message(f"\n==== 检测 {tree_name} 的括号匹配情况 ====")

        try:
            # 进行括号匹配检测
            errors = self.current_tree.detect_bracket_errors()

            if not errors:
                self.log_message("未发现括号匹配问题：所有括号都正确匹配")
                return

            # 按行号分组错误
            errors_by_line = {}
            for error in errors:
                line = error['line']
                if line not in errors_by_line:
                    errors_by_line[line] = []
                errors_by_line[line].append(error)

            # 显示错误
            code_lines = self.current_tree.source_code.split('\n')
            for line_num in sorted(errors_by_line.keys()):
                errors = errors_by_line[line_num]
                self.log_message(f"\n在行 {line_num} 发现 {len(errors)} 个括号错误:")

                for error in errors:
                    self.log_message(f"  - {error['message']}")

                # 显示相关代码行
                if line_num - 1 < len(code_lines):
                    code_line = code_lines[line_num - 1].rstrip()
                    self.log_message(f"    代码: {code_line}")

        except Exception as e:
            self.log_message(f"括号检测时出错: {str(e)}")

    def log_message(self, message):
        """在输出区域记录消息"""
        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert(tk.END, message + "\n")
        self.text_output.see(tk.END)  # 滚动到底部
        self.text_output.config(state=tk.NORMAL)

    def clear_output(self):
        """清空输出区域"""
        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.config(state=tk.NORMAL)

    def input_code(self, is_tree1=True):
        """输入代码通用方法"""
        source_dialog = tk.Toplevel(self)
        source_dialog.title("选择输入方式")
        source_dialog.geometry("400x200")
        source_dialog.transient(self)
        source_dialog.grab_set()

        def manual_input():
            input_dialog = tk.Toplevel(source_dialog)
            input_dialog.title("手动输入代码")
            input_dialog.geometry("600x500")

            label = tk.Label(input_dialog, text="请输入C代码（包含main函数）:")
            label.pack(pady=10)

            text_area = scrolledtext.ScrolledText(input_dialog, wrap=tk.WORD, width=70, height=25)
            text_area.pack(padx=10, pady=5)

            if is_tree1 and self.tree1.preprocessed_code:
                text_area.insert(tk.END, self.tree1.preprocessed_code)
            elif not is_tree1 and self.tree2.preprocessed_code:
                text_area.insert(tk.END, self.tree2.preprocessed_code)

            def save_code():
                code = text_area.get("1.0", tk.END).strip()
                input_dialog.destroy()
                source_dialog.destroy()
                self.build_tree(code, is_tree1)

            btn_frame = tk.Frame(input_dialog)
            btn_frame.pack(pady=10)

            ttk.Button(btn_frame, text="确定", command=save_code).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="取消", command=input_dialog.destroy).pack(side=tk.LEFT, padx=5)

        def file_input():
            file_path = filedialog.askopenfilename(
                filetypes=[("C files", "*.c"), ("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        code = file.read()
                    source_dialog.destroy()
                    self.build_tree(code, is_tree1)
                except Exception as e:
                    messagebox.showerror("错误", f"读取文件失败: {str(e)}")

        def example_input():
            example_dialog = tk.Toplevel(source_dialog)
            example_dialog.title("选择示例代码")
            example_dialog.geometry("500x500")

            label = tk.Label(example_dialog, text="选择示例代码:")
            label.pack(pady=10)

            listbox = tk.Listbox(example_dialog, width=70, height=15)
            listbox.pack(padx=10, pady=5, fill="both", expand=True)

            for i, code in enumerate(self.example_codes):
                first_line = code.split('\n', 2)[1].strip()
                if len(first_line) > 60:
                    first_line = first_line[:57] + "..."
                listbox.insert(tk.END, f"示例 {i + 1}: {first_line}")

            def select_example():
                selection = listbox.curselection()
                if selection:
                    index = selection[0]
                    code = self.example_codes[index]
                    example_dialog.destroy()
                    source_dialog.destroy()
                    self.log_message(f"使用示例代码 {index + 1}")
                    self.build_tree(code, is_tree1)

            btn_frame = tk.Frame(example_dialog)
            btn_frame.pack(pady=10)

            ttk.Button(btn_frame, text="选择", command=select_example).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="取消", command=example_dialog.destroy).pack(side=tk.LEFT, padx=5)

        # 输入方式选择按钮
        ttk.Button(source_dialog, text="手动输入", command=manual_input).pack(pady=10, padx=20, fill="x")
        ttk.Button(source_dialog, text="文件导入", command=file_input).pack(pady=10, padx=20, fill="x")
        ttk.Button(source_dialog, text="示例代码", command=example_input).pack(pady=10, padx=20, fill="x")
        ttk.Button(source_dialog, text="取消", command=source_dialog.destroy).pack(pady=10, padx=20, fill="x")

    def input_code1(self):
        """输入代码1"""
        self.log_message("\n==== 输入代码1 ====")
        self.input_code(is_tree1=True)

    def input_code2(self):
        """输入代码2"""
        self.log_message("\n==== 输入代码2 ====")
        self.input_code(is_tree1=False)

    def build_tree(self, code, is_tree1=True):
        """构建代码树并同时进行括号检测"""
        tree = self.tree1 if is_tree1 else self.tree2
        tree_name = "代码1" if is_tree1 else "代码2"

        # 清除之前的树状态
        tree.root = None
        tree.source_code = code

        # 首先进行括号检测
        bracket_errors = tree.detect_bracket_errors()
        if bracket_errors:
            self.log_message(f"⚠️ {tree_name}检测到括号错误:")

            # 按行号分组错误
            errors_by_line = {}
            for error in bracket_errors:
                line = error['line']
                if line not in errors_by_line:
                    errors_by_line[line] = []
                errors_by_line[line].append(error)

            # 显示错误详情
            code_lines = code.split('\n')
            for line_num in sorted(errors_by_line.keys()):
                errors = errors_by_line[line_num]
                self.log_message(f"\n在行 {line_num} 发现 {len(errors)} 个括号错误:")

                for error in errors:
                    self.log_message(f"  - {error['message']}")

                    # 显示相关代码行
                    if line_num - 1 < len(code_lines):
                        code_line = code_lines[line_num - 1].rstrip()
                        self.log_message(f"    代码: {code_line}")

            # 更新状态
            if self.current_tree == tree:
                self.status_var.set(f"当前操作代码: {tree_name} (括号错误)")

            return False

        try:
            # 尝试构建代码树
            tree.build_tree(code)
            self.log_message(f"✅ {tree_name}树构建完成")

            # 更新当前树状态
            if self.current_tree == tree:
                self.status_var.set(f"当前操作代码: {tree_name} (已构建)")

            # 显示预处理后的代码
            self.log_message(f"\n{tree_name}预处理代码:")
            self.log_message(tree.preprocessed_code)

            return True

        except Exception as e:
            # 构建失败时提供详细错误信息
            error_msg = f"❌ 构建{tree_name}树失败: {str(e)}"
            self.log_message(error_msg)

            # 显示预处理后的代码（如果可用）
            if hasattr(tree, 'preprocessed_code'):
                self.log_message("\n预处理后的代码:")
                self.log_message(tree.preprocessed_code)

            # 更新状态
            if self.current_tree == tree:
                self.status_var.set(f"当前操作代码: {tree_name} (构建失败)")

            return False

    def show_preprocessed(self):
        """显示预处理后的代码"""
        if not self.current_tree.source_code:
            self.log_message("请先构建代码树")
            return

        tree_name = self.tree_names[id(self.current_tree)]
        self.log_message(f"\n==== {tree_name}预处理代码 ====")

        try:
            # 每次显示都重新预处理，确保是最新结果
            preprocessed = self.current_tree.preprocess_code(self.current_tree.source_code)
            self.log_message(preprocessed)

            # 在输出区域高亮显示
            self.text_output.config(state=tk.NORMAL)
            self.text_output.delete(1.0, tk.END)
            self.text_output.insert(tk.END, "预处理后的代码:\n\n")
            self.text_output.insert(tk.END, preprocessed)
            self.text_output.config(state=tk.NORMAL)
        except Exception as e:
            self.log_message(f"显示预处理代码时出错: {str(e)}")

    def switch_current(self):
        """切换当前代码"""
        self.current_tree = self.tree2 if self.current_tree == self.tree1 else self.tree1
        tree_name = self.tree_names[id(self.current_tree)]
        self.status_var.set(f"当前操作代码: {tree_name}")
        self.log_message(f"已切换到: {tree_name}")

    def show_tree_structure(self):
        """显示当前代码树结构"""
        if not self.current_tree.root:
            self.log_message("请先构建代码树")
            return

        tree_name = self.tree_names[id(self.current_tree)]
        self.log_message(f"\n==== {tree_name}树结构 ====")

        try:
            # 生成树结构文本
            tree_text = self.current_tree.text_representation()

            # 更新树结构显示区域
            self.tree_text.config(state=tk.NORMAL)
            self.tree_text.delete(1.0, tk.END)
            self.tree_text.insert(tk.END, tree_text)
            self.tree_text.config(state=tk.NORMAL)

            # 切换到树结构标签页
            self.output_frame.select(self.tree_frame)
            self.log_message("树结构已显示在'树结构'标签页中")
        except Exception as e:
            self.log_message(f"显示树结构时出错: {str(e)}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.log_message(f"错误发生在行: {exc_tb.tb_lineno}")

    def visualize_tree(self):
        """可视化当前代码树"""
        if not self.current_tree.root:
            self.log_message("请先构建代码树")
            return

        tree_name = self.tree_names[id(self.current_tree)]
        filename = f"{tree_name}_tree"

        def run_visualization():
            try:
                file_path = self.current_tree.visualize_tree(filename).filename + ".png"
                self.log_message(f"代码树可视化已保存为 {file_path}")

                # 显示图像
                self.display_image(file_path)
            except Exception as e:
                self.log_message(f"可视化失败: {str(e)}")

        threading.Thread(target=run_visualization).start()
        self.log_message(f"\n正在生成{tree_name}树的可视化图像...")

    def display_image(self, image_path):
        """在界面上显示图像"""
        try:
            from PIL import Image, ImageTk
            img = Image.open(image_path)
            img.thumbnail((700, 700))
            img_tk = ImageTk.PhotoImage(img)

            # 保存图像
            self.tree_view_images[image_path] = img_tk

            self.image_label.configure(image=img_tk)
            self.log_message(f"图像加载完成: {image_path}")
            self.output_frame.select(2)  # 切换到图像标签页
        except ImportError:
            self.log_message("请安装Pillow库来显示图像: pip install pillow")
            webbrowser.open(f"file://{os.path.abspath(image_path)}")
        except Exception as e:
            self.log_message(f"显示图像失败: {str(e)}")

    def insert_code_line(self):
        """插入代码行界面，并维护缩进格式"""
        if not self.current_tree.source_code:
            self.log_message("请先构建代码树")
            return

        # 创建弹出窗口
        popup = tk.Toplevel(self)
        popup.title("插入代码行")
        popup.geometry("600x450")
        popup.transient(self)
        popup.grab_set()

        # 创建一个主框架
        main_frame = ttk.Frame(popup)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建列表框
        ttk.Label(main_frame, text="选择插入位置:").grid(row=0, column=0, sticky="w")

        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        popup.rowconfigure(1, weight=1)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        # 添加列表框
        line_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            width=70,
            height=8,
            font=("Courier New", 10)  # 使用等宽字体
        )
        line_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=line_listbox.yview)

        # 填充列表
        lines = self.current_tree.source_code.splitlines()
        for i, line in enumerate(lines, 1):
            # 显示行号和缩进级别
            indent_level = len(line) - len(line.lstrip())
            indented_line = f"行 {i}: {' ' * indent_level}└▶ {line[0:70]}"
            if len(line) > 70:
                indented_line += "..."
            line_listbox.insert(tk.END, indented_line)

        # 添加代码输入区域
        ttk.Label(main_frame, text="插入的代码行:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        code_entry = ttk.Entry(main_frame, width=40)
        code_entry.grid(row=3, column=0, sticky="we", pady=(0, 10))

        # 添加缩进预览
        ttk.Label(main_frame, text="预计缩进级别:").grid(row=2, column=1, sticky="w", pady=(10, 0))
        indent_label = ttk.Label(main_frame, text="无")
        indent_label.grid(row=3, column=1, sticky="we", pady=(0, 10))

        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        def update_indent_preview():
            """更新缩进预览"""
            try:
                selection = line_listbox.curselection()
                if selection:
                    line_idx = selection[0]
                    if line_idx >= 0:
                        # 获取上一行的缩进级别
                        prev_line = lines[line_idx]
                        indent_level = len(prev_line) - len(prev_line.lstrip())
                        indent_text = f"{indent_level} 空格" if indent_level > 0 else "无缩进"

                        # 如果有代码输入，显示预览
                        if code_entry.get():
                            code_preview = " " * indent_level + code_entry.get()
                            indent_text += f" → '{code_preview}'"

                        indent_label.config(text=indent_text)
            except:
                indent_label.config(text="错误")

        def on_selection_change(event):
            update_indent_preview()

        def on_code_change(event):
            update_indent_preview()

        # 绑定事件
        line_listbox.bind("<<ListboxSelect>>", on_selection_change)
        code_entry.bind("<KeyRelease>", on_code_change)

        def do_insert():
            try:
                selection = line_listbox.curselection()
                if not selection:
                    messagebox.showerror("错误", "请选择插入位置的行号")
                    return

                line_idx = selection[0]
                if line_idx < 0 or line_idx >= len(lines):
                    messagebox.showerror("错误", "无效的行号选择")
                    return

                # 索引从0开始，实际行号从1开始
                line_num = line_idx + 1
                code_line = code_entry.get()

                if not code_line:
                    messagebox.showerror("错误", "请输入要插入的代码行")
                    return

                # 调用插入方法（传入行号）
                self.current_tree.insert_code_line(code_line, line_num)
                self.log_message(f"已在行号 {line_num} 后插入代码: {code_line}")

                # 显示更新后的预处理代码
                self.show_preprocessed()
                popup.destroy()

            except ValueError:
                messagebox.showerror("错误", "请输入有效的行号")
            except Exception as e:
                self.log_message(f"插入失败: {str(e)}")

        ttk.Button(btn_frame, text="插入", command=do_insert).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=popup.destroy).pack(side=tk.LEFT, padx=5)

    def calculate_similarity(self):
        """计算重复率"""
        if not self.tree1.root or not self.tree2.root:
            self.log_message("请先构建两段代码的树")
            return

        try:
            similarity = self.tree1.calculate_similarity(self.tree2)
            self.log_message("\n==== 代码相似度计算 ====")
            self.log_message(f"两段代码的相似度: {similarity:.2%}")
        except Exception as e:
            self.log_message(f"计算相似度失败: {str(e)}")

    def show_similar_trees(self):
        """显示相似子树"""
        if not self.tree1.root or not self.tree2.root:
            self.log_message("请先构建两段代码的树")
            return

        try:
            similar_subtrees = self.tree1.find_similar_subtrees(self.tree2)
            if not similar_subtrees:
                self.log_message("未找到相似子树")
                return

            self.log_message(f"\n==== 相似子树发现 ====")
            self.log_message(f"找到 {len(similar_subtrees)} 对相似子树:")

            # 只显示前三对相似子树
            for i, (sub1, sub2, score) in enumerate(similar_subtrees[:3], 1):
                self.log_message(f"\n相似子树对 {i} (相似度: {score:.0%})")

                self.log_message(f"\n{self.tree_names[id(self.tree1)]}中的子树:")
                self.log_message(self.tree1.display_tree(sub1, max_depth=3))

                self.log_message(f"\n{self.tree_names[id(self.tree2)]}中的子树:")
                self.log_message(self.tree2.display_tree(sub2, max_depth=3))
        except Exception as e:
            self.log_message(f"查找相似子树失败: {str(e)}")

    def demo_example(self):
        """示例代码演示"""
        example_dialog = tk.Toplevel(self)
        example_dialog.title("示例代码演示")
        example_dialog.geometry("600x400")

        label = tk.Label(example_dialog, text="选择要演示的示例:")
        label.pack(pady=10)

        listbox = tk.Listbox(example_dialog, width=70, height=15)
        listbox.pack(padx=10, pady=5, fill="both", expand=True)

        for i, code in enumerate(self.example_codes):
            first_line = code.split('\n', 2)[1].strip()
            if len(first_line) > 60:
                first_line = first_line[:57] + "..."
            listbox.insert(tk.END, f"示例 {i + 1}: {first_line}")

        def run_demo():
            selection = listbox.curselection()
            if not selection:
                return

            index = selection[0]
            code = self.example_codes[index]
            example_dialog.destroy()

            self.log_message(f"\n==== 示例代码 {index + 1} 演示 ====")
            self.log_message(f"示例代码:\n{code}")

            demo_tree = CodeTree()
            try:
                demo_tree.build_tree(code)
                self.log_message("\n预处理后的代码:")
                self.log_message(demo_tree.preprocessed_code)

                self.log_message("\n代码树文本表示:")
                tree_text = demo_tree.text_representation()
                self.log_message(tree_text)

                # 更新树结构标签页
                self.tree_text.config(state=tk.NORMAL)
                self.tree_text.delete(1.0, tk.END)
                self.tree_text.insert(tk.END, tree_text)
                self.tree_text.config(state=tk.DISABLED)

                self.log_message("\n计算自我相似度...")
                similarity = demo_tree.calculate_similarity(demo_tree)
                self.log_message(f"代码自我相似度: {similarity:.2%} (预期值为100%)")

                self.log_message("\n正在生成可视化图像...")
                threading.Thread(target=lambda: self.visualize_demo_tree(demo_tree, index + 1)).start()
            except Exception as e:
                self.log_message(f"示例演示失败: {str(e)}")
                if hasattr(e, 'preprocessed_code'):
                    self.log_message("预处理后的代码:")
                    self.log_message(e.preprocessed_code)

        btn_frame = tk.Frame(example_dialog)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="运行演示", command=run_demo).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=example_dialog.destroy).pack(side=tk.LEFT, padx=10)

    def visualize_demo_tree(self, demo_tree, index):
        """可视化演示树"""
        try:
            filename = f"demo_tree_{index}"
            file_path = demo_tree.visualize_tree(filename).filename + ".png"
            self.log_message(f"代码树可视化已保存为 {file_path}")

            # 显示图像
            self.display_image(file_path)
        except Exception as e:
            self.log_message(f"可视化失败: {str(e)}")