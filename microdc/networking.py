def generate_subnets(network_cidr):
    subnets_19 = []
    subnets_22 = []
    cidr_octs = network_cidr.split('.')
    subnets_19.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 32, '0/19'))
    subnets_19.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 64, '0/19'))
    subnets_19.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 96, '0/19'))
    subnets_22.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], cidr_octs[2], '0/22'))
    subnets_22.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 4, '0/22'))
    subnets_22.append("{}.{}.{}.{}".format(cidr_octs[0], cidr_octs[1], int(cidr_octs[2]) + 8, '0/22'))

    return subnets_19, subnets_22
