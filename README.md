# 简介



使用Python快速将Obsidian库中的Markdown文件同步Hexo中

主要包括2种使用方式

1. 使用脚本
2. 使用脚本+Quicker

推荐第二种工作流，比较快捷





## 功能



已实现的功能

1. 快速同步：快速将文章同步到Hexo中，`Front-matter`自动修改
2. Callout自动转换：将Obsidian的Callout转换成一定的样式，目前仅针对`fluid` 主题
   ![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1676632236375-95a6f5c6-d6ef-4659-b6ba-dad5c7285b74.png)
3. 图片支持：发布到 Hexo 的带有图片的文章，正常显示
   - 支持图片名写法：`![](xxxxxx.jpg)`
   - 支持相对路径写法：`![](../xxxxx.png)`
   - 支持绝对路径写法：`![](D:/Photo/Zh2fx35uqDRVSs5V.png)`
   - 支持wiki写法：`![[]]`
4. 批量同步：支持指定标签一次性批量同步至Hexo
5. 别名选择：支持使用别名进行发布



待实现的功能

- [ ] 双链支持（使文中的引用链接，也可以被访问，待实现）



## 文件结构



```
Obsidian2Hexo
 ├── Front_matter_edit.py
 ├── Ob2Hexo.py
 └── setting.json
```

- `Front_matter_edit.py`：依赖库，主要用于`Front_matter`的编辑操作
- `Ob2Hexo.py`：主要脚本文件，用于同步使用
- `setting.json`：配置文件





# 部署



## 配置信息


![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1681306532476-23c56482-4368-4f19-aa27-484739dfeb1b.png)

编辑文件夹下的`setting.json`，修改对应信息

- `ob_path`：Obsidian 库的位置 
-  `photo_path`：Obsidian 库的放图片位置 
-  `hexo_path`：Hexo 站点的目录位置 
-  `hexo_photo_path`：Hexo 站点的图片位置 
-  `rep_dict`：需要替换的 Front-matter 字段，键为要替换的字段，值为替换后的字段 ，例如上图中`name`转化成`title`、`date created`转换成`date`、`date updated`转换成`updated`

- `del_list`：需要删除的 Front-matter 字段，添加字段名即可，例如上图是删除`date created`字段，多个字段使用`,`间隔，例如：`["date created",""date updated""]`

- `sync_tags`：同步标签，用于批量同步使用
- `syncTags_rep`：移除同步标签，如果不想Hexo的文章中显示同步标签，设置`true`，否则设置`false`
- `aliases_check`：别名检测功能，用于选择别名作为文件标题





## Quicker配置

可选，可以直接使用脚本，也可以配合 Quicker 使用

推荐配合 Quicker 使用，比较快捷



1. 复制粘贴这个[动作](https://getquicker.net/Sharedaction?code=a07971ae-343a-478c-e26f-08daf70dc81e)

2. 修改下脚本的位置，右键编辑下 quicker 粘贴的动作，修改下面的运行脚本
   ![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1681306365489-b717f8b7-9acd-4fc3-9b22-bd49ae7d626f.png)

   将这个路径修改成脚本的所在位置后，保存即可
   例如脚本存放在 C 盘，那么就写成`cd c:`
   ![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1676634454548-858d30fa-64ea-4b85-bf2e-cb603adb8364.png)

# 使用方法



## 单篇同步

配置好[配置信息](##配置信息)，否则无法同步



### 脚本同步

在`Ob2Hexo.py`所在目录下运行以下命令即可

```cmd
python Ob2Hexo.py xxx
```

例如同步文件名为`测试同步.md`的文件

那么使用命令：`python Ob2Hexo.py 测试同步 `即可



### Quicker同步

选中 Obsidian 标题，运行 Quicker 的同步Hexo动作即可

1. 选中标题
   ![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1676635019625-045d91a0-b1c3-4f7f-829f-19d3f99abfd5.png)
2. 运行动作（同步Hexo）
   ![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1676635058875-e983a254-0f6f-4d7b-a2d5-7c0604d2ef25.png)





使用效果图

![](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/%E6%95%88%E6%9E%9C%E6%BC%94%E7%A4%BA.gif)





## 批量同步

先通过[配置信息](##配置信息)的`sync_tags`设置同步标签

例如使用`public`，那么库中所有包含`public`标签的文章会自动同步到Hexo



使用方法：打开`Ob2Hexo.py`，使用`tags_sync`函数即可

```python
if __name__ == '__main__':
    # file_name = sys.argv[1]
    # ob2hexo = Ob2Hexo(file_name)
    # ob2hexo.main()

    # 现有全部更新
    ob2hexo = Ob2Hexo()
    ob2hexo.tags_sync(True)
```



注意事项：

本操作是覆写操作！！！
如果原先有同名的，会将原先的同名直接覆盖掉，不会提示
例如Hexo有篇为Demo.md的文章，Obsidian库中待同步的文章也有Demo.md，那么会用Obsidian的这篇去覆盖掉Hexo原先的，不会有任何提示！！！





## 更新文章

无需任何额外配置，会自动根据Hexo中的文件名从Obsidian中查找，找到将Obsidian中的文件去覆盖掉Hexo现有的，即会从Obsidian拉取最新的现有的Hexo文章，覆盖掉老旧的

打开`Ob2Hexo.py`，使用`update_sync`函数即可

```python
if __name__ == '__main__':
    # file_name = sys.argv[1]
    # ob2hexo = Ob2Hexo(file_name)
    # ob2hexo.main()

    # 对已有文章进行更新
    ob2hexo = Ob2Hexo()
    ob2hexo.update_sync()
```

注意事项：

本操作是覆写操作！！！
同上面批量同步一样，会覆盖操作不会进行提示
将Hexo的文章同名的文章从Obsidian库复制最新的覆盖过去



## 别名检测



通过[配置信息](##配置信息)的`aliases_check`设置别名检测，默认开启

如果`FrontMatter`有别名的话，允许采用别名来同步至Hexo





`FrontMatter`的别名检测支持2种写法



单个写法

```yaml
---
name: 测试同步使用
aliases: 测试同步= =
date created: 2023-02-14 13:12
date updated: 2023-02-17 19:38
---
```

![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1676636631072-f560d192-46af-4cb0-a4a2-49113c768d7b.png)



多个写法

```yaml
---
name: 测试同步使用
aliases: 
 - 测试同步= =
 - 别名2
date created: 2023-02-14 13:12
date updated: 2023-02-17 19:38
---
```

![img](https://obsidian-picgo-lin.oss-cn-shenzhen.aliyuncs.com/img/1676636813498-b49a0eac-28e6-4628-ad98-151674006dab.png)