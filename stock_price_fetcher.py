import requests
import argparse
from datetime import datetime

def fetch_stock_info(stock_code):
    """
    获取指定股票的行情信息
    
    参数:
    stock_code (str): 股票代码，如 sh601006 或 sz000001
    
    返回:
    dict: 包含股票信息的字典，如果出错则返回空字典
    """
    # 验证股票代码格式
    if not (stock_code.startswith('sh') or stock_code.startswith('sz')):
        print("错误: 股票代码必须以 'sh' (沪市) 或 'sz' (深市) 开头")
        return {}
    
    url = f"http://hq.sinajs.cn/list={stock_code}"
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析返回的数据
        data = response.text.strip()
        if not data.startswith(f"var hq_str_{stock_code}="):
            print("错误: 返回数据格式不符合预期")
            return {}
        
        # 提取等号后的内容并去掉引号
        stock_info = data.split('=')[1].strip('"').split(',')
        
        # 定义返回数据的字段
        fields = [
            '股票名称', '今日开盘价', '昨日收盘价', '当前价格', '今日最高价', 
            '今日最低价', '竞买价', '竞卖价', '成交股数', '成交金额', 
            '买一数量', '买一价格', '买二数量', '买二价格', '买三数量', 
            '买三价格', '买四数量', '买四价格', '买五数量', '买五价格', 
            '卖一数量', '卖一价格', '卖二数量', '卖二价格', '卖三数量', 
            '卖三价格', '卖四数量', '卖四价格', '卖五数量', '卖五价格', 
            '日期', '时间'
        ]
        
        # 构建结果字典
        result = dict(zip(fields, stock_info))
        
        # 转换数值类型
        for key in ['今日开盘价', '昨日收盘价', '当前价格', '今日最高价', '今日最低价']:
            if key in result:
                try:
                    result[key] = float(result[key])
                except ValueError:
                    pass
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return {}
    except Exception as e:
        print(f"发生未知错误: {e}")
        return {}

def display_stock_info(stock_info, brief=False):
    """
    格式化显示股票信息
    
    参数:
    stock_info (dict): 包含股票信息的字典
    brief (bool): 是否简洁显示，默认为False
    """
    if not stock_info:
        print("没有获取到股票信息")
        return
    
    # 计算涨跌幅
    if '当前价格' in stock_info and '昨日收盘价' in stock_info:
        current_price = stock_info['当前价格']
        prev_close = stock_info['昨日收盘价']
        if prev_close != 0:
            change_amount = current_price - prev_close
            change_percent = (change_amount / prev_close) * 100
            stock_info['涨跌额'] = change_amount
            stock_info['涨跌幅'] = f"{change_percent:.2f}%"
    
    if brief:
        # 简洁模式：一行显示股票名称、当前价格、涨跌幅
        sign = '+' if stock_info.get('涨跌额', 0) >= 0 else ''
        print(f"{stock_info['股票名称']}: {stock_info['当前价格']:.2f} {sign}{stock_info.get('涨跌幅', '0.00%')}")
        return
    
    # 详细模式（原有显示逻辑）
    print(f"\n{stock_info['股票名称']} ({stock_info.get('股票代码', '')})")
    print(f"日期: {stock_info['日期']} {stock_info['时间']}")
    print("-" * 50)
    
    # 显示主要价格信息
    print(f"当前价格: {stock_info['当前价格']:.2f}")
    print(f"今日开盘: {stock_info['今日开盘价']:.2f}")
    print(f"昨日收盘: {stock_info['昨日收盘价']:.2f}")
    print(f"今日最高: {stock_info['今日最高价']:.2f}")
    print(f"今日最低: {stock_info['今日最低价']:.2f}")
    
    # 显示涨跌幅
    if '涨跌额' in stock_info:
        sign = '+' if stock_info['涨跌额'] >= 0 else ''
        print(f"涨跌额: {sign}{stock_info['涨跌额']:.2f}")
        print(f"涨跌幅: {sign}{stock_info['涨跌幅']}")
    
    print("-" * 50)
    
    # 显示买卖盘信息
    print("买盘信息:")
    for i in range(1, 6):
        buy_quantity = stock_info.get(f'买{i}数量', '')
        buy_price = stock_info.get(f'买{i}价格', '')
        if buy_quantity and buy_price:
            print(f"买{i}: {int(buy_quantity):,}股 @ {float(buy_price):.2f}")
    
    print("\n卖盘信息:")
    for i in range(1, 6):
        sell_quantity = stock_info.get(f'卖{i}数量', '')
        sell_price = stock_info.get(f'卖{i}价格', '')
        if sell_quantity and sell_price:
            print(f"卖{i}: {int(sell_quantity):,}股 @ {float(sell_price):.2f}")

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='获取股票行情信息')
    parser.add_argument('stock_codes', type=str, nargs='?', help='股票代码，支持单个或多个代码（用逗号分隔），例如: sh601006 或 sh601006,sz000001')
    parser.add_argument('--brief', '-b', action='store_true', help='简洁模式：仅显示股票名称、当前价格、涨跌幅')
    parser.add_argument('--file', '-f', type=str, help='从文件读取股票代码列表，每行一个代码')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理股票代码输入
    stock_code_list = []
    
    if args.file:
        # 从文件读取股票代码
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                for line in f:
                    code = line.strip()
                    if code and not code.startswith('#'):  # 跳过空行和注释行
                        stock_code_list.append(code)
        except FileNotFoundError:
            print(f"错误: 文件 {args.file} 不存在")
            exit(1)
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
            exit(1)
    elif args.stock_codes:
        # 从命令行参数读取股票代码
        stock_code_list = [code.strip() for code in args.stock_codes.split(',')]
    else:
        print("错误: 必须提供股票代码或文件路径")
        parser.print_help()
        exit(1)
    
    # 获取并显示股票信息
    for stock_code in stock_code_list:
        stock_info = fetch_stock_info(stock_code)
        display_stock_info(stock_info, brief=args.brief)
        if not args.brief:
            print("\n" + "="*60 + "\n")