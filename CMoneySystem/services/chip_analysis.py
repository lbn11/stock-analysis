"""筹码分布分析模块

筹码分布（Chip Distribution）是技术分析中的重要指标，用于分析不同价格区间的
持仓成本分布情况，从而判断支撑位和压力位。

核心概念：
- 筹码：指投资者的持仓成本
- 筹码分布：不同价格区间的持仓数量分布
- 筹码集中度：筹码在特定价格区间的集中程度
- 筹码转移：筹码从低价区向高价区或相反方向的流动
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import numpy as np

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("pandas not installed. Install with: pip install pandas")


class ChipDistributionAnalyzer:
    """筹码分布分析器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 分析参数
        self.price_bins = 100  # 价格区间数量
        self.min_volume_threshold = 0  # 最小成交量阈值

    def calculate_chip_distribution(self, historical_data: List[Dict[str, Any]],
                                    price_range: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        计算筹码分布

        Args:
            historical_data: 历史数据列表
                [{"date": "2024-01-01", "open": 10.0, "close": 11.0, "high": 11.5, "low": 9.5, "volume": 1000000}, ...]
            price_range: 价格区间 (min_price, max_price)，None 表示自动计算

        Returns:
            筹码分布数据
        """
        if not PANDAS_AVAILABLE:
            self.logger.error("pandas not available")
            return {}

        if not historical_data:
            self.logger.warning("No historical data provided")
            return {}

        try:
            # 转换为 DataFrame
            df = pd.DataFrame(historical_data)

            # 确保有必要的列
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    self.logger.error(f"Missing required column: {col}")
                    return {}

            # 计算价格区间
            if price_range is None:
                min_price = df['low'].min()
                max_price = df['high'].max()
            else:
                min_price, max_price = price_range

            # 创建价格区间
            price_bins = np.linspace(min_price, max_price, self.price_bins + 1)
            bin_centers = (price_bins[:-1] + price_bins[1:]) / 2

            # 初始化筹码分布数组
            chip_distribution = np.zeros(self.price_bins)

            # 计算每日的筹码分布
            for _, row in df.iterrows():
                high = row['high']
                low = row['low']
                close = row['close']
                volume = row['volume']

                # 假设成交均匀分布在高低价之间
                # 计算每个价格区间的筹码贡献
                for i in range(self.price_bins):
                    bin_low = price_bins[i]
                    bin_high = price_bins[i + 1]

                    # 计算该价格区间与当日价格区间的重叠部分
                    overlap_low = max(low, bin_low)
                    overlap_high = min(high, bin_high)

                    if overlap_high > overlap_low:
                        # 重叠比例
                        overlap_ratio = (overlap_high - overlap_low) / (high - low) if high > low else 1

                        # 筹码贡献 = 成交量 * 重叠比例
                        chip_contribution = volume * overlap_ratio
                        chip_distribution[i] += chip_contribution

            # 计算统计数据
            total_chips = chip_distribution.sum()

            # 找到筹码集中区域（筹码最多的区域）
            max_chip_idx = np.argmax(chip_distribution)
            peak_price = bin_centers[max_chip_idx]
            peak_chips = chip_distribution[max_chip_idx]

            # 计算筹码集中度
            concentration_ratio = peak_chips / total_chips if total_chips > 0 else 0

            # 计算加权平均价格（筹码重心）
            weighted_avg_price = np.sum(bin_centers * chip_distribution) / total_chips if total_chips > 0 else 0

            # 找到支撑位和压力位
            # 支撑位：下方筹码密集区域
            # 压力位：上方筹码密集区域
            support_level, pressure_level = self._find_support_pressure(
                bin_centers, chip_distribution, weighted_avg_price
            )

            return {
                'price_bins': price_bins.tolist(),
                'bin_centers': bin_centers.tolist(),
                'chip_distribution': chip_distribution.tolist(),
                'total_chips': float(total_chips),
                'peak_price': float(peak_price),
                'peak_chips': float(peak_chips),
                'concentration_ratio': float(concentration_ratio),
                'weighted_avg_price': float(weighted_avg_price),
                'support_level': float(support_level),
                'pressure_level': float(pressure_level),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error calculating chip distribution: {e}")
            return {}

    def _find_support_pressure(self, price_centers: np.ndarray,
                              chip_distribution: np.ndarray,
                              current_price: float) -> Tuple[float, float]:
        """
        识别支撑位和压力位

        Args:
            price_centers: 价格中心点数组
            chip_distribution: 筹码分布数组
            current_price: 当前价格

        Returns:
            (支撑位, 压力位)
        """
        # 找到当前价格所在的区间
        current_idx = np.argmin(np.abs(price_centers - current_price))

        # 支撑位：当前价格下方的筹码密集区
        support_chips = chip_distribution[:current_idx]
        if len(support_chips) > 0:
            support_idx = np.argmax(support_chips)
            support_level = float(price_centers[support_idx])
        else:
            support_level = 0.0

        # 压力位：当前价格上方的筹码密集区
        pressure_chips = chip_distribution[current_idx:]
        if len(pressure_chips) > 0:
            pressure_idx = current_idx + np.argmax(pressure_chips)
            pressure_level = float(price_centers[pressure_idx])
        else:
            pressure_level = 0.0

        return support_level, pressure_level

    def analyze_chip_movement(self, historical_data_list: List[List[Dict[str, Any]]],
                             period_days: int = 5) -> Dict[str, Any]:
        """
        分析筹码移动情况

        Args:
            historical_data_list: 多个时期的历史数据列表
                [period1_data, period2_data, ...]
            period_days: 每个时期的天数

        Returns:
            筹码移动分析结果
        """
        if len(historical_data_list) < 2:
            self.logger.warning("Need at least 2 periods to analyze chip movement")
            return {}

        try:
            # 计算每个时期的筹码分布
            distributions = []
            for i, data in enumerate(historical_data_list):
                dist = self.calculate_chip_distribution(data)
                dist['period'] = i
                distributions.append(dist)

            # 比较筹码分布的变化
            movement_analysis = {
                'periods': len(distributions),
                'period_days': period_days,
                'movements': []
            }

            for i in range(len(distributions) - 1):
                current = distributions[i]
                next_dist = distributions[i + 1]

                # 比较筹码重心的移动
                price_change = next_dist['weighted_avg_price'] - current['weighted_avg_price']
                price_change_pct = (price_change / current['weighted_avg_price'] * 100) if current['weighted_avg_price'] > 0 else 0

                # 比较集中度变化
                concentration_change = next_dist['concentration_ratio'] - current['concentration_ratio']

                # 判断筹码移动方向
                if price_change > 0:
                    direction = 'up'
                elif price_change < 0:
                    direction = 'down'
                else:
                    direction = 'stable'

                movement_analysis['movements'].append({
                    'from_period': i,
                    'to_period': i + 1,
                    'price_change': float(price_change),
                    'price_change_pct': float(price_change_pct),
                    'concentration_change': float(concentration_change),
                    'direction': direction
                })

            return movement_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing chip movement: {e}")
            return {}

    def get_chip_signals(self, chip_data: Dict[str, Any], current_price: float) -> Dict[str, Any]:
        """
        根据筹码分布生成交易信号

        Args:
            chip_data: 筹码分布数据
            current_price: 当前价格

        Returns:
            交易信号
        """
        if not chip_data:
            return {'signal': 'neutral', 'strength': 0}

        try:
            weighted_avg_price = chip_data.get('weighted_avg_price', 0)
            support_level = chip_data.get('support_level', 0)
            pressure_level = chip_data.get('pressure_level', 0)
            concentration_ratio = chip_data.get('concentration_ratio', 0)

            # 信号强度计算
            signal_strength = 0
            reasons = []

            # 1. 当前价格与筹码重心的关系
            if current_price > weighted_avg_price:
                # 价格在筹码重心上方，偏多头
                signal_strength += 1
                reasons.append('price_above_center')
            elif current_price < weighted_avg_price:
                # 价格在筹码重心下方，偏空头
                signal_strength -= 1
                reasons.append('price_below_center')

            # 2. 筹码集中度
            if concentration_ratio > 0.3:
                # 高集中度，说明筹码集中，可能有突破
                signal_strength += 0.5 if current_price > weighted_avg_price else -0.5
                reasons.append('high_concentration')

            # 3. 支撑位和压力位
            if current_price <= support_level * 1.02:  # 在支撑位附近
                signal_strength += 1
                reasons.append('near_support')

            if current_price >= pressure_level * 0.98:  # 在压力位附近
                signal_strength -= 1
                reasons.append('near_pressure')

            # 判断最终信号
            if signal_strength >= 1.5:
                signal = 'strong_buy'
            elif signal_strength >= 0.5:
                signal = 'buy'
            elif signal_strength <= -1.5:
                signal = 'strong_sell'
            elif signal_strength <= -0.5:
                signal = 'sell'
            else:
                signal = 'neutral'

            return {
                'signal': signal,
                'strength': float(signal_strength),
                'reasons': reasons,
                'weighted_avg_price': float(weighted_avg_price),
                'support_level': float(support_level),
                'pressure_level': float(pressure_level),
                'concentration_ratio': float(concentration_ratio)
            }

        except Exception as e:
            self.logger.error(f"Error generating chip signals: {e}")
            return {'signal': 'neutral', 'strength': 0}

    def calculate_chip_turnover(self, historical_data: List[Dict[str, Any]],
                               days: int = 20) -> Dict[str, Any]:
        """
        计算筹码换手率

        Args:
            historical_data: 历史数据
            days: 计算周期

        Returns:
            换手率数据
        """
        if not PANDAS_AVAILABLE:
            return {}

        try:
            df = pd.DataFrame(historical_data)

            if 'volume' not in df.columns or 'turnover' not in df.columns:
                self.logger.error("Missing volume or turnover column")
                return {}

            # 计算最近 days 天的换手率
            recent_df = df.tail(days)

            if len(recent_df) < days:
                self.logger.warning(f"Only {len(recent_df)} days data available, less than {days}")

            total_volume = recent_df['volume'].sum()
            total_turnover = recent_df['turnover'].sum()

            # 计算平均日换手率
            avg_daily_turnover_ratio = total_turnover / len(recent_df) if len(recent_df) > 0 else 0

            # 计算换手率（简化版，实际需要流通股本数据）
            # 这里假设流通股本为总成交额/换手率
            estimated_float_shares = total_turnover / (avg_daily_turnover_ratio * 100) if avg_daily_turnover_ratio > 0 else 0

            # 计算筹码换手率（一定时间内筹码的换手程度）
            chip_turnover_rate = min(total_turnover / estimated_float_shares * 100, 100) if estimated_float_shares > 0 else 0

            return {
                'period_days': days,
                'total_volume': float(total_volume),
                'total_turnover': float(total_turnover),
                'avg_daily_turnover_ratio': float(avg_daily_turnover_ratio),
                'chip_turnover_rate': float(chip_turnover_rate),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error calculating chip turnover: {e}")
            return {}

    def analyze_chip_distribution_complete(self, stock_code: str,
                                          historical_data: List[Dict[str, Any]],
                                          current_price: float) -> Dict[str, Any]:
        """
        完整的筹码分布分析

        Args:
            stock_code: 股票代码
            historical_data: 历史数据
            current_price: 当前价格

        Returns:
            完整的分析结果
        """
        # 计算筹码分布
        chip_dist = self.calculate_chip_distribution(historical_data)

        # 生成交易信号
        signals = self.get_chip_signals(chip_dist, current_price)

        # 计算换手率
        turnover = self.calculate_chip_turnover(historical_data)

        return {
            'stock_code': stock_code,
            'chip_distribution': chip_dist,
            'signals': signals,
            'turnover': turnover,
            'timestamp': datetime.now().isoformat()
        }

    def format_chip_analysis_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        格式化筹码分析报告

        Args:
            analysis_result: 分析结果

        Returns:
            格式化的报告文本
        """
        if not analysis_result:
            return "无法生成筹码分析报告"

        try:
            chip_dist = analysis_result.get('chip_distribution', {})
            signals = analysis_result.get('signals', {})
            turnover = analysis_result.get('turnover', {})

            report = f"""
=== 筹码分布分析报告 ===

股票代码: {analysis_result.get('stock_code', 'N/A')}
分析时间: {analysis_result.get('timestamp', 'N/A')}

--- 筹码分布情况 ---
筹码重心价格: {chip_dist.get('weighted_avg_price', 0):.2f} 元
筹码峰位价格: {chip_dist.get('peak_price', 0):.2f} 元
筹码集中度: {chip_dist.get('concentration_ratio', 0) * 100:.2f}%
支撑位: {chip_dist.get('support_level', 0):.2f} 元
压力位: {chip_dist.get('pressure_level', 0):.2f} 元

--- 交易信号 ---
信号: {signals.get('signal', 'neutral')}
信号强度: {signals.get('strength', 0):.2f}
信号依据: {', '.join(signals.get('reasons', []))}

--- 换手率分析 ---
周期: {turnover.get('period_days', 0)} 天
筹码换手率: {turnover.get('chip_turnover_rate', 0):.2f}%

--- 分析结论 ---
"""

            # 添加分析结论
            signal = signals.get('signal', 'neutral')
            if signal in ['strong_buy', 'buy']:
                report += "筹码分布偏向多头，建议关注买入机会。"
            elif signal in ['strong_sell', 'sell']:
                report += "筹码分布偏向空头，建议谨慎或考虑减仓。"
            else:
                report += "筹码分布相对平衡，建议观望。"

            # 添加风险提示
            concentration = chip_dist.get('concentration_ratio', 0)
            if concentration > 0.4:
                report += "\n\n注意：筹码高度集中，价格波动可能加剧。"

            return report

        except Exception as e:
            self.logger.error(f"Error formatting report: {e}")
            return "报告生成失败"
