from CodeTree import *
class CodeTree:
    # 定义C语言关键字和运算符集合
    KEYWORDS = set(keyword.kwlist).union({
        'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
        'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
        'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof',
        'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void',
        'volatile', 'while', 'printf', 'scanf', 'main'
    })

    # 运算符优先级字典
    OPERATOR_PRECEDENCE = {
        '=': 1, '+=': 1, '-=': 1, '*=': 1, '/=': 1,
        '||': 2, '&&': 3, '|': 4, '^': 5, '&': 6,
        '==': 7, '!=': 7, '<': 8, '>': 8, '<=': 8, '>=': 8,
        '<<': 9, '>>': 9, '+': 10, '-': 10, '*': 11, '/': 11, '%': 11
    }
    def __init__(self):
        self.root = None
        self.source_code = ""
        self.preprocessed_code = ""
        self.total_nodes = 0

    def print_tree(self):
        """打印代码树结构"""
        if self.root is None:
            print("代码树为空")
            return

        # 使用RenderTree生成树的可视化表示
        for pre, fill, node in RenderTree(self.root):
            # 获取节点的类型和额外信息（如果有）
            node_info = node.name
            if hasattr(node, 'expr_str') and node.expr_str:
                node_info += f": {node.expr_str}"
            print(f"{pre}{node_info}")

    def _build_expression_tree(self, expr, parent):
        """构建表达式二叉树"""
        tokens = self._tokenize_expression(expr)
        if not tokens:
            return

        # 使用输出栈构建树
        output = [] # 存储后缀表达式
        ops = [] # 运算符栈

        # Shunting-yard算法
        for token in tokens:
            if token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    output.append(ops.pop())
                if ops and ops[-1] == '(':
                    ops.pop()  # 移除左括号
            elif token in self.OPERATOR_PRECEDENCE:
                # 处理运算符优先级
                while (ops and ops[-1] != '(' and
                       self.OPERATOR_PRECEDENCE.get(ops[-1], 0) >= self.OPERATOR_PRECEDENCE.get(token, 0)):
                    output.append(ops.pop())
                ops.append(token)
            else:
                # 操作数
                output.append(token)

        # 处理剩余运算符
        while ops:
            output.append(ops.pop())

        # 使用后缀表达式构建表达式树
        stack = [] # 表达式节点栈
        for token in output:
            if token in self.OPERATOR_PRECEDENCE:
                # 运算符节点
                right = stack.pop()
                left = stack.pop()
                op_node = Node(token, parent=parent)
                # 添加为操作数的父节点
                left.parent = op_node
                right.parent = op_node
                stack.append(op_node)
            else:
                # 操作数节点
                node = Node(token, parent=parent)
                stack.append(node)

        """
        eg:
            中缀表达式："(a + b) * c"
            后缀表达式：['a', 'b', '+', 'c', '*']
        """

    def _tokenize_expression(self, expr):
        """将表达式拆分为token"""
        tokens = []
        current = ''
        i = 0
        n = len(expr)

        while i < n:
            c = expr[i]
            # 处理空格：作为token分隔符
            if c.isspace():
                if current:
                    tokens.append(current)
                    current = ''
                i += 1
                continue

            # 处理运算符
            if c in '+-*/%=!<>&|^':
                if current:
                    tokens.append(current)
                    current = ''

                # 处理复合运算符
                if i < n - 1:
                    two_chars = c + expr[i + 1]
                    if two_chars in ('==', '!=', '<=', '>=', '+=', '-=', '*=', '/=', '&&', '||'):
                        tokens.append(two_chars)
                        i += 2
                        continue

                tokens.append(c)
                i += 1
                continue

            # 处理括号
            if c in '()':
                if current:
                    tokens.append(current)
                    current = ''
                tokens.append(c)
                i += 1
                continue

            # 处理其他字符（变量、数字等）
            current += c
            i += 1

        if current:
            tokens.append(current)

        return tokens

    def preprocess_code(self, code=None):
        """
        预处理代码：移除注释，替换标识符为var
        新增参数：允许传入特定代码进行预处理
        """
        input_code = code if code is not None else self.source_code
        if not input_code:
            return ""

        # 移除多行注释
        code_cleaned = re.sub(r'/\*.*?\*/', '', input_code, flags=re.DOTALL)  # 匹配包括换行符在内的所有字符
        # 移除单行注释
        code_cleaned = re.sub(r'//.*$', '', code_cleaned, flags=re.MULTILINE)  # 使$匹配每行的结尾
        # 替换标识符为var（非关键字）
        tokens = re.split(r'(\W)', code_cleaned)
        new_tokens = []
        for token in tokens:
            if token.strip() and not token.isspace():
                # 如果是标识符（字母/下划线开头，包含字母/数字/下划线）且不是关键字，替换为'var'
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token) and token not in self.KEYWORDS:
                    new_tokens.append('var')
                else:
                    new_tokens.append(token)
            else:
                new_tokens.append(token)  # 空白字符（空格、制表符等）直接保留
        return ''.join(new_tokens).replace('  ', ' ').replace('\t', ' ')

    def extract_main_body(self, code):
        """提取main函数体"""
        # 查找main函数的大致位置
        main_pos = re.search(r'\bmain\s*\(', code)
        if not main_pos:
            return None

        start = main_pos.start()  # 获取main函数的起始索引位置
        brace_count = 0  # 用于跟踪大括号层级（处理嵌套代码块）
        in_body = False  # 标记是否已进入函数体
        body_start = None  # 记录函数体起始位置

        # 从main位置开始扫描
        for i in range(start, len(code)):
            c = code[i]

            # 检测到第一个左大括号时，标记进入函数体
            if c == '{' and not in_body:
                brace_count = 1
                in_body = True
                body_start = i + 1  # 记录函数体起始位置（左大括号后的位置）
                continue

            # 在函数体内处理大括号计数
            if in_body:
                if c == '{':
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # 找到函数体结束
                        return code[body_start:i].strip()
        return None

    def _parse_control_structure(self, line, ctrl, parent):
        """解析控制结构（if, for, while, switch）"""
        if ctrl == 'switch':
            # 提取switch条件部分
            cond_start = line.find('(')
            cond_end = line.rfind(')')
            if cond_start == -1 or cond_end == -1:
                return None

            condition = line[cond_start + 1:cond_end].strip()

            # 创建switch节点
            switch_node = Node("switch", parent=parent)
            self.total_nodes += 1

            # 条件部分
            cond_node = Node("condition", parent=switch_node)
            cond_node.expr_str = condition
            self._build_expression_tree(condition, cond_node)

            # 创建switch的代码块节点
            block_node = Node("block", parent=switch_node)
            self.total_nodes += 1

            return switch_node
        else:
            # 原有if/for/while的解析逻辑保持不变
            cond_start = line.find('(')
            cond_end = line.rfind(')')
            if cond_start == -1 or cond_end == -1:
                # 尝试匹配没有括号的情况
                pattern = r'^(if|for|while)\s+(.+?)\s*(?:\{|$)'
                match = re.match(pattern, line)
                if not match:
                    return None
                condition = match.group(2)
            else:
                condition = line[cond_start + 1:cond_end].strip()

            # 创建控制结构节点
            ctrl_node = Node(ctrl, parent=parent)
            self.total_nodes += 1

            # 条件部分
            cond_node = Node("condition", parent=ctrl_node)
            cond_node.expr_str = condition
            self._build_expression_tree(condition, cond_node)

            return ctrl_node

    def _parse_line(self, line, parent):
        """解析单行代码并添加到树"""
        line = line.strip()
        if not line:
            return None

        # 特殊处理控制结构
        control_structures = ['if', 'for', 'while', 'switch']
        for ctrl in control_structures:
            if line.startswith(ctrl):
                return self._parse_control_structure(line, ctrl, parent)

        # 处理case和default
        if line.startswith('case'):
            # 创建case节点
            case_node = Node("case", parent=parent)
            self.total_nodes += 1

            # 提取case值
            case_value = line[4:].strip().split(':', 1)[0].strip()
            value_node = Node("value", parent=case_node)
            value_node.expr_str = case_value
            self._build_expression_tree(case_value, value_node)

            return case_node
        elif line.startswith('default:'):
            # 创建default节点
            default_node = Node("default", parent=parent)
            self.total_nodes += 1
            return default_node

        # 原有其他结构的解析逻辑保持不变
        if line.startswith('int var') or line.startswith('float var') or line.startswith('char var'):
            # 变量声明
            decl_node = Node("variable", parent=parent)
            self.total_nodes += 1
            # 处理初始化
            if '=' in line:
                expr = line.split('=', 1)[1].strip()
                expr = expr.rstrip(';')
                expr_node = Node("expression", parent=decl_node)
                expr_node.expr_str = expr
                self._build_expression_tree(expr, expr_node)
            return decl_node
        elif line.startswith('printf') or line.startswith('scanf'):
            # 输入输出语句
            io_node = Node("sentence", parent=parent)
            self.total_nodes += 1
            io_type = "printf" if line.startswith('printf') else "scanf"
            Node(io_type, parent=io_node)
            # 提取参数
            args = line.split('(', 1)[1].rsplit(')', 1)[0]
            for arg in args.split(','):
                arg = arg.strip().strip('"')
                if arg:
                    Node(f"arg: {arg}", parent=io_node)
            return io_node
        elif line.startswith('break') or line.startswith('continue'):
            # 跳转语句
            stmt_node = Node("sentence", parent=parent)
            self.total_nodes += 1
            line = line.rstrip(';')
            Node(line, parent=stmt_node)
            return stmt_node
        elif line.startswith('return'):
            # return语句
            return_node = Node("return", parent=parent)  # 直接挂到根节点
            self.total_nodes += 1
            expr = line[6:].strip()
            if expr:
                expr = expr.rstrip(';')
                expr_node = Node("expression", parent=return_node)
                expr_node.expr_str = expr
                self._build_expression_tree(expr, expr_node)
            return return_node
        else:
            # 表达式语句
            expr_node = Node("expression", parent=parent)
            self.total_nodes += 1
            line = line.rstrip(';')
            expr_node.expr_str = line
            self._build_expression_tree(line, expr_node)
            return expr_node

    def build_tree(self, code):
        """构建代码树"""
        self.source_code = code
        self.preprocessed_code = self.preprocess_code()
        main_body = self.extract_main_body(self.preprocessed_code)
        if not main_body:
            raise ValueError("未找到有效的main函数体")

        self.root = Node("main")
        self.total_nodes = 1

        stack = [self.root]  # 当前层次的父节点堆栈
        lines = main_body.split('\n')
        current_control = None  # 当前控制节点
        pending_else = None  # 待处理的else节点
        block_stack = []  # 代码块堆栈
        skip_next_line = False  # 标记是否跳过下一行

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if skip_next_line:
                skip_next_line = False
                continue

            # 处理 } else 组合
            if '}' in line and 'else' in line:
                parts = re.split(r'(})', line)
                if parts[0].strip():
                    self._parse_line(parts[0].strip(), stack[-1])

                if block_stack:
                    stack.pop()
                    block_stack.pop()

                else_part = ''.join(parts[2:]).strip()
                if else_part:
                    if 'if' in else_part:
                        # 处理 else if
                        cond_start = else_part.find('if') + 2
                        condition = else_part[cond_start:].strip().strip('()')
                        else_if_node = Node("else if", parent=stack[-1])
                        self.total_nodes += 1
                        cond_node = Node("condition", parent=else_if_node)
                        cond_node.expr_str = condition
                        self._build_expression_tree(condition, cond_node)
                        current_control = else_if_node
                        pending_else = None
                        block_node = Node("block", parent=current_control)
                        self.total_nodes += 1
                        stack.append(block_node)
                        block_stack.append(block_node)
                    else:
                        # 处理普通 else
                        else_node = Node("else", parent=stack[-1])
                        self.total_nodes += 1
                        pending_else = else_node
                        block_node = Node("block", parent=else_node)  # 直接挂载到 else 节点
                        self.total_nodes += 1
                        stack.append(block_node)
                        block_stack.append(block_node)
                continue

            # 处理代码块结束标记
            if line.startswith('}'):
                if block_stack:
                    stack.pop()
                    block_stack.pop()
                continue

            # 处理代码块开始标记 {
            if line.endswith('{'):
                code_part = line[:-1].strip()
                if code_part:
                    node = self._parse_line(code_part, stack[-1])
                    # 仅更新当前控制节点，不处理 pending_else（避免循环引用）
                    if node and node.name in ['if', 'for', 'while', 'else if', 'switch']:
                        current_control = node
                # 创建块节点并指定正确的父节点（当前控制节点或栈顶节点）
                block_parent = current_control if current_control else stack[-1]
                block_node = Node("block", parent=block_parent)
                self.total_nodes += 1
                stack.append(block_node)
                block_stack.append(block_node)
                continue

            # 解析普通行
            self._parse_line(line, stack[-1])

        return self.root

# 测试代码
code = """
int main() {
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
}
"""

tree = CodeTree()
tree.build_tree(code)
tree.print_tree()