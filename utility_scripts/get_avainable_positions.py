from utils.models import Order

def get_available_positions():
    taken_positions = Order.objects.exclude(position='storage').values_list('position', flat=True)
    all_positions = [ i for i in range(1, 9)] + ['storage']
    avainable_positions = [pos for pos in all_positions if pos not in taken_positions]

    return avainable_positions 