import matplotlib.pyplot as plt
import pandas as pd
import operator
from trading_2.testing.trade import Trade
from trading_2.testing.trade_settings import TradeSetting


class TestService(TradeSetting):
    total_results: list[dict] = []

    def _calc_percent(self, open_price, close_price, direction: str) -> float:
        delta = close_price - open_price if direction == "buy" else open_price - close_price
        return 100 * delta / open_price

    def calc_trade_result(self, row: pd.Series, direction: str, trade: Trade, *args, **kwargs) -> None:
        fee = trade.maker_fee + trade.taker_fee
        exit_prices = {
            "stop": trade.stop_price,
            "profit": trade.profit_price,
            "change_direction": trade.change_direction_price,
            "close_by_market": trade.close_by_market_price,
            "close_by_time": trade.close_by_time_price
        }

        exit_price = exit_prices.get(trade.exit_type)
        if exit_price is None:
            print(f"❌ Неизвестный тип выхода: {trade.exit_type}")
            return

        result_percent = self._calc_percent(trade.open_price, exit_price, direction)

        trade_result = {
            "enter_date": trade.enter_date,
            "exit_date": row.name,
            "result_percent": 2 * result_percent - 2 * fee if trade.added_position else result_percent - fee,
            "direction": direction,
            "enter_price": trade.open_price,
            "exit_price": exit_price,
            "exit_type": trade.exit_type,
            "trade_id": trade.id,
            "day_id": trade.day_id,
            "impulse_id": trade.impulse_id,
            "weekday_1d": trade.weekday_1d,
            "added_position": trade.added_position
        }

        self.add_trade_result(trade_result)

    def add_trade_result(self, trade_result: dict) -> None:
        self.total_results.append(trade_result)

    def _apply_filters(self, df: pd.DataFrame, condition: dict) -> pd.DataFrame:
        ops = {
            "eq": operator.eq,
            "ne": operator.ne,
            "lt": operator.lt,
            "lte": operator.le,
            "gt": operator.gt,
            "gte": operator.ge,
            "between": lambda s, val: s.between(val[0], val[1]),
            "in": lambda s, val: s.isin(val),
        }

        for key, val in condition.items():
            if isinstance(val, dict) and "op" in val and "value" in val:
                op_func = ops.get(val["op"])
                if op_func:
                    try:
                        df = df[op_func(df[key], val["value"])]
                    except Exception as e:
                        print(f"⚠️ Ошибка при фильтрации {key} {val}: {e}")
                else:
                    print(f"⚠️ Неизвестный оператор: {val['op']}")
            else:
                df = df[df[key] == val]
        return df

    def _build_stats_text(self, df: pd.DataFrame) -> str:
        df = df.sort_values("enter_date").copy()
        df["cumulative_total"] = df["result_percent"].cumsum()
        total_trades = len(df)
        final_cumulative = float(df["cumulative_total"].iloc[-1])
        running_max = df["cumulative_total"].cummax()
        drawdown = df["cumulative_total"] - running_max
        max_drawdown = float(drawdown.min())
        fv = abs(final_cumulative / max_drawdown) if max_drawdown != 0 else 0

        return (
            f"📈 Сделок: {total_trades} | "
            f"Итог: {final_cumulative:.2f}% | "
            f"Макс. просадка: {max_drawdown:.2f}% | "
            f"FV: {fv:.2f}"
        )

    def _plot_curve(self, df: pd.DataFrame, label: str, linestyle="--", color=None, bold=False):
        df = df.sort_values("exit_date").copy()
        df["cumulative_result"] = df["result_percent"].cumsum()
        plt.plot(df["exit_date"], df["cumulative_result"], label=label,
                 linestyle=linestyle, color=color,
                 linewidth=2 if bold else 1)

    def plot_cumulative_results(self, filter_conditions: list[dict] = None, show_individual: bool = True) -> None:
        df = pd.DataFrame(self.total_results)

        if df.empty or not {"direction", "exit_date", "result_percent", "trade_id"}.issubset(df.columns):
            print("❗ Недостаточно данных для построения графика.")
            return

        plt.figure(figsize=(12, 6))

        if not filter_conditions:
            for direction, group in df.groupby("direction"):
                self._plot_curve(group, f"{direction} cumulative")

            self._plot_curve(df, "total cumulative", linestyle="-", color="black", bold=True)
            stats_text = self._build_stats_text(df)
        else:
            combined_df = pd.DataFrame()

            for condition in filter_conditions:
                filtered = self._apply_filters(df.copy(), condition)

                if filtered.empty:
                    print(f"⚠️ Нет данных для фильтра {condition}")
                    continue

                label = ", ".join(
                    f"{k}={v if not isinstance(v, dict) else v['op'] + str(v['value'])}"
                    for k, v in condition.items()
                )

                if show_individual:
                    self._plot_curve(filtered, label)

                combined_df = pd.concat([combined_df, filtered])

            if combined_df.empty:
                print("⚠️ Все фильтры вернули пустые выборки.")
                return

            self._plot_curve(combined_df, "total selected cumulative", linestyle="-", color="black", bold=True)
            stats_text = self._build_stats_text(combined_df)

        # Статистика на графике
        plt.annotate(
            stats_text,
            xy=(0.01, 0.01),
            xycoords="axes fraction",
            fontsize=10,
            color="darkblue",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
        )

        plt.title("Кумулятивная доходность по выбранным сегментам")
        plt.xlabel("Дата выхода из сделки")
        plt.ylabel("Накопленная доходность (%)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
