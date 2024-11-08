# -*- coding: utf-8 -*-
"""TrainWithClassifier.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/github/KevinMusgrave/pytorch-metric-learning/blob/master/examples/notebooks/TrainWithClassifier.ipynb

# PyTorch Metric Learning
### Example for the TrainWithClassifier trainer
See the documentation [here](https://kevinmusgrave.github.io/pytorch-metric-learning/)

## Install the necessary packages
"""

"""## Import the packages"""
import logging
from scipy.special import softmax
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torchvision
import umap
from cycler import cycler
from PIL import Image
from torchvision import datasets, transforms


import pytorch_metric_learning
import pytorch_metric_learning.utils.logging_presets as logging_presets
from pytorch_metric_learning import losses, miners, samplers, testers, trainers
from pytorch_metric_learning.utils.accuracy_calculator import AccuracyCalculator, precision_at_k
import pandas as pd
from sklearn.metrics import roc_auc_score,accuracy_score


from sklearn.metrics import accuracy_score, roc_auc_score
import torch
import numpy as np
from pytorch_metric_learning.utils import accuracy_calculator
from sklearn.preprocessing import MinMaxScaler
class Yinda_calculator(accuracy_calculator.AccuracyCalculator):
    def calculate_acc_yinda(self, knn_labels, query_labels, **kwargs):
        # 将 query_labels 转换为一维数组
        data=kwargs['classifier_and_labels']
        data_logit = data[0].cpu().numpy()
        labels = data[1].cpu().numpy()
        argmax_indices = np.argmax(data_logit, axis=1)
        # 计算准确率
        return accuracy_score(labels,argmax_indices )
    
    def calculate_mean_acc_auc_yinda(self, knn_labels, query_labels, **kwargs):
        # 将 query_labels 转换为一维数组
        data=kwargs['classifier_and_labels']
        data_logit = data[0].cpu().numpy()
        labels = data[1].cpu().numpy()
        argmax_indices = np.argmax(data_logit, axis=1)
        acc=accuracy_score(labels,argmax_indices )

        probabilities = softmax(data_logit, axis=1)
        # 获取正类的概率
        positive_class_probabilities = probabilities[:, 1]
        # 使用 sklearn 计算 AUC
        
        auc = roc_auc_score(labels, positive_class_probabilities)
        return 0.5*acc+0.5*auc
    
    def requires_knn(self):
        return super().requires_knn() + ["acc_yinda", "auc_yinda","mean_acc_auc_yinda"]

    def calculate_auc_yinda(self, knn_labels, query_labels, **kwargs):
        data = kwargs['classifier_and_labels']
        labels = data[1].cpu().numpy()  # 真实标签
        data_logit = data[0].cpu().numpy()  # 预测分数
        # 然后使用归一化后的值计算置信度分数
        probabilities = softmax(data_logit, axis=1)
        # 获取正类的概率
        positive_class_probabilities = probabilities[:, 1]
        # 使用 sklearn 计算 AUC
        auc = roc_auc_score(labels, positive_class_probabilities)
        return auc

    def requires_clustering(self):
        return super().requires_clustering()


class MLP(nn.Module):
    # layer_sizes[0] is the dimension of the input
    # layer_sizes[-1] is the dimension of the output
    def __init__(self, layer_sizes, final_relu=False):
        super().__init__()
        layer_list = []
        layer_sizes = [int(x) for x in layer_sizes]
        num_layers = len(layer_sizes) - 1
        final_relu_layer = num_layers if final_relu else num_layers - 1
        for i in range(len(layer_sizes) - 1):
            input_size = layer_sizes[i]
            curr_size = layer_sizes[i + 1]
            if i < final_relu_layer:
                layer_list.append(nn.ReLU(inplace=False))
            layer_list.append(nn.Linear(input_size, curr_size))
        self.net = nn.Sequential(*layer_list)
        self.last_linear = self.net[-1]

    def forward(self, x):
        return self.net(x)

class Conv1DModel(nn.Module):
    def __init__(self):
        super(Conv1DModel, self).__init__()
        # 定义一维卷积层
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(in_channels=32, out_channels=1, kernel_size=3, padding=1)
        # 定义激活函数
        self.relu = nn.ReLU()

    def forward(self, x):
        # 将输入形状调整为 (batch_size, channels, length)
        x = x.unsqueeze(1)
        # 通过卷积层和激活函数
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.conv3(x)
        # 去掉通道维度
        x = x.squeeze(1)
        return x


