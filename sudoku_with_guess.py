'''计算机自动解9x9数独游戏，输入题目后进行推断，若无法继续推断，则进行猜测，若猜测错误，则进行回溯，直到成功解出结果'''
'''题目信息保存在9x9的数组中，推断信息以set集合的形式存储于cheet_with_infer数组中'''
'''有两个主要的数据结构，一个是元素全为int的cheet_without_infer，一个是元素为int或set的cheet_with_infer'''

# 需要用到深拷贝
import copy

def print_cheet_without_infer(cheet):
    '''打印没有推断信息的数组'''
    print()
    for line in cheet:
        for num in line:
            print('{:^3}'.format(num), end='')
        print()

def print_cheet_without_infer_to_input_again(cheet):
    '''以与输入相同的格式，打印没有推断信息的数组，便于手动猜测后再次输入'''
    print()
    for line in cheet:
        print(','.join([str(x) for x in line]).replace('-1', ' '))

def print_cheet_with_infer(cheet):
    '''打印包含推断信息的数组'''
    print()
    for line in cheet:
        for infer in line:
            print('{:^15}'.format(str(infer).replace(' ', '')), end='')
        print()

def infer(cheet, cheet_origin):
    '''
    cheet为不包含推断信息的数组，cheet_origin为包含推断信息的数组
    根据基本规则进行推断，每一个数所在行、列以及九宫格不能包含相同的数字
    若数组中的所有元素都已经推断出，则返回2
    若数组中的某个元素在此次函数调用中可以明确推断出，则返回1
    若不能推断出任何未知元素，则返回0
    若有错（某一位置的推断信息为空set集合），说明不满足任何数独的基本规则，返回-1
    '''
    finish = True # 如果数组中的所有元素都已经推断出，则finish为True
    for i in range(9):
        for j in range(9):
            if cheet_origin[i][j] == -1:
                finish = False # 数组中尚有元素未推断出，finish为False
                infer_set = set(range(1, 10)) # 初始化推断信息
                # 通过行和列不能包含相同的数字进行推断
                for k in range(9):
                    if k != j and cheet_origin[i][k] != -1:
                        infer_set.discard(cheet[i][k])
                    if k != i and cheet_origin[k][j] != -1:
                        infer_set.discard(cheet[k][j])
                # 通过九宫格内不能包含相同的数字进行推断
                x = j // 3 * 3
                y = i // 3 * 3
                for m in range(y, y + 3):
                    for n in range(x, x + 3):
                        if (m != i or n != j) and cheet_origin[m][n] != -1:
                            infer_set.discard(cheet[m][n])
                # 判断此位置的推断信息，据此控制程序流程
                if len(infer_set) == 1:
                    cheet[i][j] = infer_set.pop()
                    cheet_origin[i][j] = cheet[i][j]
                    return 1
                elif len(infer_set) == 0:
                    return -1
                else:
                    cheet[i][j] = infer_set
    if finish:
        return 2
    else:
        return 0

def power_set(s):
    '''求一个集合的所有非空真子集（二进制法），为了进行速度优化，需要在返回前对其进行排序'''
    set_list = []
    l = list(s)
    n = len(l)
    # 非空，所以下界为1；真子集，所以上界是2的n次方
    for i in range(1, 2**n - 1):
        combo = set()
        for j in range(n):
            if (i >> j) % 2 == 1:
                combo.add(l[j])
        set_list.append(combo)
    set_list = sorted(set_list, key=lambda x: len(x))
    return set_list

