# utf-8
# 多语言导出工具
import re

import openpyxl
import xml.etree.ElementTree as ET
wb = openpyxl.load_workbook('AigoSmart_app_2.0.41.xlsx')
ws = wb.active

# 创建XML根节点
root = ET.Element('resources')


def has_special_char(s):
    pattern = re.compile(r'[`~!@#$%^&*()+={}\[\]:;"\'<>,.?/\\|]')
    return pattern.search(s) is not None


# 遍历Excel表格，将每一行数据转换为XML子节点，并添加到XML根节点中
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[0] is not None and has_special_char(row[0]) is False:
        # 创建XML子节点
        child = ET.SubElement(root, 'string')
        child.set('name', row[0])
        child.text = row[1]

# 将XML写入文件
tree = ET.ElementTree(root)
tree.write('output.xml', encoding='utf-8', xml_declaration=True)

