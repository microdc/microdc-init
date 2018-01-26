def generate_subnets(network_cidr, offset):
    subnets_19 = []
    subnets_22 = []
    cidr_octs = network_cidr.split('.')
    subnets_19.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 32 + offset, '0/19'))
    subnets_19.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 64 + offset, '0/19'))
    subnets_19.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 96 + offset, '0/19'))
    subnets_22.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 0 + offset, '0/22'))
    subnets_22.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 4 + offset, '0/22'))
    subnets_22.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 8 + offset, '0/22'))

    return subnets_19, subnets_22
