# 股票行情获取工具

这是一个简单的股票行情获取工具，可以通过命令行获取指定股票的实时行情信息。

## 功能特点
- 获取沪市和深市股票的实时行情信息
- 显示股票基本信息、价格信息、买卖盘信息
- 计算并显示股票的涨跌额和涨跌幅

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法
```bash
python stock_price_fetcher.py <股票代码>
```

示例：
```bash
python stock_price_fetcher.py sh601006
```

## 股票代码格式
- 沪市股票：以 `sh` 开头，如 `sh601006`
- 深市股票：以 `sz` 开头，如 `sz000001`