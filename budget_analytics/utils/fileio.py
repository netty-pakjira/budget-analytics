from dataclasses import dataclass
import datetime as dt
import os
from pathlib import Path

import pandas as pd

from budget_analytics.constants import (
    BankAccount,
    DataSource,
    User,
    AmexExpenditureCategory,
    ExpenditureCategory,
    Country,
)


@dataclass
class FileIO:
    root_data_path: Path = Path(
        "/Users/pakjirachancheochingchai/DataPython/daily_spending"
    )
    data_path: Path | str = None
    user: User = None

    def __post_init__(self):
        if self.data_path:
            self.file_path = self.root_data_path / self.data_path
        else:
            self.file_path = self.root_data_path

    def set_data_path(self, data_path: Path | str):
        self.data_path = data_path
        self.__post_init__()

    def validate_user(self):
        if not type(self.user) == User:
            raise TypeError("User not set / invalid.")

    def read_csv(self, filename: str, **kwargs) -> pd.DataFrame:
        df = pd.read_csv(self.file_path / f"{filename}.csv", **kwargs)
        return df

    def read_all_csv(self, **kwargs) -> dict[str, pd.DataFrame]:
        files = os.listdir(str(self.file_path))
        all_dfs = dict()
        for file in files:
            file_split = file.split(".")
            if file_split[-1] == "csv":
                filename = ".".join(file_split[:-1])
                df = self.read_csv(self.file_path / filename, **kwargs)
                all_dfs[filename] = df
        return all_dfs

    def read_recurring(
        self, data_path: Path | str = "cashflows", filename: str = "recurring", **kwargs
    ) -> pd.DataFrame:
        data_path = data_path or self.data_path
        df = pd.read_csv(self.root_data_path / data_path / f"{filename}.csv", **kwargs)
        if self.user is not None:
            df = df[df["User"] == self.user.value]
        return df

    def read_splitwise(self):
        files = os.listdir(self.root_data_path / "splitwise")
        dates = [file.split("_")[1] for file in files]
        max_date = max(dates)
        df = pd.read_csv(
            self.root_data_path / "splitwise" / files[dates.index(max_date)]
        )
        return df.iloc[:-1]


def description_to_expense_category(text: str) -> ExpenditureCategory | None:
    if "oystercard" in text.lower():
        return ExpenditureCategory.TRANSPORT
    return None


@dataclass
class CardsFileIO(FileIO):
    def read_amex(
        self,
        bank_account: BankAccount,
    ) -> pd.DataFrame:
        data_path = f"cards_{self.user.value}/{bank_account.value}"
        self.set_data_path(data_path)
        df = pd.concat(self.read_all_csv().values(), axis=0)
        df = df[~df["Description"].str.contains("PAYMENT RECEIVED - THANK YOU")]
        df["Date"] = df["Date"].map(
            lambda s: dt.datetime.strptime(s, "%d/%m/%Y").date()
        )
        df["Category"] = (
            df["Description"]
            .map(description_to_expense_category)
            .fillna(
                df["Category"]
                .map(AmexExpenditureCategory.from_value)
                .map(ExpenditureCategory.from_amex)
            )
        ).map(lambda e: e.value)
        df["Country"] = df["Country"].map(Country.from_value).map(lambda e: e.value)
        df["Reference"] = df["Reference"].map(str).map(lambda s: s.replace("'", ""))
        return (
            df.drop(columns=["Appears On Your Statement As", "Extended Details"])
            .sort_values(by=["Date"])
            .reset_index(drop=True)
            .rename(columns={"Amount": "Amount_GBP"})
        )[
            [
                "Date",
                "Description",
                "Amount_GBP",
                "Category",
                "Postcode",
                "Town/City",
                "Country",
                "Reference",
            ]
        ]

    def read_chase(
        self,
        bank_account: BankAccount,
    ):
        data_path = f"cards_{self.user.value}/{bank_account.value}"
        self.set_data_path(data_path)
        df = pd.concat(self.read_all_csv(skiprows=1).values(), axis=0).reset_index()
        df = df.loc[df["Transaction Type"] == "Purchase"]
        assert (df["Currency"] == "GBP").all()
        df = df[["Date", "Transaction Description", "Amount", "Time"]]
        df["Date"] = df["Date"].map(lambda d: dt.datetime.strptime(d, "%d %b %Y"))
        return (
            df.rename(columns={"Transaction Description": "Description"})
            .sort_values(by="Date")
            .reset_index(drop=True)
        )

    def read_statement(
        self,
        bank_account: BankAccount,
    ) -> pd.DataFrame:
        reader = None
        self.validate_user()
        match data_source := bank_account.data_source:
            case DataSource.AMEX:
                reader = self.read_amex
            case DataSource.CHASE:
                reader = self.read_chase
            case _:
                raise ValueError(f"Invalid Data Source: {data_source}")
        return reader(bank_account)
