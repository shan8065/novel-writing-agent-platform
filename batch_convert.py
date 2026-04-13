from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
import os
import re

def extract_content(html_path, unfold_collapsible=True):
    """从SCP HTML文件中提取内容"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到主要内容区域
    page_content = soup.find('div', id='page-content')
    
    if not page_content:
        return None
    
    if unfold_collapsible:
        # 展开所有折叠块
        collapsible_blocks = page_content.find_all('div', class_='collapsible-block')
        
        for block in collapsible_blocks:
            # 找到展开的内容区域
            unfolded_content = block.find('div', class_='collapsible-block-unfolded')
            
            if unfolded_content:
                # 找到实际的内容并替换整个折叠块
                content_div = unfolded_content.find('div', class_='collapsible-block-content')
                
                if content_div:
                    # 用内容替换整个折叠块
                    block.replace_with(content_div)
    
    # 清理掉一些不需要的元素
    for element in page_content.find_all(['script']):
        element.decompose()
    
    return str(page_content)

def create_clean_html(content, title="SCP Document"):
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
        try:
            await page.goto(file_url, wait_until="domcontentloaded", timeout=60000)
        except:
            # 如果超时也继续，可能本地文件不需要网络等待
            pass
        
        await asyncio.sleep(3)
        
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

def get_scp_title(filename):
    """从文件名中提取SCP编号"""
    match = re.search(r'SCP-(\d+)', filename)
    if match:
        return f"SCP-{match.group(1)}"
    return "SCP Document"

async def convert_single_scp(html_path, output_dir, unfold_collapsible=True):
    """转换单个SCP文档"""
    filename = os.path.basename(html_path)
    scp_title = get_scp_title(filename)
    
    print(f"\n正在处理: {filename}")
    
    # 提取内容
    content = extract_content(html_path, unfold_collapsible=unfold_collapsible)
    
    if not content:
        print(f"❌ 无法提取内容: {filename}")
        return False
    
    # 创建HTML
    clean_html = create_clean_html(content, scp_title)
    
    clean_html_path = os.path.join(output_dir, f"{scp_title}-clean.html")
    with open(clean_html_path, 'w', encoding='utf-8') as f:
        f.write(clean_html)
    
    # 转换为PDF
    pdf_path = os.path.join(output_dir, f"{scp_title}.pdf")
    await html_to_pdf(clean_html_path, pdf_path)
    
    print(f"✅ 完成: {scp_title}.pdf")
    return True

async def main():
    # 输出目录
    output_dir = r"e:\小说\SCP_PDF"
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # SCP文档列表（按顺序处理）
    scp_files = [
        (r"e:\小说\SCP\SCP-6488 - SCP基金会.html", True),
        (r"e:\小说\SCP\SCP-6659 - SCP基金会.html", True),
        (r"e:\小说\SCP\SCP-6747 - SCP基金会.html", True),
        (r"e:\小说\SCP\SCP-6820 - SCP基金会.html", True),
        (r"e:\小说\SCP\SCP-7528 - SCP基金会.html", True),
        (r"e:\小说\SCP\SCP-6183 - SCP基金会.html", False),  # 最后一个，不展开
    ]
    
    print("开始批量转换SCP文档...")
    print("=" * 50)
    
    success_count = 0
    for html_path, unfold in scp_files:
        filename = os.path.basename(html_path)
        scp_title = get_scp_title(filename)
        pdf_path = os.path.join(output_dir, f"{scp_title}.pdf")
        
        # 检查是否已经转换过
        if os.path.exists(pdf_path):
            print(f"\n跳过: {filename} (已存在)")
            success_count += 1
            continue
        
        if await convert_single_scp(html_path, output_dir, unfold_collapsible=unfold):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"批量转换完成！成功转换 {success_count}/{len(scp_files)} 个文档")
    print(f"输出目录: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())
