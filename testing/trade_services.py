from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd


class TradeSetting:
    stop_size: float = 2.0
    profit_size: float = 4.0
    delay_period: int = 24 # hours amount


class Trade(TradeSetting):
    def __init__(self, row: pd.Series, direction: str):
        self.id = 1
        self.enter_date = row.name
        self.open_price = row["close_4h"]
        self.end_delay_period = pd.Timestamp(row.name) + timedelta(hours=self.delay_period)
        self.stop_price = self.open_price * (1 - (self.stop_size / 100)) if direction == "buy" \
            else self.open_price * (1 + (self.stop_size / 100))
        self.profit_price = self.open_price * (1 + (self.profit_size / 100)) if direction == "buy" \
            else self.open_price * (1 - (self.profit_size / 100))
        self.change_direction_price = 0


class TradesResults:
    total_results: list[dict] = []

    def calc_trade_result(self, row: pd.Series, direction: str, trade: Trade, exit_type: str, *args, **kwargs) -> None:
        calc_service = {
            "stop_buy": 100 * (trade.stop_price - trade.open_price) / trade.open_price,
            "stop_sell": 100 * (trade.open_price - trade.stop_price) / trade.open_price,
            "profit_buy": 100 * (trade.profit_price - trade.open_price) / trade.open_price,
            "profit_sell": 100 * (trade.open_price - trade.profit_price) / trade.open_price,
            "change_direction_buy": 100 * (trade.change_direction_price - trade.open_price) / trade.open_price,
            "change_direction_sell": 100 * (trade.open_price - trade.change_direction_price) / trade.open_price
        }

        trade_result = {
            "enter_date": trade.enter_date,
            "exit_date": row.name,
            "result_percent": calc_service[f"{exit_type}_{direction}"],
            "direction": direction,
            "exit_type": exit_type,
            "trade_id": trade.id,
            "impulse_id": row["impulse_id"]
        }

        return self.add_trade_result(trade_result)

    def add_trade_result(self, trade_result):
        self.total_results.append(trade_result)

    def plot_cumulative_results(
            self,
            filter_conditions: list[dict] = None,
            show_individual: bool = True
    ) -> None:
        """
        filter_conditions — список словарей фильтров, например:
            [{"direction": "buy", "trade_id": 1}, {"direction": "buy", "trade_id": 2}]
        show_individual — рисовать ли отдельные кривые для каждого фильтра (если False, будет одна общая кривая)
        """

        df = pd.DataFrame(self.total_results)

        if df.empty or not {"direction", "exit_date", "result_percent", "trade_id"}.issubset(df.columns):
            print("Недостаточно данных для построения графика.")
            return

        plt.figure(figsize=(12, 6))

        if not filter_conditions:
            # Без фильтров — как раньше
            df = df.sort_values("exit_date")
            for direction, group in df.groupby("direction"):
                group = group.copy()
                group["cumulative_result"] = group["result_percent"].cumsum()
                plt.plot(group["exit_date"], group["cumulative_result"], label=f"{direction} cumulative",
                         linestyle="--")

            df["cumulative_total"] = df["result_percent"].cumsum()
            plt.plot(df["exit_date"], df["cumulative_total"], label="total cumulative", color="black", linewidth=2)
        else:
            # С фильтрами — каждый сегмент отдельно
            combined_df = pd.DataFrame()
            for idx, condition in enumerate(filter_conditions):
                filtered = df.copy()
                for key, val in condition.items():
                    filtered = filtered[filtered[key] == val]

                if filtered.empty:
                    print(f"⚠️ Нет данных для фильтра {condition}")
                    continue

                filtered = filtered.sort_values("exit_date")
                filtered["cumulative_result"] = filtered["result_percent"].cumsum()

                label = f"{condition.get('direction', '')} id={condition.get('trade_id', '')}"

                if show_individual:
                    plt.plot(filtered["exit_date"], filtered["cumulative_result"], label=label, linestyle="--")

                combined_df = pd.concat([combined_df, filtered])

            # Общая кривая по всем выбранным сегментам
            if not combined_df.empty:
                combined_df = combined_df.sort_values("exit_date")
                combined_df["cumulative_total"] = combined_df["result_percent"].cumsum()
                plt.plot(combined_df["exit_date"], combined_df["cumulative_total"],
                         label="total selected cumulative", color="black", linewidth=2)
            else:
                print("⚠️ Все фильтры вернули пустые выборки.")
                return

        # Оформление графика
        plt.title("Кумулятивная доходность по выбранным сегментам")
        plt.xlabel("Дата выхода из сделки")
        plt.ylabel("Накопленная доходность (%)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
