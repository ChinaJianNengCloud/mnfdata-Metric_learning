# 项目概述
该项目是分类任务，由于数据集的性质，采用度量学习的方式来进行训练分类。
原项目路径:https://kevinmusgrave.github.io/pytorch-metric-learning/inference_models/
参考项目路径:https://github.com/xxcheng0708/pytorch-metric-learning-template/tree/main/utils

# 数据介绍
数据格式是xlsx，有4个表，分别是训练集，留出集，西溪验证集，浙一验证集
每个表的列数相同，其中第一列为类别(因变量)，其余类为自变量
其中训练集有318条数据，留出集有45条数据，西溪验证集有49条数据，浙一验证集有52条数据

# 环境
将site-packer存储到了s盘
注意env.txt，可以提供一些环境安装的帮助，一般来说只需要使用放在百度网盘的env即可

# 实验介绍
目前要进行四类实验，分别是
第一类实验：特征提取层(trunk选择哪个比较好，MLP还是一维卷积)
第二类实验：模型深度(采用了多核卷积)
第三类实验：损失函数比例
第四类实验：超参数优化

## 第一类实验

实验4MLP(a):trunk采用MLP，用新数据集重现实验3

实验4oneconv(b):trunk采用一维卷积，用新数据集重现实验3

实验6(c):trunk采用不同的卷积核大小

## 第二类实验
实验6(c):trunk采用不同的卷积核大小

实验8(d):在实验6的基础上，减少模型参数

实验9(e):在实验8的基础上，增加模型参数

## 第三类实验
实验9(e):在实验8的基础上，增加模型参数


重要实验1.1(g):在实验9的基础上,设置交叉熵损失权重为0

重要实验2(h):在实验9的基础上,设置三元组损失权重为0,并且取消mine机制

实验11(f):在实验9的基础上，取消CEloss的类别权重


## 第四类实验

实验14(i):在实验11基础上，修改margin和esplion

实验15（j）:loss变成Circleloss-nominer

实验16（k）:loss变成FastAPloss

实验17（l）:loss变成IntraPairVarianceloss-nominer

实验18（m）:loss变成Multisimilarity-nominer

实验19（n）:loss变成NCAloss

实验20（o）:loss变成SignalToNoiseRatioContrastiveloss

实验21（p）:loss变成Supconloss

## 实验总体说明
这些实验的指标有acc，auc，并以0.5acc+0.5auc为运行指标
实验记录表在:实验记录8.26.21.00.xlsx
使用的数据:对数归一化后的数据（十七支队）.xlsx
在进行第四类实验的时候，i组实验的margin和esplion是经过遍历调参的，且第四类的这些loss先是用默认的参数运行，经过筛选得到了7个，在得到了7个之后在进行遍历调优，得到了调优之后的7组结果。