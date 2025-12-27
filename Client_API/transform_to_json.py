import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('output10lines.csv', sep='\t')

# Convert each row to JSON string (newline-delimited JSON)
df['json'] = df.to_json(orient='records', lines=True).splitlines()

# Extract the JSON strings
dfjson = df['json']

# Save to output.txt
np.savetxt('./output10lines.txt', dfjson.values, fmt='%s')

print("Transformation complete. Output saved to output.txt")