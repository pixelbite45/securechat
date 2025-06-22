import random
import string
from config import *
def meeting_id_create() -> str:
    current_running_meeting_ids = set()  # This should be managed externally in real use

    def generate_random_id():
        chars = string.ascii_lowercase + string.digits
        parts = [''.join(random.choices(chars, k=3)) for _ in range(3)]
        return '-'.join(parts)

    while True:
        meeting_id = generate_random_id()
        if meeting_id not in CURRENT_RUNNING_MEETINGS:
            CURRENT_RUNNING_MEETINGS.append(meeting_id)
            return meeting_id
def meeting_pass_key():
    return random.randint(111111,999999)