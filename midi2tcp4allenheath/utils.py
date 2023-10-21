
def validate_ip(candidate):
    """Validates IP addresses.

    For the purposes of this program, it is considered valid if it:

    1. Is comprised of 4 integers, each within 0 and 255 inclusive, separated by
       full stops;
    2. Is not the global broadcast address.

    There's probably some fancy regex capable of doing the following, but I
    prefer readability over unscrutable one-liners.
    """

    try:
        segments = [int(seg) for seg in candidate.split('.')]
    except ValueError:
        return False

    if len(segments) != 4:
        return False

    for idx in range(4):
        if segments[idx] < 0 or segments[idx] > 255:
            return False

    if candidate in ["0.0.0.0", "255.255.255.255"]:
        return False

    return True

def restrict_ip(candidate):
    """
    Restrict IP entry to a subset of all possible IP addresses.
    
    Notably, the candidate address must:

    1. Exist within an allotted Private Address block,
    2. Not be the Network or Broadcast Address for that block.
    
    We assume that the provided candidate is a valid IPv4 address.
    """
    segments = [int(seg) for seg in candidate.split('.')]

    # 10.0.0.0/8
    if segments[0] == 10:
        if candidate in ["10.0.0.0", "10.255.255.255"]:
            return False
        for idx in range(1, 4):
            if segments[idx] < 0 or segments[idx] > 255:
                return False
        return True

    # 172.16.0.0/12
    if segments[0] == 172 and 16 <= segments[1] <= 31:
        if candidate in ["172.16.0.0", "172.31.255.255"]:
            return False
        for idx in range(2, 4):
            if segments[idx] < 0 or segments[idx] > 255:
                return False
        return True

    # 192.168.0.0/16
    if segments[0] == 192 and segments[1] == 168:
        if candidate in ["192.168.0.0", "192.168.255.255"]:
            return False
        for idx in range(2, 4):
            if segments[idx] < 0 or segments[idx] > 255:
                return False
        return True

    # 169.254.0.0/16
    if segments[0] == 169 and segments[1] == 254:
        if candidate in ["169.254.0.0", "169.254.255.255"]:
            return False
        for idx in range(2, 4):
            if segments[idx] < 0 or segments[idx] > 255:
                return False
        return True

    return False
