"""
Qlib 数据管理模块

实现 A 股数据的加载、获取和预处理功能。
支持 qlib 内置数据源和 AKShare 等外部数据源。
"""

import logging
from pathlib import Path
from typing import Optional, Union
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from ..config import config
from ..utils import setup_logger, parse_date, format_stock_code

logger = setup_logger(__name__)


class QlibDataManager:
    """
    Qlib 数据管理器
    
    负责 A 股数据的加载、获取和预处理。
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初始化数据管理器
        
        Args:
            data_dir: qlib 数据目录路径，默认使用配置中的路径
        """
        self.data_dir = Path(data_dir or config.QLIB_DATA_DIR)
        self.qlib_initialized = False
        
        # 确保数据目录存在
        config.ensure_dirs()
        
        logger.info(f"QlibDataManager 初始化完成，数据目录：{self.data_dir}")
    
    def init_qlib(self):
        """
        初始化 qlib 环境
        
        注意：qlib 需要在有数据的目录下初始化
        """
        if self.qlib_initialized:
            logger.debug("Qlib 已初始化，跳过")
            return
        
        try:
            import qlib
            from qlib.config import REG_CN
            
            # 初始化 qlib
            qlib.init(
                provider_uri=str(self.data_dir),
                region=REG_CN,
            )
            
            self.qlib_initialized = True
            logger.info("Qlib 初始化成功")
            
        except ImportError:
            logger.warning("qlib 未安装，将使用备用数据源")
            self.qlib_initialized = False
        except Exception as e:
            logger.warning(f"qlib 初始化失败：{e}，将使用备用数据源")
            self.qlib_initialized = False
    
    def get_stock_data(
        self,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        fields: Optional[list[str]] = None,
        use_qlib: bool = True
    ) -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码 (如 "000001.SZ" 或 "000001")
            start_date: 开始日期
            end_date: 结束日期
            fields: 需要的字段列表，默认包含开盘价、收盘价、最高价、最低价、成交量
            use_qlib: 是否使用 qlib 数据源，失败时自动切换到备用源
            
        Returns:
            包含股票数据的 DataFrame
        """
        symbol = format_stock_code(symbol)
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        # 默认字段
        if fields is None:
            fields = ["$open", "$close", "$high", "$low", "$volume", "$factor"]
        
        # 尝试使用 qlib
        if use_qlib and self.qlib_initialized:
            try:
                data = self._get_data_from_qlib(symbol, start, end, fields)
                if data is not None and not data.empty:
                    logger.info(f"从 qlib 获取 {symbol} 数据成功，共 {len(data)} 条记录")
                    return data
            except Exception as e:
                logger.warning(f"从 qlib 获取数据失败：{e}，尝试备用数据源")
        
        # 使用备用数据源 (AKShare)
        logger.info(f"使用备用数据源获取 {symbol} 数据")
        return self._get_data_from_akshare(symbol, start, end)
    
    def _get_data_from_qlib(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        fields: list[str]
    ) -> Optional[pd.DataFrame]:
        """
        从 qlib 获取数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            fields: 字段列表
            
        Returns:
            股票数据 DataFrame
        """
        from qlib.data import D
        
        # qlib 使用 instrument 表达式
        instrument = symbol
        
        df = D.features(
            [instrument],
            fields,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )
        
        if df is None or df.empty:
            return None
        
        # 重置索引，将 date 作为列
        df = df.reset_index()
        df.columns = ["datetime"] + [col.replace("$", "") for col in fields]
        df.set_index("datetime", inplace=True)
        
        return df
    
    def _get_data_from_akshare(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        从 AKShare 获取 A 股数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票数据 DataFrame
        """
        try:
            import akshare as ak
        except ImportError:
            logger.error("AKShare 未安装，请运行：pip install akshare")
            return pd.DataFrame()
        
        # 提取纯数字代码
        code = symbol.split(".")[0]
        
        try:
            # 获取历史行情
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                logger.warning(f"AKShare 未返回 {symbol} 的数据")
                return pd.DataFrame()
            
            # 重命名列以匹配 qlib 格式
            column_mapping = {
                "日期": "datetime",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "振幅": "amplitude",
                "涨跌幅": "pct_change",
                "涨跌额": "change",
                "换手率": "turnover"
            }
            
            df = df.rename(columns=column_mapping)
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)
            
            logger.info(f"从 AKShare 获取 {symbol} 数据成功，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"从 AKShare 获取数据失败：{e}")
            return pd.DataFrame()
    
    def get_index_data(
        self,
        index_code: str = "000001.SH",
        start_date: Optional[Union[str, datetime]] = None,
        end_date: Optional[Union[str, datetime]] = None
    ) -> pd.DataFrame:
        """
        获取指数数据
        
        Args:
            index_code: 指数代码，默认上证指数
            start_date: 开始日期，默认过去 1 年
            end_date: 结束日期，默认今天
            
        Returns:
            指数数据 DataFrame
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        
        return self.get_stock_data(index_code, start_date, end_date)
    
    def download_qlib_data(self, region: str = "cn"):
        """
        下载 qlib 数据
        
        注意：这会下载大量数据，需要较长时间和存储空间
        
        Args:
            region: 市场区域，"cn" 表示中国
        """
        logger.info(f"开始下载 qlib {region} 市场数据...")
        logger.warning("此操作可能需要较长时间和大量存储空间")
        
        try:
            # 使用 qlib 的数据下载脚本
            import subprocess
            
            cmd = [
                "python", "-m", "qlib.run.get_data",
                "--qlib_data_1d_dir", str(self.data_dir),
                "--region", region
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("qlib 数据下载完成")
            else:
                logger.error(f"qlib 数据下载失败：{result.stderr}")
                
        except Exception as e:
            logger.error(f"下载 qlib 数据时出错：{e}")
    
    def cache_data(self, df: pd.DataFrame, symbol: str):
        """
        缓存数据到本地
        
        Args:
            df: 要缓存的 DataFrame
            symbol: 股票代码
        """
        cache_file = self.data_dir / "cache" / f"{symbol.replace('.', '_')}.csv"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(cache_file)
        logger.debug(f"数据已缓存到：{cache_file}")
    
    def load_cached_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        加载缓存的数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            缓存的 DataFrame，如果不存在则返回 None
        """
        cache_file = self.data_dir / "cache" / f"{symbol.replace('.', '_')}.csv"
        
        if cache_file.exists():
            df = pd.read_csv(cache_file, index_col="datetime", parse_dates=True)
            logger.debug(f"已加载缓存数据：{cache_file}")
            return df
        
        return None


# 全局数据管理器实例
data_manager = QlibDataManager()