class DeepConv1DModel(nn.Module):
    def __init__(self):
        super(DeepConv1DModel, self).__init__()
        # 定义一维卷积层
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.conv4 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.conv5 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.conv6 = nn.Conv1d(in_channels=256, out_channels=128, kernel_size=3, padding=1)
        self.conv7 = nn.Conv1d(in_channels=128, out_channels=64, kernel_size=3, padding=1)
        self.conv8 = nn.Conv1d(in_channels=64, out_channels=32, kernel_size=3, padding=1)
        self.conv9 = nn.Conv1d(in_channels=32, out_channels=16, kernel_size=3, padding=1)
        self.conv10 = nn.Conv1d(in_channels=16, out_channels=1, kernel_size=3, padding=1)

        # 定义激活函数
        self.relu = nn.ReLU()

    def forward(self, x):
        # 将输入形状调整为 (batch_size, channels, length)
        x = x.unsqueeze(1)  # 添加一个通道维度

        # 通过卷积层和激活函数
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        x = self.relu(self.conv4(x))
        x = self.relu(self.conv5(x))
        x = self.relu(self.conv6(x))
        x = self.relu(self.conv7(x))
        x = self.relu(self.conv8(x))
        x = self.relu(self.conv9(x))
        x = self.conv10(x)

        # 去掉通道维度
        x = x.squeeze(1)
        return x

class MultiBranchConv1DModel(nn.Module):
    def __init__(self):
        super(MultiBranchConv1DModel, self).__init__()

        # 并行卷积模块
        self.branch1 = nn.Conv1d(in_channels=1, out_channels=4, kernel_size=3, padding=1)
        self.branch2 = nn.Conv1d(in_channels=1, out_channels=4, kernel_size=5, padding=2)
        self.branch3 = nn.Conv1d(in_channels=1, out_channels=4, kernel_size=7, padding=3)

        # 合并后的卷积和全连接层
        self.conv_merge = nn.Conv1d(in_channels=12, out_channels=16, kernel_size=3, padding=1)
        self.conv_end1 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.conv_end2 = nn.Conv1d(in_channels=32, out_channels=16, kernel_size=3, padding=1)
        self.conv_end3 = nn.Conv1d(in_channels=16, out_channels=8, kernel_size=3, padding=1)
        self.conv_end4 = nn.Conv1d(in_channels=8, out_channels=4, kernel_size=3, padding=1)
        self.fc = nn.Linear(4 * 32, 32)
        # 激活函数
        self.relu = nn.ReLU()

    def forward(self, x):
        # 输入形状调整为 (batch_size, channels, length)
        x = x.unsqueeze(1)  # (batch_size, 1, 32)

        # 并行卷积模块
        x1 = self.relu(self.branch1(x))
        x2 = self.relu(self.branch2(x))
        x3 = self.relu(self.branch3(x))

        # 拼接输出
        x = torch.cat((x1, x2, x3), dim=1)

        # 通过合并后的卷积层
        x = self.relu(self.conv_merge(x))
        x4 = self.relu(self.conv_end1(x))
        x5 = self.relu(self.conv_end2(x4))
        x6 = self.relu(self.conv_end3(x5))
        x7 = self.relu(self.conv_end4(x6))

        x = x7.view(x7.size(0), -1)

        x = self.fc(x)
        return x

class mnfDataset(torch.utils.data.Dataset):
    def __init__(self, file_path, sheet_name, transform=None, device=None):
        # 读取Excel文件
        self.tmp = pd.read_excel(file_path, sheet_name=sheet_name)

        # 将数据转换为NumPy数组，并限制小数位数
        self.data = np.round(self.tmp.iloc[:, 1:33].to_numpy(dtype=np.float32), decimals=16)
        self.targets = self.tmp.iloc[:, 0].to_numpy(dtype=np.float32)
        self.transform = transform
        self.device = device if device else torch.device('cpu')

        # 统一数值表示
        self.data = self._convert_to_decimal(self.data)

        # 标准化数据形状
        self.data = self._standardize_data(self.data)

    def _convert_to_decimal(self, data):
        # 将所有数值转换为统一的小数表示
        return np.array([[float(f"{value:.16f}") for value in row] for row in data], dtype=np.float32)

    def _standardize_data(self, data):
        max_length = max(len(row) for row in data)
        standardized_data = np.zeros((len(data), max_length), dtype=np.float32)
        for i, row in enumerate(data):
            standardized_data[i, :len(row)] = row
        return standardized_data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        data = self.data[index]
        target = self.targets[index]

        if self.transform is not None:
            data = self.transform(data)
        return data, target


