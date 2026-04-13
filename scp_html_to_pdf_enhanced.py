#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCP HTML转PDF批量转换脚本（增强版）- Grok优化
使用Playwright实现1:1还原HTML格式
支持智能折叠内容处理 - 优化版本
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright


async def expand_collapsible_content(page):
    """
    展开页面中的所有折叠内容 - Grok优化版
    """
    try:
        print("  彻底展开所有折叠内容...")
        
        # 第一步：点击所有折叠链接
        await page.evaluate("""
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
        
        await asyncio.sleep(1)
        
        # 第二步：强制展开所有内容
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
        
        # 第三步：添加CSS确保打印时显示
        await page.evaluate("""
            () => {
                const style = document.createElement('style');
                style.textContent = `
                    .collapsible-block-folded { display: none !important; }
                    .collapsible-block-unfolded { display: block !important; }
                    .collapsible-block-content { display: block !important; }
                `;
                document.head.appendChild(style);
            }
        """)
        
        await asyncio.sleep(1)
        print("  折叠内容展开完成")
        
    except Exception as e:
        print(f"  展开折叠内容时遇到问题: {str(e)}")


async def html_to_pdf_enhanced(html_file: Path, output_dir: Path, is_scp6183: bool = False):
    """
    将单个HTML文件转换为PDF（增强版）- 最终优化版
    """
    pdf_file = output_dir / f"{html_file.stem}_最终版.pdf"
    
    print(f"正在转换: {html_file.name} -> {pdf_file.name}")
    if is_scp6183:
        print("  (SCP-6183文档，保持折叠状态)")
    else:
        print("  (展开所有折叠内容)")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        page = await browser.new_page(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        try:
            file_url = f"file:///{html_file.absolute().as_posix()}"
            print(f"  正在加载页面: {file_url}")
            
            await page.goto(
                file_url, 
                timeout=60000
            )
            
            print("  等待资源加载...")
            await asyncio.sleep(10)
            
            if not is_scp6183:
                await expand_collapsible_content(page)
            
            # Grok优化：只显示主内容，隐藏其他部分 + 最终优化
            print("  优化页面显示（最终版优化）...")
            await page.evaluate("""
                () => {
                    // 1. 隐藏无关部分
                    const hideSelectors = [
                        '#header', '#top-bar', '#side-bar', '#footer', 
                        '.login-info', '.site-tools', '#breadcrumbs',
                        '.page-tags', '.page-rate-widget-box', '.pagerate',
                        '#action-area-top', '#action-area', '.page-info'
                    ];
                    hideSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            el.style.display = 'none';
                        });
                    });
                    
                    // 2. 最终优化1：隐藏info-container里的作者块（DJK等）
                    const infoContainers = document.querySelectorAll('.info-container');
                    infoContainers.forEach(container => {
                        const text = container.textContent || '';
                        if (text.includes('DJK') || 
                            text.includes('The Based God') || 
                            text.includes('作者的更多作品') ||
                            text.includes('djkaktus')) {
                            container.style.display = 'none';
                            container.style.visibility = 'hidden';
                        }
                    });
                    
                    // 额外：隐藏所有可能的作者签名块
                    document.querySelectorAll('*').forEach(el => {
                        const text = el.textContent || '';
                        if ((text.includes('DJK') || text.includes('djkaktus')) && 
                            (el.classList.contains('info-container') || 
                             el.closest('.info-container'))) {
                            el.style.display = 'none';
                        }
                    });
                    
                    // 3. 最终优化2：移除所有折叠按钮残留文字
                    const unfoldedLinks = document.querySelectorAll('.collapsible-block-unfolded-link');
                    unfoldedLinks.forEach(link => {
                        link.style.display = 'none';
                        link.style.visibility = 'hidden';
                        link.style.height = '0';
                        link.style.margin = '0';
                        link.style.padding = '0';
                    });
                    
                    // 4. 确保主内容区域完全显示
                    const pageContent = document.querySelector('#page-content');
                    if (pageContent) {
                        pageContent.style.margin = '0';
                        pageContent.style.padding = '20px';
                        pageContent.style.maxWidth = 'none';
                    }
                    
                    document.body.style.margin = '0';
                    document.body.style.padding = '0';
                    
                    // 5. 添加打印优化CSS，避免图片/表格中间分页
                    const printStyle = document.createElement('style');
                    printStyle.textContent = `
                        @media print {
                            img, table, .warning-box {
                                page-break-inside: avoid !important;
                            }
                            .collapsible-block-unfolded-link { 
                                display: none !important; 
                            }
                        }
                    `;
                    document.head.appendChild(printStyle);
                }
            """)
            
            await asyncio.sleep(2)
            
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
            
            # 最终优化3：PDF参数 - 0.4cm边距
            print("  正在生成最终版PDF（横向A4，0.4cm边距）...")
            await page.pdf(
                path=pdf_file,
                format="A4",
                landscape=True,
                print_background=True,
                prefer_css_page_size=False,
                margin={
                    "top": "0.4cm",
                    "right": "0.4cm",
                    "bottom": "0.4cm",
                    "left": "0.4cm"
                },
                scale=1.0
            )
            
            print(f"✓ 转换成功: {pdf_file.name}")
            
        except Exception as e:
            print(f"✗ 转换失败 {html_file.name}: {str(e)}")
            raise
        finally:
            await browser.close()


async def convert_single_grok(html_file: Path, output_dir: Path):
    """转换单个文件 - 最终优化版"""
    print("=" * 60)
    print("SCP HTML转PDF - 最终优化版")
    print("=" * 60)
    print(f"源文件: {html_file}")
    print(f"输出目录: {output_dir}")
    print()
    
    output_dir.mkdir(parents=True, exist_ok=True)
    is_scp6183 = "6183" in html_file.name
    
    try:
        await html_to_pdf_enhanced(html_file, output_dir, is_scp6183)
        print()
        print("=" * 60)
        print("✓ 最终版完成！请将新PDF发给Grok做最终验证。")
        output_file = output_dir / f"{html_file.stem}_最终版.pdf"
        print(f"输出文件: {output_file}")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ 转换失败: {str(e)}")
        print("=" * 60)


if __name__ == "__main__":
    html_file = Path(r"e:\小说\SCP\SCP-3812 - SCP基金会.html")
    output_directory = Path(r"e:\小说\SCP_PDF")
    asyncio.run(convert_single_grok(html_file, output_directory))