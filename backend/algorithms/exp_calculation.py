from datetime import datetime
import math
def calc_exp(start_time, end_time, score, sum_diff):
    start = datetime.fromisoformat(start_time)
    end   = datetime.fromisoformat(end_time)
    elapsed = end - start
    score = math.ceil(((score * sum_diff) / elapsed.seconds) * 100)
    return score