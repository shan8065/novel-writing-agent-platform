
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML转PDF批量转换脚本
使用Playwright实现1:1还原HTML格式
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def html_to_pdf(html_file: Path, output_dir: Path = None):
    """
    将单个HTML文件转换为PDF
    
    Args:
        html_file: HTML文件路径
        output_dir: 输出目录（默认为HTML文件所在目录）
    """
    if output_dir is None:
        output_dir = html_file.parent
    
    pdf_file = output_dir / f"{html_file.stem}.pdf"
    
    print(f"正在转换: {html_file.name} -&gt; {pdf_file.name}")
    
    async with async_playwright() as p:
        # 启动Chromium浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # 设置视口大小，确保页面完全显示
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 打开HTML文件
            file_url = f"file:///{html_file.absolute().as_posix()}"
            await page.goto(file_url, wait_until="networkidle", timeout=60000)
            
            # 等待额外时间确保所有资源加载完成
            await asyncio.sleep(3)
            
            # 保存为PDF
            await page.pdf(
                path=pdf_file,
                format="A4",
                print_background=True,
                margin={
                    "top": "0.5in",
                    "right": "0.5in",
                    "bottom": "0.5in",
                    "left": "0.5in"
                }
            )
            
            print(f"✓ 转换成功: {pdf_file.name}")
            
        except Exception as e:
            print(f"✗ 转换失败 {html_file.name}: {str(e)}")
            raise
        finally:
            await browser.close()


async def batch_convert(scp_dir: Path):
    """
    批量转换SCP目录下的所有HTML文件
    
    Args:
        scp_dir: SCP目录路径
    """
    print("=" * 60)
    print("HTML转PDF批量转换工具")
    print("=" * 60)
    print(f"工作目录: {scp_dir}")
    print()
    
    # 查找所有HTML文件
    html_files = list(scp_dir.glob("*.html"))
    
    if not html_files:
        print("未找到HTML文件！")
        return
    
    print(f"找到 {len(html_files)} 个HTML文件:")
    for html_file in html_files:
        print(f"  - {html_file.name}")
    print()
    
    # 逐个转换
    success_count = 0
    failed_files = []
    
    for html_file in html_files:
        try:
            await html_to_pdf(html_file)
            success_count += 1
        except Exception as e:
            failed_files.append(html_file.name)
            print(f"错误: {str(e)}")
    
    print()
    print("=" * 60)
    print(f"转换完成！成功: {success_count}/{len(html_files)}")
    
    if failed_files:
        print(f"失败文件: {', '.join(failed_files)}")
    print("=" * 60)


if __name__ == "__main__":
    # SCP目录路径
    scp_directory = Path(r"e:\小说\SCP")
    
    # 运行批量转换
    asyncio.run(batch_convert(scp_directory))

