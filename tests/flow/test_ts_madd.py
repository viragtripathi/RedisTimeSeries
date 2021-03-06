import time

from RLTest import Env


def test_madd():
    sample_len = 1024

    with Env().getConnection() as r:
        r.execute_command("ts.create", 'test_key1')
        r.execute_command("ts.create", 'test_key2')
        r.execute_command("ts.create", 'test_key3')

        for i in range(sample_len):
            assert [i + 1000, i + 3000, i + 6000] == r.execute_command("ts.madd", 'test_key1', i + 1000, i,
                                                                       'test_key2', i + 3000, i, 'test_key3',
                                                                       i + 6000, i, )

        res = r.execute_command('ts.range', 'test_key1', 1000, 1000 + sample_len)
        i = 0
        for sample in res:
            assert sample == [1000 + i, str(i).encode('ascii')]
            i += 1

        res = r.execute_command('ts.range', 'test_key2', 3000, 3000 + sample_len)
        i = 0
        for sample in res:
            assert sample == [3000 + i, str(i).encode('ascii')]
            i += 1

        res = r.execute_command('ts.range', 'test_key3', 6000, 6000 + sample_len)
        i = 0
        for sample in res:
            assert sample == [6000 + i, str(i).encode('ascii')]
            i += 1


def test_ooo_madd():
    sample_len = 100
    start_ts = 1600204334000

    with Env().getConnection() as r:
        r.execute_command("ts.create", 'test_key1')
        last_sample = None
        samples = []
        for i in range(0, sample_len, 3):
            assert [start_ts + (i * 1000 + 2000), start_ts + (i * 1000 + 1000),
                    start_ts + (i * 1000)] == r.execute_command("ts.madd", 'test_key1', start_ts + (i * 1000 + 2000), i,
                                                                'test_key1', start_ts + i * 1000 + 1000, i, 'test_key1',
                                                                start_ts + i * 1000, i)
            samples.append([start_ts + (i * 1000), str(i).encode('ascii')])
            samples.append([start_ts + (i * 1000 + 1000), str(i).encode('ascii')])
            samples.append([start_ts + (i * 1000 + 2000), str(i).encode('ascii')])
            last_sample = [start_ts + (i * 1000 + 2000), str(i).encode('ascii')]

        assert r.execute_command('ts.get', 'test_key1') == last_sample
        assert r.execute_command('ts.range', 'test_key1', '-', '+') == samples


def test_partial_madd():
    with Env().getConnection() as r:
        r.execute_command("ts.create", 'test_key1')
        r.execute_command("ts.create", 'test_key2')
        r.execute_command("ts.create", 'test_key3')

        now = int(time.time() * 1000)
        res = r.execute_command("ts.madd", 'test_key1', "*", 10, 'test_key2', 2000, 20, 'test_key3', 3000, 30)
        assert now <= res[0]
        assert 2000 == res[1]
        assert 3000 == res[2]

        res = r.execute_command("ts.madd", 'test_key1', now + 1000, 10, 'test_key2', 1000, 20, 'test_key3', 3001, 30)
        assert (now + 1000, 1000, 3001) == (res[0], res[1], res[2])
        assert len(r.execute_command('ts.range', 'test_key1', "-", "+")) == 2
        assert len(r.execute_command('ts.range', 'test_key2', "-", "+")) == 2
        assert len(r.execute_command('ts.range', 'test_key3', "-", "+")) == 2
