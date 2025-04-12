#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从PDF文件中提取文本内容的工具
"""

import os
import glob
import json
import logging
from tqdm import tqdm
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import numpy as np


class PDFExtractor:
    """PDF内容提取器
    
    从PDF文件中提取文本内容，支持普通文本提取和OCR提取。
    """
    
    def __init__(self, pdf_dir, output_dir, use_ocr=False, ocr_lang='chi_sim+eng'):
        """
        初始化PDF提取器
        
        Args:
            pdf_dir: PDF文件目录
            output_dir: 提取结果输出目录
            use_ocr: 是否使用OCR (对于扫描PDF)
            ocr_lang: OCR语言配置
        """
        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
        self.use_ocr = use_ocr
        self.ocr_lang = ocr_lang
        self.logger = logging.getLogger("KnowledgeGraph.PDFExtractor")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_all(self):
        """提取所有PDF文件内容"""
        pdf_files = glob.glob(os.path.join(self.pdf_dir, "*.pdf"))
        self.logger.info(f"找到 {len(pdf_files)} 个PDF文件需要处理")
        
        for pdf_file in tqdm(pdf_files, desc="提取PDF"):
            try:
                filename = os.path.basename(pdf_file)
                output_file = os.path.join(
                    self.output_dir, 
                    f"{os.path.splitext(filename)[0]}.json"
                )
                
                # 如果输出文件已存在且较新，则跳过
                if os.path.exists(output_file) and os.path.getmtime(output_file) > os.path.getmtime(pdf_file):
                    self.logger.debug(f"跳过已处理文件: {filename}")
                    continue
                
                # 提取文本
                text_content = self.extract_from_file(pdf_file)
                
                # 保存结果
                result = {
                    "filename": filename,
                    "path": pdf_file,
                    "content": text_content
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                self.logger.debug(f"成功提取并保存: {filename}")
                
            except Exception as e:
                self.logger.error(f"处理文件 {pdf_file} 时出错: {str(e)}")
    
    def extract_from_file(self, pdf_path):
        """
        从单个PDF文件中提取文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本内容
        """
        try:
            doc = fitz.open(pdf_path)
            content = []
            
            for page_num, page in enumerate(doc):
                page_text = ""
                
                # 直接提取文本
                extracted_text = page.get_text("text")
                
                # 如果文本为空或内容太少，且启用了OCR，则使用OCR
                if (not extracted_text.strip() or len(extracted_text) < 50) and self.use_ocr:
                    page_text = self._extract_with_ocr(page)
                else:
                    page_text = extracted_text
                
                # 添加页码和内容
                content.append({
                    "page": page_num + 1,
                    "text": self._clean_text(page_text)
                })
            
            doc.close()
            return content
            
        except Exception as e:
            self.logger.error(f"提取文件 {pdf_path} 内容时出错: {str(e)}")
            return []
    
    def _extract_with_ocr(self, page):
        """
        使用OCR提取页面内容
        
        Args:
            page: PDF页面对象
            
        Returns:
            OCR识别的文本
        """
        try:
            # 将页面渲染为图像
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # 使用Tesseract OCR识别文本
            ocr_text = pytesseract.image_to_string(img, lang=self.ocr_lang)
            return ocr_text
            
        except Exception as e:
            self.logger.error(f"OCR处理时出错: {str(e)}")
            return ""
    
    def _clean_text(self, text):
        """
        清理提取的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 基本清理
        text = text.strip()
        
        # 移除多余的空白字符
        text = ' '.join(text.split())
        
        # 移除特殊控制字符
        text = ''.join(ch for ch in text if ord(ch) >= 32 or ch == '\n')
        
        return text


if __name__ == "__main__":
    # 简单测试代码
    logging.basicConfig(level=logging.DEBUG)
    extractor = PDFExtractor(
        pdf_dir="./test_pdfs",
        output_dir="./extracted_texts",
        use_ocr=True
    )
    extractor.extract_all() 