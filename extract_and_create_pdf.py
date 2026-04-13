from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
import os

def extract_and_unfold_content(html_path):
    """从SCP HTML文件中提取内容并展开所有折叠块"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到主要内容区域
    page_content = soup.find('div', id='page-content')
    
    if not page_content:
        return None
    
    # 展开所有折叠块
    collapsible_blocks = page_content.find_all('div', class_='collapsible-block')
    
    for block in collapsible_blocks:
        # 找到展开的内容区域
        unfolded_content = block.find('div', class_='collapsible-block-unfolded')
        
        if unfolded_content:
            # 移除display:none样式，让内容显示
            unfolded_content['style'] = ''
            
            # 或者找到实际的内容并替换整个折叠块
            content_div = unfolded_content.find('div', class_='collapsible-block-content')
            
            if content_div:
                # 用内容替换整个折叠块
                block.replace_with(content_div)
    
    # 清理掉一些不需要的元素
    # 移除折叠链接等
    for element in page_content.find_all(['script']):
        element.decompose()
    
    return str(page_content)

def create_clean_html(content, title="SCP-3812"):
    """创建一个排版完美的HTML文件"""
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.8;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #222;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: bold;
        }}
        h1 {{
            text-align: center;
            border-bottom: 3px solid #882244;
            padding-bottom: 15px;
            font-size: 24pt;
        }}
        h2 {{
            font-size: 18pt;
            color: #882244;
            border-left: 4px solid #882244;
            padding-left: 10px;
        }}
        p {{
            margin: 1em 0;
            text-align: justify;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 15px 0;
            padding: 10px 20px;
            background-color: #f9f9f9;
        }}
        .warning-box {{
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }}
        .collapsible-block-content {{
            border: 1px solid #e0e0e0;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #882244;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        strong {{
            color: #882244;
        }}
        em {{
            color: #666;
            font-style: italic;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""
    return html_template

async def html_to_pdf(html_path, pdf_path):
    """使用Playwright将HTML转换为PDF"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        file_url = f"file:///{html_path.replace(os.sep, '/')}"
        await page.goto(file_url, wait_until="networkidle")
        
        await asyncio.sleep(2)
        
        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={
                "top": "2cm",
                "bottom": "2cm",
                "left": "2cm",
                "right": "2cm"
            }
        )
        
        await browser.close()

if __name__ == "__main__":
    # 路径设置
    original_html = r"e:\小说\SCP\SCP-3812 - SCP基金会.html"
    clean_html_path = r"e:\小说\SCP_PDF\SCP-3812-clean.html"
    final_pdf_path = r"e:\小说\SCP_PDF\SCP-3812-perfect.pdf"
    
    print("步骤1: 提取SCP文档内容并展开所有折叠块...")
    content = extract_and_unfold_content(original_html)
    
    if content:
        print("步骤2: 创建排版完美的HTML...")
        clean_html = create_clean_html(content, "SCP-3812 - 我身后的声音")
        
        with open(clean_html_path, 'w', encoding='utf-8') as f:
            f.write(clean_html)
        
        print(f"步骤3: 转换为PDF...")
        asyncio.run(html_to_pdf(clean_html_path, final_pdf_path))
        
        print(f"✅ 完成！完美PDF已保存到: {final_pdf_path}")
    else:
        print("❌ 无法提取内容！")
