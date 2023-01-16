# encoding: utf-8
"""
@author: lin
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: 739217783@qq.com
@software: Pycharm
@file: Ob2Hexo.py
@time: 2023/1/14 23:31
@desc:
传入指定文件名，将对应Ob库下的md文件复制一份到Hexo目录下
修改Front-matter成Hexo需要的格式
TODO:图片路径的优化
TODO:Obsidian的callout的转换问题
"""
import os
import re
import shutil
import sys
import Front_matter_edit as fm


def replace(file, old_content, new_content):
    """
    传入文件(file),将旧内容(old_content)替换为新内容(new_content)
    """
    content = read_file(file)
    content = content.replace(old_content, new_content)
    write_file(file, content)


def read_file(file):
    """
    读文件内容
    """
    with open(file, 'r', encoding='UTF-8') as f:
        read_all = f.read()
        # read_all = f.readlines()
        f.close()

    return read_all


def write_file(file, data):
    """
    写内容到文件
    """
    with open(file, 'w', encoding='UTF-8') as f:
        f.write(data)
        f.close()


def get_photo(file_path):
    """
    将md文件中的所有图片复制到Hexo目录下
    修改图片路径成相对路径
    获取md文档中的所有图片链接
    @param file_path:
    @return:
    """
    content = read_file(file_path)
    pattern = re.compile(r'(?:!\[(.*?)\]\((.*?)\))', re.M)

    result = pattern.findall(content)

    for photo in result:
        photo_name = photo[1].replace('%20', ' ')
        shutil.copyfile(os.path.join(photo_path, photo_name), os.path.join(hexo_photo_path, photo_name))
        content = content.replace(photo[1], f"{os.path.join('../images/',photo[1])}")

    write_file(file_path, content)


def main(file_name):
    """
    @param file_name: 文件名，通过quicke获取标题传入，只有文件名无扩展名
    @return:
    """
    # 复制文件
    for root, dirs, files in os.walk(ob_path):
        for file in files:
            if os.path.splitext(file)[0] == file_name:
                md_file_path = os.path.join(root, file)
                hexo_file_path = os.path.join(hexo_path, file)

                if os.path.exists(hexo_file_path):
                    if input('文件已存在，是否更新文件(yes/no)?') != 'yes':
                        sys.exit(0)
                shutil.copyfile(md_file_path, hexo_file_path)

    # 对拷贝过去的副本规范化（将ob的front-matter转化为Hexo的格式规范）
    # name 转换成 title
    # 删除 date updated属性
    # date created 转换成 date
    fm.file_path = hexo_file_path
    fm.delete_attr("date updated")
    fm.edit_attr("name", "title")
    fm.edit_attr("date created", "data")

    # 复制图片到Hexo目录下
    get_photo(hexo_file_path)


if __name__ == '__main__':
    ob_path = r"C:/0资源库/0_笔记库"  # OB库的位置
    photo_path = r"C:/0资源库/0_笔记库/assets"  # OB库附件存放位置
    hexo_path = r"C:/Hexo/source/_posts"  # Hexo存放文章的位置
    hexo_photo_path = r"C:/Hexo/source/images"  # Hexo存放图片的位置

    file_name = str(sys.argv[1])
    main(file_name)
    # get_photo(r"C:\Hexo\source\_posts\Python_字符串格式化.md")
