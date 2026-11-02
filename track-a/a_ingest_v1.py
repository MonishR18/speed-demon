import argparse
import os

INPUT_NAME = "requests.log"
OUTPUT_NAME = "summary.txt"


def percentile(values, p):
    n = len(values)
    rank = (p * n + 99) // 100
    return values[rank - 1]


def main(data_dir, out_dir):
    groups = {}

    with open(os.path.join(data_dir, INPUT_NAME), "rb") as f:
        for raw in f:
            ts, method, endpoint, status, latency = raw.split(b" ")

            hour = ts[:13]
            key = (hour, endpoint)

            group = groups.get(key)

            if group is None:
                group = [[], 0]
                groups[key] = group

            group[0].append(int(latency))

            if status[0] == 53:
                group[1] += 1

    output = []

    for (hour, endpoint), (values, errors) in sorted(groups.items()):
        values.sort()
        count = len(values)

        output.append(
            b"%s:00:00Z %s %d %d %d %d %d %d\n"
            % (
                hour,
                endpoint,
                count,
                percentile(values, 50),
                percentile(values, 95),
                percentile(values, 99),
                errors,
                errors * 1_000_000 // count,
            )
        )

    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, OUTPUT_NAME), "wb") as f:
        f.write(b"".join(output))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="/data")
    parser.add_argument("--out", default="/out")
    args = parser.parse_args()

    main(args.data, args.out)
