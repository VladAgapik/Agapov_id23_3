from app.core.celery_app import celery_app
import itertools
import time

def generate_passwords(charset, max_length):
    for length in range(1, max_length + 1):
        for pwd in itertools.product(charset, repeat=length):
            yield ''.join(pwd)

@celery_app.task(bind=True)
def brute_task(self, hash_str, charset, max_length):
    total = sum(len(charset) ** i for i in range(1, max_length + 1))
    tried = 0
    for password in generate_passwords(charset, max_length):
        tried += 1
        if tried % 100 == 0:
            self.update_state(state='PROGRESS', meta={'progress': int(tried / total * 100)})
        time.sleep(0.01)
        if password == "secret":
            return password
    return None

def start_brute_force(hash_str, charset, max_length):
    return brute_task.delay(hash_str, charset, max_length)
