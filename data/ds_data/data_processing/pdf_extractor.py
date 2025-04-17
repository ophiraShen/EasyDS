import fitz  # PyMuPDF
import os
import pdfplumber
from PIL import Image
import io
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import numpy as np

class PDFExtractor:
    def __init__(self, pdf_path, output_dir, is_scanned=False, lang='ch'):
        """
        初始化PDF提取器
        :param pdf_path: PDF文件路径
        :param is_scanned: 是否是扫描版PDF
        :param lang: OCR识别的语言，默认中文
        """
        self.pdf_path = pdf_path
        self.is_scanned = is_scanned
        self.lang = lang
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # 创建必要的子目录
        os.makedirs(os.path.join(self.output_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "text"), exist_ok=True)
        if is_scanned:
            os.makedirs(os.path.join(self.output_dir, "pages"), exist_ok=True)
        
        # 如果是扫描版PDF，初始化OCR
        if is_scanned:
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)

    def extract_text_from_scanned_pdf(self):
        """使用OCR提取扫描版PDF中的文本内容"""
        print("正在将PDF转换为图片...")
        # 将PDF转换为图片
        images = convert_from_path(self.pdf_path)
        
        print("开始OCR识别...")
        for page_num, image in enumerate(images, 1):
            print(f"正在处理第 {page_num} 页...")
            
            # 保存页面图片
            page_image_path = os.path.join(self.output_dir, "pages", f"page_{page_num}.jpg")
            image.save(page_image_path)
            
            # OCR识别
            result = self.ocr.ocr(page_image_path)
            
            # 提取文本
            text = ""
            if result[0]:  # 确保有识别结果
                for line in result[0]:
                    text += line[1][0] + "\n"  # 添加识别的文本
            
            # 保存文本
            if text:
                output_file = os.path.join(self.output_dir, "text", f"page_{page_num}.txt")
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)

    def extract_text(self):
        """提取PDF中的文本内容"""
        if self.is_scanned:
            self.extract_text_from_scanned_pdf()
        else:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        output_file = os.path.join(self.output_dir, "text", f"page_{page_num}.txt")
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(text)

    def extract_images(self):
        """提取PDF中的图片"""
        if self.is_scanned:
            print("扫描版PDF的图片已在页面处理中提取")
            return
            
        doc = fitz.open(self.pdf_path)
        img_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # 获取图片格式
                ext = base_image["ext"]
                
                # 保存图片
                image = Image.open(io.BytesIO(image_bytes))
                img_count += 1
                image_path = os.path.join(self.output_dir, "images", f"image_{page_num+1}_{img_count}.{ext}")
                image.save(image_path)

    def process(self):
        """处理PDF文件，提取所有内容"""
        print(f"开始处理PDF文件: {self.pdf_path}")
        print(f"处理模式: {'扫描版' if self.is_scanned else '电子版'} PDF")
        
        print("提取文本...")
        self.extract_text()
        
        if not self.is_scanned:
            print("提取图片...")
            self.extract_images()
        
        print(f"处理完成！提取的内容保存在: {self.output_dir}")
        if self.is_scanned:
            print(f"- 原始页面图片：{os.path.join(self.output_dir, 'pages')}")
        print(f"- 提取的文本：{os.path.join(self.output_dir, 'text')}")
        if not self.is_scanned:
            print(f"- 提取的图片：{os.path.join(self.output_dir, 'images')}")

if __name__ == "__main__":
    # 使用示例
    pdf_path = "/root/autodl-tmp/EasyDS/data/DS2026.pdf"  # 替换为实际的PDF文件路径
    output_dir = "/root/autodl-tmp/EasyDS/data/DS2026_extracted"  # 替换为实际的输出目录
    is_scanned = True  # 如果是扫描版PDF，设置为True
    lang = 'ch'  # 设置OCR语言，支持：ch(中文)、en(英文)等
    
    extractor = PDFExtractor(pdf_path, output_dir, is_scanned=is_scanned, lang=lang)
    extractor.process() 