# utf-8
import os

from pythonProject.utils import replace
import re
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, RepeatVector, TimeDistributed, Dense
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import xml.etree.ElementTree as ET


# 声明一个多语言工具类，用于生成目标文件
# 输入文件为:原始文件
# 输入文件为：比对文件
# 目标输出文件为:target
class MultiLanguageGenerator:
    def __init__(self):
        pass

    pass

    # 多语言比对方法，传入的文件目录
    # fileDirs:文件目录名称
    @staticmethod
    def compact(fileDirs, source, compact, target):
        print(os.path.join(fileDirs,source))
        tree = ET.parse(os.path.join(fileDirs,source))
        root = tree.getroot()
        # 生成字典
        doc1 = {}
        # 最终字典序列，后续需要进行还原
        finalDict = {}
        for child in root:
            new_key = replace(child.attrib['name'])
            doc1[new_key] = child.text
            finalDict[child.attrib['name']] = child.text

        tree = ET.parse(os.path.join(fileDirs,compact))
        root = tree.getroot()
        # 生成字典
        doc2 = {}
        for child in root:
            new_key = replace(child.attrib['name'])
            doc2[new_key] = child.text
            if child.attrib['name'] not in finalDict:
                finalDict[child.attrib['name']] = child.text
        # 将doc2中不存在于doc1中的键添加到doc1中，并将其值设置为空字符串
        for k in doc1.keys():
            if k not in doc2:
                if doc1[k] is not None:
                    doc2[k] = doc1[k]
                else:
                    doc2[k] = ''
                    pass

        for v in doc2.keys():
            if v not in doc1:
                doc1[v] = doc2[v]
        pass
        # 定义一个Tokenizer对象
        tokenizer = Tokenizer()
        # 将文档1和文档2中的单词转换为ID，并构建词汇表
        tokenizer.fit_on_texts(doc1.keys())
        tokenizer.fit_on_texts(doc2.keys())

        # 将文档1和文档2中的单词序列进行填充
        doc1_sequence = pad_sequences(tokenizer.texts_to_sequences(doc1.keys()), padding='post')
        doc2_sequence = pad_sequences(tokenizer.texts_to_sequences(doc2.keys()), padding='post')

        # 定义Seq2Seq模型
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(input_dim=len(tokenizer.word_index) + 1, output_dim=64),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.LSTM(64),
            # 将输入重复7次
            tf.keras.layers.RepeatVector(len(doc2)),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.LSTM(64, return_sequences=True),
            tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(len(tokenizer.word_index) + 1, activation='softmax'))
        ])

        # 编译模型
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
        # 训练模型
        model.fit(doc2_sequence.reshape(1, -1, 1), doc1_sequence.reshape(1, -1, 1), epochs=100)

        # 使用训练好的模型对第二个文档进行排序，并将排序后的文档输出到一个新的文档中
        doc2_sorted = model.predict(doc2_sequence.reshape(1, -1, 1)).argmax(axis=-1)[0]
        doc2_sorted = [tokenizer.index_word[i] for i in doc2_sorted]

        # 将排序后的文档2中的字典KEY按照文档1中的字典KEY有序排序，VALUE的值还是使用字典2的VALUE值
        doc2_sorted_dict = {}
        for k in doc1.keys():
            if k in doc2:
                # if isConvertString(doc1[k]):
                #     doc2_sorted_dict[k] = doc1[k] + "/r/ncode=3123123"
                # else:
                doc2_sorted_dict[k] = doc2[k]
            else:
                doc2_sorted_dict[k] = doc2.get(k, '')
        # 还原字典KEY
        recoveryDict = {}
        root = ET.Element('resources')
        for v in finalDict.keys():
            result = replace(v)
            if result in doc2_sorted_dict:
                recoveryDict[v] = doc2_sorted_dict[result]
                value = ET.SubElement(root, 'string', {'name': v})
                value.text = recoveryDict[v]
            else:
                recoveryDict[v] = ''
                value = ET.SubElement(root, 'string', {'name': v})
                value.text = recoveryDict[v]
        tree = ET.ElementTree(root)
        tree.write(os.path.join(fileDirs,target), encoding='utf-8')
