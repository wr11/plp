# 编写代码注意
## 命名规范
### 局部变量与常量
小写类型字母+驼峰名称 如：iFlag 

小写类型字母:
i ---- int
s ---- str
t ---- tuple
lst ---- list
d ---- dict
o ---- object

### 全局变量
"g_"开头 + 驼峰名称 如：g_Flag
注意全局变量声明时需要按照如下格式写:
if "g_xxx" not in globals():
    g_xxx = ...
用于防止热更时重置该变量

### 全局常量
全部大写即可 如：FLAG

### 类
类名 大写C 开头+ 驼峰命名 如：CClass
类/实例 变量/常量 m_ + 驼峰命名 如：m_Flag

## 定时器规范
定时器flag需要全局唯一，不可重复

## 热更规范
热更分为手动热更和自动热更
自动热更为服务器定时读取项目中所有文件进行热更新，在正式环境下不开启，debug环境下可以在conf中选择是否开启
手动热更为服务器定时读取hotfix/reloadbox文件中的FILE_LIST，对其中模块进行热更，自动热更不开启则自动开启手动热更

热更相关代码 hotfix 文件夹下，相关配置可以在conf.py下找到
具体热更方式可以在hotfix下的文件中查看

## import规范
import时统一从根目录开始（因为需要统一模块在sys.modules中的名字）
如：import hotfix.myreload

## 打印规范
开发中不要直接使用print打印，所有封装好的打印接口在mylog下的logcmd中
包括 PrintNotify, PrintDebug, PrintError, PrintWarning, PrintStack
以上所有接口均在启服时加入python内置方法，所以使用时无需import，直接使用即可

需要注意PrintDebug/PrintStack为debug环境下才会实际输出

每个接口打印出颜色不同：
PrintNotify     白色
PrintDebug      梅色
PrintError      红色
PrintWarning    蓝色
PrintStack      绿色
（此颜色跨平台，均生效）

打印内容及含义：
[time][进程类型_进程索引号:线程类型][文件名:行号][Print类型] xxxxxxxxxxx
ps: 线程类型:每个进程都有网络线程和脚本线程(NET和SCR)
