import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def count_total_users(day_df):
    total_users = day_df.query(str('date >= "2011-01-01" and date < "2012-12-31"'))
    return total_users

def trend_hour(hour_df):
    hourly_trend = hour_df.groupby(['date', 'hour'])['total_users'].sum().unstack()
    return hourly_trend

def trend_customers(day_df):
    trend = day_df.groupby('date')['total_users'].sum()
    return trend

def season_graph(hour_df):
    weather_counts = hour_df.groupby(by="weather_situation", observed=False).agg({"total_users": "count"})
    weather_counts.reset_index(inplace=True)
    return weather_counts

def time_group(hour):
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        return 'Peak'
    else:
        return 'Off-Peak'

def weather_group(weather_situation):
    if weather_situation in ['Clear', 'Partly Cloudy']:
        return 'Good Weather'
    else:
        return 'Bad Weather'

def usage_group(total_users):
    if total_users > 1000:
        return 'High Usage'
    elif 500 <= total_users <= 1000:
        return 'Moderate Usage'
    else:
        return 'Low Usage'

days_df = pd.read_csv("data_clean/clean_data_day.csv")
hours_df = pd.read_csv("data_clean/clean_data_hour.csv")



    


datetime_columns = ["date"]
days_df.sort_values(by="date", inplace=True)
days_df.reset_index(inplace=True)   

hours_df.sort_values(by="date", inplace=True)
hours_df.reset_index(inplace=True)

for column in datetime_columns:
    days_df[column] = pd.to_datetime(days_df[column])
    hours_df[column] = pd.to_datetime(hours_df[column])

min_date_days = days_df["date"].min()
max_date_days = days_df["date"].max()

min_date_hour = hours_df["date"].min()
max_date_hour = hours_df["date"].max()

with st.sidebar:
    
    st.image("https://i.pinimg.com/originals/2e/d1/15/2ed115c13891fd913afe5d2f32dfa85f.jpg")
    
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])
    
main_df_days = days_df[(days_df["date"] >= str(start_date)) & (days_df["date"] <= str(end_date))]

main_df_hour = hours_df[(hours_df["date"] >= str(start_date)) & (hours_df["date"] <= str(end_date))]


total_orders = count_total_users(main_df_days)
trend = trend_customers(main_df_days)
hour = trend_hour(main_df_hour)
season = season_graph(main_df_hour)

st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_users = total_orders.total_users.sum()
    st.metric("Total Sharing Bike", value=total_users)

with col2:
    total_users = total_orders.registered.sum()
    st.metric("Total regitered", value=total_users)

with col3:
    total_users = total_orders.casual.sum()
    st.metric("Total casual", value=total_users)

st.subheader("Pengaruh cuaca terhadap penyewaan sepeda:")

colors = ["#D3D3D3", "#72BCD4", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(
    y="total_users", 
    x="season",
    data=days_df.sort_values(by="season", ascending=False),
    palette=colors,
    hue="season",
    dodge=False,
    legend=False
)
ax.set_title("Number of Customer by Season", loc="center", fontsize=15)
ax.set_ylabel("Total Users")
ax.set_xlabel("Month")
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

st.subheader("Bagaimana tren penyewaan sepeda berdasarkan jam di sepanjang tahun?")


fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(hour.mean(axis=0).index, hour.mean(axis=0).values, marker='o', linewidth=2, color="#72BCD4")

ax.set_title('Average Hourly Bike Usage Trend Over the Year')
ax.set_xlabel('Hour')
ax.set_ylabel('Average Bike Users')
ax.set_xticks(range(0, 24))
ax.set_yticks(range(0, 600, 100))
st.pyplot(fig)

st.subheader("Bagaimana peforma penyewaan sepada per harinya?")

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(trend.index, trend.values, c="#90CAF9", s=10, marker='o')
ax.plot(trend.index, trend.values)
ax.set_title('Daily Bike Usage Trend Over the Year')
ax.set_xlabel('Date')
ax.set_ylabel('Total Bike Users')
st.pyplot(fig)

st.subheader("Pengaruh cuaca terhadap sewa")

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(season['weather_situation'], season['total_users'], color='#72BCD4')
ax.set_title('Total Users Based on Weather Situation')
ax.set_xlabel('Weather Situation')
ax.set_ylabel('Total Users')
ax.set_xticks(range(len(season['weather_situation']))) 
ax.set_xticklabels(season['weather_situation'], rotation=45)
ax.grid(axis='y')
st.pyplot(fig)

hours_df['Time Group'] = hours_df['hour'].apply(time_group)
hours_df['Weather Group'] = hours_df['weather_situation'].apply(weather_group)
hours_df['Usage Group'] = hours_df['total_users'].apply(usage_group)

st.subheader("Membuat group berdasarkan jam dan cuaca")

fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=hours_df, x='Time Group', hue='Weather Group')
ax.set_title('Distribution of Time Groups by Weather Conditions')
ax.set_ylabel('Number of Observations')
st.pyplot(fig)


st.subheader("Membuat group berdasarkan total users (Usage group)")

fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=hours_df, x='Usage Group', y='total_users')
ax.set_title('Total Users Across Different Usage Groups')
ax.set_ylabel('Total Users')
st.pyplot(fig)


st.subheader("Heatmap Correlations")

fig, ax = plt.subplots(figsize=(10, 6))
correlation_matrix = hours_df[['hour', 'temperature', 'humidity', 'wind_speed', 'casual', 'registered', 'total_users']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
ax.set_title('Heatmap of Feature Correlations')
st. pyplot(fig)