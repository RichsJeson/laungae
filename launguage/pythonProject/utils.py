import os
import re

import openpyxl
import xml.etree.ElementTree as ET


# utf-8
def has_special_char(s):
    pattern = re.compile(r'[`~!@#$%^&*()+={}\[\]:;"\'<>,.?/\\|]')
    return pattern.search(s) is not None


def isConvertString(str):
    array = ['\\', '%', '$', '&', '#', ';', '@', 'X', '€']
    for char in array:
        if char is not None and char in str:
            return True
    return False
    pass


def replace(r):
    if "_" in r:
        words = r.split("_")  # 将字符串按照下划线分割成单词列表
        words = [word.capitalize() for word in words]  # 将每个单词的首字母大写
        res = "".join(words)
        return res
    elif " " in r:
        words = r.split(" ")  # 将字符串按照下划线分割成单词列表
        words = [word.capitalize() for word in words]  # 将每个单词的首字母大写
        res = "".join(words)
        return res
    elif has_special_char(r) is True:
        words = str(r)
        words = re.sub(r"[^a-zA-Z0-9\s]+", "", words)
        print(words)
        return words
        pass
    else:
        return r


# 获取路径
def getPwd():
    current_path = os.getcwd()
    parent_path = os.path.abspath(os.path.join(current_path, ".."))
    print(parent_path)
    return parent_path
    pass


# 恢复字典字段
# generatorDict：通过生成后的字典
# sourceDict:初始字段的字典
def getDict(generatorDict, sourceDict):
    recoveryDict = {}
    for v in sourceDict.keys():
        result = replace(v)
        if result in generatorDict:
            recoveryDict[v] = generatorDict[result]
        else:
            recoveryDict[v] = ''
    return recoveryDict


# 导出多语言
# rowCount：传入的多语言列数
# fileDir：传入待解析的XML 表格
# target：生成目标文件
def exportXMLFromExcel(fileDir, rowCount, target):
    root = ET.Element('resources')
    wb = openpyxl.load_workbook(fileDir)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is not None and has_special_char(row[0]) is False:
            # 创建XML子节点
            child = ET.SubElement(root, 'string')
            child.set('name', row[0])
            child.text = row[rowCount]
            if child.text is not None:
                child.text = str(child.text)
                if isConvertString(child.text):
                    child.text = child.text + "@richsjeson.gmail.com"
    # 将XML写入文件
    tree = ET.ElementTree(root)
    print(tree)
    tree.write(target, encoding='utf-8', xml_declaration=True)


# 统计最终输出的函数
def calculateKeyCount(fileDirs, source):
    global child
    tree = ET.parse(os.path.join(fileDirs, source))
    root = tree.getroot()
    # 生成字典
    doc1 = {}
    str1 = "["
    # 最终字典序列，后续需要进行还原
    for child in root:
        doc1[child.attrib['name']] = child.text
        # print(child.attrib['name'])
        str1 += "\"" + child.attrib['name'] + "\","
    str1 += "]"
    return str(len(doc1))


# 输出缺失的KEY
def calculateKeyisLack(fileDirs, source, targetKeys):
    tree = ET.parse(os.path.join(fileDirs, source))
    root = tree.getroot()
    # 最终字典序列，后续需要进行还原
    for child in root:
        if child.attrib['name'] not in targetKeys:
            print("lacks key:" + child.attrib['name'])
            pass
        else:
            targetKeys.remove(child.attrib['name'])
