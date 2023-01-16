

# 项目简介



我目前在使用Obsidian作为我的本地Markdown编辑器，使用Hexo作为个人博客

在Obsidian写文章，需要复制文件到Hexo中去，同时还要修改Front-matter，过程比较麻烦

写个脚本，用于将Obsidian中文章快速部署到博客中去





# 快速开始



1. 搭建 Hexo 博客

   > 如果你还没有 Hexo 博客，请按照 [Hexo 官方文档](https://hexo.io/zh-cn/docs/) 进行安装、建站。

2. 安装[Python](https://www.python.org/)，安装脚本

   ```
   
   ```

   

3. 安装Quicker（可选、推荐安装），粘贴动作



# 使用方式

## 配置

需要先设置下位置

编辑`Ob2Hexo.py`脚本，将下面变量修改成个人使用的对应位置即可

- `ob_path`：Obsidian库的位置
- `photo_path`：Obsidian库存储图片的位置
- `hexo_path`：Hexo存放文章的位置
- `hexo_photo_path`：Hexo存放图片的位置



有安装Quicker的话，编辑下quicker粘贴的动作，修改下面的运行脚本

![image-20230116183325452](assets/image-20230116183325452.png)

将这一行修改成脚本存放的位置

例如脚本存放在C盘，那么就写成`CD C：`即可

![image-20230116183414508](assets/image-20230116183414508.png)

## 脚本同步

如果没有安装Quicker的话，那么直接在对应的

有安装Quicker