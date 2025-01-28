import pandas as pd
import streamlit as st
import plotly.express as px
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")

genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

data_path = 'Myntra_Analytics_Dataset.csv'
data = pd.read_csv(data_path)

st.title("Myntra E-commerce Analytics Dashboard")

st.sidebar.header("Filters")
selected_city = st.sidebar.multiselect("Select City", options=data['City'].unique(), default=data['City'].unique())
selected_gender = st.sidebar.multiselect("Select Gender", options=data['Gender'].unique(), default=data['Gender'].unique())

filtered_data = data[(data['City'].isin(selected_city)) & (data['Gender'].isin(selected_gender))]

st.header("Key Metrics")
total_sales = filtered_data['Price'].sum()
total_customers = filtered_data['Customer_ID'].nunique()
avg_browsing_time = filtered_data['Browsing_Time_mins'].mean()
cart_abandonment_rate = (filtered_data['Cart_Abandonment_Flag'].sum() / len(filtered_data)) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales (INR)", f"{total_sales:,.2f}")
col2.metric("Total Customers", total_customers)
col3.metric("Avg. Browsing Time (mins)", f"{avg_browsing_time:.2f}")
col4.metric("Cart Abandonment Rate (%)", f"{cart_abandonment_rate:.2f}")

# Sales by Product Category - Bar Chart
st.subheader("Sales by Product Category")
sales_by_category = filtered_data.groupby('Product_Category')['Price'].sum().reset_index()
fig1 = px.bar(sales_by_category, 
              x='Product_Category', 
              y='Price', 
              title="Sales by Product Category", 
              labels={'Price': 'Sales (INR)'})
fig1.update_layout(xaxis_title='Product Category', yaxis_title='Total Sales (INR)')
st.plotly_chart(fig1)

# Discounts vs Loyalty Points - Scatter Plot
st.subheader("Discounts vs Loyalty Points")
fig2 = px.scatter(filtered_data, 
                  x='Discount_Applied', 
                  y='Loyalty_Points_Earned', 
                  size='Price', 
                  color='Product_Category',
                  title="Discounts vs Loyalty Points", 
                  labels={'Discount_Applied': 'Discount Applied (INR)', 'Loyalty_Points_Earned': 'Loyalty Points Earned'})
fig2.update_layout(xaxis_title='Discount Applied (INR)', yaxis_title='Loyalty Points Earned')
st.plotly_chart(fig2)

# Cart Abandonment by Age Group - Line Chart
st.subheader("Cart Abandonment by Age Group")
abandonment_by_age = filtered_data.groupby('Age')['Cart_Abandonment_Flag'].mean().reset_index()
abandonment_by_age['Cart_Abandonment_Flag'] *= 100
fig3 = px.line(abandonment_by_age, 
               x='Age', 
               y='Cart_Abandonment_Flag', 
               title="Cart Abandonment Rate by Age Group", 
               labels={'Cart_Abandonment_Flag': 'Cart Abandonment Rate (%)'})
fig3.update_layout(xaxis_title='Age Group', yaxis_title='Abandonment Rate (%)')
st.plotly_chart(fig3)

# Payment Method Distribution - Pie Chart
st.subheader("Payment Method Distribution")
payment_distribution = filtered_data['Payment_Method'].value_counts().reset_index()
payment_distribution.columns = ['Payment Method', 'Count']
fig4 = px.pie(payment_distribution, 
              names='Payment Method', 
              values='Count', 
              title="Payment Method Distribution")
fig4.update_layout(title_text="Payment Method Distribution")
st.plotly_chart(fig4)

# GenAI Feedback Generation
st.header("Automated Insights from GenAI")

feedback_prompt = f"""
Generate a summary of the following insights based on the given data:

1. Total Sales (INR): {total_sales:,.2f}
2. Total Customers: {total_customers}
3. Average Browsing Time: {avg_browsing_time:.2f} minutes
4. Cart Abandonment Rate: {cart_abandonment_rate:.2f}%
5. Sales by Product Category: {', '.join([f'{row["Product_Category"]}: INR {row["Price"]:.2f}' for index, row in sales_by_category.iterrows()])}
6. Discounts vs Loyalty Points trends.
7. Cart Abandonment by Age Group trends.

Provide actionable insights and recommendations for improving sales, reducing cart abandonment, and increasing customer engagement. Also give KPI.
"""

# have fun :)
feedback_response = gemini_model.generate_content(feedback_prompt)
feedback = feedback_response.text

st.write(feedback)