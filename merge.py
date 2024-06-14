import os
import zipfile
import pandas as pd

# Define the folder containing the zipped folders
zip_folder_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\'
output_folder_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\temp_extracted\\'
merged_output_file = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\merged_output.csv'

# Ensure the output folder exists
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Define the names of the two CSV files to be merged
file1_name = 'documentmetadata.csv'
file2_name = 'emotion_docs.csv'
shared_column = 'ID'

# Function to extract specific files from zip
def extract_specific_files(zip_path, output_path, file_names):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if any(file.endswith(name) for name in file_names):
                zip_ref.extract(file, output_path)

# Initialize DataFrames to None
df1 = None
df2 = None

# Extract the specific CSV files from each zipped folder and read into DataFrames
zip_files = [f for f in os.listdir(zip_folder_path) if f.endswith('.zip')]

for idx, zip_filename in enumerate(zip_files):
    zip_file_path = os.path.join(zip_folder_path, zip_filename)
    extract_specific_files(zip_file_path, output_folder_path, [file1_name, file2_name])
    
    # Read the extracted CSV files into DataFrames
    for root, dirs, files in os.walk(output_folder_path):
        for file in files:
            if file == file1_name:
                temp_df1 = pd.read_csv(os.path.join(root, file))
                if df1 is None:
                    df1 = temp_df1
                else:
                    df1 = pd.concat([df1, temp_df1], ignore_index=True)
            elif file == file2_name:
                temp_df2 = pd.read_csv(os.path.join(root, file))
                if df2 is None:
                    df2 = temp_df2
                else:
                    df2 = pd.concat([df2, temp_df2], ignore_index=True)

    # Clean up extracted files
    for file in files:
        os.remove(os.path.join(root, file))

    # Provide progress feedback
    print(f"Processed {idx + 1}/{len(zip_files)}: {zip_filename}")

# Check if both DataFrames are loaded
if df1 is not None and df2 is not None:
    # Merge the DataFrames on the shared column
    merged_df = pd.merge(df1, df2, on=shared_column)
    
    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(merged_output_file, index=False)
    print(f"Merged CSV file saved to {merged_output_file}")
else:
    print("One or both of the specified files were not found in the zipped folders.")