class CombinedDataset(torch.utils.data.Dataset):
    def __init__(self, datasets):
        self.data = []
        self.targets = []

        # 合并所有数据集
        for dataset in datasets:
            self.data.append(dataset.data)
            self.targets.append(dataset.targets)

        # 将列表转换为 NumPy 数组
        self.data = np.concatenate(self.data, axis=0)
        self.targets = np.concatenate(self.targets, axis=0)

    def __len__(self):
        return len(self.targets)

    def __getitem__(self, idx):
        sample = self.data[idx]
        target = self.targets[idx]
        return sample, target

def visualizer_hook(umapper, umap_embeddings, labels, split_name, keyname, marker_size=64, *args):
    logging.info(
        "UMAP plot for the {} split and label set {}".format(split_name, keyname)
    )
    label_set = np.unique(labels)
    num_classes = len(label_set)
    plt.figure(figsize=(20, 15))
    plt.gca().set_prop_cycle(
        cycler(
            "color", [plt.cm.nipy_spectral(i) for i in np.linspace(0, 0.9, num_classes)]
        )
    )
    for i in range(num_classes):
        idx = labels == label_set[i]
        plt.plot(umap_embeddings[idx, 0], umap_embeddings[idx, 1], ".", markersize=marker_size)
    plt.show()

