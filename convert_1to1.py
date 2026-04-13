
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
import os
import requests
import re
import urllib.parse

def download_and_inline_css(soup, html_dir):
    """下载外部CSS并内联到HTML中"""
    # 处理 @import 语句
    style_tags = soup.find_all('style')
    for style in style_tags:
        if style.string:
            # 匹配 @import url(...) 格式
            import_pattern = re.compile(r'@import\s+url\([\'"]?([^\'"\)]+)[\'"]?\)', re.IGNORECASE)
            css_content = style.string
            
            def replace_import(match):
                css_url = match.group(1)
                try:
                    print(f"  下载CSS: {css_url[:60]}...")
                    response = requests.get(css_url, timeout=30)
                    if response.status_code == 200:
                        return response.text
                except Exception as e:
                    print(f"  警告: 无法下载CSS {css_url}: {e}")
                return match.group(0)
            
            style.string = import_pattern.sub(replace_import, css_content)
    
    # 处理 &lt;link rel="stylesheet"&gt; 标签
    link_tags = soup.find_all('link', rel='stylesheet')
    for link in link_tags:
        href = link.get('href')
        if href:
            try:
                print(f"  下载CSS: {href[:60]}...")
                response = requests.get(href, timeout=30)
                if response.status_code == 200:
                    # 创建新的style标签
                    new_style = soup.new_tag('style')
                    new_style.string = response.text
                    link.replace_with(new_style)
            except Exception as e:
                print(f"  警告: 无法下载CSS {href}: {e}")

def fix_local_resources(soup, html_dir, html_filename):
    """修复本地资源路径"""
    # 找到对应的_files目录
    base_name = os.path.splitext(html_filename)[0]
    files_dir = os.path.join(html_dir, f"{base_name}_files")
    
    if not os.path.exists(files_dir):
        print(f"  警告: 未找到资源目录 {files_dir}")
        return
    
    # 修复图片路径
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith('http'):
            # 提取文件名
            filename = os.path.basename(src)
            local_path = os.path.join(files_dir, filename)
            if os.path.exists(local_path):
                # 转换为file:// URL
                abs_path = os.path.abspath(local_path)
                file_url = f"file:///{abs_path.replace(os.sep, '/')}"
                img['src'] = file_url
    
    # 修复其他资源路径（CSS背景图等）
    for style in soup.find_all('style'):
        if style.string:
            # 简单处理背景图
            url_pattern = re.compile(r'url\([\'"]?([^\'"\)]+)[\'"]?\)')
            def replace_url(match):
                url = match.group(1)
                if url and not url.startswith('http') and not url.startswith('data:'):
                    filename = os.path.basename(url)
                    local_path = os.path.join(files_dir, filename)
                    if os.path.exists(local_path):
                        abs_path = os.path.abspath(local_path)
                        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
                        return f'url("{file_url}")'
                return match.group(0)
            style.string = url_pattern.sub(replace_url, style.string)

def clean_unwanted_elements(soup):
    """移除不需要的元素（脚本、分析代码等）"""
    # 移除所有script标签
    for script in soup.find_all('script'):
        script.decompose()
    
    # 移除noscript标签
    for noscript in soup.find_all('noscript'):
        noscript.decompose()

def prepare_html_for_pdf(html_path):
    """准备HTML文件用于PDF转换"""
    html_dir = os.path.dirname(html_path)
    html_filename = os.path.basename(html_path)
    
    print(f"处理文件: {html_filename}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print("  下载并内联CSS...")
    download_and_inline_css(soup, html_dir)
    
    print("  修复本地资源路径...")
    fix_local_resources(soup, html_dir, html_filename)
    
    print("  清理不需要的元素...")
    clean_unwanted_elements(soup)
    
    # 添加打印优化样式
    print_style = soup.new_tag('style')
    print_style.string = '''
    @media print {
        /* 隐藏不需要的元素 */
        #side-bar, #header, #footer, .page-rate-widget-box, .page-info,
        .wd-print-btn, .action-area, .tags, .pager {
            display: none !important;
        }
        
        /* 优化主内容区域 */
        #main-content {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }
        
        #page-content {
            margin: 0 auto !important;
            max-width: 800px !important;
            padding: 20px !important;
        }
        
        /* 确保图片打印 */
        img {
            max-width: 100% !important;
            page-break-inside: avoid !important;
        }
        
        /* 避免段落内分页 */
        p, div {
            page-break-inside: avoid !important;
        }
    }
    
    /* 屏幕显示时也应用优化 */
    #side-bar, #header, #footer, .page-rate-widget-box, .page-info,
    .wd-print-btn, .action-area, .tags, .pager {
        display: none !important;
    }
    
    #main-content {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    #page-content {
        margin: 0 auto !important;
        max-width: 800px !important;
        padding: 20px !important;
    }
    '''
    soup.head.append(print_style)
    
    return str(soup)

async def html_to_pdf(html_content, pdf_path, temp_html_path):
    """使用Playwright将HTML转换为PDF"""
    # 保存临时HTML文件
    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        file_url = f"file:///{temp_html_path.replace(os.sep, '/')}"
        print(f"  加载HTML: {os.path.basename(temp_html_path)}")
        
        await page.goto(file_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        
        print(f"  生成PDF: {os.path.basename(pdf_path)}")
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
    
    # 删除临时HTML文件
    try:
        os.remove(temp_html_path)
    except:
        pass

def get_scp_title(filename):
    """从文件名中提取SCP编号"""
    match = re.search(r'SCP-(\d+)', filename)
    if match:
        return f"SCP-{match.group(1)}"
    return "SCP Document"

async def convert_single_file(html_path, output_dir):
    """转换单个文件"""
    filename = os.path.basename(html_path)
    scp_title = get_scp_title(filename)
    
    print("=" * 60)
    print(f"开始转换: {filename}")
    print("=" * 60)
    
    # 准备HTML
    html_content = prepare_html_for_pdf(html_path)
    
    # 保存处理后的HTML（可选，用于调试）
    debug_html_path = os.path.join(output_dir, f"{scp_title}-debug.html")
    with open(debug_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  调试HTML已保存: {os.path.basename(debug_html_path)}")
    
    # 转换为PDF
    pdf_path = os.path.join(output_dir, f"{scp_title}-1to1.pdf")
    temp_html_path = os.path.join(output_dir, f"{scp_title}-temp.html")
    
    await html_to_pdf(html_content, pdf_path, temp_html_path)
    
    print("=" * 60)
    print(f"✅ 完成! PDF保存到: {pdf_path}")
    print("=" * 60)
    return pdf_path

async def main():
    # 输出目录
    output_dir = r"e:\小说\SCP_PDF"
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 要转换的文件
    html_path = r"e:\小说\SCP\SCP-3812 - SCP基金会.html"
    
    if not os.path.exists(html_path):
        print(f"❌ 文件不存在: {html_path}")
        return
    
    await convert_single_file(html_path, output_dir)

if __name__ == "__main__":
    asyncio.run(main())
