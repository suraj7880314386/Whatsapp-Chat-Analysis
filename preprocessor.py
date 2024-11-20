import re
import pandas as pd


def preprocess(data):
    # Step 1: Replace non-breaking spaces and uncommon space types
    data = data.replace('\u202F', ' ').replace('\xa0', ' ')  # Non-breaking spaces and others

    # Step 2: Enhanced regex pattern to handle variations in formatting
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APM]+)\s-\s'

    # Step 3: Split messages and extract dates
    messages = re.split(pattern, data)[1:]  # Skip the first element, which is empty
    dates = re.findall(pattern, data)

    # Debugging output: Check if the messages and dates are split correctly
    print(f"Number of messages: {len(messages)}")
    print(f"Number of dates: {len(dates)}")

    # Check if messages and dates match
    if len(messages) != len(dates):
        print("Mismatch between dates and messages. Adjusting the data.")
        # If there is a mismatch, let's adjust based on possible formatting issues
        if len(messages) > len(dates):
            messages = messages[:len(dates)]  # Trim extra messages
        elif len(dates) > len(messages):
            dates = dates[:len(messages)]  # Trim extra dates

    # Create DataFrame from split data
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Step 4: Convert message_date to datetime format
    df['message_date'] = pd.to_datetime(df['message_date'], format='%m/%d/%y, %I:%M %p', errors='coerce')

    # Rename columns
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Step 5: Parse users and messages from user_message column
    users = []
    messages = []

    for message in df['user_message']:
        # Check if the message contains a user (using ':')
        if ": " in message:
            entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
            if len(entry) > 2:  # If split was successful, append user and message
                users.append(entry[1])  # Extract user
                messages.append(entry[2])  # Extract message content
            else:
                # If split failed (likely a system message), assign default
                users.append("group_notification")
                messages.append(message.strip())
        else:
            # Handle non-user messages (system notifications, etc.)
            users.append("group_notification")
            messages.append(message.strip())

    # Add parsed users and messages to DataFrame
    df['user'] = users
    df['message'] = messages

    # Step 6: Drop the original user_message column
    df.drop(columns=['user_message'], inplace=True)
    df = df[df['user'] != 'group_notification']

    # Step 7: Add additional date-related columns
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Step 8: Add period column (time ranges based on hour)
    period = []
    for hour in df['hour']:
        if pd.isna(hour):
            period.append("nan-nan")
        elif hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour + 1}")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period

    # Debugging output: Check final dataframe
    print(df.head())

    return df
