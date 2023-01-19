# encoding: utf-8
"""
@author: lin
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: 739217783@qq.com
@software: Pycharm
@file: tes.py
@time: 2022/6/9 19:47
@desc:
- 检索文件是否有Front-matter
- 检索Front-matter中标题名是否与文件名相同
- 修改任意属性和值
TODO:字段（标签）是否有#，有的去除
TODO:使用正则检测时间格式是否符合特定格式

"""
import os
import re
from functools import wraps


def rw_file(func):
    @wraps(func)
    def wrapper(*args, **kw):
        with open(file_path, 'r', encoding='utf-8') as r:
            # 使用正则，通过全文(字符串，r.read)，识别Front-matter 和 正文区域
            _regex = re.compile(r'([-]{3})(.*?)([-]{3})', re.S | re.M)
            result = _regex.search(r.read())
            r.seek(0)

            try:
                # 划分内容
                content = r.readlines()  # 获取全文(list)，用于划分
                yaml_row = len(result.group().split('\n'))  # YAML区域的行数
                yaml_content = content[0:yaml_row]  # Front-matter
                body = content[yaml_row:]  # 正文

                if func.__name__ == 'get_info':
                    # 如果是读取信息，直接返回信息
                    return func(yaml_content, body, *args, **kw)

            except AttributeError:
                print(f'{os.path.split(kw["path"])[1]},没有Front-matter')
                return None

            # 执行需要的操作
            w_content = func(yaml_content, body, *args, **kw)

        with open(file_path, 'w', encoding='utf-8') as w:
            w.write(w_content)

    return wrapper


@rw_file
def get_info(yaml_content: list, body: list):
    """
    获取信息
    @return:
    """
    return dict(yaml=yaml_content, body=body)


@rw_file
def edit_attr(yaml_content: list, body: list, attr_before: str = None, attr_after: str = None, replace_dict: dict = None) -> str:
    """修改属性名称
    @param yaml_content:Front-matter内容
    @param body:正文内容
    @param attr_before:需要修改的属性名称
    @param attr_after:修改后的属性名称
    允许单个替换或者多个替换(如果同时提供单个替换和多个替换，多个替换优先级高于单个替换)
    单个替换,提供attr_before和attr_after参数
    多个替换,仅提供replace_dict参数即可(键为要替换的属性名称，值为新属性名称)
    """

    for index, value in enumerate(yaml_content):
        if replace_dict:
            # 有值，采用多个替换(根据提供的字典)
            for item in replace_dict.items():
                if value.find(item[0]) > -1 and value.find(':') > -1:
                    s_attr, s_value = value.split(':', 1)  # 获取属性名称和值
                    s_attr = s_attr.replace(item[0], item[1])
                    yaml_content[index] = s_attr + ':' + s_value
        else:
            # 采用单个替换
            if value.find(attr_before) > -1 and value.find(':') > -1:
                s_attr, s_value = value.split(':', 1)  # 获取属性名称和值
                s_attr = s_attr.replace(attr_before, attr_after)
                yaml_content[index] = s_attr + ':' + s_value

    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


@rw_file
def edit_value(yaml_content: list, body: list, attr: str, before_value: str = None, after_value: str = None):
    """修改属性值
    值如果是单个,仅用提供更改后的值
    值如果是多个,需要准确提供修改前和修改后的值
    Args:
        yaml_content (list): Front-matter内容
        body (list): 正文内容
        attr (str): 值属于哪个属性下
        before_value (str): 更改前的值
        after_value (str): 更改后的值
    """
    r_value = re.compile(r'[a-z\s]+[:]')

    for index, value in enumerate(yaml_content):
        if r_value.search(value) and value.find(attr) > -1:
            yaml_attr, yaml_value = value.split(':', 1)
            # 判断值是否数组类型
            if yaml_value != '\n':
                yaml_content[index] = yaml_attr + ': ' + after_value + '\n'
            else:
                yaml_dict = yaml_list2dict()
                if not before_value and not after_value:
                    raise Exception('请提供准确参数')

                # 计算位置、整体位置位于：当前行+要更新的属性值在数组中的位置
                up_value_index = index + yaml_dict[attr].index(before_value) + 1
                yaml_content[up_value_index] = yaml_content[up_value_index].replace(before_value, after_value)
            break
    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


