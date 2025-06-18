import re  # 正则表达式
import graphviz  # 可视化库
import keyword  # Python关键字列表
from anytree import Node, RenderTree  # 树结构
from collections import deque  # 双端队列
from io import StringIO  # 内存文件操作

# ====================
# CodeTree类：处理代码解析和树结构操作
# ====================
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
        self.root = None # 树的根节点
        self.preprocessed_code = "" # 预处理后的代码
        self.source_code = ""  # 原始源代码
        self.total_nodes = 0 # 节点总数

    def set_source_code(self, code):
        """设置源代码"""
        self.source_code = code # 将传入的代码赋值给实例变量source_code，用于存储原始源代码
        self.preprocessed_code = "" # 清空预处理后的代码，因为源代码已更新，需要重新预处理
        self.root = None # 将根节点重置为None，因为源代码已更新，需要重新构建树结构
        self.total_nodes = 0  # 将节点计数器重置为0，因为树结构需要重新构建

    def preprocess_code(self, code=None):
        """
        预处理代码：移除注释，替换标识符为var
        新增参数：允许传入特定代码进行预处理
        """
        input_code = code if code is not None else self.source_code
        if not input_code:
            return ""

        # 移除多行注释
        code_cleaned = re.sub(r'/\*.*?\*/', '', input_code, flags=re.DOTALL) # 匹配包括换行符在内的所有字符
        # 移除单行注释
        code_cleaned = re.sub(r'//.*$', '', code_cleaned, flags=re.MULTILINE) # 使$匹配每行的结尾
        # 替换标识符为var（非关键字）
        tokens = re.split(r'(\W)', code_cleaned) # 分割成列表
        new_tokens = []
        for token in tokens:
            if token.strip() and not token.isspace():
                # 如果是标识符（字母/下划线开头，包含字母/数字/下划线）且不是关键字，替换为'var'
                if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token) and token not in self.KEYWORDS:
                    new_tokens.append('var')
                else:
                    new_tokens.append(token)
            else:
                new_tokens.append(token) # 空白字符（空格、制表符等）直接保留
        return ''.join(new_tokens).replace('  ', ' ').replace('\t', ' ')

    def extract_main_body(self, code):
        """提取main函数体"""
        # 查找main函数的大致位置
        main_pos = re.search(r'\bmain\s*\(', code)
        if not main_pos:
            return None

        start = main_pos.start() # 获取main函数的起始索引位置
        brace_count = 0 # 用于跟踪大括号层级（处理嵌套代码块）
        in_body = False # 标记是否已进入函数体
        body_start = None # 记录函数体起始位置

        # 从main位置开始扫描
        for i in range(start, len(code)):
            c = code[i]

            # 检测到第一个左大括号时，标记进入函数体
            if c == '{' and not in_body:
                brace_count = 1
                in_body = True
                body_start = i + 1 # 记录函数体起始位置（左大括号后的位置）
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


    # 答辩点 1
    def detect_bracket_errors(self, code=None):
        """
        检测括号匹配错误（只检测小括号和中括号）
        """
        if code is None:
            if not self.source_code:
                return []
            code = self.source_code

        errors = []  # 存储检测到的错误
        bracket_stack = []  # 括号匹配栈
        in_comment = False  # 多行注释状态
        in_single_comment = False  # 单行注释状态
        in_string = False  # 字符串状态
        in_char = False  # 字符常量状态
        # 行号和位置计数器：精确定位错误位置
        current_line = 1
        current_position = 0

        # 逐字符扫描代码
        i = 0
        n = len(code)
        while i < n:
            char = code[i]
            current_position += 1

            # 处理换行
            if char == '\n':
                current_line += 1
                current_position = 0
                in_single_comment = False  # 单行注释在换行时结束
                i += 1
                continue

            # 处理多行注释
            if in_comment:
                # 检查注释结束
                if char == '*' and i + 1 < n and code[i + 1] == '/':
                    in_comment = False
                    i += 2  # 跳过 '/' 字符
                    current_position += 1
                    continue
                i += 1
                continue

            # 处理单行注释
            if in_single_comment:
                i += 1
                continue

            # 处理字符串中的内容
            if in_string:
                # 处理转义字符
                if char == '\\':
                    # 跳过下一个字符
                    i += 1
                    current_position += 1
                # 字符串结束
                elif char == '"':
                    in_string = False
                i += 1
                continue

            # 处理字符常量
            if in_char:
                # 处理转义字符
                if char == '\\':
                    # 跳过下一个字符
                    i += 1
                    current_position += 1
                # 字符结束
                elif char == "'":
                    in_char = False
                i += 1
                continue

            # 检测注释开始
            if char == '/':
                # 检查是单行注释还是多行注释
                if i + 1 < n:
                    next_char = code[i + 1]
                    if next_char == '/':  # 单行注释
                        in_single_comment = True
                    elif next_char == '*':  # 多行注释
                        in_comment = True
                i += 1
                continue

            # 检测字符串开始
            if char == '"':
                in_string = True
                i += 1
                continue

            # 检测字符常量开始
            if char == "'":
                in_char = True
                i += 1
                continue

            # 括号匹配检测
            if char in '([':
                # 遇到开括号，压入栈
                bracket_stack.append({
                    'type': char,
                    'line': current_line,
                    'position': current_position
                })
            elif char in ')]':
                # 遇到闭括号
                if not bracket_stack:
                    # 栈为空，多余的闭括号
                    errors.append({
                        'type': 'bracket',
                        'message': f"多余的闭括号 '{char}'",
                        'line': current_line,
                        'position': current_position
                    })
                else:
                    # 弹出最近的括号
                    last_open = bracket_stack.pop()
                    # 检查括号类型是否匹配
                    if (char == ')' and last_open['type'] != '(') or \
                            (char == ']' and last_open['type'] != '['):
                        errors.append({
                            'type': 'bracket',
                            'message': f"括号不匹配: '{last_open['type']}' 与 '{char}'",
                            'line': last_open['line'],
                            'position': last_open['position']
                        })

            i += 1

        # 检查栈中剩余的未关闭括号
        for bracket in bracket_stack:
            errors.append({
                'type': 'bracket',
                'message': f"未关闭的开括号 '{bracket['type']}'",
                'line': bracket['line'],
                'position': bracket['position']
            })

        return errors

    # 答辩点 2
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

        # 其他结构的解析
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
            # if/for/while的解析
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

    # 答辩点 3
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

    def visualize_tree(self, filename="code_tree"):
        """可视化代码树"""
        if not self.root:
            raise ValueError("树未构建")

        # 使用graphviz可视化
        dot = graphviz.Digraph(comment='Code Tree', format='png')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='#f0f0f0')

        # 添加节点
        node_queue = deque([(self.root, str(id(self.root)))]) # 使用deque作为广度优先遍历(BFS)的队列
        dot.node(str(id(self.root)), "main")

        while node_queue:
            current_node, current_id = node_queue.popleft() # 获取当前节点及其ID
            for child in current_node.children:
                child_id = str(id(child))
                label = child.name

                # 对于表达式节点，显示整个表达式
                if hasattr(child, 'expr_str'):
                    expr_str = child.expr_str
                    # 截断过长的表达式
                    if len(expr_str) > 30:
                        expr_str = expr_str[:27] + "..."
                    label = f"{child.name}\n{expr_str}"
                elif child.name == "expression" and not child.children:
                    # 空表达式节点
                    label = "expression"

                # 控制结构节点使用不同颜色
                if child.name in ['if', 'else if', 'for', 'while', 'else', 'switch']:
                    dot.node(child_id, label, fillcolor='#d0e0f0')
                elif child.name == 'variable':
                    dot.node(child_id, label, fillcolor='#f0d0d0')
                elif child.name == 'sentence':
                    dot.node(child_id, label, fillcolor='#d0f0d0')
                else:
                    dot.node(child_id, label)

                # 添加边（父子关系）
                dot.edge(current_id, child_id)
                node_queue.append((child, child_id))

        # 保存并渲染
        dot.render(filename, format='png', cleanup=True)
        print(f"代码树可视化已保存为 {filename}.png")
        return dot

    def text_representation(self):
        """生成代码树的文本表示"""
        if not self.root:
            return ""

        output = StringIO() # 内存缓冲区
        """
        RenderTree:anytree库的树遍历工具
        pre: 当前节点的前缀字符串
        fill: 填充字符(用于子节点)
        node: 当前节点对象
        """
        for pre, fill, node in RenderTree(self.root):
            # 添加表达式信息
            if hasattr(node, 'expr_str'):
                expr_str = node.expr_str
                # 截断过长的表达式
                if len(expr_str) > 30:
                    expr_str = expr_str[:27] + "..."
                node_repr = f"{node.name} ({expr_str})"
            else:
                node_repr = node.name
            output.write(f"{pre}{node_repr}\n")

        return output.getvalue()

    # 答辩点 4
    def _get_all_nodes(self, node):
        """获取所有节点（包括根节点和叶子节点）BFS算法"""
        nodes = []
        stack = [node]
        while stack:
            current = stack.pop(0)
            nodes.append(current)
            stack.extend(current.children) # 将当前节点的所有子节点加入队列尾部
        return nodes

    def _is_node_similar(self, node1, node2):
        """检查两个节点是否相似"""
        # 节点名称必须相同
        if node1.name != node2.name:
            return False

        # 对于控制结构和表达式节点需要特殊处理
        if node1.name in ['if', 'else if', 'for', 'while', 'expression', 'condition', 'else']:
            # 比较子节点结构
            if len(node1.children) != len(node2.children):
                return False
            # 比较表达式字符串
            if hasattr(node1, 'expr_str') and hasattr(node2, 'expr_str'):
                # 忽略操作数的具体值
                expr1 = self._simplify_expression(node1.expr_str)
                expr2 = self._simplify_expression(node2.expr_str)
                return expr1 == expr2
            return True

        # 变量声明类型
        if node1.name == "variable":
            # 提取类型信息
            type1 = node1.expr_str.split()[0] if hasattr(node1, 'expr_str') else None
            type2 = node2.expr_str.split()[0] if hasattr(node2, 'expr_str') else None
            return type1 == type2  # 比较变量类型
        # IO语句类型
        if node1.name == "sentence":
            # 比较IO类型(printf/scanf)
            io_type1 = node1.children[0].name if node1.children else None
            io_type2 = node2.children[0].name if node2.children else None
            return io_type1 == io_type2

        # 深度相似性
        depth_diff = abs(node1.depth - node2.depth)
        if depth_diff > 2:  # 深度差异过大视为不相似
            return False

        return True

    def _simplify_expression(self, expr):
        """简化表达式，忽略操作数具体值"""
        # 移除所有空格
        expr = expr.replace(" ", "")
        # 标准化运算符
        expr = expr.replace("!=", "≠").replace("==", "=")
        # 将变量名替换为"var"
        expr = re.sub(r'\bvar\b', 'var', expr)
        # 将数值替换为"#"
        expr = re.sub(r'\b\d+(\.\d+)?\b', '#', expr)
        # 将字符串替换为"str"
        expr = re.sub(r'".*?"', 'str', expr)
        return expr

    # 答辩点 5
    def calculate_similarity(self, other):
        """计算代码重复率 - 使用公式 (2*匹配节点数)/(总节点数)"""
        if not self.root or not other.root:
            return 0.0

        # 获取所有节点
        all_nodes_self = self._get_all_nodes(self.root)
        all_nodes_other = other._get_all_nodes(other.root)

        # 记录已匹配的节点
        matched_self = set()
        matched_other = set()
        matched_count = 0

        # 遍历所有节点对
        for i, node_self in enumerate(all_nodes_self): # i为节点索引 node_self为节点对象
            for j, node_other in enumerate(all_nodes_other):
                if i not in matched_self and j not in matched_other:
                    if self._is_node_similar(node_self, node_other):
                        matched_self.add(i)
                        matched_other.add(j)
                        matched_count += 1
                        break

        # 应用公式: (2 * matched_count) / (total_nodes)
        total_nodes = len(all_nodes_self) + len(all_nodes_other)
        if total_nodes == 0:
            return 0.0

        similarity = (2 * matched_count) / total_nodes
        return min(similarity, 1.0)  # 确保不超过100%

    def _get_all_subtrees(self, node, min_nodes=3):
        """获取节点数至少为min_nodes的子树"""
        subtrees = [] # 存储符合条件的子树根节点
        # 计算以该节点为根的子树节点数
        count = self._count_nodes(node)
        if count >= min_nodes:
            subtrees.append(node)
        for child in node.children:
            subtrees.extend(self._get_all_subtrees(child, min_nodes)) # 深度优先遍历(DFS)
        return subtrees

    # 答辩点 6
    def _count_nodes(self, node):
        """计算子树节点数"""
        # 广度优先遍历(BFS)
        stack = [node]
        count = 0
        while stack:
            current = stack.pop(0)
            count += 1
            stack.extend(current.children)
        return count

    # 答辩点 7
    def _is_subtree_similar(self, node1, node2):
        """检查两个子树是否结构相似（DFS算法）"""
        # 1. 节点名称检查
        if node1.name != node2.name:
            return False
        # 2. 子节点数量检查
        if len(node1.children) != len(node2.children):
            return False
        # 3. 递归检查子节点
        for child1, child2 in zip(node1.children, node2.children):
            if not self._is_subtree_similar(child1, child2):
                return False
        return True

    def find_similar_subtrees(self, other, min_similarity=0.6):
        """查找相似的子树

        参数:
            other (CodeTree): 另一个代码树对象
            min_similarity (float): 最小相似度阈值，默认0.6(60%)

        返回:
            list: 包含相似子树对的列表，每个元素为(st1, st2, score)元组
        """
        # 1. 检查树是否有效
        if not self.root or not other.root:
            return []

        # 2. 获取所有符合条件的子树
        similar_pairs = []
        self_subtrees = self._get_all_subtrees(self.root, min_nodes=3)
        other_subtrees = self._get_all_subtrees(other.root, min_nodes=3)

        # 3. 遍历所有子树对
        for st1 in self_subtrees:
            for st2 in other_subtrees:
                if self._is_subtree_similar(st1, st2):
                    # 计算子树相似度分数
                    score = self._calculate_subtree_similarity(st1, st2)
                    if score >= min_similarity:
                        similar_pairs.append((st1, st2, score))

        # 按相似度分数排序
        similar_pairs.sort(key=lambda x: x[2], reverse=True) # 降序
        return similar_pairs

    def _calculate_subtree_similarity(self, node1, node2):
        """计算两棵子树的相似度分数（0.0~1.0）"""
        # 1. 结构相似性检查
        if not self._is_subtree_similar(node1, node2):
            return 0.0

        # 计算节点匹配比例
        total_nodes = min(self._count_nodes(node1), self._count_nodes(node2))
        matched_nodes = self._count_matched_nodes(node1, node2)
        return matched_nodes / total_nodes if total_nodes > 0 else 0.0

    # 答辩点 8
    def _count_matched_nodes(self, node1, node2):
        """计算两棵树中匹配的节点数量"""
        # 1. 节点名称检查
        if node1.name != node2.name:
            return 0
        # 2. 当前节点匹配计数
        count = 1
        # 3. 递归处理子节点
        for child1, child2 in zip(node1.children, node2.children):
            count += self._count_matched_nodes(child1, child2) # 深度优先遍历(DFS)
        return count

    # 答辩点 9
    def _print_subtree(self, root_node, max_depth=3, max_children=5):
        """使用树状符号(├──, │, └──)打印子树结构，带深度和广度限制

        参数:
            root_node: 子树根节点
            max_depth: 最大显示深度（默认3）
            max_children: 每层最大显示子节点数（默认5）

        返回:
            str: 格式化后的子树结构
        """
        # 处理深度限制
        if max_depth <= 0:
            return "...\n"

        # 使用列表收集输出行
        output_lines = []

        # 使用栈进行深度优先遍历
        stack = [(root_node, 0, [], True)]  # (节点, 当前深度, 父节点的前缀模式, 是否是最后一个子节点)

        while stack:
            node, depth, parent_prefix, is_last = stack.pop()

            # 构建当前节点的前缀
            prefix = ''.join(parent_prefix)

            # 构建连接符号
            if depth == 0:  # 根节点
                connector = ""
            else:
                connector = "└── " if is_last else "├── "

            # 构建节点标签
            label = node.name

            # 添加表达式信息
            if hasattr(node, 'expr_str'):
                expr = node.expr_str
                # 截断长表达式
                if len(expr) > 30:
                    expr = expr[:27] + "..."
                label += f" ({expr})"

            # 添加当前行到输出
            output_lines.append(f"{prefix}{connector}{label}")

            # 处理子节点（深度和广度限制）
            if depth < max_depth and node.children:
                children_to_show = node.children[:max_children]
                children_count = len(children_to_show)
                omitted_count = len(node.children) - children_count

                # 添加省略信息
                if omitted_count > 0:
                    omit_prefix = ''.join(parent_prefix + (["    " if is_last else "│   "]))
                    output_lines.append(f"{omit_prefix}... +{omitted_count} more children")

                # 准备子节点的前缀
                new_prefix = []
                for p in parent_prefix:
                    # 如果父节点是最后一个子节点，使用空格而不是垂直连接线
                    if "    " in p:  # 已经处理过的空格前缀
                        new_prefix.append(p)
                    else:
                        # 替换连接线部分
                        replaced = p.replace("├──", "│   ").replace("└──", "    ")
                        new_prefix.append(replaced)

                # 如果是最后一个子节点，使用空格而不是垂直连接线
                if is_last:
                    new_prefix.append("    ")
                else:
                    new_prefix.append("│   ")

                # 添加子节点到栈（反转顺序以确保正确显示）
                for i, child in enumerate(reversed(children_to_show)):
                    is_last_child = (i == 0)  # 因为是反向添加的，最后一个变为第一个
                    stack.append((child, depth + 1, new_prefix.copy(), is_last_child))

        return "\n".join(output_lines) + "\n"

    def display_tree(self, root_node=None, max_depth=3):
        """显示指定子树"""
        if root_node is None:
            root_node = self.root
        if root_node is None:
            return "树未构建"

        return self._print_subtree(root_node, max_depth)

    # 答辩点 10
    def insert_code_line(self, code_line, line_number):
        """在指定行号插入代码行，保持正确的缩进格式"""
        # 1. 处理源代码为空的情况
        if not self.source_code:
            self.source_code = code_line
            return self.build_tree(self.source_code)

        # 2. 分割源代码为行列表
        lines = self.source_code.splitlines()

        # 3. 处理行号超出范围的情况（插入到末尾）
        if line_number < 1 or line_number > len(lines):
            if lines:  # 代码不为空
                last_line = lines[-1]
                base_indent = len(last_line) - len(last_line.lstrip())
                # 根据最后一行决定缩进
                if code_line.strip() == '}':
                    # 结束括号需要减少缩进
                    indent_level = max(0, base_indent - 4)
                elif last_line.rstrip().endswith('{'):
                    # 在开括号后需要增加缩进
                    indent_level = base_indent + 4
                else:
                    # 保持上一行的缩进
                    indent_level = base_indent
                # 添加带缩进的代码行
                lines.append(" " * indent_level + code_line)
            else:  # 代码为空
                lines.append(code_line)
        else:
            # 4. 处理在指定行号插入
            # 获取上一行（要插入位置的前一行）
            prev_line = lines[line_number - 2] if line_number - 2 >= 0 else ""

            # 计算基础缩进
            base_indent = len(prev_line) - len(prev_line.lstrip()) if prev_line else 0

            # 检查是否在代码块中（上一行以{结尾）
            in_block = False
            if prev_line.rstrip().endswith('{'):
                in_block = True

            # 计算正确的缩进级别
            if code_line.strip() == '}':
                # 处理插入结束括号的情况
                if in_block:
                    indent_level = base_indent  # 在开括号后结束括号应与开括号对齐
                else:
                    # 不在开括号后需要减少缩进
                    indent_level = max(0, base_indent - 4)
            else:
                # 处理普通代码行
                if in_block:
                    indent_level = base_indent + 4  # 在代码块内需要增加缩进
                else:
                    # 检查是否在控制结构后
                    control_keywords = ["if", "else", "for", "while", "switch", "case", "default", "try", "catch", 'else if']
                    control_context = any(
                        prev_line.strip().startswith(kw) and
                        not prev_line.rstrip().endswith(';') and
                        not prev_line.rstrip().endswith('}')
                        for kw in control_keywords
                    )

                    if control_context:
                        # 在控制结构后需要增加缩进
                        indent_level = base_indent + 4
                    else:
                        # 保持上一行的缩进
                        indent_level = base_indent

            # 创建带缩进的代码行
            indented_code = " " * indent_level + code_line
            lines.insert(line_number - 1, indented_code)

        self.source_code = "\n".join(lines)
        return self.build_tree(self.source_code)