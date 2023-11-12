import numpy as np

def decode_index(i, max_time):
  job_id = i // max_time
  start_time = i - job_id * max_time
  return job_id, start_time

def encode_index(job_id, start_time, max_time):
  return job_id * max_time + start_time

def make_qubo(times, deadlines, profits):
  max_time = np.max(deadlines)
  num_jobs = len(times)

  size = max_time * num_jobs
  Q = np.zeros((size, size))

  P = 1000
  for job_id in range(num_jobs):
    for start_time in range(max_time):
      time = times[job_id]
      deadline = deadlines[job_id]
      i = encode_index(job_id, start_time, max_time)

      # Apply profit, if completed before deadline
      if start_time + time <= deadline: Q[i, i] = -1.0 * profits[job_id]

      # Should start each job only once
      # Otherwise, apply penalty P
      for t in range(max_time):
        if start_time != t:
          j = encode_index(job_id, t, max_time)
          Q[i][j] = P
          Q[j][i] = P

      # Should start one job after another
      # Otherwise, apply penalty P
      for job_id_2 in range(num_jobs):
        if job_id_2 != job_id:
          time = times[job_id]
          for t in range(start_time, min(start_time + time, max_time)):
            j = encode_index(job_id_2, t, max_time)
            Q[i][j] = P
            Q[j][i] = P
  return Q

def decode_result(times, deadlines, profits, x):
  max_time = np.max(deadlines)
  results = []
  score = 0
  for i in range(len(x)):
    if x[i] == 1:
      job_id, start_time = decode_index(i, max_time)
      duration = times[job_id]
      score = score + profits[job_id]
      job = {"Job": f"Task {job_id}",\
        "Machine": "1", "Start": start_time,\
        "Duration": duration, "Finish": start_time + duration,
        "deadline": deadlines[job_id]}
      results.append(job)
  return results, score
