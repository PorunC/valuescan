"""
TradingView 图表生成模块
使用 chart-img.com API 生成 TradingView 图表图片
"""

import requests
import os
from io import BytesIO
from logger import logger

# 默认配置（将在 config.py 中设置）
DEFAULT_API_KEY = "123456789abcdef0123456789abcdef"
DEFAULT_LAYOUT_ID = "oeTZqtUR"
DEFAULT_CHART_WIDTH = 1200
DEFAULT_CHART_HEIGHT = 800
DEFAULT_TIMEOUT = 90


def generate_tradingview_chart(
    symbol,
    api_key=None,
    layout_id=None,
    width=None,
    height=None,
    timeout=None,
    save_to_file=False,
    output_path=None
):
    """
    生成 TradingView 图表并返回图片数据

    Args:
        symbol: 交易对符号（如 'BTC', 'ETH'）
        api_key: chart-img.com API Key（从 config 读取）
        layout_id: TradingView 布局 ID（从 config 读取）
        width: 图表宽度（像素）
        height: 图表高度（像素）
        timeout: 请求超时时间（秒）
        save_to_file: 是否保存到文件
        output_path: 保存路径（如果 save_to_file=True）

    Returns:
        bytes: 图片数据（PNG 格式），失败返回 None
    """
    # 尝试从 config 加载配置
    try:
        from config import (
            CHART_IMG_API_KEY,
            CHART_IMG_LAYOUT_ID,
            CHART_IMG_WIDTH,
            CHART_IMG_HEIGHT,
            CHART_IMG_TIMEOUT
        )
        api_key = api_key or CHART_IMG_API_KEY
        layout_id = layout_id or CHART_IMG_LAYOUT_ID
        width = width or CHART_IMG_WIDTH
        height = height or CHART_IMG_HEIGHT
        timeout = timeout or CHART_IMG_TIMEOUT
    except ImportError:
        # 如果 config 中没有这些配置，使用默认值
        api_key = api_key or DEFAULT_API_KEY
        layout_id = layout_id or DEFAULT_LAYOUT_ID
        width = width or DEFAULT_CHART_WIDTH
        height = height or DEFAULT_CHART_HEIGHT
        timeout = timeout or DEFAULT_TIMEOUT

    if not api_key or not layout_id:
        logger.error("❌ TradingView 图表配置不完整（缺少 API Key 或 Layout ID）")
        return None

    # 构建 API 请求
    url = f"https://api.chart-img.com/v2/tradingview/layout-chart/{layout_id}"

    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }

    # 标准化交易对符号（币安格式）
    # 移除 $ 符号，统一添加 USDT
    symbol_clean = symbol.upper().replace('$', '').strip()
    if not symbol_clean.endswith('USDT'):
        symbol_clean = f"{symbol_clean}USDT"

    # 优先使用期货符号（永续合约）
    binance_futures_symbol = f"BINANCE:{symbol_clean}.P"
    binance_spot_symbol = f"BINANCE:{symbol_clean}"

    # 尝试生成图表的符号列表（优先期货）
    symbols_to_try = [binance_futures_symbol, binance_spot_symbol]
    
    logger.info(f"📊 正在为 ${symbol.upper().replace('$', '')} 生成 TradingView 图表...")
    
    # 尝试不同的符号格式
    for attempt, binance_symbol in enumerate(symbols_to_try, 1):
        logger.info(f"📊 正在生成 TradingView 图表: {binance_symbol}")
        if attempt > 1:
            logger.info(f"   (尝试备用符号格式 {attempt}/{len(symbols_to_try)})")
        
        payload = {
            'width': width,
            'height': height,
            'format': 'png',
            'symbol': binance_symbol
        }

        logger.debug(f"   API URL: {url}")
        logger.debug(f"   尺寸: {width}x{height}")

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')

                if 'image' in content_type:
                    image_data = response.content
                    size_kb = len(image_data) / 1024
                    logger.info(f"✅ 图表生成成功: {binance_symbol} ({size_kb:.2f} KB)")

                    # 可选：保存到文件
                    if save_to_file and output_path:
                        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(image_data)
                        logger.info(f"💾 图表已保存: {output_path}")

                    return image_data
                else:
                    logger.error(f"❌ 响应类型错误: {content_type}")
                    logger.error(f"   响应内容: {response.text[:500]}")

            elif response.status_code == 403:
                # 尝试解析错误详情
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', '未知 403 错误')
                    logger.error(f"❌ 图表生成失败: 403 Forbidden - {error_msg}")
                    
                    if "Resolution Limit" in error_msg:
                        logger.error(f"   原因: API 分辨率限制，当前请求 {width}x{height}")
                        logger.error(f"   解决方案: 降低图表分辨率到允许范围内")
                        return None  # 分辨率问题不需要尝试其他符号
                    elif "layout" in error_msg.lower():
                        logger.error(f"   可能原因: TradingView 布局未公开分享")
                        logger.error(f"   解决方案:")
                        logger.error(f"   1. 访问: https://www.tradingview.com/chart/{layout_id}/")
                        logger.error(f"   2. 点击右上角 '分享' 按钮")
                        logger.error(f"   3. 选择 'Make chart public' 或启用 'Anyone with the link can view'")
                        return None  # 布局问题不需要尝试其他符号
                    else:
                        logger.error(f"   详细错误: {error_msg}")
                except:
                    # 无法解析 JSON，使用原始文本
                    logger.error(f"❌ 图表生成失败: 403 Forbidden")
                    logger.error(f"   响应内容: {response.text[:200]}")

            elif response.status_code == 422:
                # Invalid Symbol - 尝试下一个符号格式
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Invalid Symbol')
                    if attempt < len(symbols_to_try):
                        logger.warning(f"⚠️ 符号无效: {binance_symbol} - {error_msg}，尝试备用格式...")
                        continue  # 尝试下一个符号
                    else:
                        logger.error(f"❌ 所有符号格式都无效: {error_msg}")
                except:
                    if attempt < len(symbols_to_try):
                        logger.warning(f"⚠️ 符号无效: {binance_symbol}，尝试备用格式...")
                        continue
                    else:
                        logger.error(f"❌ 所有符号格式都无效: {response.text[:200]}")

            else:
                logger.error(f"❌ 图表生成失败: HTTP {response.status_code}")
                logger.error(f"   响应: {response.text[:500]}")
                if attempt < len(symbols_to_try):
                    continue  # 尝试下一个符号

        except requests.exceptions.Timeout:
            logger.error(f"❌ 图表生成超时 ({timeout}s)")
            return None

        except requests.exceptions.ConnectionError:
            logger.error(f"❌ 网络连接失败，无法访问 chart-img.com")
            return None

        except Exception as e:
            logger.exception(f"❌ 图表生成异常: {e}")
            return None
    
    # 所有符号格式都尝试失败
    logger.error(f"❌ 无法为 ${symbol.upper().replace('$', '')} 生成图表（已尝试期货和现货符号）")
    return None


def test_chart_generation(symbol='BTC'):
    """
    测试图表生成功能

    Args:
        symbol: 测试的交易对符号

    Returns:
        bool: 测试成功返回 True
    """
    logger.info(f"🧪 测试图表生成: ${symbol}")

    image_data = generate_tradingview_chart(
        symbol=symbol,
        save_to_file=True,
        output_path=f"output/test_chart_{symbol}.png"
    )

    if image_data:
        logger.info(f"✅ 测试成功！图片大小: {len(image_data) / 1024:.2f} KB")
        return True
    else:
        logger.error(f"❌ 测试失败")
        return False


if __name__ == '__main__':
    # 测试代码
    print("=" * 80)
    print("TradingView 图表生成器测试")
    print("=" * 80)

    # 测试几个常见交易对
    test_symbols = ['BTC', 'ETH', 'SOL']

    for symbol in test_symbols:
        print(f"\n测试 {symbol}...")
        success = test_chart_generation(symbol)
        print(f"结果: {'✅ 成功' if success else '❌ 失败'}")

    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)
