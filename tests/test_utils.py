def mock_send_message(*args):
    print(args[0])

def mock_schedule_next_day_at(*args):
    print(f'scheduled task {args[1].__name__} at {args[0]}')