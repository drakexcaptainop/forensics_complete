import csv
import random
from datetime import datetime, timedelta

def generate_random_cdr(main_number, n_records, output_file='cdr.csv'):
    types = ['voice', 'sms', 'video']
    type_probs = [0.3, 0.6, 0.1]
    bts_choices = ['BTS001', 'BTS002', 'BTS003']

    base_date = datetime.strptime('2025-04-20', '%Y-%m-%d')

    cdr_rows = []
    for _ in range(n_records):
        # Adjust source and destination logic
        if random.random() < 0.3:
            destination = main_number
            source = str(random.randint(70000000, 79999999))
        else:
            source = main_number
            destination = str(random.randint(70000000, 79999999))
        time_offset = timedelta(minutes=random.randint(0, 23*60 + 59))
        timestamp = (base_date + time_offset).strftime('%Y-%m-%d %H:%M:%S')
        message_type = random.choices(types, weights=type_probs)[0]
        bts = random.choice(bts_choices)

        cdr_rows.append([source, destination, timestamp, message_type, bts])

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Source', 'Destination', 'DateTime', 'Type', 'BTS_ID'])
        writer.writerows(cdr_rows)

    print(f"Generated {n_records} records in {output_file}")

# Example usage
print(generate_random_cdr(main_number='71234567', n_records=50))
