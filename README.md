## Genetic-Algorithm-System-with-UI-
### This  is a system that you can add more algorithms into it. And now, it has GA and a farely beautiful interface 
# 遗传算法以及界面设计
上述文件中有两个`python`源程序文件，其中`get_dubins.py`是用来计算`dubins`路径长度的，相关的定义请自行查阅文献。主程序是`genetic_algorithm.py`，这是用来整个系统的框架，里面包含了界面的定义信息以及遗传算法的实现过程。我要说明的一点是，这个系统的背景是`SEAD`多目标任务协同规划，属于无人机领域的一个研究方向，参考的论文我也一并上传到仓库了，感兴趣的读者可以查阅。<br>
### 当你仔细阅读代码时你会发现代码是非常容易读懂的，因为我使用了许多相同的结构。
# 其他文件
两个`.jpg`图片当然是在界面中用到的显示图片，其中一个是我的头像，还有一个就是基因结构，因为这是遗传算法，所以我就随便找了一个。你可以随意的切换这些图片，但是不要忘记修改图片的引用名称。<br>
`.ico`文件是窗口右上角的图标，就像是你打开`IE`浏览器时，窗口左上角的`e`一样，当然这也是可以随便切换的，但是，你需要将自己的图片转换为`.ico`的格式，这并不难，网络上有许多免费的在线转换的工具，比如说这个网站：http://static.krpano.tech/image2ico 转换完成后，不要忘记修改图片的引用名。<br>
# 使用方法
首先我们来看一下系统的界面：<br>
&emsp;<img src= ga.png width=1365 height=500/><br>
界面中的基因图片还有右上角的头像就是两个`.jpg`文件啦，左上角的蓝色标志就是我们说的`.ico`文件。因为是课程项目，所以我用了我们学校的校徽，嘻嘻，感觉有点暴露身份。<br>
然后就是详细的使用方法了：<br>
1.使用起来真的超级简单，输入数据后，随时都可以确认，前四项无需清除，如果要修改的话，直接重新输入并确认即可。<br>
2.后面两项的输入请按照格式，在上传的`.txt`文件中，有详细的示例，这里就不多说了。清除的话可以清除上一条数据。<br>
3.为了方便，我设置了全局清除键，会将所有的数据清除。<br>
4.你没进行一项操作，在系统框的最上面都会有红色的提示信息，可以进行核对，检查系统接收到的消息和自己想要输入的消息是否吻合。如果不吻合，请删除上一条数据，并重新输入。<br>
5.最下边是一个程序更新框，这里将显示实时的运行状况以及历史最优解。从这里，我们可以清楚的看到`GA`的运行过程。<br>
## 最后，由于时间比较紧张，左侧的功能选项框还没有完全设计好，希望学弟学妹们继续努力啦，哈哈，老学长就把这乱七八糟的剩余工作交给你们了！！！
