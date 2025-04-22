import os
import csv
from datetime import datetime, timezone, timedelta
from collections import Counter
import matplotlib.pyplot as plt

# Directory to search
directory = os.getcwd()

# Function to extract timestamp from filenames
def extract_timestamp(filename):
    try:
        parts = filename.split('-')
        timestamp_str = '-'.join(parts[-6:-1])  # Extract timestamp part
        # Convert to a timezone-aware datetime (UTC)
        return datetime.strptime(timestamp_str, "%Y-%m-%d-%H-%M").replace(tzinfo=timezone.utc)
    except ValueError:
        return None

newest_file = None
newest_timestamp = None

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    #print(f"Found file: {filename}")
    if os.path.isfile(file_path):
        timestamp = extract_timestamp(filename)
        if timestamp:
            if newest_timestamp is None or timestamp > newest_timestamp:
                newest_timestamp = timestamp
                newest_file = file_path


if newest_file:
    # Convert UTC to local timezone (example: UTC+2)
    local_timezone = timezone(timedelta(hours=2))  # Replace 2 with your timezone offset
    newest_timestamp_local = newest_timestamp.astimezone(local_timezone)
    print(f"Timestamp in local timezone: {newest_timestamp_local}")
else:
    print("No valid files found.")


with open(newest_file, 'r') as file:
    # Read and clean the file contents, skipping the header
    versions = [line.strip().replace('"', '') for line in file if line.strip() != "_device_os_version"]

# Count occurrences dynamically
version_counts = Counter(versions)

# Combine small counts into "Others" category
threshold = 4  # Group versions with counts less than or equal to this value
grouped_counts = {
    version: count for version, count in version_counts.items() if count > threshold
}
others_count = sum(count for version, count in version_counts.items() if count <= threshold)
if others_count > 0:
    grouped_counts["Others"] = others_count

# Sort grouped_counts by version number
def version_key(version):
    if version == "Others":
        return (float('inf'),)  # Ensure "Others" appears at the end
    return tuple(map(int, version.split('.')))  # Convert version strings to tuples of integers

sorted_grouped_counts = dict(sorted(grouped_counts.items(), key=lambda item: version_key(item[0])))

# Prepare data for the donut chart
labels = list(sorted_grouped_counts.keys())   # Versions
sizes = list(sorted_grouped_counts.values())  # Counts
total_count = sum(sizes)  # Total for calculating percentages

# Append percentages to labels with a hyphen separator
labels_with_percentages = [f"{label} - {count / total_count * 100:.1f}%" for label, count in zip(labels, sizes)]


# Create the donut chart with dark mode
fig, ax = plt.subplots(figsize=(9.15, 12), facecolor="#212121")  # Dark background for the figure
ax.set_facecolor("#212121")  # Dark background for the plot area
ax.pie(
    sizes, 
    labels=labels_with_percentages,  # Use labels with percentages and a hyphen
    startangle=90,                   # Rotate for better appearance
    wedgeprops={'width': 0.3},       # Adjust the width to create a donut
    textprops={'fontsize': 12, 'color': "#ECECEC"}       # Adjust font size for readability
)

# Add a title
ax.set_title(
    f"Data collected at {newest_timestamp_local.strftime('%Y-%m-%d %H:%M:%S %Z')}",
    fontsize=16,
    pad=20,
    color="#ECECEC"
)

# Create a table below the chart
table_data = [[version, count] for version, count in sorted_grouped_counts.items()]
column_labels = ["Version", "Count"]
ax_table = plt.table(
    cellText=table_data, 
    colLabels=column_labels, 
    loc='bottom',  # Position at the bottom of the plot
    cellLoc='center',  # Center-align the text
)

# Adjust the font size of the table
ax_table.auto_set_font_size(False)  # Disable automatic font scaling
ax_table.set_fontsize(14)  # Set font size manually
ax_table.scale(0.5, 1.5)  # Adjust the width and height scaling
for key, cell in ax_table.get_celld().items():
    cell.set_facecolor("#212121")  # Dark background for cells
    cell.set_text_props(color="#ECECEC")  # Light text
    cell.set_edgecolor("#212121")
    cell.set_height(0.042)

# Adjust layout to fit the table and graph
plt.subplots_adjust(
    bottom=0.15,  # Provide enough space for the table
    top=0.85,     # Reduce top margin to minimize dead space
)

# Save the figure as a PNG file with a timestamp in the filename
output_filename = f"version_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
plt.savefig(output_filename, dpi=300, bbox_inches="tight")  # Save tightly cropped figure

print(f"Figure saved as: {output_filename}")
