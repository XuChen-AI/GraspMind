from typing import List, Dict, Any, Optional


class InputMessage:
    """
    简化的输入消息类，包含text字典列表和image路径
    """
    
    def __init__(self, text_messages: Optional[List[Dict[str, Any]]] = None, 
                 image_path: Optional[str] = None):
        """
        初始化输入消息
        
        Args:
            text_messages: 文本消息字典列表
            image_path: 图像路径，可以为None
        """
        self.text = text_messages if text_messages is not None else []
        self.image = image_path
    
    def add_dict(self, text_dict: Dict[str, Any]) -> None:
        """
        在text列表中添加一个字典
        
        Args:
            text_dict: 要添加的字典
        """
        if not isinstance(text_dict, dict):
            raise TypeError("必须添加字典类型的数据")
        self.text.append(text_dict)
    
    def remove_dict(self, index: int) -> bool:
        """
        根据索引删除text列表中的字典
        
        Args:
            index: 要删除的字典索引
            
        Returns:
            删除成功返回True，否则返回False
        """
        if 0 <= index < len(self.text):
            self.text.pop(index)
            return True
        return False
    
    def to_sentence(self, separator: str = "; ", key_value_connector: str = ": ") -> str:
        """
        将text列表中的所有字典拼接成一句话
        
        Args:
            separator: 字典之间的分隔符，默认为"; "
            key_value_connector: 键值对之间的连接符，默认为": "
            
        Returns:
            拼接后的字符串
        """
        if not self.text:
            return ""
        
        sentences = []
        for text_dict in self.text:
            if isinstance(text_dict, dict):
                dict_items = []
                for key, value in text_dict.items():
                    dict_items.append(f"{key}{key_value_connector}{value}")
                sentences.append(", ".join(dict_items))
        
        return separator.join(sentences)
    
    def set_image(self, image_path: Optional[str]) -> None:
        """
        设置图像路径
        
        Args:
            image_path: 图像路径
        """
        self.image = image_path
    
    def __len__(self) -> int:
        """返回text列表的长度"""
        return len(self.text)
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"InputMessage(text_count={len(self.text)}, image={self.image})"


# 示例用法
if __name__ == "__main__":
    # 创建输入消息
    input_msg = InputMessage()
    
    # 添加字典
    input_msg.add_dict({"type": "text", "content": "这是一个文本消息"})
    input_msg.add_dict({"type": "detection", "content": "检测到对象", "confidence": 0.95})
    input_msg.add_dict({"action": "process", "status": "完成"})
    
    # 设置图像路径
    input_msg.set_image("path/to/image.jpg")
    
    print(f"消息数量: {len(input_msg)}")
    print(f"图像路径: {input_msg.image}")
    print(f"拼接成句子: {input_msg.to_sentence()}")
    
    # 删除一个字典
    input_msg.remove_dict(1)
    print(f"删除后消息数量: {len(input_msg)}")
    print(f"删除后拼接: {input_msg.to_sentence()}")
