import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def fetch_round_urls():
    url = "https://www.worldsbk.com/en/calendar"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX and 5XX status codes
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            round_links = {}
            for track_link in soup.find_all('a', class_='track-link'):
                round_name = track_link.text.strip()
                round_url = track_link['href']
                round_links[round_name] = round_url
            return round_links
        else:
            print("Failed to fetch the round URLs. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("An error occurred:", e)
        return None
    
def convert_timezone(dt_str, original_offset_hours, target_offset_hours):
    # Parse the datetime string
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S%z')
    # Convert to the target timezone
    dt += timedelta(hours=target_offset_hours - original_offset_hours)
    # Format the datetime as HH:MM
    return dt.strftime('%H:%M')




def clean_round_name(round_name):
    # Remove excess blank lines
    cleaned_name = re.sub(r'\n{2,}', '\n', round_name.strip())
    # Remove specific substrings
    cleaned_name = cleaned_name.replace("More info", "").replace("Buy tickets", "").strip()
    return cleaned_name


def fetch_schedule(round_url, target_offset_hours):
    url = f"https://www.worldsbk.com{round_url}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            schedules = []
            for day_index in range(3):  # Assuming days are indexed from 0 to 2
                day_id = f"day_{day_index}"
                day_schedule_element = soup.find('div', id=day_id)
                if day_schedule_element:
                    day_schedule_info = []
                    # Find all elements containing schedule information
                    schedule_items = day_schedule_element.find_all('div', class_='timeIso')
                    for schedule_item in schedule_items:
                        # Convert the start time to the target timezone
                        time_in = convert_timezone(schedule_item.find('div', {'data_ini': True}).get('data_ini'), 11, target_offset_hours)
                        # Convert the end time to the target timezone
                        time_out_tag = schedule_item.find('div', {'data_out': True})
                        time_out = convert_timezone(time_out_tag.get('data_out'), 11, target_offset_hours) if time_out_tag else ''
                        schedule_text = schedule_item.find('div', class_='cat-session').text.strip()
                        # Handle the case where end time is missing
                        if time_out:
                            day_schedule_info.append(f"{time_in} - {time_out} - {schedule_text}\n")
                        else:
                            day_schedule_info.append(f"{time_in} - {schedule_text}\n")
                    schedules.append(f"Day {day_index}:\n {' '.join(day_schedule_info)}")
                else:
                    print(f"No schedule found for Day {day_index}.")
            return schedules
        else:
            print("Failed to fetch the schedule. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("An error occurred:", e)
        return None



def main():
    round_urls = fetch_round_urls()
    target_offset_hours = +9  # Example target timezone
    if round_urls:
        # Print round options for user to choose
        print("Choose a round:")
        for idx, round_name in enumerate(round_urls.keys(), 1):
            cleaned_name = clean_round_name(round_name) 
            print(f"{idx}. {cleaned_name}\n")

        # Get user input for round selection
        choice = input("Enter the number of the round: ")
        try:
            choice = int(choice)
            round_names = list(round_urls.keys())
            if 1 <= choice <= len(round_names):
                selected_round_name = round_names[choice - 1]
                cleaned_round_name = clean_round_name(selected_round_name)
                selected_round_url = round_urls[selected_round_name]
                print(f"Fetching schedule for {cleaned_round_name}...")
                schedules = fetch_schedule(selected_round_url, target_offset_hours)
                if schedules:
                    print("Schedule:")
                    for schedule in schedules:
                        print(schedule)
                else:
                    print("Failed to fetch the schedule.")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    else:
        print("Failed to fetch round URLs.")


if __name__ == "__main__":
    main()