@rw_file
def delete_attr(yaml_content: list, body: list, attr: str):
    """删除指定属性
    @param yaml_content:Front-matter内容
    @param body:正文内容
    @param attr: 需要删除（移除）的属性
    @return:
    """
    r_value = re.compile(r'[a-z\s]+[:]')
    n_yaml_list = []

    for index, value in enumerate(yaml_content):
        if r_value.search(value) and value.find(attr) > -1:
            yaml_attr, yaml_value = value.split(':')
            # 判断值是否数组类型
            if yaml_value != '\n':
                yaml_content.remove(value)
            else:
                # 数组类型,切片重新组合
                yaml_dict = yaml_list2dict()
                start = index + 1 + len(yaml_dict[yaml_attr])
                n_yaml_list.extend(yaml_content[:index])
                n_yaml_list.extend(yaml_content[start:])
            break
    n_yaml_list.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(n_yaml_list)  # 列表转回文本


@rw_file
def delete_value(yaml_content: list, body: list, del_dict: list):
    """删除指定属性值(仅适用于多个值，单个值直接使用delete_attr删除指定属性)
    注:采取计算行数方式,如果采用全局遍历的话，可能会误删其他的
    @param yaml_content:Front-matter内容
    @param body:正文内容
    @param del_dict: 需要删除值，[哪个属性下:值名称] [attr:value]
    @return:
    """
    r_value = re.compile(r'[a-z\s]+[:]')
    n_yaml_list = []

    for index, value in enumerate(yaml_content):
        if r_value.search(value) and value.find(del_dict[0]) > -1:
            yaml_attr, yaml_value = value.split(':', 1)
            # 判断值是否数组类型
            if yaml_value != '\n':
                yaml_content.remove(value)
                n_yaml_list.extend(yaml_content)
            else:
                # 数组类型,采用切片重新组合
                yaml_dict = yaml_list2dict()
                start = index + yaml_dict[yaml_attr].index(del_dict[1]) + 1
                n_yaml_list.extend(yaml_content[:start])
                n_yaml_list.extend(yaml_content[start + 1:])
            break

    n_yaml_list.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(n_yaml_list)  # 列表转回文本


@rw_file
def replce_shuangyin(yaml_content, body):
    """移除YAML区域所有双引号"""
    for index, value in enumerate(yaml_content):
        yaml_content[index] = value.replace('"', "")

    yaml_content.extend(body)  # 重新组合成全文(yaml_content+body)
    return ''.join(yaml_content)  # 列表转回文本


def yaml_list2dict() -> dict:
    """将yaml列表转换为字典"""

    r_value = re.compile(r'[a-z\s]+[:]')
    yaml_content = get_info()['yaml']
    yaml_dict = {}
    yaml_key = None
    yaml_value = None
    switch = False

    for index, value in enumerate(yaml_content):

        if switch and value.find('---') == -1 and not r_value.search(value):
            yaml_dict[yaml_key].append(value.replace('-', '').strip())
        else:
            if r_value.search(value):
                yaml_key, yaml_value = value.split(':', 1)
                # 值不等于换行，直接写入字典
                if yaml_value != '\n':
                    yaml_dict[yaml_key] = yaml_value.strip()
                else:
                    yaml_dict[yaml_key] = []
                    switch = True
                    continue

            switch = False
    return yaml_dict


def get_tags() -> list:
    """返回Front-matter的所有标签"""
    yaml = get_info()['yaml']
    taglist = []
    tag_min = 0
    tag_max = 0
    symbol = re.compile(r'([a-z\s]+[:])')
    max_yaml = re.compile(r'\-{3}')

    # 查找标签区域
    for index, attr in enumerate(yaml):
        if attr.find("tags:") > -1:
            tag_min += index + 1
            continue

        if tag_min:
            if symbol.search(attr) or max_yaml.search(attr):
                tag_max = index
                break

    taglist = [i.replace('\n', '').replace('- ', '').strip() for i in yaml[tag_min:tag_max]]
    return taglist


def sx(x):
    """
    判断指定路径在不在要跳过的列表中，在的话返回True，不在的话False
    @param x:
    @return:
    """
    ignore = [
        r'C:\0资源库\0_笔记库\.obsidian', r"C:\0资源库\0_笔记库\.stfolder", r"C:\0资源库\0_笔记库\.trash", r"C:\0资源库\0_笔记库\assets",
        r"C:\0资源库\0_笔记库\config", r"C:\0资源库\0_笔记库\config\Templates"
    ]  # 要忽略，跳过的文件（例如工作区文件就肯定是没有Front-matter的）

    for i in ignore:
        if x.find(i) > -1:
            return True
    return False


if __name__ == '__main__':
    # for root, dirs, file in os.walk(r"C:\0系统库\桌面\新建文件夹 (3)"):
    #     if sx(root):
    #         continue
    #     for i in file:
    #         if i.endswith('.md'):
    #             file_path = root + '/' + i
    #             edit_attr()

    # print(get_tags())
    file_path = r"C:\0系统库\桌面\Python_链接字符串.md"
