from dashboard.dashboard.cards.business_insights import BusinessInsightsCard
from dashboard.dashboard.cards.contract_renovations import ContractRenovationCard
from dashboard.dashboard.cards.monthly_history import MonthlyHistoryCard
from dashboard.dashboard.cards.payment_pendding import PaymentPenddingCard
from dashboard.dashboard.cards.rental_debts import RentalDebtsCard
from dashboard.dashboard.cards.repair_debts import RepairDebtsCard
from dashboard.dashboard.cards.trailers_availables import TrailersAvailableCard
from dashboard.dashboard.cards.trailers_storage import StorageCard


DASHBOARD = [
    BusinessInsightsCard(),
    MonthlyHistoryCard(),
    RepairDebtsCard(),
    TrailersAvailableCard(),
    RentalDebtsCard(),
    PaymentPenddingCard(),
    StorageCard(),
    ContractRenovationCard(),
]
