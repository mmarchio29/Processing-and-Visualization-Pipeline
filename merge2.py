import os
import zipfile
import pandas as pd

# Define the folder containing the zipped folders
zip_folder_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\METADATA'
output_folder_path = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\temp_extracted\\'
final_output_file = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\final_merged_output.xlsx'
additional_csv_file = r'C:\\Users\\mamar\\Questrom Sentiment Project\\Capitalism\\merged_output.csv'

# Ensure the output folder exists
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Define the name of the Excel file to be merged
excel_file_name = 'citation.csv'
shared_column_excel = 'GOID'  # Column name in the Excel files
shared_column_csv = 'ID'  # Column name in the additional CSV file

# Function to extract specific file from zip
def extract_specific_file(zip_path, output_path, file_name):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith(file_name):
                zip_ref.extract(file, output_path)

# Initialize DataFrame to None
merged_excel_df = pd.DataFrame()

# Extract the specific Excel file from each zipped folder and read into DataFrame
zip_files = [f for f in os.listdir(zip_folder_path) if f.endswith('.zip')]

for idx, zip_filename in enumerate(zip_files):
    zip_file_path = os.path.join(zip_folder_path, zip_filename)
    extract_specific_file(zip_file_path, output_folder_path, excel_file_name)
    
    # Read the extracted Excel file into DataFrame
    for root, dirs, files in os.walk(output_folder_path):
        for file in files:
            if file == excel_file_name:
                temp_df = pd.read_csv(os.path.join(root, file))
                if merged_excel_df.empty:
                    merged_excel_df = temp_df
                else:
                    merged_excel_df = pd.merge(merged_excel_df, temp_df, on=shared_column_excel, how='outer')

    # Clean up extracted files
    for file in files:
        os.remove(os.path.join(root, file))

    # Provide progress feedback
    print(f"Processed {idx + 1}/{len(zip_files)}: {zip_filename}")

# Print the columns of the merged Excel DataFrame
print("Columns in merged Excel DataFrame:", merged_excel_df.columns)

# Perform a full outer join with the additional CSV file
additional_df = pd.read_csv(additional_csv_file)

# Print the columns of the additional CSV DataFrame
print("Columns in additional CSV DataFrame:", additional_df.columns)

# Check if the columns exist before merging
if shared_column_excel in merged_excel_df.columns and shared_column_csv in additional_df.columns:
    final_merged_df = pd.merge(merged_excel_df, additional_df, left_on=shared_column_excel, right_on=shared_column_csv, how='outer')
    # Save the final merged DataFrame to an Excel file
    final_merged_df.to_excel(final_output_file, index=False)
    print(f"Final merged data saved to {final_output_file}")
else:
    print(f"Column '{shared_column_excel}' not found in merged Excel DataFrame or column '{shared_column_csv}' not found in additional CSV DataFrame.")
