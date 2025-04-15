# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午5:18
# @Author : Yaro
# @Des: 
"""
import hashlib
def generate_unique_id(input_string: str) :
    hash_object = hashlib.sha256(input_string.encode())
    unique_id = hash_object.hexdigest()
    return unique_id