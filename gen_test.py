import random, datetime

errors = ['FileNotFoundError: model.safetensors', 'CUDA out of memory', 'RuntimeError: expected scalar type Float', 'ConnectionRefusedError: localhost:8188', 'ValueError: invalid literal']

with open('J:/Projects/PulpGulp/test_log.txt', 'w') as f:
    for i in range(5000):
        ts = datetime.datetime(2025,6,5,10,0,0) + datetime.timedelta(seconds=i)
        r = random.random()
        if r < 0.02:
            f.write('[%s] ERROR: %s\n' % (ts, random.choice(errors)))
            for j in range(5):
                f.write('  File src/pipeline.py, line %d, in process_frame\n' % random.randint(10,500))
            f.write('  raise %s\n' % random.choice(errors))
        elif r < 0.1:
            f.write('[%s] WARNING: VRAM usage at %d%%\n' % (ts, random.randint(80,99)))
        elif r < 0.3:
            f.write('[%s] Processing frame %d/5000... %.2fs\n' % (ts, i, random.uniform(0.5,3.0)))
        elif r < 0.35:
            f.write('[%s] %%%%%%%%%%%%%%%% %d%%\n' % (ts, random.randint(20,95)))
        else:
            f.write('[%s] DEBUG: node_cache hit=%d queue_size=%d\n' % (ts, random.randint(0,1), random.randint(0,12)))

print('Created test_log.txt with 5000 lines')
