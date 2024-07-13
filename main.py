import pandas as pd
import streamlit as st
import json

def load_file(uploaded_file):
    """Load the uploaded file based on its extension."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def load_json_safe(x):
    """Safely load JSON data from a string."""
    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError):
        return {}

def extract_employee_data(df, selected_keys, options):
    """Extract employee data based on selected keys and format the results."""
    df['Additional Info'] = df['Additional Info'].apply(load_json_safe)
    df_sorted = df.sort_values(by=['Employee ID'], ascending=True)

    result = []
    seen_employees = set()

    for index, item in df_sorted.iterrows():
        employee_id = item['Employee ID']
        if employee_id not in seen_employees:
            seen_employees.add(employee_id)
            json_info = item['Additional Info']
            for key in selected_keys:
                if key in json_info:
                    for sub_item in json_info[key]:
                        formatted_data = {
                            'Employee ID': employee_id,
                            'Employee Name': item['Employee Name'],
                            'Department': item['Department'],
                            'Info Type': options[key],
                            'Info Detail': sub_item.get('detail', ''),
                            'Info Description': sub_item.get('description', '')
                        }
                        result.append(formatted_data)
    
    return pd.DataFrame(result, columns=['Employee ID', 'Employee Name', 'Department', 'Info Type', 'Info Detail', 'Info Description'])

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Employee Data Extractor",
        page_icon="👤",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "This app extracts and displays employee information from uploaded datasets."
        }
    )

    st.title("Employee Data Extractor")

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xls', 'xlsx'])

    if uploaded_file is not None:
        df = load_file(uploaded_file)
        if df is not None:
            st.success("File successfully uploaded.")
            st.write("Preview of the uploaded DataFrame:")
            st.write(df.head(25))

            options = {
                'projects': 'Projects',
                'skills': 'Skills',
                'certifications': 'Certifications',
                'trainings': 'Trainings'
            }
            selected_keys = st.multiselect('Select the keys to extract data:', options.keys())

            if selected_keys:
                selected_df = extract_employee_data(df, selected_keys, options)
                st.write(selected_df)

                @st.cache_data
                def convert_df_to_csv(df):
                    return df.to_csv(index=False).encode('utf-8')

                csv_data = convert_df_to_csv(selected_df)

                st.download_button(
                    label="Download data as CSV",
                    data=csv_data,
                    file_name='extracted_employee_data.csv',
                    mime='text/csv',
                    use_container_width=True
                )

        else:
            st.error("Failed to load the file. Please try again.")

if __name__ == "__main__":
    main()
