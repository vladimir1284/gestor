from dashboard.dashboard.cards.business_insights import BusinessInsightsCard
from dashboard.dashboard.cards.monthly_history import MonthlyHistoryCard
from dashboard.dashboard.cards.payment_pendding import PaymentPenddingCard
from dashboard.dashboard.cards.rental_debts import RentalDebtsCard
from dashboard.dashboard.cards.repair_debts import RepairDebtsCard


DASHBOARD = [
    BusinessInsightsCard(),
    MonthlyHistoryCard(),
    RepairDebtsCard(),
    RentalDebtsCard(),
    PaymentPenddingCard(),
]
