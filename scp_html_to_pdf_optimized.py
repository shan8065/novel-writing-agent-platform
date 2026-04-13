#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCP HTML转PDF批量转换脚本（优化版）
使用Playwright实现1:1还原HTML格式
支持智能折叠内容处理，增强稳定性
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def expand_collapsible_content(page):
    """
    展开页面中的所有折叠内容（优化版）
    """
    try:
        print("  尝试展开折叠内容...")
        
        # 尝试点击所有可能的折叠按钮
        collapsible_selectors = [
            "[class*='collapsible']",
            "[class*='fold']",
            "[class*='expand']",
            "[class*='toggle']",
            ".spoiler",
            ".spoiler-btn",
            "button[onclick*='toggle']",
            "button[onclick*='expand']",
            "button[onclick*='show']",
            "a[onclick*='toggle']",
            "a[onclick*='expand']",
            "a[onclick*='show']"
        ]
        
        expanded_count = 0
        for selector in collapsible_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"  找到 {len(elements)} 个元素 (选择器: {selector})")
                
                for element in elements:
                    try:
                        # 检查元素是否可见且可点击
                        is_visible = await element.is_visible()
                        if is_visible:
                            # 滚动到元素位置
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            
                            # 尝试点击，设置更短的超时时间
                            await element.click(timeout=5000)
                            expanded_count += 1
                            await asyncio.sleep(0.5)  # 等待动画完成
                            
                    except Exception as e:
                        print(f"    点击元素失败: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"  查询元素失败 (选择器: {selector}): {str(e)}")
                continue
        
        if expanded_count > 0:
            print(f"  成功展开 {expanded_count} 个折叠内容")
        else:
            print("  未找到可展开的折叠内容")
        
        # 额外等待确保所有内容完全展开
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"  展开折叠内容失败: {str(e)}")


async def html_to_pdf_optimized(html_file: Path, output_dir: Path, is_scp6183: bool = False):
    """
    将单个HTML文件转换为PDF（优化版）
    
    Args:
        html_file: HTML文件路径
        output_dir: 输出目录
        is_scp6183: 是否为SCP-6183文档
    """
    pdf_file = output_dir / f"{html_file.stem}.pdf"
    
    print(f"正在转换: {html_file.name} -> {pdf_file.name}")
    if is_scp6183:
        print("  (SCP-6183文档，保持折叠状态)")
    else:
        print("  (展开所有折叠内容)")
    
    async with async_playwright() as p:
        # 启动Chromium浏览器，增加超时时间
        browser = await p.chromium.launch(
            headless=True,
            timeout=120000  # 增加启动超时时间
        )
        page = await browser.new_page()
        
        try:
            # 设置视口大小，确保页面完全显示
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 增加页面超时设置
            page.set_default_timeout(120000)  # 120秒超时
            page.set_default_navigation_timeout(120000)
            
            # 打开HTML文件，使用更宽松的等待条件
            file_url = f"file:///{html_file.absolute().as_posix()}"
            print(f"  加载文件: {file_url}")
            
            await page.goto(file_url, wait_until="domcontentloaded", timeout=120000)
            print("  页面加载完成")
            
            # 等待额外时间确保所有资源加载完成
            await asyncio.sleep(5)
            
            # 对于非SCP-6183文档，展开所有折叠内容
            if not is_scp6183:
                await expand_collapsible_content(page)
            else:
                print("  保持SCP-6183折叠状态...")
            
            # 保存为PDF
            print("  生成PDF...")
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
            return True
            
        except Exception as e:
            print(f"✗ 转换失败 {html_file.name}: {str(e)}")
            return False
        finally:
            await browser.close()


async def batch_convert_optimized(scp_dir: Path, output_dir: Path):
    """
    批量转换SCP目录下的所有HTML文件（优化版）
    
    Args:
        scp_dir: SCP目录路径
        output_dir: 输出目录路径
    """
    print("=" * 60)
    print("SCP HTML转PDF批量转换工具（优化版）")
    print("=" * 60)
    print(f"源目录: {scp_dir}")
    print(f"输出目录: {output_dir}")
    print()
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有HTML文件
    html_files = list(scp_dir.glob("*.html"))
    
    if not html_files:
        print("未找到HTML文件！")
        return
    
    print(f"找到 {len(html_files)} 个HTML文件:")
    for html_file in html_files:
        print(f"  - {html_file.name}")
    print()
    
    # 逐个转换，增加重试机制
    success_count = 0
    failed_files = []
    
    for html_file in html_files:
        # 检查是否为SCP-6183文档
        is_scp6183 = "6183" in html_file.name
        
        # 尝试转换，最多重试2次
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"  第 {attempt + 1} 次重试...")
                
                success = await html_to_pdf_optimized(html_file, output_dir, is_scp6183)
                
                if success:
                    success_count += 1
                    break
                else:
                    if attempt == max_retries:
                        failed_files.append(html_file.name)
                    else:
                        print(f"  等待 {5 * (attempt + 1)} 秒后重试...")
                        await asyncio.sleep(5 * (attempt + 1))
                        
            except Exception as e:
                print(f"  转换异常: {str(e)}")
                if attempt == max_retries:
                    failed_files.append(html_file.name)
                else:
                    await asyncio.sleep(5 * (attempt + 1))
    
    print()
    print("=" * 60)
    print(f"转换完成！成功: {success_count}/{len(html_files)}")
    
    if failed_files:
        print(f"失败文件: {', '.join(failed_files)}")
    
    # 显示转换统计
    print()
    print("转换统计:")
    print(f"  - 总文件数: {len(html_files)}")
    print(f"  - 成功转换: {success_count}")
    print(f"  - 失败文件: {len(failed_files)}")
    print(f"  - SCP-6183文档: {len([f for f in html_files if '6183' in f.name])}")
    print(f"  - 其他文档: {len([f for f in html_files if '6183' not in f.name])}")
    print("=" * 60)


if __name__ == "__main__":
    # 目录路径
    scp_directory = Path(r"e:\小说\SCP")
    output_directory = Path(r"e:\小说\SCP_PDF")
    
    # 运行批量转换
    asyncio.run(batch_convert_optimized(scp_directory, output_directory))