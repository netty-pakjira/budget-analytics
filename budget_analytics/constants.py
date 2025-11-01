from enum import Enum


class User(Enum):
    NETTY = "netty"
    MICHAEL = "michael"


class DataSource(Enum):
    AMEX = "amex"
    CHASE = "chase"
    RECURRING = "recurring"


class BankAccount(Enum):
    AMEX_CASHBACK = "amex_cashback"
    CHASE_SAVER = "chase_saver"
    CHASE_BA = "chase_ba"
    CHASE_ROUND_UP = "chase_round_up"
    MONZO_BA = "monzo_ba"
    SBC_BA = "hsbc_ba"
    REVOLUT_BA = "revolut_ba"
    SCOT_WIDOWS = "scot_widows"

    @property
    def data_source(self):
        if self in [self.AMEX_CASHBACK]:
            return DataSource.AMEX
        elif self in [
            self.CHASE_SAVER,
            self.CHASE_BA,
            self.CHASE_ROUND_UP,
        ]:
            return DataSource.CHASE
        else:
            raise NotImplementedError()


class AmexExpenditureCategory(Enum):
    GROCERIES = "General Purchases-Groceries"
    RESTAURANT = "Entertainment-Restaurants"
    BARS_CAFES = "Entertainment-Bars & Cafés"
    OTHER_ENTERTAINMENT = "Entertainment-Other Entertainment"
    GOVT_SERVICE = "General Purchases-Government Services"
    ONLINE_PURCHASE = "General Purchases-Online Purchases"
    GENERAL_RETAIL = "General Purchases-General Retail"
    DEPARTMENT_STORES = "General Purchases-Department Stores"
    PRINTING = "Business Services-Printing & Publishing"
    TELECOM = "Communications-Mobile Telecommunication"
    HEALTHCARE = "Business Services-Health Care Services"
    PHARMACIES = "General Purchases-Pharmacies"
    TRAVEL = "Travel-Other Travel"
    CLUBS = "Entertainment-Clubs"
    TAXIS = "Travel-Taxis & Coach"
    TRAVEL_AGENCIES = "Travel-Travel Agencies"
    OTHER_SERVICES = "Business Services-Other Services"
    NAN = "NaN"

    @classmethod
    def from_value(cls, value):
        try:
            return cls(value)
        except ValueError:
            return cls.NAN


class ExpenditureCategory(Enum):
    ENTERTAINMENT = "entertainment"
    GROCERIES = "groceries"
    HEALTHCARE = "healthcare"
    HOLIDAY = "holiday"
    ONE_OFF = "one-off"
    RESTAURANT = "restaurant"
    SUBSCRIPTION = "subscription"
    TRANSPORT = "transport"
    OTHER = "other"

    @classmethod
    def from_amex(cls, amex: AmexExpenditureCategory):
        return {
            AmexExpenditureCategory.GROCERIES: cls.GROCERIES,
            AmexExpenditureCategory.RESTAURANT: cls.RESTAURANT,
            AmexExpenditureCategory.BARS_CAFES: cls.RESTAURANT,
            AmexExpenditureCategory.OTHER_ENTERTAINMENT: cls.ENTERTAINMENT,
            AmexExpenditureCategory.GOVT_SERVICE: cls.OTHER,
            AmexExpenditureCategory.ONLINE_PURCHASE: cls.ONE_OFF,
            AmexExpenditureCategory.GENERAL_RETAIL: cls.ONE_OFF,
            AmexExpenditureCategory.DEPARTMENT_STORES: cls.ONE_OFF,
            AmexExpenditureCategory.PRINTING: cls.OTHER,
            AmexExpenditureCategory.TELECOM: cls.SUBSCRIPTION,
            AmexExpenditureCategory.HEALTHCARE: cls.HEALTHCARE,
            AmexExpenditureCategory.PHARMACIES: cls.HEALTHCARE,
            AmexExpenditureCategory.TRAVEL: cls.HOLIDAY,
            AmexExpenditureCategory.CLUBS: cls.OTHER,
            AmexExpenditureCategory.TAXIS: cls.TRANSPORT,
            AmexExpenditureCategory.TRAVEL_AGENCIES: cls.OTHER,
            AmexExpenditureCategory.OTHER_SERVICES: cls.OTHER,
            AmexExpenditureCategory.NAN: cls.OTHER,
        }[amex]


class Country(Enum):
    UK = "UK"
    NAN = "NAN"

    @classmethod
    def from_value(cls, value):
        try:
            return cls(value)
        except ValueError:
            if "united kingdom" in str(value).lower():
                return cls.UK
            else:
                return cls.NAN


class Calendar(Enum):
    EVERYDAY = "EVERYDAY"
    GB = "GB"


class Frequency(Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class HolidayAdjustment(Enum):
    NONE = "NONE"
    MOVE_EARLIER = "MOVE_EARLIER"
    MOVE_LATER = "MOVE_LATER"


class CashflowDirection(Enum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"

    @property
    def multiplier(self):
        match self.value:
            case "INFLOW":
                return 1
            case "OUTFLOW":
                return -1
            case _:
                raise ValueError("Unknown direction")
