from abc import abstractmethod, ABC
import xml.etree.ElementTree as ET
import xml.dom.minidom


class IParser(ABC):
    @abstractmethod
    def parser(self, dict,target):
        pass


class XMLParser(IParser, ABC):
    def parser(self, dicts,target):
        root = ET.Element('resources')
        for v in dicts.keys():
            value = ET.SubElement(root, 'string', {'name': v})
            value.text = dicts[v]
            # 将XML写入文件
        tree = ET.ElementTree(root)
        tree.write(target, encoding='utf-8', xml_declaration=True)
