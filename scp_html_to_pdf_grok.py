#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCP HTML转PDF批量转换脚本（Grok优化版）
根据Grok的紧急优化指令进行修改
只渲染主内容，彻底展开折叠，完整保留样式
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def expand_collapsible_content(page):
    """
    彻底展开所有折叠内容 - Grok优化版
    """
    try:
        print("  彻底展开所有折叠内容...")
        
        # 第一步：先点击所有折叠链接
        click_result = await page.evaluate("""
            () => {
                let clickCount = 0;
                const links = document.querySelectorAll('.collapsible-block-folded .collapsible-block-link');
                links.forEach(link => {
                    try {
                        link.click();
                        clickCount++;
                    } catch(e) {}
                });
                return clickCount;
            }
        """)
        print(f"  点击了 {click_result} 个折叠链接")
        
        await asyncio.sleep(1)
        
        # 第二步：强制显示所有折叠内容
        expand_result = await page.evaluate("""
            () => {
                let expandedCount = 0;
                const blocks = document.querySelectorAll('.collapsible-block');
                
                blocks.forEach((block, index) => {
                    const folded = block.querySelector('.collapsible-block-folded');
                    const unfolded = block.querySelector('.collapsible-block-unfolded');
                    const content = block.querySelector('.collapsible-block-content');
                    
                    if (folded) {
                        folded.style.display = 'none';
                        folded.style.visibility = 'hidden';
                    }
                    
                    if (unfolded) {
                        unfolded.style.display = 'block';
                        unfolded.style.visibility = 'visible';
                        unfolded.removeAttribute('style');
                    }
                    
                    if (content) {
                        content.style.display = 'block';
                        content.style.visibility = 'visible';
                    }
                    
                    expandedCount++;
                });
                
                return expandedCount;
            }
        """)
        print(f"  处理了 {expand_result} 个折叠块")
        
        # 第三步：添加CSS确保打印时全部显示
        await page.evaluate("""
            () => {
                const style = document.createElement('style');
                style.textContent = `
                    .collapsible-block-folded { display: none !important; }
                    .collapsible-block-unfolded { display: block !important; visibility: visible !important; }
                    .collapsible-block-content { display: block !important; visibility: visible !important; }
                    [style*="display:none"] { display: block !important; }
                `;
                document.head.appendChild(style);
                return style;
            }
        """)
        
        await asyncio.sleep(2)
        print("  折叠内容展开完成！")
        
    except Exception as e:
        print(f"  展开折叠内容时遇到问题: {str(e)}")


async def html_to_pdf_grok_optimized(html_file: Path, output_file: Path):
    """
    将HTML文件转换为PDF - Grok优化版
    
    Args:
        html_file: HTML文件路径
        output_file: 输出PDF文件路径
    """
    print(f"正在转换: {html_file.name} -> {output_file.name}")
    
    async with async_playwright() as p:
        # 启动Chromium浏览器
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--allow-file-access-from-files',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        page = await browser.new_page(
            viewport={"width": 1920, "height": 3000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page.set_default_timeout(180000)
        
        try:
            file_url = f"file:///{html_file.absolute().as_posix()}"
            print(f"  正在加载页面: {file_url}")
            
            await page.goto(file_url, timeout=60000)
            
            print("  等待资源加载...")
            await asyncio.sleep(10)
            
            # 第一步：彻底展开所有折叠内容
            await expand_collapsible_content(page)
            
            # 第二步：只显示主内容，隐藏其他部分
            print("  优化页面显示（只保留主内容）...")
            await page.evaluate("""
                () => {
                    // 隐藏无关部分
                    const hideSelectors = [
                        '#header', 
                        '#top-bar', 
                        '#side-bar', 
                        '#footer', 
                        '.login-info',
                        '.site-tools',
                        '#breadcrumbs',
                        '.page-tags',
                        '.page-rate-widget-box',
                        '.pagerate',
                        '#action-area-top',
                        '#action-area',
                        '.page-info'
                    ];
                    
                    hideSelectors.forEach(selector => {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            el.style.display = 'none';
                            el.style.visibility = 'hidden';
                        });
                    });
                    
                    // 确保主内容区域完全显示
                    const pageContent = document.querySelector('#page-content');
                    if (pageContent) {
                        pageContent.style.margin = '0';
                        pageContent.style.padding = '20px';
                        pageContent.style.maxWidth = 'none';
                        pageContent.style.width = '100%';
                    }
                    
                    // 优化body样式
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    document.body.style.background = '#fff';
                    
                    return true;
                }
            """)
            
            # 添加打印优化CSS
            await page.evaluate("""
                () => {
                    const printStyle = document.createElement('style');
                    printStyle.textContent = `
                        @media print {
                            #header, #top-bar, #side-bar, #footer { display: none !important; }
                            #page-content { 
                                display: block !important; 
                                margin: 0 !important; 
                                padding: 0 !important;
                                width: 100% !important;
                                max-width: none !important;
                            }
                            body { 
                                margin: 0 !important; 
                                padding: 0 !important;
                                background: white !important;
                            }
                            .collapsible-block-unfolded { display: block !important; }
                            .collapsible-block-folded { display: none !important; }
                        }
                    `;
                    document.head.appendChild(printStyle);
                }
            """)
            
            await asyncio.sleep(3)
            
            # 获取页面高度
            page_height = await page.evaluate("""
                () => {
                    return Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    );
                }
            """)
            print(f"  页面高度: {page_height}px")
            
            # 生成PDF - Grok优化参数
            print("  正在生成PDF（横向A4，高质量）...")
            await page.pdf(
                path=output_file,
                format="A4",
                landscape=True,  # 横向
                print_background=True,
                prefer_css_page_size=False,
                margin={
                    "top": "0.5cm",
                    "right": "0.5cm",
                    "bottom": "0.5cm",
                    "left": "0.5cm"
                },
                scale=1.0,
                display_header_footer=False
            )
            
            print(f"✓ 转换成功: {output_file.name}")
            
        except Exception as e:
            print(f"✗ 转换失败: {str(e)}")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    # 转换单个文件 - SCP-3812 新版
    html_file = Path(r"e:\小说\SCP\SCP-3812 - SCP基金会.html")
    output_file = Path(r"e:\小说\SCP_PDF\SCP-3812 - SCP基金会_新版.pdf")
    
    print("=" * 60)
    print("SCP HTML转PDF - Grok优化版")
    print("=" * 60)
    print()
    
    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 运行转换
    asyncio.run(html_to_pdf_grok_optimized(html_file, output_file))
    
    print()
    print("=" * 60)
    print("完成！请将新PDF发给Grok验证。")
    print(f"输出文件: {output_file}")
    print("=" * 60)