def deep_infer(cheet, cheet_origin):
    '''
    根据推断信息进行推断，去除某些位置的可能性数字
    对于每一行、每一列、每一九宫格内的推断信息，
    先求出这些推断信息的并集，再求出此并集的所有非空真子集，对于每一个非空真子集，
    若推断信息中有 小于等于此真子集大小 数目的超集，并且对于其他推断信息，此真子集与其的交集均为空（不包含此真子集中的元素），
    则这些位置的推断信息可置为此真子集
    如某一行中有四个待推断元素，推断信息为：{1,3,6}, {1,3,6}, {1,4}, {1,4}
    在对其并集的非空真子集的遍历过程中，发现集合{3,6}的超集有{1,3,6}和{1,3,6}，并且其他推断信息{1,4}与此集合{3,6}的交集为空，
    因此，可以将两个推断信息{1,3,6}置为{3,6}
    若不能推断出任何未知元素，则返回2
    若数组中的某个元素在此次函数调用中可以明确推断出，则返回1
    若推断信息在此次函数调用中有修改，则返回0
    '''
    change = False # 推断信息是否有修改的标志

    # 根据每一行已有的推断信息进行推断
    for i in range(9):
        # 求并集
        union_set = set()
        for j in range(9):
            if isinstance(cheet[i][j], set):
                union_set = union_set.union(cheet[i][j])
        # 遍历根据长度排序的所有非空真子集
        for s in power_set(union_set):
            contain_set_list = [] # 保存列号
            finish = True # 若此行中的所有列上的推断信息的长度都小于等于集合s的长度，则可以提前退出，finish为True
            satisfy = True # 若除了集合s的超集以外，此行还含有推断信息与集合s的交集不为空的位置，则不能进行推断，satisfy为False
            for j in range(9):
                if isinstance(cheet[i][j], set):
                    if len(cheet[i][j]) > len(s):
                        finish = False
                    if s.issubset(cheet[i][j]):
                        contain_set_list.append(j)
                    elif len(s.intersection(cheet[i][j])) > 0:
                        satisfy = False
            if finish:
                break
            if not satisfy:
                continue
            if len(contain_set_list) <= len(s) and len(contain_set_list) > 0:
                # 若s长度为1，则表明已经明确推断出此位置的数字，于是将set中的元素提取出来放到此位置上
                if len(s) == 1:
                    j = contain_set_list[0]
                    cheet[i][j] = s.pop()
                    cheet_origin[i][j] = cheet[i][j]
                    return 1
                for j in contain_set_list:
                    if len(cheet[i][j]) > len(s):
                        cheet[i][j] = s.copy()
                        change = True
    # 根据每一列已有的推断信息进行推断，和前面类似
    for j in range(9):
        union_set = set()
        for i in range(9):
            if isinstance(cheet[i][j], set):
                union_set = union_set.union(cheet[i][j])
        for s in power_set(union_set):
            contain_set_list = []
            finish = True
            satisfy = True
            for i in range(9):
                if isinstance(cheet[i][j], set):
                    if len(cheet[i][j]) > len(s):
                        finish = False
                    if s.issubset(cheet[i][j]):
                        contain_set_list.append(i)
                    elif len(s.intersection(cheet[i][j])) > 0:
                        satisfy = False
            if finish:
                break
            if not satisfy:
                continue
            if len(contain_set_list) <= len(s) and len(contain_set_list) > 0:
                if len(s) == 1:
                    i = contain_set_list[0]
                    cheet[i][j] = s.pop()
                    cheet_origin[i][j] = cheet[i][j]
                    return 1
                for i in contain_set_list:
                    if len(cheet[i][j]) > len(s):
                        cheet[i][j] = s.copy()
                        change = True
    # 根据每一九宫格已有的推断信息进行推断，和前面类似
    for m in range(3):
        for n in range(3):
            union_set = set()
            for i in range(m * 3, m * 3 + 3):
                for j in range(n * 3, n * 3 + 3):
                    if isinstance(cheet[i][j], set):
                        union_set = union_set.union(cheet[i][j])
            for s in power_set(union_set):
                contain_set_list = []
                finish = True
                satisfy = True
                for i in range(m * 3, m * 3 + 3):
                    for j in range(n * 3, n * 3 + 3):
                        if isinstance(cheet[i][j], set):
                            if len(cheet[i][j]) > len(s):
                                finish = False
                            if s.issubset(cheet[i][j]):
                                contain_set_list.append((i, j))
                            elif len(s.intersection(cheet[i][j])) > 0:
                                satisfy = False
                if finish:
                    break
                if not satisfy:
                    continue
                if len(contain_set_list) <= len(s) and len(contain_set_list) > 0:
                    if len(s) == 1:
                        i, j = contain_set_list[0]
                        cheet[i][j] = s.pop()
                        cheet_origin[i][j] = cheet[i][j]
                        return 1
                    for i, j in contain_set_list:
                        if len(cheet[i][j]) > len(s):
                            cheet[i][j] = s.copy()
                            change = True

    if not change:
        return 2
    else:
        return 0

def find_min_to_guess(cheet_with_infer):
    '''找到并返回一个推断信息的长度最小的位置'''
    min_length = 10 # 初始化最小长度标记
    for i in range(9):
        for j in range(9):
            if isinstance(cheet_with_infer[i][j], set):
                length = len(cheet_with_infer[i][j])
                if min_length > length:
                    min_length = length
                    m = i
                    n = j
    return m, n

def start(cheet_with_infer, cheet_without_infer):
    '''开始进行推断，若推断成功，则返回True，否则返回False'''
    while True:
        print_cheet_without_infer(cheet_without_infer)
        res = infer(cheet_with_infer, cheet_without_infer)
        if res == 1:
            continue
        elif res == 2:
            return True
        elif res == -1:
            return False
        while True:
            res = deep_infer(cheet_with_infer, cheet_without_infer)
            if res == 1:
                break
            elif res == 2:
                # 无法继续进行推断，于是在推断信息长度最小的位置进行假设，然后继续进行推断（递归），若猜测错误，则进行回溯
                print_cheet_without_infer_to_input_again(cheet_without_infer)
                print_cheet_with_infer(cheet_with_infer)
                print('Can not continue refer! Begin guess!')
                i, j = find_min_to_guess(cheet_with_infer)
                for num in cheet_with_infer[i][j]:
                    new_cheet_with_infer = copy.deepcopy(cheet_with_infer)
                    new_cheet_without_infer = copy.deepcopy(cheet_without_infer)
                    new_cheet_with_infer[i][j] = num
                    new_cheet_without_infer[i][j] = num
                    res = start(new_cheet_with_infer, new_cheet_without_infer)
                    if res:
                        cheet_with_infer.clear()
                        cheet_with_infer.extend(new_cheet_with_infer)
                        cheet_without_infer.clear()
                        cheet_without_infer.extend(new_cheet_without_infer)
                        return True
                    else:
                        print('Guess error, begin next guess!')

# 输入题目信息，以英文逗号进行分隔，若某一位置的信息为空，则以一个空格代替，行末不能有逗号
# 没有推断信息的数组
cheet_without_infer = []
print('Please input:')
for i in range(9):
    line = input()
    line = line.replace(' ', '-1')
    numbers = line.split(',')
    numbers = list(map(lambda x: int(x), numbers))
    cheet_without_infer.append(numbers)

# 有推断信息的数组，推断信息在推断的过程中加入
cheet_with_infer = copy.deepcopy(cheet_without_infer)

# 开始推断
res = start(cheet_with_infer, cheet_without_infer)
if not res:
    print('Error')
