import re


def parse_single_or_list(value: str):
    value = value.strip()
    match = re.match(r"(.*)\[(\d+-\d+)\]", value)

    if match:
        prefix, interval = match.groups()
        lower, upper = tuple(map(int, interval.split("-")))
        assert (
            lower <= upper
        ), "interval should be greater than lower and less than upper"

        sequence = list(range(lower, upper + 1))
        return list(map(lambda x: prefix + str(x), sequence))
    else:
        return [value]


def read_hosts(config_path) -> list[str]:
    with open(config_path) as config_path:
        host_lines = list(
            filter(lambda l: "host " in l.lower(), config_path.readlines())
        )
        return list(map(lambda l: l.strip().split()[-1], host_lines))