if __name__ == '__main__':
    from multiprocessing import freeze_support
    import random
    embedding_outputs = [16, 32, 64, 128]
    pos_epss= [0,0.01,0.1]
    neg_epss=[1,2,3,4]
    epsilonss=[0.05, 0.1, 0.2, 0.25, 0.3, 0.4]
    for i in range(30):
        embedding_output = random.choice(embedding_outputs)
        pos_eps = random.choice(pos_epss)
        neg_eps = random.choice(neg_epss)
        epsilons = random.choice(epsilonss)
        exp_name = f"shiyan11-SignalToNoiseRatioContrastiveloss-embeding_output{embedding_output}-pos_eps{pos_eps}-neg_eps{neg_eps}-epsilons{epsilons}-{i}"
        # exp_name = "test"
        log_dir = fr"/root/autodl-tmp/result/Lossresult/youhua/SignalToNoiseRatioContrastiveloss/{exp_name}/log"
        tensorboard_dir = fr"/root/autodl-tmp/result/Lossresult/youhua/SignalToNoiseRatioContrastiveloss/{exp_name}/tensorboard"
        model_save_dir = fr"/root/autodl-tmp/result/Lossresult/youhua/SignalToNoiseRatioContrastiveloss/{exp_name}/model"

        freeze_support()
        # Set other training parameters
        batch_size = 32
        num_epochs = 400
        """## Simple model def"""
        logging.getLogger().setLevel(logging.INFO)
        logging.info("VERSION %s" % pytorch_metric_learning.__version__)

        """## Initialize models, optimizers and image transforms"""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Set trunk model and replace the softmax layer with an identity function
        trunk_output_size = 32  # 根据你的输入维度来设定
        trunk = torch.nn.DataParallel(MultiBranchConv1DModel()).to(device)
        embedder = torch.nn.DataParallel(MLP([trunk_output_size, embedding_output]).to(device))
        classifier = torch.nn.DataParallel(MLP([embedding_output, 2])).to(device)
        # Set optimizers
        trunk_optimizer = torch.optim.Adam(trunk.parameters(), lr=0.0001, weight_decay=0.0001)
        embedder_optimizer = torch.optim.Adam(
            embedder.parameters(), lr=0.0001, weight_decay=0.0001
        )
        classifier_optimizer = torch.optim.Adam(
            classifier.parameters(), lr=0.0001, weight_decay=0.0001
        )
        trunk_scheduler = torch.optim.lr_scheduler.ExponentialLR(trunk_optimizer, gamma=0.995)
        # embedder_scheduler = torch.optim.lr_scheduler.ExponentialLR(embedder_optimizer, gamma=0.995)
        # classifier_scheduler = torch.optim.lr_scheduler.ExponentialLR(classifier_optimizer, gamma=0.995)
        lr_dict = {
            "trunk_scheduler_by_epoch": trunk_scheduler,
            # "embedder_scheduler_by_epoch": embedder_scheduler,
            # "classifier_scheduler_by_epoch": classifier_scheduler
        }
        """## Create the dataset and class-disjoint train/val splits"""

        train_dataset = mnfDataset(file_path='/root/autodl-tmp/对数归一化后的数据（十七支队）.xlsx', sheet_name='训练集',
                                   transform=None, device=device)
        val_dataset = mnfDataset(file_path='/root/autodl-tmp/对数归一化后的数据（十七支队）.xlsx', sheet_name='西溪验证集',
                                 transform=None, device=device)
        hold_out_dataset = mnfDataset(file_path='/root/autodl-tmp/对数归一化后的数据（十七支队）.xlsx', sheet_name='留出集',
                                      transform=None,
                                      device=device)
        zheyi_dataset = mnfDataset(file_path='/root/autodl-tmp/对数归一化后的数据（十七支队）.xlsx', sheet_name='浙一验证集',
                                   transform=None,
                                   device=device)
        total_dataset = CombinedDataset([train_dataset, val_dataset, hold_out_dataset, zheyi_dataset])
        total_dataset_withouttrain = CombinedDataset([val_dataset, hold_out_dataset, zheyi_dataset])
        """##Create the loss, miner, sampler, and package them into dictionaries
        """
        # Set the loss function

        # loss = losses.TripletMarginLoss(margin=0.1)
        loss = losses.SignalToNoiseRatioContrastiveLoss(pos_margin=pos_eps, neg_margin=neg_eps)

        classification_loss = torch.nn.CrossEntropyLoss()
        miner = miners.MultiSimilarityMiner(epsilon=epsilons)
        # Set the dataloader sampler
        sampler = samplers.MPerClassSampler(
            train_dataset.targets, m=4, length_before_new_iter=len(train_dataset)
        )

        # Package the above stuff into dictionaries.
        models = {"trunk": trunk, "embedder": embedder, "classifier": classifier}
        optimizers = {
            "trunk_optimizer": trunk_optimizer,
            "embedder_optimizer": embedder_optimizer,
            "classifier_optimizer": classifier_optimizer

        }
        loss_funcs = {"metric_loss": loss, "classifier_loss": classification_loss}
        mining_funcs = {"tuple_miner": miner}

        # We can specify loss weights if we want to. This is optional
        loss_weights = {"metric_loss": 0.5, "classifier_loss": 1.5}

        """## Create the training and testing hooks"""

        record_keeper, _, _ = logging_presets.get_record_keeper(
            log_dir, tensorboard_dir
        )
        hooks = logging_presets.get_hook_container(record_keeper, record_group_name_prefix="best_acc_auc_yinda",
                                                   primary_metric="mean_acc_auc_yinda")
        dataset_dict = {"val": val_dataset, "train": train_dataset, "hold_out": hold_out_dataset, "zheyi": zheyi_dataset,
                        "total": total_dataset, "total_without_train": total_dataset_withouttrain}
        model_folder = model_save_dir
        metric_yinda = Yinda_calculator(
            include=(
                "precision_at_1",
                "r_precision",
                "mean_average_precision_at_r",
                "acc_yinda",
                "auc_yinda",
                "mean_acc_auc_yinda",
            )
        )

        # Create the tester
        tester = testers.GlobalEmbeddingSpaceTester(
            batch_size=batch_size,
            end_of_testing_hook=hooks.end_of_testing_hook,
            visualizer=None,
            visualizer_hook=None,
            dataloader_num_workers=1,
            accuracy_calculator=metric_yinda,
        )

        end_of_epoch_hook = hooks.end_of_epoch_hook(
            tester, dataset_dict, model_folder, test_interval=1, patience=500
        )

        """## Create the trainer"""

        trainer = trainers.TrainWithClassifier(
            models,
            optimizers,
            batch_size,
            loss_funcs,
            train_dataset,
            mining_funcs=mining_funcs,
            sampler=sampler,
            dataloader_num_workers=1,
            loss_weights=loss_weights,
            end_of_iteration_hook=hooks.end_of_iteration_hook,
            end_of_epoch_hook=end_of_epoch_hook,
            lr_schedulers=lr_dict
        )

        """## Start Tensorboard
        (Turn off adblock and other shields)
        """

        # Commented out IPython magic to ensure Python compatibility.
        # %load_ext tensorboard
        # %tensorboard --logdir example_tensorboard

        """## Train the model"""
        trainer.train(num_epochs=num_epochs)