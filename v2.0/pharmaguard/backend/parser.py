TARGET_GENES = [
    "CYP2D6",
    "CYP2C19",
    "CYP2C9",
    "SLCO1B1",
    "TPMT",
    "DPYD"
]

def parse_info_field(info_string, field_name):
    """Parse a simple INFO field from the INFO string like 'GENE=CYP2D6'"""
    if not info_string:
        return None
    for item in info_string.split(';'):
        if '=' in item:
            key, value = item.split('=', 1)
            if key == field_name:
                return value
    return None

def parse_vcf(file_path):
    extracted = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        raise Exception(f"Invalid VCF file: {str(e)}")

    for line in lines:
        # Skip header lines
        if line.startswith('#'):
            continue
        
        # Parse data line
        parts = line.strip().split('\t')
        if len(parts) < 8:
            continue
        
        try:
            chrom = parts[0]
            pos = parts[1]
            rsid = parts[2]
            ref = parts[3]
            alt = parts[4]
            qual = parts[5]
            filter_col = parts[6]
            info = parts[7]
            
            gene = parse_info_field(info, "GENE")
            star = parse_info_field(info, "STAR")

            if gene and gene in TARGET_GENES:
                extracted.append({
                    "gene": gene,
                    "rsid": rsid if rsid and rsid != "." else ".",
                    "star": star if star else "."
                })

        except Exception:
            continue

    return extracted
