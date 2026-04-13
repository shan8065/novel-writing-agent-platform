#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCP HTML转PDF - Grok优化版（基于原有成功脚本）
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
        await page.evaluate("""
            () => {
                let clickCount = 0;
                const links = document.querySelectorAll('.collapsible-block-folded .collapsible-block-link');
                links.forEach(link => {
                    try { link.click(); clickCount++; } catch(e) {}
                });
                return clickCount;
            }
        """)
        
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
                `;
                document.head.appendChild(style);
            }
        """)
        
        await asyncio.sleep(2)
        print("  折叠内容展开完成！")
        
    except Exception as e:
        print(f"  展开折叠内容时遇到问题: {str(e)}")


async def html_to_pdf_final(html_file: Path, output_file: Path):
    """
    将HTML文件转换为PDF - 最终优化版
    """
    pdf_file = output_file
    
    print(f"正在转换: {html_file.name} -> {pdf_file.name}")
    print("  (展开所有折叠内容)")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--allow-file-access-from-files'
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
            
            # 使用之前工作的方式
            await page.goto(
                file_url, 
                wait_until="networkidle", 
                timeout=120000
            )
            
            print("  等待资源加载...")
            await asyncio.sleep(5)
            
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
                    
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    document.body.style.background = '#fff';
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
                path=pdf_file,
                format="A4",
                landscape=True,
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
            
            print(f"✓ 转换成功: {pdf_file.name}")
            
        except Exception as e:
            print(f"✗ 转换失败 {html_file.name}: {str(e)}")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    html_file = Path(r"e:\小说\SCP\SCP-3812 - SCP基金会.html")
    output_file = Path(r"e:\小说\SCP_PDF\SCP-3812 - SCP基金会_新版.pdf")
    
    print("=" * 60)
    print("SCP HTML转PDF - Grok优化版（基于成功脚本）")
    print("=" * 60)
    print()
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    asyncio.run(html_to_pdf_final(html_file, output_file))
    
    print()
    print("=" * 60)
    print("完成！请将新PDF发给Grok验证。")
    print(f"输出文件: {output_file}")
    print("=" * 60)