import streamlit as st
import pandas as pd
import plotly.express as px
import re
from PIL import Image
import base64
import os
# ------ App Config ----------
st.set_page_config(
    page_title="YOLO Object Detection Dashboard",
    page_icon="🧊",
    initial_sidebar_state="expanded",
    layout="wide",
)

with open('detection_results.txt', 'r') as file:
    text = file.read()

# Regular expression pattern to match the desired lines
pattern = r"image \d/\d (.+?): (\d+x\d+) (.+?), (\d+\.\d+)ms"

# Extract data using regular expression
matches = re.findall(pattern, text)

data = []
for match in matches:
    filename, _, objects, _ = match
    filename = filename.split('/')[-1]
    objects_list = [obj.strip() for obj in objects.split(',')]
    data.append({
        'Filename': filename,
        'Objects': objects_list
    })

df = pd.DataFrame(data)
# Count the number of objects detected in each image
df['Object Count'] = df['Objects'].apply(len)

# Extract unique objects
all_objects = sum(df['Objects'].apply(lambda x: [obj.split()[1] for obj in x]), [])
unique_objects = list(set(all_objects))

for obj in unique_objects:
    df[obj] = df['Objects'].apply(lambda x: sum([int(item.split()[0]) if item.split()[1] == obj else 0 for item in x]))

df.drop(columns=['Objects'], inplace=True)

def main():
    # logo information
    cwd = os.getcwd()
    LOGO = os.path.join(cwd, 'YOLO.png')
    LOGO = base64.b64encode(open(LOGO, 'rb').read())
    LOGO = 'data:image/png;base64,{}'.format(LOGO.decode())
    # Add CSS styling for positioning
    st.markdown(
        """
        <style>
        .container {
            display: flex;
            justify-content: flex-end;  /* Align content to the right */
        }
        .logo-img {
            float: right;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Embed the logo image using HTML
    st.markdown(
        f"""
        <div class="container">
            <div class="logo-img">
                <img src={LOGO} alt="logo" width="280" height="110">
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # you can change the title here
    st.title("Object Detection Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df, use_container_width=True)
    fig1 = px.bar(df, 
                x='Filename', 
                y='Object Count',
                title='Objects Detected in Each Picture',
                labels={'Object Count': 'Count', 'Filename': 'Image Filename'},
                hover_data=['Object Count'],
                barmode='stack')
    fig1.update_layout(title={'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
    with col2:
        st.plotly_chart(fig1, use_container_width=True)

    col_names = df.columns[2:]
    fig2 = px.bar(df, x='Filename', y=col_names,
                    title='Each Object detected in Each Picture',
                    labels={'value': 'Count', 'Filename': 'Image Filename', 'variable': 'Object Type'},
                    hover_data=['Object Count'],
                    barmode='group',
                    ) 
    fig2.update_layout(title={'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        object_selected = st.selectbox('Select an object to view the count in each image', col_names)
        fig3 = px.pie(df, names='Filename', values=object_selected,
                        title=f'Number of Counts per image',
                        hover_data=['Object Count'])
        fig3.update_layout(title={'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'})
        fig3.update_layout(margin=dict(l=0, r=0, t=150, b=20))
        st.plotly_chart(fig3, use_container_width=True)



if __name__ == "__main__":
    main()